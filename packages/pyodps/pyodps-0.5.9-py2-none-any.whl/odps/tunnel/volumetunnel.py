#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

import sys
import struct

from requests.exceptions import StreamConsumedError

from . import io
from .router import TunnelServerRouter
from .checksum import Checksum
from .errors import TunnelError
from .. import serializers, options
from ..rest import RestClient
from ..models import Projects, errors
from ..compat import irange, urlparse, Enum, six
from ..utils import to_binary, to_text

MAX_CHUNK_SIZE = 256 * 1024 * 1024
MIN_CHUNK_SIZE = 1
CHECKSUM_SIZE = 4

CHECKSUM_PACKER = '>i' if six.PY2 else '>I'


class VolumeTunnel(object):
    def __init__(self, odps=None, client=None, project=None, endpoint=None):
        self._client = odps.rest if odps is not None else client
        self._account = self._client.account
        if project is None and odps is None:
            raise AttributeError('VolumeTunnel requires project parameter.')
        if isinstance(project, six.string_types):
            self._project = Projects(client=self._client)[project or odps.project]
        elif project is None:
            self._project = odps.get_project()
        else:
            self._project = project

        self._router = TunnelServerRouter(self._client)
        self._endpoint = endpoint or self._project._tunnel_endpoint

        self._tunnel_rest = None

    @property
    def endpoint(self):
        return self._endpoint

    @property
    def tunnel_rest(self):
        if self._tunnel_rest is not None:
            return self._tunnel_rest

        endpoint = self._endpoint
        if endpoint is None:
            scheme = urlparse(self._client.endpoint).scheme
            endpoint = self._router.get_tunnel_server(self._project, scheme)
        self._tunnel_rest = RestClient(self._account, endpoint, self._client.project)
        return self._tunnel_rest

    def create_download_session(self, volume, partition_spec, file_name, download_id=None, compress_option=None,
                                compress_algo=None, compress_level=None, compress_strategy=None):
        if not isinstance(volume, six.string_types):
            volume = volume.name
        volume = Projects(client=self.tunnel_rest)[self._project.name].volumes[volume]
        compress_option = compress_option
        if compress_option is None and compress_algo is not None:
            compress_option = io.CompressOption(
                compress_algo=compress_algo, level=compress_level, strategy=compress_strategy)

        return VolumeDownloadSession(self.tunnel_rest, volume, partition_spec, file_name, download_id=download_id,
                                     compress_option=compress_option)

    def create_upload_session(self, volume, partition_spec, upload_id=None, compress_option=None,
                              compress_algo=None, compres_level=None, compress_strategy=None):
        if not isinstance(volume, six.string_types):
            volume = volume.name
        volume = Projects(client=self.tunnel_rest)[self._project.name].volumes[volume]
        compress_option = compress_option
        if compress_option is None and compress_algo is not None:
            compress_option = io.CompressOption(
                compress_algo=compress_algo, level=compres_level, strategy=compress_strategy)

        return VolumeUploadSession(self.tunnel_rest, volume, partition_spec, upload_id=upload_id,
                                   compress_option=compress_option)


