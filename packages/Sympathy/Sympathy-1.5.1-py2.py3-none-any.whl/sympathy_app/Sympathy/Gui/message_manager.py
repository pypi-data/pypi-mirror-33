# This file is part of Sympathy for Data.
# Copyright (c) 2016 System Engineering Software Society
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
import collections
import logging
import PySide.QtCore as QtCore

from sympathy.platform import message
from . flow import types

core_logger = logging.getLogger('core')


def nodups(lst):
    return reversed(
        collections.OrderedDict.fromkeys(reversed(lst)).keys())


class MessageManager(QtCore.QObject):
    message_output = QtCore.Signal(int, message.Message)

    def __init__(self, appcore):
        super(MessageManager, self).__init__(appcore)
        self._appcore = appcore

    def _got_agg_config_update(self, ident, msg):
        data = msg.data
        uuid = data['uuid']
        core_logger.info('AggConfigUpdateMessage for: %s', uuid)
        self._appcore.handle_subflow_parameter_view_done(uuid, data)

    def _dependent_node_status(self, node):
        error = False
        nodes = []
        inodes = list(nodups(node._incoming_nodes()))
        for inode in inodes:
            if inode.is_executing() or inode.is_done():
                pass
            elif inode.is_queued() or inode.is_armed():
                nodes.append(inode)
            else:
                error = True
                break
        return error, nodes, inodes

    def _got_data_request(self, ident, msg):
        uuid = msg.data
        core_logger.info('DataRequestMessage for: %s', uuid)
        node = self._appcore.get_flode(uuid)
        error, nodes, inodes = self._dependent_node_status(node)

        if not error:
            for inode in nodes:
                inode.flow.execute_node(inode)

            if not inodes:
                self.message_output.emit(
                    -1, message.DataReadyMessage(node.full_uuid))
            elif not nodes:
                self.message_output.emit(
                    -1, message.DataReadyMessage(node.full_uuid))

    @QtCore.Slot(int, message.Message)
    def message_input(self, ident, msg):

        if msg.type == message.DataRequestMessage:
            self._got_data_request(ident, msg)

        elif msg.type == message.AggConfigUpdateMessage:
            self._got_agg_config_update(ident, msg)

        if msg.type == message.StatusDataRequestMessage:
            uuid = msg.data
            node = self._appcore.get_flode(uuid)
            error = self._dependent_node_status(node)[0]
            if error:
                self.message_output.emit(
                    ident, message.DataBlockedMessage(node.full_uuid))

    def execution_done(self, node):
        if node.type == types.Type.Node:
            # TODO(erik): implement support for flows and stop using
            # private Node member.
            for onode in nodups(node._outgoing_nodes()):
                if onode.all_incoming_nodes_are_successfully_executed():
                    self.message_output.emit(
                        -1, message.DataReadyMessage(onode.full_uuid))
