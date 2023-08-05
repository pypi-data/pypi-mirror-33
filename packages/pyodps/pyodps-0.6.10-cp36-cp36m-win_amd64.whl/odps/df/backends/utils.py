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

from collections import deque

from ..expr.dynamic import DynamicMixin


def refresh_dynamic(executed, dag, func=None):
    q = deque()
    q.append(executed)

    while len(q) > 0:
        curr = q.popleft()

        for p in dag.successors(curr):
            if isinstance(p, DynamicMixin):
                q.append(p)

        if isinstance(curr, DynamicMixin):
            deps = set([id(d) for d in curr.deps or []])
            if any(id(c) not in deps and isinstance(c, DynamicMixin) for c in curr.children()):
                continue
            sub = curr.to_static()
            dag.substitute(curr, sub)
            if func:
                func(sub)