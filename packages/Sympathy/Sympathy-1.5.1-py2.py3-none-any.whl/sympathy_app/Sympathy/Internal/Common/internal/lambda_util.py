# This file is part of Sympathy for Data.
# Copyright (c) 2015-2016 System Engineering Software Society
#
# Sympathy for Data is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Sympathy for Data is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sympathy for Data.  If not, see <http://www.gnu.org/licenses/>.
from __future__ import (print_function, division, unicode_literals,
                        absolute_import)
import six
import base64
import json
import sys

import Gui.application
import Gui.flow.functions
import Gui.datatypes
import Gui.execore
from sympathy.platform.exceptions import sywarn
from sympathy.platform import version_support as vs


class ExtractLambdaSubprocess(object):
    _marker = '__SY_EXTRACT_OUTPUT_MARKER__'

    def _lambdas_from_flow(self, flow):
        return Gui.flow.functions.top_lambdas_from_flow(flow)

    def execute(self, json_data, datatype, filenames, **kwargs):
        vs.wrap_encode_std()
        data = json.loads(base64.b64decode(json_data).decode('ascii'))
        env = data['env']
        lib = data['lib']
        folders = data['folders']
        identifier = data['identifier']

        flows, errors = Gui.application.extract_lambdas(
            filenames, datatype, env, lib, folders, identifier)

        for filename, error in errors:
            if filename is None:
                raise six.reraise(error[0], error[1], error[2])
            else:
                sywarn('File "{}" could not be read.'.format(filename))
                # sywarn("".join(traceback.format_exception(*error)))

        datatype = Gui.datatypes.DataType.from_str(datatype)
        lambdas = []

        for flow in flows:
            try:
                top_lambdas = self._lambdas_from_flow(flow)
                lambdas.extend(Gui.flow.functions.filter_lambdas_datatype(
                    top_lambdas, datatype))
            except:
                sywarn('File "{}" could not be read.'.format(flow.filename))
                # sywarn("".join(traceback.format_exc()))

        flowdata = []

        for lambda_ in lambdas:
            try:
                flowdata.append(json.loads(Gui.execore.flowdata(lambda_)[
                    'parameters']['data']['flow']['value']))
            except:
                sywarn('Lambda function: "{}" could not be extracted due to '
                       'errors.'.format(lambda_.name))
                # sywarn("".join(traceback.format_exc()))

        sys.stdout.write(self._marker)
        sys.stdout.write(
            base64.b64encode(json.dumps(flowdata).encode('ascii')).decode(
                'ascii'))


class ExtractFlowSubprocess(ExtractLambdaSubprocess):
    def _lambdas_from_flow(self, flow):
        return Gui.flow.functions.flow_to_lambda(flow)
