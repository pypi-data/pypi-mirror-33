# Copyright (c) 2013, 2017, System Engineering Software Society
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

import os
import sys
from collections import OrderedDict
from sympathy.api import node as synode
from sympathy.api import datasource as dsrc
from sympathy.api import text
from sympathy.api import importers
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags
from sympathy.api import exceptions
from sympathy.api import qt as qt_compat
QtGui = qt_compat.import_module('QtGui')

EXCEPTION, EMPTY, SKIP = ('Exception', 'Create Empty Entry', 'Skip File')

FAILURE_STRATEGIES = OrderedDict(
    [(EXCEPTION, 0), (EMPTY, 1)])

LIST_FAILURE_STRATEGIES = OrderedDict(
    [(EXCEPTION, 0), (EMPTY, 1), (SKIP, 2)])


def import_text_data(text_importer, datasource, output_sytype,
                     parameters, progress):
    """Function to handle the special case when importing an ADAF file
    due to the way they are opened.
    """
    dspath = datasource.decode_path()
    importer = text_importer(dspath, parameters)
    if importer.is_text():
        raise NotImplemented('Text Sydata is not supported yet.')
    else:
        importer.import_data(output_sytype, parameters, progress)


def _parameters_base():
    parameters = synode.parameters()
    parameters.set_string(
        'active_importer', label='Importer', value='Auto',
        description=('Select data format importer'))
    custom_importer_group = parameters.create_group(
        'custom_importer_data')
    custom_importer_group.create_group('Auto')
    return parameters


class ImportText(synode.Node):
    """
    Import data as a Text.

    :Opposite node: :ref:`Export Texts`
    :Ref. nodes: :ref:`Texts`
    """

    author = "Erik der Hagopian <erik.hagopian@sysess.org>"
    copyright = "(C) 2013 System Engineering Software Society"
    version = '1.0'
    icon = 'import_text.svg'

    name = 'Text'
    description = 'Data source as text'
    nodeid = 'org.sysess.sympathy.data.text.importtext'

    inputs = Ports([Port.Datasource(
        'Datasource', name='port1', requiresdata=True)])
    outputs = Ports([Port.Text('Imported Text', name='port1')])

    tags = Tags(Tag.Input.Import)
    plugins = (importers.base.TextDataImporterBase, )

    parameters = _parameters_base()
    parameters.set_list(
        'fail_strategy', label='Action on import failure',
        list=FAILURE_STRATEGIES.keys(), value=[0],
        description='Decide how failure to import a file should be handled.',
        editor=synode.Util.combo_editor())

    def exec_parameter_view(self, node_context):
        dspath = None
        try:
            datasource = node_context.input['port1']
            dspath = datasource.decode_path()

            if dspath is not None:
                assert(os.path.isfile(dspath))
        except exceptions.NoDataError:
            # This is if no input is connected.
            pass

        widget = importers.base.ImporterConfigurationWidget(
            importers.utils.available_text_importers(),
            synode.parameters(node_context.parameters), dspath)
        return widget

    def execute(self, node_context):
        """Import file into platform as Text."""
        parameters = node_context.parameters
        importer_type = parameters['active_importer'].value
        try:
            if 'fail_strategy' in parameters:
                fail_strategy = parameters['fail_strategy'].selected
            else:
                fail_strategy = EXCEPTION

            datasource = node_context.input['port1']
            text_importer = (
                importers.utils.text_importer_from_datasource_factory(
                    datasource, importer_type))
            if text_importer is None:
                raise exceptions.SyDataError(
                    "No importer could automatically be found for this file.")
            import_text_data(
                text_importer, datasource, node_context.output['port1'],
                parameters["custom_importer_data"][importer_type],
                self.set_progress)
        except Exception:
            if fail_strategy == EXCEPTION:
                raise
            elif fail_strategy == EMPTY:
                pass
            else:
                assert False, 'Bad failure strategy'

        self.set_progress(100)


class ImportTexts(synode.Node):
    """
    Import data as Texts.

    :Opposite node: :ref:`Export Texts`
    :Ref. nodes: :ref:`Text`
    """

    author = "Erik der Hagopian <erik.hagopian@sysess.org>"
    copyright = "(C) 2013 System Engineering Software Society"
    version = '1.0'
    icon = 'import_text.svg'

    name = 'Texts'
    description = 'Data source as Texts'
    nodeid = 'org.sysess.sympathy.data.text.importtexts'

    inputs = Ports([Port.Datasources(
        'Datasource', name='port1', requiresdata=True)])
    outputs = Ports([Port.Texts('Imported Texts', name='port1')])

    tags = Tags(Tag.Input.Import)
    plugins = (importers.base.TextDataImporterBase, )

    parameters = _parameters_base()
    parameters.set_list(
        'fail_strategy', label='Action on import failure',
        list=LIST_FAILURE_STRATEGIES.keys(), value=[0],
        description='Decide how failure to import a file should be handled.',
        editor=synode.Util.combo_editor())

    def exec_parameter_view(self, node_context):
        dspath = None
        try:
            try:
                datasource = node_context.input['port1'][0]
            except IndexError:
                datasource = dsrc.File()

            dspath = datasource.decode_path()

            if dspath is not None:
                assert(os.path.isfile(dspath))
        except exceptions.NoDataError:
            # This is if no input is connected.
            pass
        widget = importers.base.ImporterConfigurationWidget(
            importers.utils.available_text_importers(),
            synode.parameters(node_context.parameters), dspath)
        return widget

    def execute(self, node_context):
        """Import file(s) into platform as Text(s)."""
        parameters = node_context.parameters
        importer_type = parameters['active_importer'].value

        if 'fail_strategy' in parameters:
            fail_strategy = parameters['fail_strategy'].selected
        else:
            fail_strategy = EXCEPTION

        input_list = node_context.input['port1']
        output_list = node_context.output['port1']

        objects = input_list
        number_of_objects = len(objects)
        for i, datasource in enumerate(objects):
            out_file = None
            try:
                text_importer_class = (
                    importers.utils.text_importer_from_datasource_factory(
                        datasource, importer_type))
                if text_importer_class is None:
                    raise exceptions.SyDataError(
                        "No importer could automatically be found for "
                        "this file.")
                dspath = datasource.decode_path()
                text_importer = text_importer_class(
                    dspath,
                    parameters["custom_importer_data"][importer_type])
                if text_importer.is_text():
                    raise NotImplemented('Text Sydata is not supported yet.')
                else:
                    outputfile = text.File()
                    text_importer.import_data(
                        outputfile,
                        parameters["custom_importer_data"][importer_type])
                    output_list.append(outputfile)
            except Exception:
                if fail_strategy == EXCEPTION:
                    raise exceptions.SyListIndexError(i, sys.exc_info())
                elif fail_strategy == EMPTY:
                    out_file = text.File()
                elif fail_strategy == SKIP:
                    out_file = None
                else:
                    assert False, 'Bad failure strategy'

            if out_file is not None:
                output_list.append(out_file)

            self.set_progress(100 * (1 + i) / number_of_objects)
