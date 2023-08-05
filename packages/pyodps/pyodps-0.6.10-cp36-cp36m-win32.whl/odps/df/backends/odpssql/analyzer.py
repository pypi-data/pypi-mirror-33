#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 1999-2017 Alibaba Group Holding Ltd.
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#      http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import re
import sys
import itertools

from ..core import Backend
from ...expr.arithmetic import *
from ...expr.math import *
from ...expr.datetimes import *
from ...expr.strings import *
from ...expr.element import *
from ...expr.reduction import *
from ...expr.collections import *
from ...expr.merge import *
from ...utils import output, traverse_until_source
from ..errors import CompileError
from ..utils import refresh_dynamic
from ... import types
from .... import compat


class Analyzer(Backend):
    """
    Analyzer is used before optimzing,
    which analyze some operation that is not supported for this execution backend.
    """

    def __init__(self, expr_dag, traversed=None, on_sub=None):
        self._dag = expr_dag
        self._indexer = itertools.count(0)
        self._traversed = traversed or set()
        self._on_sub = on_sub

    def analyze(self):
        for node in self._iter():
            self._traversed.add(id(node))
            self._visit_node(node)

        return self._dag.root

    def _iter(self):
        for node in traverse_until_source(self._dag, top_down=True,
                                          traversed=self._traversed):
            yield node

        while True:
            all_traversed = True
            for node in traverse_until_source(self._dag, top_down=True):
                if id(node) not in self._traversed:
                    all_traversed = False
                    yield node
            if all_traversed:
                break

    def _visit_node(self, node):
        try:
            node.accept(self)
        except NotImplementedError:
            return

    def _sub(self, expr, sub, parents=None):
        self._dag.substitute(expr, sub, parents=parents)
        if self._on_sub:
            self._on_sub(expr, sub)

    def _parents(self, expr):
        return self._dag.successors(expr)

    def _visit_cut(self, expr):
        is_seq = isinstance(expr, SequenceExpr)
        kw = dict()
        if is_seq:
            kw['_data_type'] = expr.dtype
        else:
            kw['_value_type'] = expr.dtype

        conditions = []
        thens = []

        if expr.include_under:
            bin = expr.bins[0]
            if expr.right and not expr.include_lowest:
                conditions.append(expr.input <= bin)
            else:
                conditions.append(expr.input < bin)
            thens.append(expr.labels[0])
        for i, bin in enumerate(expr.bins[1:]):
            lower_bin = expr.bins[i]
            if not expr.right or (i == 0 and expr.include_lowest):
                condition = lower_bin <= expr.input
            else:
                condition = lower_bin < expr.input

            if expr.right:
                condition = (condition & (expr.input <= bin))
            else:
                condition = (condition & (expr.input < bin))

            conditions.append(condition)
            if expr.include_under:
                thens.append(expr.labels[i + 1])
            else:
                thens.append(expr.labels[i])
        if expr.include_over:
            bin = expr.bins[-1]
            if expr.right:
                conditions.append(bin < expr.input)
            else:
                conditions.append(bin <= expr.input)
            thens.append(expr.labels[-1])

        sub = Switch(_conditions=conditions, _thens=thens, **kw)
        self._sub(expr, sub)

    def visit_element_op(self, expr):
        if isinstance(expr, Between):
            if expr.inclusive:
                sub = ((expr.left <= expr.input) & (expr.input.copy() <= expr.right))
            else:
                sub = ((expr.left < expr.input) & (expr.input.copy() < expr.right))
            self._sub(expr, sub.rename(expr.name))
        elif isinstance(expr, Cut):
            self._visit_cut(expr)
        else:
            raise NotImplementedError

    def visit_sample(self, expr):
        if expr._parts is None:
            raise CompileError('ODPS SQL only support sampling by specifying `parts` arg')

        idxes = [None, ] if expr._i is None else expr._i

        condition = None
        for idx in idxes:
            inputs = [expr._parts]
            if idx is not None:
                new_val = idx.value + 1
                inputs.append(Scalar(_value=new_val, _value_type=idx.value_type))
            if expr._sampled_fields:
                inputs.extend(expr._sampled_fields)
            cond = MappedExpr(_inputs=inputs, _func='SAMPLE', _data_type=types.boolean)
            if condition is None:
                condition = cond
            else:
                condition |= cond
        sub = FilterCollectionExpr(_input=expr.input, _predicate=condition,
                                   _schema=expr.schema)
        expr.input.optimize_banned = True

        self._sub(expr, sub)

    def _visit_pivot(self, expr):
        columns_expr = expr.input.distinct([c.copy() for c in expr._columns])

        group_names = [g.name for g in expr._group]
        group_types = [g.dtype for g in expr._group]
        exprs = [expr]

        def callback(result, new_expr):
            expr = exprs[0]
            columns = [r[0] for r in result]

            if len(expr._values) > 1:
                names = group_names + \
                    ['{0}_{1}'.format(v.name, c)
                     for v in expr._values for c in columns]
                types = group_types + \
                        list(itertools.chain(*[[n.dtype] * len(columns)
                                               for n in expr._values]))
            else:
                names = group_names + columns
                types = group_types + [expr._values[0].dtype] * len(columns)
            new_expr._schema = Schema.from_lists(names, types)

            column_name = expr._columns[0].name  # column's size can only be 1
            values_names = [v.name for v in expr._values]

            @output(names, types)
            def reducer(keys):
                values = [None] * len(columns) * len(values_names)

                def h(row, done):
                    col = getattr(row, column_name)
                    for val_idx, value_name in enumerate(values_names):
                        val = getattr(row, value_name)
                        idx = len(columns) * val_idx + columns.index(col)
                        if values[idx] is not None:
                            raise ValueError('Row contains duplicate entries')
                        values[idx] = val
                    if done:
                        yield keys + tuple(values)

                return h

            fields = expr._group + expr._columns + expr._values
            pivoted = expr.input.select(fields).map_reduce(reducer=reducer, group=group_names)
            self._sub(new_expr, pivoted)

            # trigger refresh of dynamic operations
            refresh_dynamic(pivoted, self._dag)

        sub = CollectionExpr(_schema=DynamicSchema.from_lists(group_names, group_types),
                             _deps=[(columns_expr, callback)])
        self._sub(expr, sub)

    def _visit_pivot_table_without_columns(self, expr):
        def get_agg(field, agg_func, agg_func_name, fill_value):
            if isinstance(agg_func, six.string_types):
                aggregated = getattr(field, agg_func)()
            else:
                aggregated = field.agg(agg_func)
            if fill_value is not None:
                aggregated.fillna(fill_value)
            return aggregated.rename('{0}_{1}'.format(field.name, agg_func_name))

        grouped = expr.input.groupby(expr._group)
        aggs = []
        for agg_func, agg_func_name in zip(expr._agg_func, expr._agg_func_names):
            for value in expr._values:
                agg = get_agg(value, agg_func, agg_func_name, expr.fill_value)
                aggs.append(agg)
        sub = grouped.aggregate(aggs, sort_by_name=False)

        self._sub(expr, sub)

    def _visit_pivot_table_with_columns(self, expr):
        columns_expr = expr.input.distinct([c.copy() for c in expr._columns])

        group_names = [g.name for g in expr._group]
        group_types = [g.dtype for g in expr._group]
        exprs = [expr]

        def callback(result, new_expr):
            expr = exprs[0]
            columns = [r[0] for r in result]

            names = list(group_names)
            tps = list(group_types)
            aggs = []
            for agg_func_name, agg_func in zip(expr._agg_func_names, expr._agg_func):
                for value_col in expr._values:
                    for col in columns:
                        base = '{0}_'.format(col) if col is not None else ''
                        name = '{0}{1}_{2}'.format(base, value_col.name, agg_func_name)
                        names.append(name)
                        tps.append(value_col.dtype)

                        field = (expr._columns[0] == col).ifelse(
                            value_col, Scalar(_value_type=value_col.dtype))
                        if isinstance(agg_func, six.string_types):
                            agg = getattr(field, agg_func)()
                        else:
                            func = agg_func()

                            class ActualAgg(object):
                                def buffer(self):
                                    return func.buffer()

                                def __call__(self, buffer, value):
                                    if value is None:
                                        return
                                    func(buffer, value)

                                def merge(self, buffer, pbuffer):
                                    func.merge(buffer, pbuffer)

                                def getvalue(self, buffer):
                                    return func.getvalue(buffer)

                            agg = field.agg(ActualAgg)
                        if expr.fill_value is not None:
                            agg = agg.fillna(expr.fill_value)
                        agg = agg.rename(name)
                        aggs.append(agg)

            new_expr._schema = Schema.from_lists(names, tps)

            pivoted = expr.input.groupby(expr._group).aggregate(aggs, sort_by_name=False)
            self._sub(new_expr, pivoted)

            # trigger refresh of dynamic operations
            refresh_dynamic(pivoted, self._dag)

        sub = CollectionExpr(_schema=DynamicSchema.from_lists(group_names, group_types),
                             _deps=[(columns_expr, callback)])
        self._sub(expr, sub)

    def _visit_pivot_table(self, expr):
        if expr._columns is None:
            self._visit_pivot_table_without_columns(expr)
        else:
            self._visit_pivot_table_with_columns(expr)

    def visit_pivot(self, expr):
        if isinstance(expr, PivotCollectionExpr):
            self._visit_pivot(expr)
        else:
            self._visit_pivot_table(expr)

    def visit_extract_kv(self, expr):
        kv_delimiter = expr._kv_delimiter.value
        item_delimiter = expr._item_delimiter.value
        default = expr._default.value if expr._default else None

        class KeyAgg(object):
            def buffer(self):
                return set()

            def __call__(self, buf, val):
                if not val:
                    return

                def validate_kv(v):
                    parts = v.split(kv_delimiter)
                    if len(parts) != 2:
                        raise ValueError('Malformed KV pair: %s' % v)
                    return parts[0]

                buf.update([validate_kv(item) for item in val.split(item_delimiter)])

            def merge(self, buf, pbuffer):
                buf.update(pbuffer)

            def getvalue(self, buf):
                return item_delimiter.join(sorted(buf))

        columns_expr = expr.input.exclude(expr._intact).apply(KeyAgg, names=[c.name for c in expr._columns])

        intact_names = [g.name for g in expr._intact]
        intact_types = [g.dtype for g in expr._intact]
        exprs = [expr]

        def callback(result, new_expr):
            expr = exprs[0]

            names = list(intact_names)
            tps = list(intact_types)
            kv_slot_map = dict()

            for col, key_str in compat.izip(result.columns, result[0]):
                kv_slot_map[col.name] = dict()
                for k in key_str.split(item_delimiter):
                    names.append('%s_%s' % (col.name, k))
                    tps.append(expr._column_type)
                    kv_slot_map[col.name][k] = len(names) - 1
            kv_slot_names = list(kv_slot_map.keys())

            type_adapter = None
            if isinstance(expr._column_type, types.Float):
                type_adapter = float
            elif isinstance(expr._column_type, types.Integer):
                type_adapter = int

            @output(names, tps)
            def mapper(row):
                ret = [default, ] * len(names)
                ret[:len(intact_names)] = [getattr(row, col) for col in intact_names]
                for col in kv_slot_names:
                    kv_val = getattr(row, col)
                    if not kv_val:
                        continue
                    for kv_item in kv_val.split(item_delimiter):
                        k, v = kv_item.split(kv_delimiter)
                        if type_adapter:
                            v = type_adapter(v)
                        ret[kv_slot_map[col][k]] = v
                return tuple(ret)

            new_expr._schema = Schema.from_lists(names, tps)

            extracted = expr.input.map_reduce(mapper)
            self._sub(new_expr, extracted)

            # trigger refresh of dynamic operations
            refresh_dynamic(extracted, self._dag)

        sub = CollectionExpr(_schema=DynamicSchema.from_lists(intact_names, intact_types),
                             _deps=[(columns_expr, callback)])
        self._sub(expr, sub)

    def visit_value_counts(self, expr):
        collection = expr.input
        by = expr._by
        sort = expr._sort.value

        sub = collection.groupby(by).agg(count=by.count())
        if sort:
            sub = sub.sort('count', ascending=False)
        self._sub(expr, sub)

    def _gen_mapped_expr(self, expr, inputs, func, name,
                         args=None, kwargs=None, multiple=False):
        kwargs = dict(_inputs=inputs, _func=func, _name=name,
                      _func_args=args, _func_kwargs=kwargs,
                      _multiple=multiple)
        if isinstance(expr, SequenceExpr):
            kwargs['_data_type'] = expr.dtype
        else:
            kwargs['_value_type'] = expr.dtype
        return MappedExpr(**kwargs)

    def visit_binary_op(self, expr):
        if not options.df.analyze:
            raise NotImplementedError

        if isinstance(expr, FloorDivide):
            func = lambda l, r: l // r
            # multiple False will pass *args instead of namedtuple
            sub = self._gen_mapped_expr(expr, (expr.lhs, expr.rhs),
                                        func, expr.name, multiple=False)
            self._sub(expr, sub)
            return
        if isinstance(expr, Mod):
            func = lambda l, r: l % r
            sub = self._gen_mapped_expr(expr, (expr.lhs, expr.rhs),
                                        func, expr.name, multiple=False)
            self._sub(expr, sub)
            return
        if isinstance(expr, Add) and \
                all(child.dtype == types.datetime for child in (expr.lhs, expr.rhs)):
            return
        elif isinstance(expr, (Add, Substract)):
            if expr.lhs.dtype == types.datetime and expr.rhs.dtype == types.datetime:
                pass
            elif any(isinstance(child, MilliSecondScalar) for child in (expr.lhs, expr.rhs)):
                pass
            else:
                return

            if sys.version_info[:2] <= (2, 6):
                def total_seconds(self):
                    return self.days * 86400.0 + self.seconds + self.microseconds * 1.0e-6
            else:
                from datetime import timedelta
                def total_seconds(self):
                    return self.total_seconds()

            def func(l, r, method):
                from datetime import datetime, timedelta
                if not isinstance(l, datetime):
                    l = timedelta(milliseconds=l)
                if not isinstance(r, datetime):
                    r = timedelta(milliseconds=r)

                if method == '+':
                    res = l + r
                else:
                    res = l - r
                if isinstance(res, timedelta):
                    return int(total_seconds(res) * 1000)
                return res

            inputs = expr.lhs, expr.rhs, Scalar('+') if isinstance(expr, Add) else Scalar('-')
            sub = self._gen_mapped_expr(expr, inputs, func, expr.name, multiple=False)
            self._sub(expr, sub)

        raise NotImplementedError

    def visit_unary_op(self, expr):
        if not options.df.analyze:
            raise NotImplementedError

        if isinstance(expr, Invert) and isinstance(expr.input.dtype, types.Integer):
            sub = expr.input.map(lambda x: ~x)
            self._sub(expr, sub)
            return

        raise NotImplementedError

    def visit_math(self, expr):
        if not options.df.analyze:
            raise NotImplementedError

        if expr.dtype != types.decimal:
            if isinstance(expr, Arccosh):
                def func(x):
                    import numpy as np
                    return float(np.arccosh(x))
            elif isinstance(expr, Arcsinh):
                def func(x):
                    import numpy as np
                    return float(np.arcsinh(x))
            elif isinstance(expr, Arctanh):
                def func(x):
                    import numpy as np
                    return float(np.arctanh(x))
            elif isinstance(expr, Radians):
                def func(x):
                    import numpy as np
                    return float(np.radians(x))
            elif isinstance(expr, Degrees):
                def func(x):
                    import numpy as np
                    return float(np.degrees(x))
            else:
                raise NotImplementedError

            sub = expr.input.map(func, expr.dtype)
            self._sub(expr, sub)
            return

        raise NotImplementedError

    def visit_datetime_op(self, expr):
        if isinstance(expr, Strftime):
            if not options.df.analyze:
                raise NotImplementedError

            date_format = expr.date_format

            def func(x):
                return x.strftime(date_format)

            sub = expr.input.map(func, expr.dtype)
            self._sub(expr, sub)
            return

        raise NotImplementedError

    def visit_string_op(self, expr):
        if isinstance(expr, Ljust):
            rest = expr.width - expr.input.len()
            sub = expr.input + \
                     (rest >= 0).ifelse(expr._fillchar.repeat(rest), '')
            self._sub(expr, sub.rename(expr.name))
            return
        elif isinstance(expr, Rjust):
            rest = expr.width - expr.input.len()
            sub = (rest >= 0).ifelse(expr._fillchar.repeat(rest), '') + expr.input
            self._sub(expr, sub.rename(expr.name))
            return
        elif isinstance(expr, Zfill):
            fillchar = Scalar('0')
            rest = expr.width - expr.input.len()
            sub = (rest >= 0).ifelse(fillchar.repeat(rest), '') + expr.input
            self._sub(expr, sub.rename(expr.name))
            return
        elif isinstance(expr, CatStr):
            input = expr.input
            others = expr._others if isinstance(expr._others, Iterable) else (expr._others, )
            for other in others:
                if expr.na_rep is not None:
                    for e in (input, ) + tuple(others):
                        self._sub(e, e.fillna(expr.na_rep), parents=(expr, ))
                    return
                else:
                    if expr._sep is not None:
                        input = other.isnull().ifelse(input, input + expr._sep + other)
                    else:
                        input = other.isnull().ifelse(input, input + other)
            self._sub(expr, input.rename(expr.name))
            return

        if not options.df.analyze:
            raise NotImplementedError

        func = None
        if isinstance(expr, Contains) and (not expr.case or expr.flags > 0):
            flags = 0
            if not expr.case:
                flags = re.I
            if expr.flags > 0:
                flags = flags | expr.flags
            pat = re.escape(expr.pat)

            def func(x):
                r = re.compile(pat, flags)
                return r.search(x) is not None
        elif isinstance(expr, Find) and expr.end is not None:
            start = expr.start
            end = expr.end
            substr = expr.sub

            def func(x):
                return x.find(substr, start, end)
        elif isinstance(expr, RFind):
            start = expr.start
            end = expr.end
            substr = expr.sub

            def func(x):
                return x.rfind(substr, start, end)
        elif isinstance(expr, Extract):
            def func(x, pat, flags, group):
                regex = re.compile(pat, flags=flags)
                m = regex.search(x)
                if m:
                    if group is None:
                        return m.group()
                    return m.group(group)

            pat = expr._pat if not isinstance(expr._pat, StringScalar) or expr._pat._value is None \
                else Scalar(re.escape(expr.pat))
            inputs = expr.input, pat, expr._flags, expr._group
            sub = self._gen_mapped_expr(expr, inputs, func,
                                        expr.name, multiple=False)
            self._sub(expr, sub)
        elif isinstance(expr, Replace):
            def func(x, pat, repl, n, case, flags):
                use_re = not case or len(pat) > 1 or flags

                if use_re:
                    if not case:
                        flags |= re.IGNORECASE
                    regex = re.compile(pat, flags=flags)
                    n = n if n >= 0 else 0

                    return regex.sub(repl, x, count=n)
                else:
                    return x.replace(pat, repl, n)

            pat = expr._pat if not isinstance(expr._pat, StringScalar) or expr._value is None \
                else Scalar(re.escape(expr.pat))
            inputs = expr.input, pat, expr._repl, expr._n, \
                     expr._case, expr._flags
            sub = self._gen_mapped_expr(expr, inputs, func,
                                        expr.name, multiple=False)
            self._sub(expr, sub)
        elif isinstance(expr, (Lstrip, Strip, Rstrip)) and expr.to_strip != ' ':
            to_strip = expr.to_strip

            if isinstance(expr, Lstrip):
                def func(x):
                    return x.lstrip(to_strip)
            elif isinstance(expr, Strip):
                def func(x):
                    return x.strip(to_strip)
            elif isinstance(expr, Rstrip):
                def func(x):
                    return x.rstrip(to_strip)
        elif isinstance(expr, Pad):
            side = expr.side
            fillchar = expr.fillchar
            width = expr.width

            if side == 'left':
                func = lambda x: x.rjust(width, fillchar)
            elif side == 'right':
                func = lambda x: x.ljust(width, fillchar)
            elif side == 'both':
                func = lambda x: x.center(width, fillchar)
            else:
                raise NotImplementedError
        elif isinstance(expr, Slice):
            start, end, step = expr.start, expr.end, expr.step

            if end is None and step is None:
                raise NotImplementedError
            if isinstance(start, six.integer_types) and \
                    isinstance(end, six.integer_types) and step is None:
                if start >= 0 and end >= 0:
                    raise NotImplementedError

            has_start = start is not None
            has_end = end is not None
            has_step = step is not None

            def func(x, *args):
                idx = 0
                s, e, t = None, None, None
                for i in range(3):
                    if i == 0 and has_start:
                        s = args[idx]
                        idx += 1
                    if i == 1 and has_end:
                        e = args[idx]
                        idx += 1
                    if i == 2 and has_step:
                        t = args[idx]
                        idx += 1
                return x[s: e: t]

            inputs = expr.input, expr._start, expr._end, expr._step
            sub = self._gen_mapped_expr(expr, tuple(i for i in inputs if i is not None),
                                        func, expr.name, multiple=False)
            self._sub(expr, sub)
            return
        elif isinstance(expr, Swapcase):
            func = lambda x: x.swapcase()
        elif isinstance(expr, Title):
            func = lambda x: x.title()
        elif isinstance(expr, Strptime):
            date_format = expr.date_format

            def func(x):
                from datetime import datetime
                return datetime.strptime(x, date_format)
        else:
            if isinstance(expr, Isalnum):
                func = lambda x: x.isalnum()
            elif isinstance(expr, Isalpha):
                func = lambda x: x.isalpha()
            elif isinstance(expr, Isdigit):
                func = lambda x: x.isdigit()
            elif isinstance(expr, Isspace):
                func = lambda x: x.isspace()
            elif isinstance(expr, Islower):
                func = lambda x: x.islower()
            elif isinstance(expr, Isupper):
                func = lambda x: x.isupper()
            elif isinstance(expr, Istitle):
                func = lambda x: x.istitle()
            elif isinstance(expr, (Isnumeric, Isdecimal)):
                def u_safe(s):
                    try:
                        return unicode(s, "unicode_escape")
                    except:
                        return s

                if isinstance(expr, Isnumeric):
                    func = lambda x: u_safe(x).isnumeric()
                else:
                    func = lambda x: u_safe(x).isdecimal()

        if func is not None:
            sub = expr.input.map(func, expr.dtype)
            self._sub(expr, sub)
            return

        raise NotImplementedError

    @staticmethod
    def _get_moment_sub_expr(expr, _input, order, center):
        def _group_mean(e):
            m = e.mean()
            if isinstance(expr, GroupedSequenceReduction):
                m = m.to_grouped_reduction(expr._grouped)
            return m

        def _order(e, o):
            if o == 1:
                return e
            else:
                return e ** o

        if not center:
            if order == 0:
                sub = Scalar(1)
            else:
                sub = _group_mean(_input ** order)
        else:
            if order == 0:
                sub = Scalar(1)
            elif order == 1:
                sub = Scalar(0)
            else:
                sub = _group_mean(_input ** order)
                divided = 1
                divisor = 1
                for o in compat.irange(1, order):
                    divided *= order - o + 1
                    divisor *= o
                    part_item = divided // divisor * _group_mean(_order(_input, order - o)) \
                                * (_order(_group_mean(_input), o))
                    if o & 1:
                        sub -= part_item
                    else:
                        sub += part_item
                part_item = _group_mean(_input) ** order
                if order & 1:
                    sub -= part_item
                else:
                    sub += part_item
        return sub

    def visit_reduction(self, expr):
        if isinstance(expr, (Var, GroupedVar)):
            std = expr.input.std(ddof=expr._ddof)
            if isinstance(expr, GroupedVar):
                std = std.to_grouped_reduction(expr._grouped)
            sub = (std ** 2).rename(expr.name)
            self._sub(expr, sub)
            return
        elif isinstance(expr, (Moment, GroupedMoment)):
            order = expr._order
            center = expr._center

            sub = self._get_moment_sub_expr(expr, expr.input, order, center)
            sub = sub.rename(expr.name)
            self._sub(expr, sub)
            return
        elif isinstance(expr, (Skewness, GroupedSkewness)):
            std = expr.input.std(ddof=1)
            if isinstance(expr, GroupedSequenceReduction):
                std = std.to_grouped_reduction(expr._grouped)
            cnt = expr.input.count()
            if isinstance(expr, GroupedSequenceReduction):
                cnt = cnt.to_grouped_reduction(expr._grouped)
            sub = self._get_moment_sub_expr(expr, expr.input, 3, True) / (std ** 3)
            sub *= (cnt ** 2) / (cnt - 1) / (cnt - 2)
            sub = sub.rename(expr.name)
            self._sub(expr, sub)
        elif isinstance(expr, (Kurtosis, GroupedKurtosis)):
            std = expr.input.std(ddof=0)
            if isinstance(expr, GroupedSequenceReduction):
                std = std.to_grouped_reduction(expr._grouped)
            cnt = expr.input.count()
            if isinstance(expr, GroupedSequenceReduction):
                cnt = cnt.to_grouped_reduction(expr._grouped)
            m4 = self._get_moment_sub_expr(expr, expr.input, 4, True)
            sub = 1.0 / (cnt - 2) / (cnt - 3) * ((cnt * cnt - 1) * m4 / (std ** 4) - 3 * (cnt - 1) ** 2)
            sub = sub.rename(expr.name)
            self._sub(expr, sub)

        raise NotImplementedError
