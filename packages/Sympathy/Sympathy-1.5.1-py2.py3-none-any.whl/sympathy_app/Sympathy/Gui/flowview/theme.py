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
import PySide.QtGui as QtGui

theme_instance = None


class Theme(object):
    def __init__(self):
        super(Theme, self).__init__()
        self._selection_color = None
        self._active_color = None
        self._light_color = None
        self._midlight_color = None
        self._mid_color = None
        self._dark_color = None

    @property
    def selection_color(self):
        return self._selection_color

    @property
    def active_color(self):
        return self._active_color

    @property
    def light_color(self):
        return self._light_color

    @property
    def midlight_color(self):
        return self._midlight_color

    @property
    def mid_color(self):
        return self._mid_color

    @property
    def dark_color(self):
        return self._dark_color

    @property
    def darker_color(self):
        return self._darker_color


class Grey(Theme):
    """Class that holds the graphical theme of the application"""

    def __init__(self):
        super(Grey, self).__init__()
        palette = QtGui.qApp.palette()
        self._selection_color = QtGui.QColor.fromRgb(150, 150, 255, 255)
        self._active_color = QtGui.QColor.fromRgb(255, 100, 100, 220)
        self._light_color = palette.color(QtGui.QPalette.Light)
        self._midlight_color = palette.color(QtGui.QPalette.Midlight)
        self._mid_color = palette.color(QtGui.QPalette.Mid)
        self._dark_color = palette.color(QtGui.QPalette.Dark)
        self._darker_color = QtGui.QColor.fromHsv(120, 0, 152)


def create_theme():
    global theme_instance
    if theme_instance is not None:
        raise RuntimeError('Theme already instantiated')
    theme_instance = Grey()


def instance():
    """Returns the global theme instance"""
    if theme_instance is None:
        create_theme()
    return theme_instance
