# -*- coding: utf-8 -*-
# This file is part of Sympathy for Data.
# Copyright (c) 2013 System Engineering Software Society
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
import collections
import six
import itertools
import PySide.QtCore as QtCore
import PySide.QtGui as QtGui

from sympathy.platform import os_support as oss

from .types import MovableElementViewInterface
from .decoration import NodeStatusIconView, NodeViewLabel, NodeProgressView
from . import theme
from .. import flow
from .. import user_commands
from .port import PortView
from Gui import settings


def encoding_warning(path):
    try:
        if isinstance(path, six.text_type):
            path.encode(oss.fs_encoding)
        else:
            path.decode(oss.fs_encoding)
    except (UnicodeEncodeError, UnicodeDecodeError):
        warning = QtGui.QMessageBox(
            QtGui.QMessageBox.Warning, 'Spyder Error',
            'Spyder cannot start since a required file has a path that '
            'contains non ASCII characters (such as å, ä, ö, é, etc.).\n'
            'This is a a limitation of Spyder.\n\n'
            'This usually happens for user accounts which contains '
            'any of these characters or when Sympathy is installed on '
            'such a path.\n\n'
            'A workaround is to reinstall Sympathy on a path without '
            'special characters and/or change the temporary files path '
            'in "Preferences/Temporary files" to a compliant one.')
        warning.exec_()
        return False
    return True


