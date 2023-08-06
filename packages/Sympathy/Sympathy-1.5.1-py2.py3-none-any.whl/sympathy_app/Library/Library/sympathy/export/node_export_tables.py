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
import six

from sympathy.api import exporters
from sympathy.api import datasource as dsrc
from sympathy.api import table
from sympathy.api import node as synode
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags
from sympathy.api.exceptions import SyNodeError
from sylib.plot import backend as plot_backends
from sylib.plot import model as plot_models
from sylib.export import common
from sylib.export import table as exporttable


class ExportTables(synode.Node):
    __doc__ = common.COMMON_DOC + """

If the input Table(s) has a plot attribute (as created by e.g.,
:ref:`Plot Tables`) it can be exported to a separate file by selecting one
of the extensions in the output section.

:Opposite node: :ref:`Tables`
:Ref. nodes: :ref:`Export ADAFs`
    """
    name = 'Export Tables'
    description = 'Export Tables'
    icon = 'export_table.svg'
    inputs = Ports([Port.Tables('Tables to be exported', name='port0'),
                    Port.Datasources(
                        'External filenames',
                        name='port1', n=(0, 1, 0))])

    outputs = Ports([Port.Datasources(
        'Datasources of exported files', name='port0', scheme='text')])

    tags = Tags(Tag.Output.Export)
    plugins = (exporttable.TableDataExporterBase, )
    author = 'Alexander Busck <alexander.busck@combine.se>'
    copyright = '(c) 2013 System Engineering Software Society'
    nodeid = 'org.sysess.sympathy.export.exporttables'
    version = '0.1'

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
        editor=synode.Util.directory_editor())
    parameters.set_string(
        'filename', label='Filename',
        description='Filename without extension.')
    parameters.set_list(
        'plot',
        label='Output separate plot file with the following extension:',
        description='If there is a plot attribute in the input tables(s), '
        'create a separate file with the plot.',
        value=[0],
        plist=['-', 'eps', 'pdf', 'svg', 'png'],
        editor=synode.Util.combo_editor())

    def verify_parameters(self, node_context):
        parameter_root = synode.parameters(node_context.parameters)
        parameters_ok = "" != parameter_root.value_or_empty('active_exporter')
        return parameters_ok

    def exec_parameter_view(self, node_context):
        parameter_root = synode.parameters(node_context.parameters)
        export_params_widget = exporters.base.ExporterConfigurationWidget(
            exporters.utils.available_table_exporters(),
            parameter_root, node_context.input)
        widget = exporters.base.ExporterWidget(
            node_context, parameter_root, export_params_widget, table)
        return widget

    def execute(self, node_context):
        parameter_root = node_context.parameters
        exporter_type = parameter_root['active_exporter'].value
        filename = parameter_root.value_or_empty('filename')
        directory = parameter_root.value_or_empty('directory')
        if not os.path.isdir(directory):
            os.makedirs(directory)
        exporter_parameter_root = parameter_root[
            'custom_exporter_data'][exporter_type]

        exporter = exporters.utils.table_exporter_factory(exporter_type)(
            exporter_parameter_root)
        # Create filenames from the parameter_root and the data available
        # as input. If active the exporter will use a specific filename
        # strategy when creating the filenames.

        fq_filenames = exporters.base.create_fq_filenames(
            directory, exporter.create_filenames(node_context.input, filename))

        filename_port_list = node_context.input.group('port1')

        if 'plot' in parameter_root:
            plot = parameter_root['plot'].selected
            plot = None if plot == '-' else plot
        else:
            plot = None

        if isinstance(fq_filenames, list):
            number_of_filenames = len(fq_filenames)
        else:
            number_of_filenames = None

        input_list = node_context.input['port0']
        datasource_list = node_context.output['port0']
        number_of_objects = len(input_list)

        exporter_class = (
            exporters.utils.table_exporter_factory(
                exporter_type))
        exporter_parameter_root = synode.parameters(
            node_context.parameters[
                'custom_exporter_data'][exporter_type])

        exporter = exporter_class(exporter_parameter_root)

        if number_of_filenames is None:
            if filename_port_list:
                fq_filenames = [
                    ds.decode_path() for ds in filename_port_list[0]]
                if len(fq_filenames) != len(input_list):
                    raise SyNodeError(
                        '"External filenames" and Tables list must be the '
                        'same length.')

            for object_no, (fq_outfilename, table_file) in enumerate(
                    six.moves.zip(fq_filenames, input_list)):

                if not os.path.isdir(os.path.dirname(fq_outfilename)):
                    os.makedirs(os.path.dirname(fq_outfilename))
                datasource_file = dsrc.File()
                datasource_file.encode_path(fq_outfilename)
                datasource_list.append(datasource_file)

                try:
                    exporter.export_data(table_file, fq_outfilename)
                except (IOError, OSError):
                    raise SyNodeError(
                        'Unable to create file. Please check that you have '
                        'permission to write to the selected folder.')
                if plot is not None:
                    plots_model = plot_models.get_plots_model(
                        table_file)
                    plot_exporter = plot_backends.ExporterBackend(
                        plots_model, plot)
                    plot_exporter.render(
                        os.path.splitext(fq_outfilename)[0])

                self.set_progress(
                    100.0 * (1 + object_no) / number_of_objects)

        else:
            if filename_port_list:
                fq_filenames = [
                    ds.decode_path() for ds in filename_port_list[0]]
                if len(fq_filenames) != 1:
                    raise SyNodeError(
                        '"External filenames" must contain exactly one '
                        'element.')

            fq_outfilename = fq_filenames[0]
            datasource_file = dsrc.File()
            datasource_file.encode_path(fq_outfilename)
            datasource_list.append(datasource_file)

            exporter.export_data(input_list, fq_outfilename)

            if plot is not None:
                for table_file, i in zip(input_list, range(len(input_list))):
                    plots_model = plot_models.get_plots_model(table_file)
                    plot_exporter = plot_backends.ExporterBackend(
                        plots_model, plot)
                    filename = (
                        os.path.splitext(fq_outfilename)[0] + '_' + str(i))
                    plot_exporter.render(filename)

            self.set_progress(100)
