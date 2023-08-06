# -*- coding:utf-8 -*-
# Copyright (c) 2017, System Engineering Software Society
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
from sympathy.api import exporters
from sympathy.api.exceptions import sywarn, NoDataError


class TableExporterAccessManager(exporters.base.ExporterAccessManagerBase):
    pass


class TableDataExporterBase(exporters.base.TableDataExporterBase):
    access_manager = TableExporterAccessManager

    def create_filenames(self, node_context_input, filename):
        """
        Base implementation of create_filenames.
        Please override for custom behavior.
        """
        if not self.file_based():
            return exporters.base.inf_filename_gen('-')

        elif ('table_names' in self._custom_parameter_root and
                self._custom_parameter_root['table_names'].value):
            ext = self._custom_parameter_root['filename_extension'].value
            if ext != '':
                ext = '{}{}'.format(os.path.extsep, ext)
            try:
                tablelist = node_context_input['port0']
                filenames = [u'{}{}'.format(
                    t.get_name(), ext) for t in tablelist
                    if t.get_name() is not None]

                if len(set(filenames)) == len(tablelist):
                    return (filename for filename in filenames)
                else:
                    sywarn(
                        'The Tables in the incoming list do not '
                        'have unique names. The table names are '
                        'therefore not used as filenames.')
            except (IOError, OSError, NoDataError):
                pass

        filename_extension = self._custom_parameter_root[
            'filename_extension'].value
        return exporters.base.inf_filename_gen(filename, filename_extension)
