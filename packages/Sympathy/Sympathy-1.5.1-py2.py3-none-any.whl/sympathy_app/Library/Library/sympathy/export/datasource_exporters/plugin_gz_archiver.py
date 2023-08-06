# Copyright (c) 2015, 2017, System Engineering Software Society
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
import shutil
import gzip
from sylib.export import datasource as importdatasource


class DataArchiveGz(importdatasource.DatasourceArchiveBase):
    """Compressor for GZIP files"""

    EXPORTER_NAME = "GZIP Compressor"
    FILENAME_EXTENSION = 'gz'

    def __init__(self, custom_parameter_root):
        super(DataArchiveGz, self).__init__(
            custom_parameter_root,
            importdatasource.DatasourceArchiveBase.COMPRESSOR)

    @staticmethod
    def hide_filename():
        return True

    def compress_data(self, in_datasources, directory, progress=None):
        files = []
        for ds in in_datasources:
            in_file = ds.decode_path()
            gz_file = '{}.{}'.format(
                os.path.join(directory, os.path.basename(in_file)),
                self.FILENAME_EXTENSION)
            with open(in_file, 'rb') as i_f, gzip.open(gz_file, 'wb') as o_f:
                shutil.copyfileobj(i_f, o_f)
            files.append(gz_file)
        return files

    def create_filenames(self, node_context_input):
        return ['{}.{}'.format(
            os.path.basename(path.decode_path()), self.FILENAME_EXTENSION)
            for path in node_context_input['port0']]