class BaseNodeView(MovableElementViewInterface):
    """
    The BaseNodeView provides basic functionality for node like entities that
    can be connected, executed and configured.
    """

    connection_start_requested = QtCore.Signal(object)
    connection_end_requested = QtCore.Signal(object)
    open_add_context_requested = QtCore.Signal(QtGui.QGraphicsSceneMouseEvent)
    create_subflow_from_selection_requested = QtCore.Signal()
    reload_requested = QtCore.Signal(object)

    def __init__(self, model, parent=None):
        self._input_port_views = collections.OrderedDict()
        self._output_port_views = collections.OrderedDict()
        MovableElementViewInterface.__init__(self, model, parent)
        self._init_base()
        self._label = NodeViewLabel(self._model.name, parent=self)
        self._init_node_actions()
        self._init_signalling()
        self._init_port_views()
        self._node_state_changed()
        self.update_later()

    def _init_base(self):
        self.setZValue(5.1)
        self._status_icon = NodeStatusIconView(parent=self)
        self._status_icon.setPos(self._bounding_rect.left(),
                                 self._bounding_rect.top() - 10)
        self._dialog_icon = NodeStatusIconView(parent=self)
        self._dialog_icon.setPos(
            self._bounding_rect.right() - 13,
            self._bounding_rect.top() - 10)
        self._progress_view = None

        self._border_width = 2.0
        self._border_color = theme.instance().mid_color
        self._pen = QtGui.QPen(self._border_color, self._border_width)
        self._node_color = theme.instance().midlight_color
        self._brush = QtGui.QBrush(self._node_color)

    def _init_node_actions(self):
        self._create_subflow_from_selection_action = QtGui.QAction(
            'Create Subflow From Selection', self)
        self._configure_action = QtGui.QAction('Configure', self)
        self._execute_action = QtGui.QAction('Execute', self)
        self._debug_action = QtGui.QAction('Debug', self)
        self._profile_action = QtGui.QAction('Profile', self)
        self._reload_action = QtGui.QAction('Reload', self)
        self._abort_action = QtGui.QAction('Abort', self)
        self._edit_node_action = QtGui.QAction('Edit', self)
        self._node_help_action = QtGui.QAction('Help', self)

        self._create_subflow_from_selection_action.triggered.connect(
            self.create_subflow_from_selection_requested)

        self._configure_action.triggered.connect(
            self._model.configure)
        self._execute_action.triggered.connect(
            self._model.execute)
        self._debug_action.triggered.connect(
            self._debug_requested)
        self._profile_action.triggered.connect(
            self._model.profile)
        self._reload_action.triggered.connect(
            self._model.arm)
        self._abort_action.triggered.connect(
            self._model.abort)

        self._edit_node_action.triggered.connect(
            self._edit_node_requested)
        self._node_help_action.triggered.connect(
            self._node_help_requested)

    def _debug_requested(self):
        spyder_can_debug = (
            encoding_warning(self._model.source_file) and
            encoding_warning(settings.instance()['temp_folder']))

        if spyder_can_debug:
            self._model.debug()

    def _init_signalling(self):
        self._signals.connect(
            self._model,
            self._model.input_port_created[flow.Port],
            self._handle_input_port_created)
        self._signals.connect(
            self._model,
            self._model.output_port_created[flow.Port],
            self._handle_output_port_created)
        self._signals.connect(
            self._model,
            self._model.input_port_removed[flow.Port],
            self._handle_input_port_removed)
        self._signals.connect(
            self._model,
            self._model.output_port_removed[flow.Port],
            self._handle_output_port_removed)

        self._signals.connect(
            self._model,
            self._model.parameter_viewer_changed,
            self._handle_parameter_view_changed)

        # Label related
        self._signals.connect(
            self._model,
            self._model.name_changed[six.text_type],
            self._label.set_label)
        self._signals.connect(
            self._model,
            self._label.label_edited[six.text_type],
            self._handle_label_edited)

        # State related
        self._signals.connect(
            self._model,
            self._model.state_changed,
            self._node_state_changed)
        self._signals.connect(
            self._model,
            self._model.progress_changed[int],
            self._update_progress)

    def _init_port_views(self):
        for port in self._model.inputs:
            self._handle_input_port_created(port)
        for port in self._model.outputs:
            self._handle_output_port_created(port)

    def input_port_views(self):
        return self._input_port_views.values()

    def output_port_views(self):
        return self._output_port_views.values()

    def input_port_view(self, port):
        return self._input_port_views[port]

    def output_port_view(self, port):
        return self._output_port_views[port]

    @QtCore.Slot()
    def _node_state_changed(self):
        # Change the color (and the icon) of the node depending on the state
        old_brush = self._brush

        if self._model.in_error_state():
            # Red color
            self._brush = QtGui.QBrush(QtGui.QColor.fromRgb(228, 186, 189))
            self._status_icon.set_icon_type('Error')
            self._hide_progress_view()
        elif self._model.is_successfully_executed():
            # Green
            self._brush = QtGui.QBrush(QtGui.QColor.fromRgb(0xc9, 0xe4, 0xc8))
            self._status_icon.set_icon_type('Executed')
            self._hide_progress_view()
        elif self._model.is_executing():
            # Blue
            self._brush = QtGui.QBrush(QtGui.QColor.fromRgb(164, 174, 197))
            self._status_icon.set_icon_type('None')
            self._show_progress_view()
        elif self._model.is_queued():
            # Blue
            self._brush = QtGui.QBrush(QtGui.QColor.fromRgb(164, 174, 197))
            self._status_icon.set_icon_type('Queued')
        elif (self._model.is_executable() and
              self._model.is_configuration_valid()):
            # Yellow
            self._brush = QtGui.QBrush(QtGui.QColor.fromRgb(231, 217, 188))
            self._status_icon.set_icon_type('None')
            self._hide_progress_view()
        else:
            # Standard gray
            self._brush = QtGui.QBrush(self._node_color)
            if not self._model.is_configuration_valid():
                self._status_icon.set_icon_type('Unconfigured')
            else:
                self._status_icon.set_icon_type(None)
            self._hide_progress_view()

        if self._brush != old_brush:
            self.update_later()

    @QtCore.Slot()
    def update_later(self):
        # QtCore.QTimer.singleShot(0, self.update)
        self.update()

    @QtCore.Slot(int)
    def _update_progress(self, progress):
        self._show_progress_view()
        if self._progress_view:
            self._progress_view.update_progress(progress)

    def _show_progress_view(self):
        if self._progress_view is None and self._model.is_executing():
            self._progress_view = NodeProgressView(parent=self)

    def _hide_progress_view(self):
        if self._progress_view is not None:
            if self.scene() is not None:
                self._progress_view.setParentItem(None)
                self.scene().removeItem(self._progress_view)
            del self._progress_view
            self._progress_view = None

    @QtCore.Slot(flow.Port)
    def _handle_input_port_created(self, port):
        port_view = PortView(port, self)
        self._input_port_views[port] = port_view

        self._signals.connect(
            port, port_view.connection_start_requested[object],
            self.connection_start_requested)
        self._signals.connect(
            port, port_view.connection_end_requested[object],
            self.connection_end_requested)
        self._signals.connect(
            port, port_view.open_add_context_requested[
                QtGui.QGraphicsSceneMouseEvent],
            self.open_add_context_requested)

    @QtCore.Slot(flow.Port)
    def _handle_output_port_created(self, port):
        port_view = PortView(port, self)
        self._output_port_views[port] = port_view

        self._signals.connect(
            port, port_view.connection_start_requested[object],
            self.connection_start_requested)
        self._signals.connect(
            port, port_view.connection_end_requested[object],
            self.connection_end_requested)
        self._signals.connect(
            port, port_view.open_add_context_requested[
                QtGui.QGraphicsSceneMouseEvent],
            self.open_add_context_requested)

    @QtCore.Slot(flow.Port)
    def _handle_input_port_removed(self, port):
        view = self._input_port_views.pop(port, None)
        if view is not None and self.scene():
            self.scene().removeItem(view)

    @QtCore.Slot(flow.Port)
    def _handle_output_port_removed(self, port):
        view = self._output_port_views.pop(port, None)
        if view is not None and self.scene():
            self.scene().removeItem(view)

    @QtCore.Slot(bool)
    def _handle_parameter_view_changed(self, state):
        if state:
            self._dialog_icon.set_icon_type('Open')
        else:
            self._dialog_icon.set_icon_type('None')
        self.update_later()

    def itemChange(self, change, value):
        if change == QtGui.QGraphicsItem.ItemPositionHasChanged:
            for port_view in itertools.chain(
                    self._input_port_views.values(),
                    self._output_port_views.values()):
                port_view.notify_position_changed()
        return super(BaseNodeView, self).itemChange(change, value)

    def remove(self):
        self.blockSignals(True)
        self._label.blockSignals(True)
        super(BaseNodeView, self).remove()
        for port_view in itertools.chain(
                self._input_port_views.values(),
                self._output_port_views.values()):
            port_view.remove()
            port_view.setParentItem(None)
            self.scene().removeItem(port_view)
        self.remove_all_ports()
        if self._label is not None:
            self._label.setParentItem(None)
            self.scene().removeItem(self._label)
            del self._label
            self._label = None
        self._hide_progress_view()
        self.blockSignals(False)

    def remove_all_ports(self):
        del self._input_port_views
        del self._output_port_views
        self._input_port_views = collections.OrderedDict()
        self._output_port_views = collections.OrderedDict()

    @QtCore.Slot(six.text_type)
    def _handle_label_edited(self, label):
        if self._model.name != label:
            cmd = user_commands.EditNodeLabelCommand(
                self._model, self._model.name, label)
            self._model.flow.undo_stack().push(cmd)

    def paint(self, painter, options, widget=None):
        painter.setBrush(self._brush)
        painter.setPen(self._pen)
        painter.drawPath(self._outline)

    def mouseDoubleClickEvent(self, event):
        if self._model.in_error_state():
            self._model.arm()
        elif self._model.is_executable():
            self._model.execute()
        elif self._model.is_configurable():
            self._model.configure()

    def set_this_z(self):
        self.setZValue(5)
        for port in self.input_port_views():
            port.set_this_z()
        for port in self.output_port_views():
            port.set_this_z()

    def set_other_z(self):
        self.setZValue(4)
        for port in self.input_port_views():
            port.set_other_z()
        for port in self.output_port_views():
            port.set_other_z()

    def reset_z(self):
        self.setZValue(3)
        for port in self.input_port_views():
            port.reset_z()
        for port in self.output_port_views():
            port.reset_z()

    @QtCore.Slot()
    def _edit_node_requested(self):
        raise NotImplementedError('Not implemented for interface')

    @QtCore.Slot()
    def _node_help_requested(self):
        raise NotImplementedError('Not implemented for interface')
