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
from sympathy.utils.components import get_components


class ICalcPlugin(object):
    """Interface for calculator plugins."""

    WEIGHT = 10000

    @staticmethod
    def gui_dict(generic):
        """Return a dictionary with functions that will be shown in the
        configuration gui for the calculator node.
        """
        return {}

    @staticmethod
    def globals_dict():
        """Return a dictionary that will be added to the globals dictionary
        when executing calculations.
        """
        return {}

    @staticmethod
    def imports():
        """Return a dictionary with extra imports that will be available in
        the calculator.
        For example, add the imports
            import math
            import scipy.integrate
            import scipy.signal as sig
        to your plugin, and return a dictionary like this:
            return {'math': math,
                    'spint': scipy.integrate,
                    'sig': sig}
        and math, spint and sig will be available as modules in the calculator.
        """
        return {}


class MatlabCalcPlugin(object):
    """Interface for calculator plugins."""

    WEIGHT = 10000

    @staticmethod
    def gui_dict(generic):
        """Return a dictionary with functions that will be shown in the
        configuration gui for the calculator node.
        """
        return {}

    @staticmethod
    def globals_dict():
        """Return a dictionary that will be added to the globals dictionary
        when executing calculations.
        """
        return {}


def available_plugins(backend='python'):
    """Return all available plugins derived for a specific backend."""
    plugin_classes = {'python': ICalcPlugin,
                      'matlab': MatlabCalcPlugin}
    return get_components('plugin_*.py', plugin_classes[backend])
