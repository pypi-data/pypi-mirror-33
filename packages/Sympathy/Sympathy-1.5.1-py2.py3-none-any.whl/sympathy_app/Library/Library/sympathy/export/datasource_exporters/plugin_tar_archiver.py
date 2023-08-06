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
import tarfile
from sylib.export import datasource as importdatasource


class DataArchiveTar(importdatasource.DatasourceArchiveBase):
    """Archiver for TAR files. Takes all datasources in input and puts
    them in one (uncompressed) TAR file. Folder structure is discarded.
    """

    EXPORTER_NAME = "TAR Archiver"
    FILENAME_EXTENSION = 'tar'

    def __init__(self, custom_parameter_root):
        super(DataArchiveTar, self).__init__(
            custom_parameter_root,
            importdatasource.DatasourceArchiveBase.COMPRESSOR)

    @staticmethod
    def hide_filename():
        return False

    def compress_data(self, in_datasources, location, progress=None):
        if os.path.splitext(location)[1] != self.FILENAME_EXTENSION:
            location = '{}.{}'.format(location, self.FILENAME_EXTENSION)
        if len(in_datasources):
            with tarfile.open(location, 'w') as f:
                for ds in in_datasources:
                    path = ds.decode_path()
                    f.add(path, os.path.basename(path))
        return [location]

    def create_filenames(self, node_context_input):
        return ['']