class VolumeDownloadSession(serializers.JSONSerializableModel):
    __slots__ = 'id', '_client', 'project_name', 'volume_name', 'partition_spec', 'file_name', '_compress_option'

    class Status(Enum):
        UNKNOWN = 'UNKNOWN'
        NORMAL = 'NORMAL'
        CLOSED = 'CLOSED'
        EXPIRED = 'EXPIRED'

    id = serializers.JSONNodeField('DownloadID')
    status = serializers.JSONNodeField('Status',
                                       parse_callback=lambda v: VolumeDownloadSession.Status(v.upper()))
    file_name = serializers.JSONNodeField('File', 'FileName')
    file_length = serializers.JSONNodeField('File', 'FileLength')
    volume_name = serializers.JSONNodeField('Partition', 'Volume')
    partition_spec = serializers.JSONNodeField('Partition', 'Partition')

    def __init__(self, client, volume, partition_spec, file_name=None, download_id=None, compress_option=None):
        super(VolumeDownloadSession, self).__init__()

        self._client = client
        self._compress_option = compress_option
        self.project_name = volume.project.name
        self.volume_name = volume.name
        self.partition_spec = partition_spec
        self.file_name = file_name

        if download_id is None:
            self._init()
        else:
            self.id = download_id
            self.reload()

    def resource(self):
        return self._client.endpoint + '/projects/%s/tunnel/downloads' % self.project_name

    def _init(self):
        headers = {'Content-Length': '0'}
        params = dict(type='volumefile', target='/'.join([self.project_name, self.volume_name,
                                                          self.partition_spec, self.file_name]))

        url = self.resource()
        resp = self._client.post(url, {}, params=params, headers=headers)
        if self._client.is_ok(resp):
            self.parse(resp, obj=self)
        else:
            e = TunnelError.parse(resp)
            raise e

    def reload(self):
        headers = {'Content-Length': '0'}
        params = {}

        if self._partition_spec is not None and len(self._partition_spec) > 0:
            params['partition'] = self._partition_spec

        url = self.resource() + '/' + str(self.id)
        resp = self._client.get(url, params=params, headers=headers)
        if self._client.is_ok(resp):
            self.parse(resp, obj=self)
        else:
            e = TunnelError.parse(resp)
            raise e

    def open(self, start=0, length=sys.maxsize, compress=False):
        compress_option = self._compress_option or io.CompressOption()

        params = {}

        headers = {'Content-Length': 0, 'x-odps-tunnel-version': 4}
        if compress:
            if compress_option.algorithm == io.CompressOption.CompressAlgorithm.ODPS_ZLIB:
                headers['Accept-Encoding'] = 'deflate'
            elif compress_option.algorithm != io.CompressOption.CompressAlgorithm.ODPS_RAW:
                raise TunnelError('invalid compression option')

        params['data'] = ''
        params['range'] = '(%s,%s)' % (start, length)

        url = self.resource()
        resp = self._client.get(url + '/' + self.id, params=params, headers=headers, stream=True)
        if not self._client.is_ok(resp):
            e = TunnelError.parse(resp)
            raise e

        content_encoding = resp.headers.get('Content-Encoding')
        if content_encoding is not None:
            if content_encoding == 'deflate':
                self._compress_option = io.CompressOption(
                    io.CompressOption.CompressAlgorithm.ODPS_ZLIB, -1, 0)
            else:
                raise TunnelError('Invalid content encoding')
            compress = True
        else:
            compress = False

        option = compress_option if compress else None
        return VolumeReader(self._client, resp, option)


class VolumeReader(object):
    def __init__(self, client, response, compress_option):
        self._client = client
        self._response = response.raw
        self._compress_option = compress_option
        self._crc = Checksum(method='crc32')
        self._buffer_size = 0
        self._initialized = False
        self._last_line_ending = None
        self._eof = False

        # buffer part left by sized read or read-line operation, see read()
        self._left_part = None
        self._left_part_pos = 0

        # left part of checksum block when chunked, see _read_buf()
        self._chunk_left = None

    def _init_buf(self):
        size_buf = self._response.read(4)
        if not size_buf:
            raise IOError('Tunnel reader breaks unexpectedly.')
        self._crc.update(size_buf)
        chunk_size = struct.unpack('>I', size_buf)[0]
        if chunk_size > MAX_CHUNK_SIZE or chunk_size < MIN_CHUNK_SIZE:
            raise IOError("ChunkSize should be in [%d, %d], now is %d." % (MIN_CHUNK_SIZE, MAX_CHUNK_SIZE, chunk_size))
        self._buffer_size = CHECKSUM_SIZE + chunk_size

    def _read_buf(self):
        has_stuff = False

        data_buffer = six.BytesIO()
        if self._chunk_left:
            # we have cached chunk left, add to buffer
            data_buffer.write(self._chunk_left)
            self._chunk_left = None
        while data_buffer.tell() < self._buffer_size:
            try:
                # len(buf) might be less than _buffer_size
                buf = self._response.read(self._buffer_size)
                if not buf:
                    break
                data_buffer.write(buf)
                has_stuff = True
            except StopIteration:
                break
            except StreamConsumedError:
                break
        if not has_stuff:
            return None

        # check if we need to store the rest part.
        if data_buffer.tell() <= self._buffer_size:
            buf = data_buffer.getvalue()
        else:
            buf_all = data_buffer.getvalue()
            buf, self._chunk_left = buf_all[:self._buffer_size], buf_all[self._buffer_size:]

        if len(buf) >= CHECKSUM_SIZE:
            self._data_size = len(buf) - CHECKSUM_SIZE
            self._crc.update(buf[:self._data_size])
            checksum = struct.unpack_from(CHECKSUM_PACKER, buf, self._data_size)[0]
            if checksum != self._crc.getvalue():
                raise IOError('CRC check error in VolumeReader.')
        else:
            raise IOError('Invalid VolumeReader.')
        return bytearray(buf[:self._data_size])

    def read(self, size=sys.maxsize, break_line=False):
        if self._eof:
            return None
        if size == 0:
            return six.binary_type()

        if not self._initialized:
            self._initialized = True
            self._init_buf()

        has_stuff = False

        out_buf = six.BytesIO()
        if self._left_part:
            if break_line:
                # deal with Windows line endings
                if self._left_part[self._left_part_pos] == ord('\n') and self._last_line_ending == ord('\r'):
                    self._last_line_ending = None
                    self._left_part_pos += 1

                for idx in irange(self._left_part_pos, len(self._left_part)):
                    if self._left_part[idx] not in (ord('\r'), ord('\n')):
                        continue
                    self._last_line_ending = self._left_part[idx]
                    self._left_part[idx] = ord('\n')
                    ret = self._left_part[self._left_part_pos:idx + 1]
                    self._left_part_pos = idx + 1
                    if self._left_part_pos == len(self._left_part):
                        self._left_part = None
                        self._left_part_pos = 0
                    return bytes(ret)
            if len(self._left_part) - self._left_part_pos >= size:
                ret = self._left_part[self._left_part_pos:self._left_part_pos + size]
                self._left_part_pos += size
                return bytes(ret)
            else:
                out_buf.write(bytes(self._left_part[self._left_part_pos:]))
                self._left_part = None
                self._left_part_pos = 0
                has_stuff = True
        length_left = size - out_buf.tell()
        while length_left > 0:
            buf = self._read_buf()
            if buf is None:
                self._eof = True
                break
            has_stuff = True
            start_pos = 0
            if break_line:
                if buf[0] == ord('\n') and self._last_line_ending == ord('\r'):
                    start_pos = 1
                for idx in irange(start_pos, len(buf)):
                    if buf[idx] not in (ord('\r'), ord('\n')):
                        continue
                    self._last_line_ending = buf[idx]
                    buf[idx] = ord('\n')
                    out_buf.write(bytes(buf[start_pos:idx + 1]))
                    if idx + 1 < len(buf):
                        self._left_part = buf[idx + 1:]
                        self._left_part_pos = 0
                    return out_buf.getvalue()

            if len(buf) >= length_left:
                out_buf.write(bytes(buf[start_pos:length_left]))
                length_left = 0
                if len(buf) > length_left:
                    self._left_part = buf[length_left:]
                    self._left_part_pos = 0
            else:
                out_buf.write(bytes(buf[start_pos:self._data_size]))
                length_left -= len(buf)
        return out_buf.getvalue() if has_stuff else None

    def _it(self, size=sys.maxsize, encoding='utf-8'):
        while True:
            line = self.readline(size, encoding=encoding)
            if line is None:
                break
            yield line

    def readline(self, size=sys.maxsize, encoding='utf-8'):
        line = self.read(size, break_line=True)
        return to_text(line, encoding=encoding)

    def readlines(self, size=sys.maxsize, encoding='utf-8'):
        return [line for line in self._it(size, encoding=encoding)]

    def __iter__(self):
        return self._it()


