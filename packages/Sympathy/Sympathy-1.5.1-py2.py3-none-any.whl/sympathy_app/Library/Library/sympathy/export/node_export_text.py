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
import os
import six

from sympathy.api import exporters
from sympathy.api import datasource as dsrc
from sympathy.api import text
from sympathy.api import node as synode
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags
from sympathy.api.exceptions import SyNodeError
from sylib.export import common


class ExportTexts(synode.Node):
    __doc__ = common.COMMON_DOC + """

Export of Texts to the following file formats are supported:
    - Text

:Opposite node: :ref:`Texts`
"""
    name = 'Export Texts'
    description = 'Export Texts'
    icon = 'export_text.svg'
    tags = Tags(Tag.Output.Export)
    plugins = (exporters.base.TextDataExporterBase, )
    author = 'Erik der Hagopian <erik.hagopian@sysess.org>'
    copyright = '(C) 2013 System Engineering Software Society'
    nodeid = 'org.sysess.sympathy.export.exportexts'
    version = '0.1'

    inputs = Ports([Port.Texts('Texts to be exported', name='port0'),
                    Port.Datasources(
                        'External filenames',
                        name='port1', n=(0, 1, 0))])
    outputs = Ports([Port.Datasources(
        'Datasources of exported files', name='port0', scheme='text')])

    parameters = synode.parameters()
    parameters.set_string(
        'active_exporter', label='Exporter',
        description=('Select data format exporter. Each data format has its '
                     'own exporter with its own special configuration, see '
                     'exporter information. The selection of exporter do also '
                     'suggest filename extension.'))
    custom_exporter_group = parameters.create_group('custom_exporter_data')
    parameters.set_string(
        'directory', value='.', label='Output directory',
        description='Select the directory where to export the files.',
        editor=synode.Util.directory_editor().value())
    parameters.set_string(
        'filename', label='Filename',
        description='Filename without extension.')

    def verify_parameters(self, node_context):
        parameter_root = synode.parameters(node_context.parameters)
        parameters_ok = "" != parameter_root.value_or_empty('active_exporter')
        return parameters_ok

    def exec_parameter_view(self, node_context):
        parameter_root = synode.parameters(node_context.parameters)
        export_params_widget = exporters.base.ExporterConfigurationWidget(
            exporters.utils.available_text_exporters(),
            parameter_root, '')
        widget = exporters.base.ExporterWidget(
            node_context, parameter_root, export_params_widget, text)
        return widget

    def execute(self, node_context):
        parameter_root = synode.parameters(node_context.parameters)
        exporter_type = parameter_root['active_exporter'].value
        exporter_parameter_root = parameter_root[
            'custom_exporter_data'][exporter_type]

        text_exporter = exporters.utils.text_exporter_factory(exporter_type)(
            exporter_parameter_root)
        filename = parameter_root.value_or_empty('filename')
        directory = parameter_root.value_or_empty('directory')
        if not os.path.isdir(directory):
            os.makedirs(directory)
        # Create filenames from the parameter_root and the data available
        # as input. If active the exporter will use a specific filename
        # strategy when creating the filenames.
        fq_filenames = exporters.base.create_fq_filenames(
            directory, text_exporter.create_filenames(
                node_context.input, filename))

        input_list = node_context.input['port0']
        filename_port_list = node_context.input.group('port1')
        datasource_list = node_context.output['port0']
        number_of_objects = len(input_list)

        if filename_port_list:
            fq_filenames = [ds.decode_path() for ds in filename_port_list[0]]
            if len(fq_filenames) != len(input_list):
                raise SyNodeError(
                    '"External filenames" and Texts list must be the '
                    'same length.')

        for object_no, (fq_outfilename, text_file) in enumerate(
                six.moves.zip(fq_filenames, input_list)):
            datasource_file = dsrc.File()
            datasource_file.encode_path(fq_outfilename)
            datasource_list.append(datasource_file)

            text_exporter_class = (
                exporters.utils.text_exporter_factory(exporter_type))
            exporter_parameter_root = synode.parameters(
                node_context.parameters[
                    'custom_exporter_data'][exporter_type])
            text_exporter_class(parameter_root).export_data(
                text_file, fq_outfilename, exporter_parameter_root)
            self.set_progress(100.0 * (1 + object_no) / number_of_objects)
