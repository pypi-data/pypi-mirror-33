# Copyright (c) 2015, 2017 System Engineering Software Society
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
from sylib.export import datasource as exportdatasource


class DataExtractTar(exportdatasource.DatasourceArchiveBase):
    """Extractor for TAR files."""

    EXPORTER_NAME = "TAR Extractor"
    FILENAME_EXTENSION = None

    def __init__(self, custom_parameter_root):
        super(DataExtractTar, self).__init__(
            custom_parameter_root,
            exportdatasource.DatasourceArchiveBase.EXTRACTOR)

    @staticmethod
    def hide_filename():
        return True

    def extract_data(self, in_datasource, directory, progress=None):
        file = in_datasource.decode_path()
        members = self._members(file)
        if len(members):
            tar = tarfile.TarFile(file)
            tar.extractall(directory, members)
        return self._create_filenames(members)

    def create_filenames(self, node_context_input):
        filenames = []
        for path in node_context_input['port0']:
            filenames.extend(
                self._create_filenames(self._members(path.decode_path())))
        return filenames

    def _members(self, path):
        members = []
        if tarfile.is_tarfile(path):
            tar = tarfile.TarFile(path)
            member = tar.next()
            while member:
                if not os.path.isdir(member.name):
                    members.append(member)
                member = tar.next()
        return members

    def _create_filenames(self, members):
        return [m.name for m in members]
