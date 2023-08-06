# -*- coding: utf-8 -*-
# Copyright (c) 2016, 2017, System Engineering Software Society
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

from sympathy.api import exceptions
from sympathy.api import exporters
from sympathy.api import figure
from sympathy.typeutils import datasource as dsrc
from sympathy.platform import gennode as synode
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags


class ExportFigures(synode.Node):
    """
    Export Figures to a selected data format.

    :Ref. nodes:
        :ref:`Figures from Tables`, :ref:`Figures from Tables with Table`
    """

    name = 'Export Figures'
    description = 'Export Figures to image files.'
    icon = 'export_figure.svg'
    tags = Tags(Tag.Output.Export)
    author = 'Benedikt Ziegler <benedikt.ziegler@combine.se>'
    copyright = '(c) 2016 System Engineering Software Society'
    nodeid = 'org.sysess.sympathy.export.exportfigures'
    version = '0.2'

    inputs = Ports([Port.Figures('Input figures', name='figures')])
    outputs = Ports([Port.Datasources(
        'Datasources with paths to the created files',
        name='port0', scheme='text')])

    parameters = synode.parameters()
    parameters.set_string(
        'active_exporter', label='Exporter',
        description=('Select data format exporter. Each data format has its '
                     'own exporter with its own special configuration, see '
                     'exporter information. The selection of exporter do also '
                     'suggest filename extension'))
    custom_exporter_group = parameters.create_group('custom_exporter_data')
    parameters.set_string(
        'directory', value='.', label='Output directory',
        description='Select the directory where to export the files.',
        editor=synode.Util.directory_editor().value())
    parameters.set_string(
        'filename', label='Filename',
        description=('Specify the common base for the filenames. If there are '
                     'several incoming Figures the node will add “_${index '
                     'number of corresponding Figure in the incoming list}” '
                     'after the base for each file. Do not specify extension'))

    def verify_parameters(self, node_context):
        parameter_root = synode.parameters(node_context.parameters)
        parameters_ok = "" != parameter_root.value_or_empty('active_exporter')
        return parameters_ok

    def update_parameters(self, old_params):
        extension = old_params._parameter_dict.pop('extension', None)
        width = old_params._parameter_dict.pop('width', None)
        height = old_params._parameter_dict.pop('height', None)
        if 'custom_exporter_data' not in old_params:
            custom_exporter_data = old_params.create_group(
                'custom_exporter_data')
        else:
            custom_exporter_data = old_params['custom_exporter_data']
        if 'Image' not in custom_exporter_data:
            image = custom_exporter_data.create_group('Image')
        else:
            image = custom_exporter_data['Image']
        if extension is not None:
            image.set_list('extension',
                           label=extension['label'],
                           description=extension['description'],
                           value=extension['value'],
                           plist=extension['list'],
                           editor=extension['editor'])
        if width is not None:
            image.set_integer('width',
                              label=width['label'],
                              description=width['description'],
                              value=width['value'],
                              editor=width['editor'])
        if height is not None:
            image.set_integer('height',
                              label=height['label'],
                              description=height['description'],
                              value=height['value'],
                              editor=height['editor'])
        return old_params

    def exec_parameter_view(self, node_context):
        parameter_root = node_context.parameters
        export_params_widget = exporters.base.ExporterConfigurationWidget(
            exporters.utils.available_figure_exporters(),
            parameter_root, node_context.input)
        widget = exporters.base.ExporterWidget(
            node_context, parameter_root, export_params_widget, figure)
        return widget

    def execute(self, node_context):
        parameter_root = node_context.parameters
        exporter_type = parameter_root['active_exporter'].value
        filename = parameter_root['filename'].value
        directory = parameter_root['directory'].value
        if not os.path.isdir(directory):
            os.makedirs(directory)

        exporter_parameter_root = node_context.parameters[
            'custom_exporter_data'][exporter_type]

        exporter = exporters.utils.figure_exporter_factory(
            exporter_type)(exporter_parameter_root)
        # Create filenames from the parameter_root and the data available
        # as input. If active the exporter will use a specific filename
        # strategy when creating the filenames.

        fq_filenames = exporters.base.create_fq_filenames(
            directory, exporter.create_filenames(node_context.input, filename))

        input_list = node_context.input['figures']
        datasource_list = node_context.output['port0']
        number_of_objects = len(input_list)

        for object_no, (fq_outfilename, figure_file) in enumerate(
                six.moves.zip(fq_filenames, input_list)):
            datasource_file = dsrc.File()
            datasource_file.encode_path(fq_outfilename)
            datasource_list.append(datasource_file)

            exporter.export_data(
                figure_file, fq_outfilename, exporter_parameter_root)
            self.set_progress(100.0 * (1 + object_no) / number_of_objects)