class VolumeUploadSession(serializers.JSONSerializableModel):
    __slots__ = 'id', '_client', '_compress_option', 'project_name', 'volume_name', 'partition_spec'

    class Status(Enum):
        UNKNOWN = 'UNKNOWN'
        NORMAL = 'NORMAL'
        CLOSING = 'CLOSING'
        CLOSED = 'CLOSED'
        CANCELED = 'CANCELED'
        EXPIRED = 'EXPIRED'
        CRITICAL = 'CRITICAL'

    class UploadFile(serializers.JSONSerializableModel):
        file_name = serializers.JSONNodeField('FileName')
        file_length = serializers.JSONNodeField('FileLength')

    id = serializers.JSONNodeField('UploadID')
    status = serializers.JSONNodeField('Status',
                                       parse_callback=lambda v: VolumeUploadSession.Status(v.upper()))
    file_list = serializers.JSONNodesReferencesField(UploadFile, 'FileList')

    def __init__(self, client, volume, partition_spec, upload_id=None, compress_option=None):
        super(VolumeUploadSession, self).__init__()

        self._client = client
        self._compress_option = compress_option
        self.project_name = volume.project.name
        self.volume_name = volume.name
        self.partition_spec = partition_spec

        if upload_id is None:
            self._init()
        else:
            self.id = upload_id
            self.reload()
        self._compress_option = compress_option

    def resource(self):
        return self._client.endpoint + '/projects/%s/tunnel/uploads' % self.project_name

    def _init(self):
        headers = {'Content-Length': '0'}
        params = dict(type='volumefile', target='/'.join([self.project_name, self.volume_name,
                                                          self.partition_spec]) + '/')

        url = self.resource()
        resp = self._client.post(url, {}, params=params, headers=headers)
        if self._client.is_ok(resp):
            self.parse(resp, obj=self)
        else:
            e = TunnelError.parse(resp)
            raise e

    def reload(self):
        headers = {'Content-Length': '0'}
        params = {}

        url = self.resource() + '/' + str(self.id)
        resp = self._client.get(url, params=params, headers=headers)
        if self._client.is_ok(resp):
            self.parse(resp, obj=self)
        else:
            e = TunnelError.parse(resp)
            raise e

    @staticmethod
    def _format_file_name(file_name):
        buf = six.StringIO()
        if file_name and file_name[0] == '/':
            raise TunnelError("FileName cann't start with '/', file name is " + file_name)
        pre_slash = False
        for ch in file_name:
            if ch == '/':
                if not pre_slash:
                    buf.write(ch)
                pre_slash = True
            else:
                buf.write(ch)
                pre_slash = False
        return buf.getvalue()

    def open(self, file_name, compress=False, append=False):
        compress_option = self._compress_option or io.CompressOption()
        headers = {'Content-Type': 'test/plain', 'Transfer-Encoding': 'chunked', 'x-odps-tunnel-version': 4}
        params = {}

        if compress:
            if compress_option.algorithm == io.CompressOption.CompressAlgorithm.ODPS_ZLIB:
                headers['Content-Encoding'] = 'deflate'
            elif compress_option.algorithm != io.CompressOption.CompressAlgorithm.ODPS_RAW:
                raise TunnelError('invalid compression option')

        file_name = self._format_file_name(file_name)
        params['blockid'] = file_name
        if append:
            params['resume'] = ''

        url = self.resource() + '/' + self.id

        chunk_upload = lambda data: self._client.post(url, data=data, params=params, headers=headers)
        option = compress_option if compress else None
        return VolumeWriter(self._client, chunk_upload, option)

    def commit(self, files):
        if not files:
            raise AttributeError('Invalid argument: files')
        if isinstance(files, six.string_types):
            files = [files, ]
        formatted = [self._format_file_name(fn) for fn in files]

        self.reload()
        files_uploading = set(f.file_name for f in self.file_list)

        if len(files_uploading) != len(formatted):
            raise TunnelError("File number not match, server: %d, client: %d" % (len(files_uploading), len(formatted)))
        for fn in (fn for fn in formatted if fn not in files_uploading):
            raise TunnelError("File not exits on server, file name is " + fn)

        self._complete_upload()

    def _complete_upload(self):
        headers = {'Content-Length': '0'}
        params = {}

        url = self.resource() + '/' + self.id
        resp = self._client.put(url, {}, params=params, headers=headers)
        if self._client.is_ok(resp):
            self.parse(resp, obj=self)
        else:
            e = TunnelError.parse(resp)
            raise e


