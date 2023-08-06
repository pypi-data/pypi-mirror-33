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
from sympathy.api import adaf
from sympathy.api import datasource as dsrc
from sympathy.api import node as synode
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags
from sylib.export import common
from sylib.export import adaf as exportadaf


class ExportADAFs(synode.Node):
    __doc__ = common.COMMON_DOC + """

Export of ADAFs to the following file formats are supported:
    - SyData
    - MDF

For export of ADAF to file there exist a number of strategies that
can be used to extract filenames from information stored in the ADAFs. If no
strategy is selected one has to declare the base of the filename.

The following strategies exist:
    - **Source identifier as name**
        Use the source identifier in the ADAFs as filenames.
    - **Column with name**
        Specify a column in the metadata container where the first element
        is the filename.

:Opposite nodes: :ref:`ADAFs`
:Ref. nodes: :ref:`Export Tables`
"""

    name = 'Export ADAFs'
    description = 'Export ADAFs'
    icon = 'adaf_export.svg'
    tags = Tags(Tag.Output.Export)
    plugins = (exportadaf.TabbedADAFDataExporterBase, )
    author = 'Alexander Busck <alexander.busck@combine.se>'
    copyright = '(c) 2013 System Engineering Software Society'
    nodeid = 'org.sysess.sympathy.export.exportadafs'
    version = '0.1'

    inputs = Ports([Port.ADAFs('Input ADAFs', name='port0')])
    outputs = Ports([Port.Datasources(
        'Datasources of the exported files', name='port0', scheme='text')])

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
            exporters.utils.available_adaf_exporters(),
            parameter_root, node_context.input)
        widget = exporters.base.ExporterWidget(
            node_context, parameter_root, export_params_widget, adaf)
        return widget

    def execute(self, node_context):
        parameter_root = synode.parameters(node_context.parameters)
        filename = parameter_root.value_or_empty('filename')
        directory = parameter_root.value_or_empty('directory')
        if not os.path.isdir(directory):
            os.makedirs(directory)
        exporter_type = parameter_root['active_exporter'].value
        custom_parameter_root = synode.parameters(
            node_context.parameters['custom_exporter_data'][exporter_type])
        exporter = exporters.utils.adaf_exporter_factory(exporter_type)(
            custom_parameter_root)
        # Create filenames from the parameter_root and the data available
        # as input. If active the exporter will use a specific filename
        # strategy when creating the filenames.
        fq_filenames = exporters.base.create_fq_filenames(
            directory, exporter.create_filenames(node_context.input, filename))

        input_list = node_context.input['port0']
        datasource_list = node_context.output['port0']

        for i, (fq_outfilename, adaf_file) in enumerate(
                six.moves.zip(fq_filenames, input_list)):
            datasource = dsrc.File()
            datasource.encode_path(fq_outfilename)
            datasource_list.append(datasource)
            exporter.export_data(
                adaf_file, fq_outfilename,
                lambda x: self.set_progress(
                    (100. * i + x) / len(input_list)))