class ExportFiguresWithDsrcs(synode.Node):
    """
    Export Figures to a selected data format with a list of datasources for
    output paths.
    """

    name = 'Export Figures with Datasources'
    description = 'Export Figures to image files.'
    icon = 'export_figure.svg'
    tags = Tags(Tag.Output.Export)
    author = 'Magnus Sandén <magnus.sanden@combine.se>'
    copyright = '(c) 2016 System Engineering Software Society'
    nodeid = 'org.sysess.sympathy.export.exportfigureswithdscrs'
    version = '0.1'

    inputs = Ports([
        Port.Figures('Input figures', name='figures'),
        Port.Datasources('Datasources', name='dsrcs')])
    outputs = Ports([Port.Datasources(
        'Datasources with paths to the created files', name='port0')])

    parameters = synode.parameters()
    parameters.set_string(
        'active_exporter', label='Exporter',
        description=('Select data format exporter. Each data format has its '
                     'own exporter with its own special configuration, see '
                     'exporter information. The selection of exporter do also '
                     'suggest filename extension.'))
    custom_exporter_group = parameters.create_group('custom_exporter_data')

    def verify_parameters(self, node_context):
        parameter_root = synode.parameters(node_context.parameters)
        parameters_ok = "" != parameter_root.value_or_empty('active_exporter')
        return parameters_ok

    def exec_parameter_view(self, node_context):
        parameter_root = node_context.parameters
        export_params_widget = exporters.base.ExporterConfigurationWidget(
            exporters.utils.available_figure_exporters(),
            parameter_root, node_context.input)
        export_params_widget.init_index()
        return export_params_widget

    def execute(self, node_context):
        parameter_root = node_context.parameters
        exporter_type = parameter_root['active_exporter'].value
        dsrcs = node_context.input['dsrcs']
        input_list = node_context.input['figures']
        datasource_list = node_context.output['port0']
        number_of_objects = len(input_list)

        if number_of_objects != len(dsrcs):
            raise exceptions.SyDataError(
                "The number of datasources ({}) doesn't match the number of "
                "figures ({}).".format(len(dsrcs), number_of_objects))

        in_filenames = [
            os.path.abspath(d.decode_path()) for d in dsrcs]

        exporter_parameter_root = node_context.parameters[
            'custom_exporter_data'][exporter_type]

        exporter = exporters.utils.figure_exporter_factory(
            exporter_type)(exporter_parameter_root)
        # Create filenames from the parameter_root and the data available
        # as input. If active the exporter will use a specific filename
        # strategy when creating the filenames.

        fq_filenames = [
            next(exporter.create_filenames(node_context.input, in_filename))
            for in_filename in in_filenames]

        for object_no, (fq_outfilename, figure_file) in enumerate(
                six.moves.zip(fq_filenames, input_list)):
            datasource_file = dsrc.File()
            datasource_file.encode_path(fq_outfilename)
            datasource_list.append(datasource_file)

            exporter.export_data(
                figure_file, fq_outfilename, exporter_parameter_root)
            self.set_progress(100.0 * (1 + object_no) / number_of_objects)