class VolumeWriter(object):
    CHUNK_SIZE = 512 * 1024

    def __init__(self, client, uploader, compress_option):
        self._client = client
        self._compress_option = compress_option
        self._req_io = io.RequestsIO(uploader, chunk_size=options.chunk_size)

        if compress_option is None:
            self._writer = self._req_io
        elif compress_option.algorithm == \
                io.CompressOption.CompressAlgorithm.ODPS_RAW:
            self._writer = self._req_io
        elif compress_option.algorithm == \
                io.CompressOption.CompressAlgorithm.ODPS_ZLIB:
            self._writer = io.DeflateOutputStream(self._req_io)
        else:
            raise errors.InvalidArgument('Invalid compression algorithm.')

        self._crc = Checksum(method='crc32')
        self._initialized = False
        self._chunk_offset = 0

    def _init_writer(self):
        chunk_bytes = struct.pack('>I', self.CHUNK_SIZE)
        self._writer.write(chunk_bytes)
        self._crc.update(chunk_bytes)
        self._chunk_offset = 0

    def write(self, buf, encoding='utf-8'):
        buf = to_binary(buf, encoding=encoding)
        if isinstance(buf, six.integer_types):
            buf = bytes(bytearray([buf, ]))
        elif isinstance(buf, six.BytesIO):
            buf = buf.getvalue()
        if not self._initialized:
            self._initialized = True
            self._init_writer()
            self._req_io.start()

        if not buf:
            raise IOError('Invalid data buffer!')
        processed = 0
        while processed < len(buf):
            if self._chunk_offset == self.CHUNK_SIZE:
                checksum = self._crc.getvalue()
                self._writer.write(struct.pack(CHECKSUM_PACKER, checksum))
                self._chunk_offset = 0
            else:
                size = self.CHUNK_SIZE - self._chunk_offset if len(buf) - processed > self.CHUNK_SIZE - self._chunk_offset\
                    else len(buf) - processed
                write_chunk = buf[processed:processed + size]
                self._writer.write(write_chunk)
                self._crc.update(write_chunk)
                processed += size
                self._chunk_offset += size

    def close(self):
        if not self._initialized:
            self._initialized = True
            self._init_writer()

        if self._chunk_offset != 0:
            checksum = self._crc.getvalue()
            self._writer.write(struct.pack(CHECKSUM_PACKER, checksum))
        self._writer.flush()
        result = self._req_io.finish()
        if result is None:
            raise TunnelError('No results returned in VolumeWriter.')
        if not self._client.is_ok(result):
            e = TunnelError.parse(result)
            raise e

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()
