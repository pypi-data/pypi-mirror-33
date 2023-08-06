# -*- coding: utf-8 -*-
# Copyright (c) 2016-2017, System Engineering Software Society
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the System Engineering Software Society nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.
# IN NO EVENT SHALL SYSTEM ENGINEERING SOFTWARE SOCIETY BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
from __future__ import (print_function, division, unicode_literals,
                        absolute_import)
"""
The considered category of nodes includes a number of common tuple operations.
    - Zip
    - Unzip
    - First
    - Second
    - Tuple
    - Untuple
    - Cartesian product
"""
from itertools import product
from six.moves import zip as izip
from sympathy.api import node as synode
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags
from sympathy.api.nodeconfig import TemplateTypes as t


class SuperNodeGeneric(synode.Node):
    author = 'Erik der Hagopian <erik.hagopian@sysess.org>'
    copyright = '(C) 2016 System Engineering Software Society'
    version = '1.0'
    tags = Tags(Tag.Generic.Tuple, Tag.DataProcessing.Tuple)


class Tuple(SuperNodeGeneric):
    """Create a two element tuple (pair) from two items."""

    author = 'Erik der Hagopian <erik.hagopian@sysess.org>'
    name = 'Tuple'
    nodeid = 'org.sysess.sympathy.tuple.tuple2'
    icon = 'tuple.svg'
    copyright = '(C) 2017 System Engineering Software Society'

    inputs = Ports([
        Port.Custom(t.generic(t.letters(t.index)),
                    'Input', 'input', n=(2, None))])

    outputs = Ports([
        Port.Custom(t.tuple(t.types(t.group('input'))),
                    'Output', 'output')])

    def execute(self, node_context):
        out = node_context.output[0]
        for i, item in enumerate(node_context.input):
            out[i] = node_context.input[i]


class Untuple(SuperNodeGeneric):
    """Get two output elements out of a two element tuple (pair)."""

    author = 'Erik der Hagopian <erik.hagopian@sysess.org>'
    name = 'Untuple'
    nodeid = 'org.sysess.sympathy.tuple.untuple2'
    icon = 'untuple.svg'
    copyright = '(C) 2017 System Engineering Software Society'

    inputs = Ports([
        Port.Custom(t.tuple(t.types(t.group('output'))),
                    'Input', 'input')])

    outputs = Ports([
        Port.Custom(t.generic(t.letters(t.index)),
                    'Output', 'output', n=(2, None))])

    def execute(self, node_context):
        for in_, out in izip(node_context.input[0], node_context.output):
            out.source(in_, shallow=True)


class CartesianProductTuple(synode.Node):
    """Create a list of two element tuples (pairs) from two lists."""

    copyright = '(C) 2017 System Engineering Software Society'
    version = '1.0'
    author = 'Magnus Sandén <magnus.sanden@sysess.org>'
    name = 'Cartesian Product Tuple'
    nodeid = 'org.sysess.sympathy.tuple.carthesianproduct2'
    icon = 'product.svg'
    tags = Tags(Tag.Generic.Tuple, Tag.DataProcessing.Tuple)

    inputs = Ports([
        Port.Custom(t.list(t.generic(t.letters(t.index))),
                    'Input', 'input', n=(2, None))])

    outputs = Ports([
        Port.Custom(t.list(t.tuple(t.map(
            t.unlist, t.types(t.group('input'))))),
                    'Output', 'output')])

    def execute(self, node_context):
        inputs = list(node_context.input)
        outlist = node_context.output[0]

        for pytuple in product(*inputs):
            sytuple = outlist.create()

            for i, item in enumerate(pytuple):
                sytuple[i] = item
            outlist.append(sytuple)


class ZipTuple(SuperNodeGeneric):
    """Create a list of two element tuples (pairs) from two lists."""

    author = 'Erik der Hagopian <erik.hagopian@sysess.org>'
    name = 'Zip Tuple'
    nodeid = 'org.sysess.sympathy.tuple.ziptuple2'
    icon = 'zip.svg'
    copyright = '(C) 2017 System Engineering Software Society'

    inputs = Ports([
        Port.Custom(t.list(t.generic(t.letters(t.index))),
                    'Input', 'input', n=(2, None))])

    outputs = Ports([
        Port.Custom(t.list(t.tuple(t.map(t.unlist,
                                         t.types(t.group('input'))))),
                    'Output', 'output')])

    def execute(self, node_context):
        inputs = list(node_context.input)
        outlist = node_context.output[0]

        for pytuple in izip(*inputs):
            sytuple = outlist.create()

            for i, item in enumerate(pytuple):
                sytuple[i] = item
            outlist.append(sytuple)


class UnzipTuple(SuperNodeGeneric):
    """Create two list outputs from list of two element tuples (pairs)."""

    author = 'Erik der Hagopian <erik.hagopian@sysess.org>'
    name = 'Unzip Tuple'
    nodeid = 'org.sysess.sympathy.tuple.unziptuple2'
    icon = 'unzip.svg'
    copyright = '(C) 2017 System Engineering Software Society'

    inputs = Ports([
        Port.Custom(t.list(t.tuple(t.map(t.unlist,
                                         t.types(t.group('output'))))),
                    'Input', 'input')])

    outputs = Ports([
        Port.Custom(t.list(t.generic(t.letters(t.index))),
                    'Output', 'output', n=(2, None))])

    def execute(self, node_context):
        in_list = node_context.input[0]
        outs = list(node_context.output)

        for tuplen in in_list:
            for i, item in enumerate(tuplen):
                outs[i].append(item)


class FirstTuple2(SuperNodeGeneric):
    """Get the first element out of a two element tuple (pair)."""

    author = 'Erik der Hagopian <erik.hagopian@sysess.org>'
    name = 'First Tuple2'
    nodeid = 'org.sysess.sympathy.tuple.firsttuple2'
    icon = 'first.svg'

    inputs = Ports([
        Port.Custom('(<a>, <b>)', 'Tuple')])

    outputs = Ports([
        Port.Custom('<a>', 'First')])

    def execute(self, node_context):
        node_context.output[0].source(node_context.input[0][0], shallow=True)


class SecondTuple2(SuperNodeGeneric):
    """Get the second element out of a two element tuple (pair)."""

    author = 'Erik der Hagopian <erik.hagopian@sysess.org>'
    name = 'Second Tuple2'
    nodeid = 'org.sysess.sympathy.tuple.secondtuple2'
    icon = 'second.svg'

    inputs = Ports([
        Port.Custom('(<a>, <b>)', 'Tuple2')])

    outputs = Ports([
        Port.Custom('<b>', 'Second')])

    def execute(self, node_context):
        node_context.output[0].source(node_context.input[0][1], shallow=True)
