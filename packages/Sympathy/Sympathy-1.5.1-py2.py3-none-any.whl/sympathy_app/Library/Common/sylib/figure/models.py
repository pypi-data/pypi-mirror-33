# Copyright (c) 2016-2017, System Engineering Software Society
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
from __future__ import (
    print_function, division, unicode_literals, absolute_import)
import copy
import types
from collections import OrderedDict, defaultdict

import six
import numpy as np

from sylib.icons.utils import SvgIcon, color_icon, create_icon
from sylib.tree_model.models import NodeTags, BaseNode, Property
from sylib.tree_model import widgets as tree_widgets
from sylib.figure import colors, mpl_utils, common
from sylib.figure import widgets as fig_widgets

SY_XDATA_PARAMS = {'label': 'X Data',
                   'eval': six.text_type,
                   'icon': SvgIcon.x_data,
                   'default': '',
                   'options': None,
                   'description': 'Specify the column used as x-data, '
                                  'either as column name or as python '
                                  'expression which evaluates to a numpy '
                                  'ndarray',
                   'editor': tree_widgets.SyDataEdit}

SY_YDATA_PARAMS = {'label': 'Y Data',
                   'eval': six.text_type,
                   'icon': SvgIcon.y_data,
                   'default': '',
                   'options': None,
                   'description': 'Specify the column used as y-data, '
                                  'either as column name or as python '
                                  'expression which evaluates to a numpy '
                                  'ndarray',
                   'editor': tree_widgets.SyDataEdit}

SY_ZDATA_PARAMS = {'label': 'Z Data',
                   'eval': six.text_type,
                   'icon': SvgIcon.z_data,
                   'default': '',
                   'options': None,
                   'description': 'Specify the column used as z-data, '
                                  'either as column name or as python '
                                  'expression which evaluates to a numpy '
                                  'ndarray',
                   'editor': tree_widgets.SyDataEdit}

SY_LABEL_PARAMS = {'label': 'Label',
                   'eval': six.text_type,
                   'icon': SvgIcon.label,
                   'default': '',
                   'options': None,
                   'description': 'Specify the text used as label.',
                   'editor': tree_widgets.SyLabelEdit}

SY_COLOR_PARAMS = {'label': 'Color',
                   'eval': 'colortype',
                   'icon': lambda value: color_icon(value),
                   'default': None,
                   'options': colors.COLORS,
                   'description': 'Specify a color either as RGB '
                                  '(e.g. "[1., 0., 0.]" or [255, 0, 0]), '
                                  'hex color (e.g. #ff00000), or as a '
                                  'matplotlib color name (e.g. "red" or "r").',
                   'editor': fig_widgets.SyColorEdit}

SY_COLORMAP_PARAMS = {'label': 'Colormap',
                      'eval': 'options',
                      # 'icon': lambda value: colormap_icon(value),
                      'icon': SvgIcon.color,
                      'default': 'auto',
                      'options': list(colors.COLORMAPS.keys()),
                      'description': 'Specify the name of a colormap. '
                                     'Default behavior (auto) tries to '
                                     'determine a fitting colormap depending '
                                     'on the data.',
                      'editor': tree_widgets.SyComboBox}

SY_NORMALIZATION_PARAMS = {'label': 'Colormap scale',
                           'eval': 'options',
                           'icon': SvgIcon.scales,
                           'default': 'linear',
                           'options': ['linear', 'log'],
                           'description': 'Choose between linear and '
                                          'logarithmic color scale. ',
                           'editor': tree_widgets.SyComboBox}

SY_ASPECT_PARAMS = {'label': 'Aspect',
                    'eval': 'options',
                    'icon': SvgIcon.aspect_ratio,
                    'default': 'auto',
                    'options': ('auto', 'equal'),
                    'description': 'Specify aspect ratio. Default value '
                                   '\'auto\' tries to fill up figure.',
                    'editor': tree_widgets.SyComboBox}

SY_EDGECOLOR_PARAMS = {'label': 'Edge Color',
                       'eval': 'colortype',
                       'icon': lambda value: color_icon(value),
                       'default': None,
                       'options': colors.COLORS,
                       'description': 'Specify a color either as RGB '
                                      '(e.g. "[1., 0., 0.]" or [255, 0, 0]), '
                                      'hex color (e.g. #ff00000), or as a '
                                      'matplotlib color name '
                                      '(e.g. "red" or "r").',
                       'editor': fig_widgets.SyColorEdit}

SY_LINEWIDTH_PARAMS = {'label': 'Line Width',
                       'eval': float,
                       'icon': SvgIcon.linewidth,
                       'default': '1.',
                       'options': (0., None, 1.),
                       'description': 'Specify the line width as floating '
                                      'point number.',
                       'editor': tree_widgets.SyDoubleSpinBox}

SY_LINESTYLE_PARAMS = {'label': 'Line Style',
                       'eval': 'options',
                       'icon': SvgIcon.linestyle,
                       'default': 'solid',
                       'options': mpl_utils.LINESTYLES,
                       'description': 'Specify the line style (e.g. "solid" or'
                                      '"dashed").',
                       'editor': tree_widgets.SyComboBox}

SY_MARKER_PARAMS = {'label': 'Marker',
                    'eval': six.text_type,
                    'icon': SvgIcon.marker,
                    'default': 'circle',
                    'options': list(mpl_utils.MARKERS.values()),
                    'description': 'Specify the marker used.',
                    'editor': tree_widgets.SyComboBox}

SY_DRAWSTYLE_PARAMS = {'label': 'Draw Style',
                       'eval': 'options',
                       'icon': SvgIcon.drawstyle,
                       'default': 'default',
                       'options': mpl_utils.DRAWSTYLES,
                       'description': 'Specify the draw style.',
                       'editor': tree_widgets.SyComboBox}

SY_SIZEBASE_PARAMS = {'label': 'Size',
                      'eval': float,
                      'icon': SvgIcon.ruler,
                      'default': 1.,
                      'options': (0., None, 1.),
                      'description': 'Specify the size.',
                      'editor': tree_widgets.SyDoubleSpinBox}

SY_ALPHA_PARAMS = {'label': 'Alpha',
                   'eval': float,
                   'icon': SvgIcon.alpha,
                   'default': 1.,
                   'options': (0., 1., 0.05),
                   'description': 'Specify the transparency (alpha) value.',
                   'editor': tree_widgets.SyDoubleSpinBox}

SY_ZORDER_PARAMS = {'label': 'Z-Order',
                    'eval': float,
                    'icon': SvgIcon.layer,
                    'default': 1,
                    'options': (1, None, 1),
                    'description': 'Specify the stack order. Higher numbers '
                                   'get plotted on top of lower numbers.',
                    'editor': tree_widgets.SySpinBox}

SY_BAR_LABEL_VALIGN_PARAMS = {'label': 'Bar Labels VAlign',
                              'eval': 'options',
                              'icon': SvgIcon.barlabelvalgin,
                              'default': 'center',
                              'options': [
                                  'under', 'bottom', 'center', 'top', 'over'],
                              'description': 'Specify the location for the '
                                             'Bar Label.',
                              'editor': tree_widgets.SyComboBox}

SY_VISIBLE_PARAMS = {'label': 'Visible',
                     'eval': 'options',
                     'icon': lambda v: create_icon(
                         SvgIcon.visible if v == 'True' else
                         SvgIcon.invisible),
                     'default': 'True',
                     'options': ['True', 'False'],
                     'description': 'Enable/disable if this item should be '
                                    'shown in the figure.',
                     'editor': tree_widgets.SyComboBox}


class FigureBaseNode(BaseNode):
    def create_leaf(self, leaf, data=None, params=None):
        if params is None:
            params = self.NODE_LEAFS.get(leaf)
        if data is None:
            data = params['default']
        # add the data to the model if required but not existing
        is_required = leaf in self.REQUIRED_LEAFS
        leaf_cls = FigureRequiredProperty if is_required else FigureProperty
        leaf_inst = leaf_cls({'label': params['label'],
                              'name': leaf,
                              'eval': params['eval'],
                              'default': params['default'],
                              'icon': params['icon'],
                              'options': params['options'],
                              'editor': params['editor'],
                              'description': params.get('description', ''),
                              'data': data},
                             parent=None)
        return leaf_inst


class FigureProperty(Property):
    def set_data(self, value):
        value = common.parse_type(value, self.eval, self.options)
        self.data = six.text_type(value)

    def get_icon(self):
        if isinstance(self.icon, types.FunctionType):
            value = common.parse_type(self.data, self.eval, self.options)
            icon = self.icon(value)
        else:
            icon = create_icon(self.icon)
        return icon

    def export_config(self, prefix=None):
        if prefix is None:
            prefix = []
        else:
            prefix = list(prefix)
        name = '.'.join(prefix + [self.name])
        # wrapping into list is necessary
        return [(name, self.data)]


class FigureRequiredProperty(FigureProperty):
    """A property which is not deletable."""
    cls_tags = frozenset({NodeTags.editable})


class Root(FigureBaseNode):
    """Root node."""

    node_type = 'root'
    cls_tags = frozenset({NodeTags.root})

    def __init__(self, data, parent=None):
        super(Root, self).__init__(data, parent)
        self._data_table = None
        self._given_ids = defaultdict(int)

    def init(self, data):
        self.children = []
        # Build up children member gradually
        if 'figure' in data:
            figure = Figure(data.pop('figure'), parent=self)
            self.children = [figure]

    @classmethod
    def valid_children(cls):
        return frozenset({Figure})

    def set_data_table(self, data_table):
        self._data_table = data_table

    def get_data_table(self):
        return self._data_table

    def get_id(self, node):
        """Create a unique id for every node, depending on node_type."""
        self._given_ids[node.node_type] += 1
        return '{}-{}'.format(node.node_type, self._given_ids[node.node_type])

    def export_config(self, prefix=None):
        config = []
        for child in self.children:
            config.extend(child.export_config(prefix=None))
        return config


class Figure(FigureBaseNode):
    """Figure node."""

    node_type = 'figure'
    description = 'The base figure.'

    NODE_LEAFS = OrderedDict([
        ('title', {'label': 'Title',
                   'eval': six.text_type,
                   'icon': SvgIcon.label,
                   'default': '',
                   'options': None,
                   'editor': tree_widgets.SyLabelEdit})
    ])

    @classmethod
    def valid_children(cls):
        return frozenset({Axes, Legend, FigureProperty})

    def init(self, data):
        for axes_data in data.pop('axes', []):
            axes = Axes(axes_data, parent=self)
            self.children.append(axes)
        self.add_children_to_node(data, [Legend])

    def has_axes(self):
        return any([isinstance(child, Axes) for child in self.children])

    def export_config(self, prefix=None):
        if prefix is None:
            prefix = []
        else:
            prefix = list(prefix)
        prefix += [self.node_type, ]
        config = []
        for child in self.children:
            config.extend(child.export_config(prefix=prefix))
        return config


class Axes(FigureBaseNode):
    """Axes node."""

    icon = SvgIcon.plot
    default_data = OrderedDict([
        ('type', 'axes'),
        ('xaxis', OrderedDict([('position', 'bottom')])),
        ('yaxis', OrderedDict([('position', 'left')])),
        ('plots', [])
    ])

    node_type = 'axes'
    needs_id = True
    description = ('The axes defines the axes labels, axes limits, etc. and '
                   'contains the different plot types (e.g. LinePlot, etc.).')

    cls_tags = frozenset({
        NodeTags.deletable,
        NodeTags.rearrangable,
        NodeTags.is_container,
        NodeTags.editable,
        NodeTags.copyable})

    NODE_LEAFS = OrderedDict([
        ('title', {'label': 'Title',
                   'eval': six.text_type,
                   'icon': SvgIcon.label,
                   'default': '',
                   'options': None,
                   'description': 'Specify the title of the Axes.',
                   'editor': tree_widgets.SyLabelEdit}),
        ('aspect', {'label': 'Aspect Ratio',
                    'eval': six.text_type,
                    'icon': SvgIcon.aspect,
                    'default': 'auto',
                    'options': ['auto', 'equal', '1.'],
                    'description': 'Specify the aspect ration of the axes.',
                    'editor': tree_widgets.SyComboBoxEditable}),
        ('color_cycle', {'label': 'Color cycle',
                         'eval': 'options',
                         'icon': SvgIcon.color,
                         'default': 'default',
                         'options': list(colors.COLOR_CYCLES.keys()),
                         'editor': tree_widgets.SyComboBox})
    ])

    STORED_LEAFS = {
        'xaxis_position': 'xaxis.position',
        'yaxis_position': 'yaxis.position',
        'title': 'title',
        'xlabel': 'xaxis.label',
        'ylabel': 'yaxis.label',
        'xlim': 'xaxis.lim',
        'ylim': 'yaxis.lim',
        'xscale': 'xaxis.scale',
        'yscale': 'yaxis.scale',
        'aspect': 'aspect',
        'legend': 'legend',
        'grid': 'grid',
        'color_cycle': 'color_cycle'}

    @classmethod
    def valid_children(cls):
        return frozenset({FigureProperty, XAxis, YAxis, Plots, Legend, Grid})

    def init(self, data):
        for axis_type, axis_cls in zip(['xaxis', 'yaxis'], [XAxis, YAxis]):
            c_data = data.pop(axis_type, copy.deepcopy(axis_cls.default_data))
            if c_data is not None:
                self.children.append(axis_cls(c_data, parent=self))

        plots = Plots(data.pop('plots', []), parent=self)
        self.children.append(plots)
        for child_cls in [Legend, Grid]:
            if child_cls.node_type in data:
                child = child_cls(data.pop(child_cls.node_type), parent=self)
                self.children.append(child)

    def plots(self):
        """Return a list of all plot objects."""
        plot_parent = self.plot_container
        return [c for c in plot_parent.children if isinstance(c, BasePlot)]

    @property
    def plot_container(self):
        for child in self.children:
            if isinstance(child, Plots):
                return child
        return None

    @property
    def label(self):
        title_child = self.get_leaf_with_name('title')
        if title_child is not None:
            title = title_child.data
            data_table = self.root_node().get_data_table()
            title = common.parse_value(title, data_table)
            return '{} ({})'.format(self.prettify_class_name(), title)
        return super(Axes, self).label

    def export_config(self, prefix=None):
        prefix = []  # its a root element in the configuration table
        config = []
        node_id = self.root_node().get_id(self)
        prefix += [self.node_type, node_id]
        for child in self.children:
            config.extend(child.export_config(prefix=prefix))
        return config


class Colorbar(FigureBaseNode):
    icon = SvgIcon.color
    node_type = 'colorbar'
    default_data = OrderedDict([
        ('show', 'True'),
    ])

    description = 'Defines Colorbar properties.'
    cls_tags = frozenset({
        NodeTags.rearrangable,
        NodeTags.copyable,
        NodeTags.unique,
        NodeTags.deletable})

    NODE_LEAFS = OrderedDict([
        ('show', SY_VISIBLE_PARAMS),
        ('orientation', {'label': 'Orientation',
                         'eval': 'options',
                         'icon': SvgIcon.colorbar_orientation,
                         'default': 'vertical',
                         'options': ['vertical', 'horizontal'],
                         'description': ('Specify the orientation of the '
                                         'colorbar.'),
                         'editor': tree_widgets.SyComboBox}),
        ('label', SY_LABEL_PARAMS),
    ])
    REQUIRED_LEAFS = set()

    @classmethod
    def valid_children(cls):
        return frozenset({FigureProperty})

    def export_config(self, prefix=None):
        if prefix is None:
            prefix = []
        else:
            prefix = list(prefix)
        config = []
        prefix += [self.node_type, ]
        for child in self.children:
            config.extend(child.export_config(prefix=prefix))
        return config


class BaseFont(FigureBaseNode):
    icon = SvgIcon.text
    node_type = 'font'
    default_data = OrderedDict([
        ('color', 'k'),
        ('size', 12)
    ])

    description = 'Defines Font properties.'
    cls_tags = frozenset({
        NodeTags.rearrangable,
        NodeTags.copyable,
        NodeTags.unique,
        NodeTags.deletable})

    NODE_LEAFS = OrderedDict([
        ('color', SY_COLOR_PARAMS),
        ('size', SY_SIZEBASE_PARAMS)
    ])

    REQUIRED_LEAFS = set()

    @classmethod
    def valid_children(cls):
        return frozenset({FigureProperty})

    def export_config(self, prefix=None):
        if prefix is None:
            prefix = []
        else:
            prefix = list(prefix)
        config = []
        prefix += [self.node_type, ]
        for child in self.children:
            config.extend(child.export_config(prefix=prefix))
        return config


class BarLabelsFont(BaseFont):
    node_type = 'bar_labels_font'
    description = 'Defines the Font properties of the Bar Labels.'


class BasePlot(FigureBaseNode):
    default_data = OrderedDict([
        ('xdata', ''),
        ('ydata', ''),
    ])

    needs_id = True
    cls_tags = frozenset({
        NodeTags.is_container,
        NodeTags.rearrangable,
        NodeTags.deletable,
        NodeTags.copyable})

    REQUIRED_LEAFS = {'xdata', 'ydata'}

    @classmethod
    def valid_children(cls):
        return frozenset({FigureProperty})

    def init(self, data):
        valid_child_nodes = [c for c in self.valid_children() if not c.is_leaf]
        for child_cls in valid_child_nodes:
            if child_cls.node_type in data:
                child = child_cls(data.pop(child_cls.node_type), parent=self)
                self.children.append(child)

    @property
    def label(self):
        label_child = self.get_leaf_with_name('label')
        if label_child is not None:
            label = label_child.data
            data_table = self.root_node().get_data_table()
            label = common.parse_value(label, data_table,
                                       extra_vars={'e': '_e_', 'i': '_i_'})
            return '{} ({})'.format(self.prettify_class_name(), label)
        return super(BasePlot, self).label

    def export_config(self, prefix=None):
        if prefix is None:
            prefix = []
        else:
            prefix = list(prefix)
        config = []
        node_id = self.root_node().get_id(self)
        this_prefix = [self.node_type, node_id]

        parent_id = prefix[-1]
        if (isinstance(self.parent, Plots) and
                isinstance(self.parent.parent, Axes)):
            prop_s = '.'.join(this_prefix + ['axes'])
            config.append((prop_s, parent_id))
        elif isinstance(self.parent, (BarContainer, Iterator)):
            prop_s = '.'.join(this_prefix + ['container'])
            config.append((prop_s, parent_id))
            # this shouldn't be required because container is memeber of an
            # axes
            # if isinstance(self.parent.parent.parent, Axes):
            #     prop_s = '.'.join([self.node_type, self.node_id, 'axes'])
            #     config.append((prop_s, self.parent.parent.parent.node_id))
        for child in self.children:
            config.extend(child.export_config(prefix=this_prefix))
        return config


class LinePlot(BasePlot):
    icon = SvgIcon.line
    node_type = 'line'
    description = ('A Line Plot defined by x and y-data with different '
                   'linestyles, linewidth, additional makers, etc.')

    default_data = OrderedDict([
        ('xdata', ''),
        ('ydata', ''),
    ])

    NODE_LEAFS = OrderedDict([
        ('xdata', SY_XDATA_PARAMS),
        ('ydata', SY_YDATA_PARAMS),
        ('label', SY_LABEL_PARAMS),
        ('marker', SY_MARKER_PARAMS),
        ('markersize', {'label': 'Markersize',
                        'eval': float,
                        'icon': SvgIcon.markersize,
                        'default': 5,
                        'options': (0., None, 0.01),
                        'editor': tree_widgets.SyDoubleSpinBox}),
        ('markeredgecolor', {'label': 'Marker Edge Color',
                             'eval': 'colortype',
                             'icon': lambda value: color_icon(value),
                             'default': None,
                             'options': colors.COLORS,
                             'description': 'Specify a color either as RGB '
                                            '(e.g. "[1., 0., 0.]" or '
                                            '[255, 0, 0]), hex color '
                                            '(e.g. #ff00000), or as a '
                                            'matplotlib color name '
                                            '(e.g. "red" or "r").',
                             'editor': fig_widgets.SyColorEdit}),
        ('markeredgewidth', {'label': 'Markeredgewidth',
                             'eval': float,
                             'icon': SvgIcon.linewidth,
                             'default': 0.1,
                             'options': (0., None, 0.01),
                             'editor': tree_widgets.SyDoubleSpinBox}),
        ('markerfacecolor', {'label': 'Marker Face Color',
                             'eval': 'colortype',
                             'icon': lambda value: color_icon(value),
                             'default': None,
                             'options': colors.COLORS,
                             'description': 'Specify a color either as RGB '
                                            '(e.g. "[1., 0., 0.]" or '
                                            '[255, 0, 0]), hex color '
                                            '(e.g. #ff00000), or as a '
                                            'matplotlib color name '
                                            '(e.g. "red" or "r").',
                             'editor': fig_widgets.SyColorEdit}),
        ('linestyle', SY_LINESTYLE_PARAMS),
        ('linewidth', SY_LINEWIDTH_PARAMS),
        ('color', SY_COLOR_PARAMS),
        ('alpha', SY_ALPHA_PARAMS),
        ('zorder', SY_ZORDER_PARAMS),
        ('drawstyle', SY_DRAWSTYLE_PARAMS),
    ])


class ScatterPlot(BasePlot):
    icon = SvgIcon.scatter
    node_type = 'scatter'
    description = ('A Scatter Plot defined by x and y-data with different '
                   'marker styles, sizes, etc.')

    NODE_LEAFS = OrderedDict([
        ('xdata', SY_XDATA_PARAMS),
        ('ydata', SY_YDATA_PARAMS),
        ('label', SY_LABEL_PARAMS),
        ('s', {'label': 'Markersize',
               'eval': float,
               'icon': SvgIcon.markersize,
               'default': 20,
               'options': (0., 1000, 0.01),
               'description': 'Specify the marker size.',
               'editor': tree_widgets.SyDoubleSpinBox}),
        ('color', SY_COLOR_PARAMS),
        ('cmap', SY_COLORMAP_PARAMS),
        ('vmin', {'label': 'Colormap Min',
                  'eval': float,
                  'icon': SvgIcon.colorbar_min,
                  'default': 0,
                  'options': (-np.inf, None, 1),
                  'editor': tree_widgets.SyDoubleSpinBox}),
        ('vmax', {'label': 'Colormap Max',
                  'eval': float,
                  'icon': SvgIcon.colorbar_max,
                  'default': 1,
                  'options': (-np.inf, None, 1),
                  'editor': tree_widgets.SyDoubleSpinBox}),
        ('marker', SY_MARKER_PARAMS),
        ('alpha', SY_ALPHA_PARAMS),
        ('zorder', SY_ZORDER_PARAMS),
    ])

    @classmethod
    def valid_children(cls):
        return frozenset({Colorbar, FigureProperty})

    def init(self, data):
        valid_child_nodes = [c for c in self.valid_children() if not c.is_leaf]
        for child_cls in valid_child_nodes:
            if child_cls.node_type in data:
                child = child_cls(data.pop(child_cls.node_type), parent=self)
                self.children.append(child)


class HeatmapPlot(BasePlot):
    icon = SvgIcon.heatmap
    node_type = 'heatmap'
    description = ('A heatmap plot defined by x, y, and z-data. The color of '
                   'each cell corresponds to the z-value at those x and '
                   'y-coordinates.')

    default_data = OrderedDict([
        ('xdata', ''),
        ('ydata', ''),
        ('zdata', ''),
    ])

    NODE_LEAFS = OrderedDict([
        ('xdata', SY_XDATA_PARAMS),
        ('ydata', SY_YDATA_PARAMS),
        ('zdata', SY_ZDATA_PARAMS),
        ('label', SY_LABEL_PARAMS),
        ('aspect', SY_ASPECT_PARAMS),
        ('vmin', {'label': 'Colormap Min',
                  'eval': float,
                  'icon': SvgIcon.colorbar_min,
                  'default': 0,
                  'options': (-np.inf, None, 1),
                  'editor': tree_widgets.SyDoubleSpinBox}),
        ('vmax', {'label': 'Colormap Max',
                  'eval': float,
                  'icon': SvgIcon.colorbar_max,
                  'default': 1,
                  'options': (-np.inf, None, 1),
                  'editor': tree_widgets.SyDoubleSpinBox}),
        ('colormap', SY_COLORMAP_PARAMS),
        ('normalization', SY_NORMALIZATION_PARAMS),
        ('zlabels', {'label': 'Z Labels',
                     'eval': six.text_type,
                     'icon': SvgIcon.label,
                     'default': '',
                     'options': None,
                     'description': 'Specify data used as "Labels" printed '
                                    'in each bin. Should a python expression '
                                    'which evaluates to a numpy ndarray',
                     'editor': tree_widgets.SyDataEdit}),
        ('zorder', SY_ZORDER_PARAMS),
    ])

    REQUIRED_LEAFS = {'xdata', 'ydata', 'zdata'}

    @classmethod
    def valid_children(cls):
        return frozenset({Colorbar, FigureProperty})

    def init(self, data):
        valid_child_nodes = [c for c in self.valid_children() if not c.is_leaf]
        for child_cls in valid_child_nodes:
            if child_cls.node_type in data:
                child = child_cls(data.pop(child_cls.node_type), parent=self)
                self.children.append(child)


class BarPlot(BasePlot):
    icon = SvgIcon.bar
    node_type = 'bar'
    description = ('A Bar Plot for categorical y-data. Additional '
                   '"Bin Labels" can be given as x-axis labels.')

    cls_tags = frozenset({
        NodeTags.is_container,
        NodeTags.rearrangable,
        NodeTags.deletable,
        NodeTags.copyable})

    default_data = OrderedDict([
        ('ydata', ''),
        ('bin_labels', ''),
    ])

    NODE_LEAFS = OrderedDict([
        ('ydata', SY_YDATA_PARAMS),
        ('bin_labels', {'label': 'Bin Labels',
                        'eval': six.text_type,
                        'icon': SvgIcon.label,
                        'default': '',
                        'options': None,
                        'description': 'Specify data used as "Labels" plotted '
                                       'on the x-axis, either as column '
                                       'name or as python expression which '
                                       'evaluates to a numpy ndarray',
                        'editor': tree_widgets.SyDataEdit}),
        ('rot_bin_labels', {'label': 'Rotate Bin Labels',
                            'eval': 'options',
                            'icon': SvgIcon.rotate,
                            'default': 'Horizontal',
                            'options': ['Horizontal', 'Vertical', 'Clockwise',
                                        'Counter clockwise'],
                            'description': 'Choose rotation of the bin '
                                           'labels. This is especially '
                                           'useful for long labels.',
                            'editor': tree_widgets.SyComboBox}),
        ('label', SY_LABEL_PARAMS),
        ('bar_labels', {'label': 'Bar Labels',
                        'eval': six.text_type,
                        'icon': SvgIcon.label,
                        'default': '',
                        'options': None,
                        'description': 'Specify data used as "Labels" plotted '
                                       'on top of the Bars, either as column '
                                       'name or as python expression which '
                                       'evaluates to a numpy ndarray',
                        'editor': tree_widgets.SyDataEdit}),
        ('bar_labels_valign', SY_BAR_LABEL_VALIGN_PARAMS),
        ('rwidth', {'label': 'R width',
                    'eval': float,
                    'icon': SvgIcon.barwidth,
                    'default': 1.,
                    'options': (0., 1., 0.05),
                    'description': 'Specify the total width used for one '
                                   '"bin".',
                    'editor': tree_widgets.SyDoubleSpinBox}),
        ('color', SY_COLOR_PARAMS),
        ('edgecolor', SY_EDGECOLOR_PARAMS),
        ('linewidth', SY_LINEWIDTH_PARAMS),
        ('linestyle', SY_LINESTYLE_PARAMS),
        ('alpha', SY_ALPHA_PARAMS),
        ('zorder', SY_ZORDER_PARAMS),
    ])

    REQUIRED_LEAFS = {'ydata'}

    @classmethod
    def valid_children(cls):
        return frozenset({BarLabelsFont, FigureProperty})

    def init(self, data):
        valid_child_nodes = [c for c in self.valid_children() if not c.is_leaf]
        for child_cls in valid_child_nodes:
            if child_cls.node_type in data:
                child = child_cls(data.pop(child_cls.node_type), parent=self)
                self.children.append(child)


class HistogramPlot(BasePlot):
    icon = SvgIcon.histogram1d
    node_type = 'hist'
    description = ('A Histogram Plot for plotting sequential binned y-data in '
                   'Bar or Step style. The "Bin egdes" need to be given as '
                   '"Bin min edges" and "Bin max edges".')

    cls_tags = frozenset({
        NodeTags.is_container,
        NodeTags.rearrangable,
        NodeTags.deletable,
        NodeTags.copyable})

    default_data = OrderedDict([
        ('bin_min_edges', ''),
        ('bin_max_edges', ''),
        ('ydata', ''),
    ])

    NODE_LEAFS = OrderedDict([
        ('bin_min_edges', {'label': 'Bin min edges',
                           'eval': six.text_type,
                           'icon': SvgIcon.bin_min_edge,
                           'default': '',
                           'options': None,
                           'description': 'Specify the column used as '
                                          '"Bin min edges", either as column '
                                          'name or as python expression which '
                                          'evaluates to a numpy ndarray',
                           'editor': tree_widgets.SyDataEdit}),
        ('bin_max_edges', {'label': 'Bin max edges',
                           'eval': six.text_type,
                           'icon': SvgIcon.bin_max_edge,
                           'default': '',
                           'options': None,
                           'description': 'Specify the column used as '
                                          '"Bin max edges", either as column '
                                          'name or as python expression which '
                                          'evaluates to a numpy ndarray',
                           'editor': tree_widgets.SyDataEdit}),
        ('ydata', SY_YDATA_PARAMS),
        ('bar_labels', {'label': 'Bar Labels',
                        'eval': six.text_type,
                        'icon': SvgIcon.label,
                        'default': '',
                        'options': None,
                        'description': 'Specify data used as "Labels" plotted '
                                       'on the x-axis, either as column '
                                       'name or as python expression which '
                                       'evaluates to a numpy ndarray',
                        'editor': tree_widgets.SyDataEdit}),
        ('bar_labels_valign', SY_BAR_LABEL_VALIGN_PARAMS),
        ('label', SY_LABEL_PARAMS),
        ('color', SY_COLOR_PARAMS),
        ('edgecolor', SY_EDGECOLOR_PARAMS),
        ('linewidth', SY_LINEWIDTH_PARAMS),
        ('linestyle', SY_LINESTYLE_PARAMS),
        ('alpha', SY_ALPHA_PARAMS),
        ('zorder', SY_ZORDER_PARAMS),
        ('histtype', {'label': 'Histogram Type',
                      'eval': 'options',
                      'icon': SvgIcon.histtype,
                      'default': 'bar',
                      'options': mpl_utils.HISTTYPES,
                      'description': 'Specify if the Histograms get plotted '
                                     'as individual Bars or filled step line '
                                     'plot.',
                      'editor': tree_widgets.SyComboBox}),
    ])

    REQUIRED_LEAFS = {'bin_min_edges', 'bin_max_edges', 'ydata'}

    @classmethod
    def valid_children(cls):
        return frozenset({BarLabelsFont, FigureProperty})

    def init(self, data):
        valid_child_nodes = [c for c in self.valid_children() if c.is_leaf]
        for child_cls in valid_child_nodes:
            if child_cls.node_type in data:
                child = child_cls(data.pop(child_cls.node_type), parent=self)
                self.children.append(child)


class BasePlotContainer(FigureBaseNode):
    icon = SvgIcon.layers
    needs_id = True

    cls_tags = frozenset({NodeTags.is_container})

    PLOT_TYPES = {}

    @classmethod
    def valid_children(cls):
        return frozenset({FigureProperty})

    def init(self, data):
        self.add_plots(data)

    def add_plots(self, data):
        for plot_data in data:
            if isinstance(plot_data, OrderedDict):
                plot_type = plot_data.get('type')
                if plot_type is not None:
                    plot_cls = self.PLOT_TYPES.get(plot_type)
                    plot = plot_cls(plot_data, parent=self)
                    self.children.append(plot)


class Iterator(BasePlotContainer):
    icon = SvgIcon.iterator
    needs_id = True
    node_type = 'iterator'

    cls_tags = frozenset({
        NodeTags.is_container,
        NodeTags.deletable,
        NodeTags.rearrangable,
        NodeTags.copyable})

    PLOT_TYPES = {
        'scatter': ScatterPlot,
        'line': LinePlot,
        'bar': BarPlot,
        'hist': HistogramPlot,
    }

    NODE_LEAFS = OrderedDict([
        ('iterable', {'label': 'Iterable',
                      'eval': six.text_type,
                      'icon': None,
                      'default': 'e = ',
                      'options': None,
                      'description': '',
                      'editor': tree_widgets.SyIterableEdit}),
        ('counter', {'label': 'Counter name',
                     'eval': six.text_type,
                     'icon': None,
                     'default': 'i',
                     'options': None,
                     'description': 'The variable name used for the '
                                    'incremental counter for this iterator.',
                     'editor': tree_widgets.SyBaseTextEdit})
    ])

    REQUIRED_LEAFS = {'iterable'}

    default_data = OrderedDict([
        ('plots', []),
    ])

    @classmethod
    def valid_children(cls):
        return frozenset(
            set(cls.PLOT_TYPES.values()) | {FigureProperty})

    def init(self, data):
        self.add_plots(data)

    def add_plots(self, data):
        for plot_data in data.pop('plots', []):
            plot_type = plot_data.get('type')
            if plot_type is not None:
                plot_cls = self.PLOT_TYPES.get(plot_type)
                plot = plot_cls(plot_data, parent=self)
                self.children.append(plot)

    def get_available_children(self):
        if len([c for c in self.children if c.node_type in self.PLOT_TYPES]):
            return []
        elif isinstance(self.parent, BasePlotContainer):
            return self.valid_children() & self.parent.valid_children()
        else:
            return self.valid_children()

    def export_config(self, prefix=None):
        if prefix is None:
            prefix = []
        else:
            prefix = list(prefix)
        config = []
        node_id = self.root_node().get_id(self)
        this_prefix = [self.node_type, node_id]

        parent_id = prefix[-1]
        if (isinstance(self.parent, Plots) and
                isinstance(self.parent.parent, Axes)):
            prop_s = '.'.join(this_prefix + ['axes'])
            config.append((prop_s, parent_id))
        elif isinstance(self.parent, (BarContainer, HistogramContainer)):
            prop_s = '.'.join(this_prefix + ['container'])
            config.append((prop_s, parent_id))

        for child in self.children:
            config.extend(child.export_config(prefix=this_prefix))
        return config


class BarContainer(BasePlotContainer):
    icon = SvgIcon.barcontainer
    node_type = 'barcontainer'
    description = ('A Bar Container for horizontal grouping or vertical '
                   'stacking of multiple Bar Plots.')

    cls_tags = frozenset({NodeTags.is_container,
                          NodeTags.deletable,
                          NodeTags.rearrangable,
                          NodeTags.copyable})

    default_data = OrderedDict([
        ('plots', []),
    ])

    PLOT_TYPES = {
        'bar': BarPlot,
        'iterator': Iterator,
    }

    NODE_LEAFS = OrderedDict([
        ('bin_labels', {'label': 'Bin Labels',
                        'eval': six.text_type,
                        'icon': SvgIcon.label,
                        'default': '',
                        'options': None,
                        'description': 'Specify data used as "Labels" plotted '
                                       'on the x-axis, either as column '
                                       'name or as python expression which '
                                       'evaluates to a numpy ndarray',
                        'editor': tree_widgets.SyDataEdit}),
        ('grouping', {'label': 'Grouping',
                      'eval': six.text_type,
                      'icon': SvgIcon.bar_grouping,
                      'default': 'grouped',
                      'options': ['grouped', 'stacked'],
                      'description': 'Specify if Bars should be borizontally '
                                     'grouped or vertically stacked.',
                      'editor': tree_widgets.SyComboBox}),
        ('rwidth', {'label': 'R width',
                    'eval': float,
                    'icon': SvgIcon.barwidth,
                    'default': 1.,
                    'options': (0., 1., 0.05),
                    'description': 'Specify the total width used for one '
                                   '"bin".',
                    'editor': tree_widgets.SyDoubleSpinBox}),
        ('color', SY_COLOR_PARAMS),
        ('edgecolor', SY_EDGECOLOR_PARAMS),
        ('linewidth', SY_LINEWIDTH_PARAMS),
        ('linestyle', SY_LINESTYLE_PARAMS),
        ('alpha', SY_ALPHA_PARAMS),
        ('zorder', SY_ZORDER_PARAMS),
    ])

    REQUIRED_LEAFS = {'grouping'}

    @classmethod
    def valid_children(cls):
        return frozenset(
            set(cls.PLOT_TYPES.values()) | {FigureProperty, BarLabelsFont})

    def init(self, data):
        self.add_plots(data)
        self.add_other_nodes(data)

    def add_plots(self, data):
        for plot_data in data.pop('plots', []):
            plot_type = plot_data.get('type')
            if plot_type is not None:
                plot_cls = self.PLOT_TYPES.get(plot_type)
                plot = plot_cls(plot_data, parent=self)
                self.children.append(plot)

    def add_other_nodes(self, data):
        valid_child_nodes = [c for c in self.valid_children()
                             if not c.is_leaf and
                             not issubclass(c, (BasePlot, BasePlotContainer))]
        self.add_children_to_node(data, valid_child_nodes)

    def export_config(self, prefix=None):
        if prefix is None:
            prefix = []
        else:
            prefix = list(prefix)
        config = []
        node_id = self.root_node().get_id(self)
        this_prefix = [self.node_type, node_id]

        if isinstance(self.parent.parent, Axes):
            prop_s = '.'.join(this_prefix + ['axes'])
            config.append((prop_s, prefix[-1]))

        for child in self.children:
            config.extend(child.export_config(prefix=this_prefix))
        return config


class HistogramContainer(BarContainer):
    icon = SvgIcon.histcontainer
    node_type = 'histcontainer'
    description = ('A Histogram Container to stack multiple '
                   'Histogram Plots vertically.')

    PLOT_TYPES = {
        'hist': HistogramPlot,
        'iterator': Iterator,
    }

    NODE_LEAFS = OrderedDict([
        ('bin_min_edges', {'label': 'Bin min edges',
                           'eval': six.text_type,
                           'icon': SvgIcon.bin_min_edge,
                           'default': '',
                           'options': None,
                           'description': 'Specify the column used as '
                                          '"Bin min edges", either as column '
                                          'name or as python expression which '
                                          'evaluates to a numpy ndarray',
                           'editor': tree_widgets.SyDataEdit}),
        ('bin_max_edges', {'label': 'Bin max edges',
                           'eval': six.text_type,
                           'icon': SvgIcon.bin_max_edge,
                           'default': '',
                           'options': None,
                           'description': 'Specify the column used as '
                                          '"Bin max edges", either as column '
                                          'name or as python expression which '
                                          'evaluates to a numpy ndarray',
                           'editor': tree_widgets.SyDataEdit}),
        ('color', SY_COLOR_PARAMS),
        ('edgecolor', SY_EDGECOLOR_PARAMS),
        ('linewidth', SY_LINEWIDTH_PARAMS),
        ('linestyle', SY_LINESTYLE_PARAMS),
        ('alpha', SY_ALPHA_PARAMS),
        ('zorder', SY_ZORDER_PARAMS),
        ('histtype', {'label': 'Histogram Type',
                      'eval': 'options',
                      'icon': SvgIcon.histtype,
                      'default': 'bar',
                      'options': mpl_utils.HISTTYPES,
                      'description': ('Specify if Histograms should be drawn '
                                      'as Bars or filled Steps.'),
                      'editor': tree_widgets.SyComboBox}),
    ])

    REQUIRED_LEAFS = {}

    @classmethod
    def valid_children(cls):
        return frozenset(
            set(cls.PLOT_TYPES.values()) | {FigureProperty, BarLabelsFont})


class Plots(BasePlotContainer):
    node_type = 'plots'
    needs_id = False
    description = 'A container collecting all different Plots for one Axes.'

    cls_tags = frozenset({NodeTags.is_container, NodeTags.unique})

    PLOT_TYPES = {
        'scatter': ScatterPlot,
        'line': LinePlot,
        'bar': BarPlot,
        'hist': HistogramPlot,
        'heatmap': HeatmapPlot,
        'barcontainer': BarContainer,
        'histcontainer': HistogramContainer,
        'iterator': Iterator
    }

    @classmethod
    def valid_children(cls):
        return frozenset(set(cls.PLOT_TYPES.values()) | {FigureProperty})

    def init(self, data):
        self.add_plots(data)

    def export_config(self, prefix=None):
        if prefix is None:
            prefix = []
        else:
            prefix = list(prefix)
        config = []
        for child in self.children:
            if isinstance(child, (BasePlot, BarContainer, Iterator)):
                config.extend(child.export_config(prefix=prefix))
        return config


class Legend(FigureBaseNode):
    icon = SvgIcon.legend
    node_type = 'legend'
    description = ('The Axes Legend. If defined outside of an Axes, all '
                   'Legends defined in different Axes will be joined into one '
                   'common Legend.')

    cls_tags = frozenset({NodeTags.unique,
                          NodeTags.deletable,
                          NodeTags.rearrangable})

    default_data = OrderedDict([
        ('show', 'True'),
    ])

    NODE_LEAFS = OrderedDict([
        ('show', {'label': 'Visible',
                  'eval': 'options',
                  'icon': lambda v: create_icon(SvgIcon.visible if v == 'True'
                                                else SvgIcon.invisible),
                  'default': 'True',
                  'options': ['True', 'False'],
                  'description': 'En/Disable if the Legend should be shown.',
                  'editor': tree_widgets.SyComboBox}),
        ('loc', {'label': 'Location',
                 'eval': 'options',
                 'icon': SvgIcon.location,
                 'default': 'upper right',
                 'options': list(mpl_utils.LEGEND_LOC.keys()),
                 'description': ('Specify the location of the Legend within '
                                 'the Axes.'),
                 'editor': tree_widgets.SyComboBox}),
        ('ncol', {'label': 'Number of columns',
                  'eval': int,
                  'icon': SvgIcon.number_columns,
                  'default': 1,
                  'options': (1, None, 1),
                  'description': ('Specify the number of columns used ot list '
                                  'the artist labels.'),
                  'editor': tree_widgets.SySpinBox}),
        ('fontsize', {'label': 'Font Size',
                      'eval': 'options',
                      'icon': SvgIcon.text_size,
                      'default': 'medium',
                      'options': mpl_utils.FONTSIZE,
                      'description': 'Specify the fontsize of the labels',
                      'editor': tree_widgets.SyComboBox}),
        ('frameon', {'label': 'Frame',
                     'eval': 'options',
                     'icon': SvgIcon.frame,
                     'default': 'True',
                     'options': ['True', 'False'],
                     'description': ('En/Disable the frame drawn around '
                                     'the Legned'),
                     'editor': tree_widgets.SyComboBox}),
        ('title', {'label': 'Title',
                   'eval': six.text_type,
                   'icon': SvgIcon.label,
                   'default': '',
                   'options': None,
                   'description': 'Specify the title of the Legend.',
                   'editor': tree_widgets.SyLabelEdit}),

    ])

    @classmethod
    def valid_children(cls):
        return frozenset({FigureProperty})

    def export_config(self, prefix=None):
        if prefix is None:
            prefix = []
        else:
            prefix = list(prefix)
        prefix += [self.node_type]
        config = []
        for child in self.children:
            config.extend(child.export_config(prefix=prefix))
        return config


class Grid(FigureBaseNode):
    icon = SvgIcon.grid
    node_type = 'grid'
    description = ('A Grid defines the properties of a the grid lines plotted '
                   'for an Axes.')

    cls_tags = frozenset({NodeTags.unique,
                          NodeTags.deletable,
                          NodeTags.rearrangable})

    default_data = OrderedDict([
        ('show', 'True'),
    ])

    NODE_LEAFS = OrderedDict([
        ('show', {'label': 'Visible',
                  'eval': 'options',
                  'icon': lambda v: create_icon(SvgIcon.visible if v == 'True'
                                                else SvgIcon.invisible),
                  'default': 'True',
                  'options': ['True', 'False'],
                  'description': 'En/Disable if the Grid should be shown.',
                  'editor': tree_widgets.SyComboBox}),
        ('color', SY_COLOR_PARAMS),
        ('linestyle', SY_LINESTYLE_PARAMS),
        ('linewidth', SY_LINEWIDTH_PARAMS),
        ('which', {'label': 'Which',
                   'eval': six.text_type,
                   'icon': SvgIcon.ticks,
                   'default': 'major',
                   'options': ['major', 'minor', 'both'],
                   'description': ('Specify for which ticks the grid lines '
                                   'should be drawn.'),
                   'editor': tree_widgets.SyComboBox}),
        ('axis', {'label': 'Axis',
                  'eval': six.text_type,
                  'icon': SvgIcon.plot,
                  'default': 'both',
                  'options': ['x', 'y', 'both'],
                  'description': ('Specify for which axis (x, y, or both) the '
                                  'grid lines should be drawn.'),
                  'editor': tree_widgets.SyComboBox}),
    ])

    @classmethod
    def valid_children(cls):
        return frozenset({FigureProperty})

    def export_config(self, prefix=None):
        if prefix is None:
            prefix = []
        else:
            prefix = list(prefix)
        prefix += [self.node_type]
        config = []
        for child in self.children:
            config.extend(child.export_config(prefix=prefix))
        return config


class BaseAxis(FigureBaseNode):
    """Definition of an axes dimension."""

    node_type = 'axis'
    description = ('An Axis defines the position, label and limit of an '
                   'x or y Axis.')

    valid_children = frozenset({FigureProperty})
    cls_tags = frozenset({NodeTags.unique})

    NODE_LEAFS = OrderedDict([
        ('position', {'label': 'Axis',
                      'eval': 'axesposition',
                      'icon': None,
                      'default': 'bottom',
                      'options': None,
                      'description': 'Specify the position of this Axis.',
                      'editor': tree_widgets.SyComboBox}),
        ('label', SY_LABEL_PARAMS),
        ('lim', {'label': 'Limit',
                 'eval': six.text_type,
                 'icon': SvgIcon.limit,
                 'default': (None, None),
                 'options': None,
                 'description': ('Specify the lower and upper limits of '
                                 'this Axis.'),
                 'editor': tree_widgets.SyDataEdit}),
        ('scale', {'label': 'Scale',
                   'eval': six.text_type,
                   'icon': SvgIcon.scales,
                   'default': 'linear',
                   'options': ('linear', 'log'),
                   'description': ('Specify the scale (log or linear) of '
                                   'this Axis.'),
                   'editor': tree_widgets.SyComboBox}),
    ])

    REQUIRED_LEAFS = {'position'}

    @classmethod
    def valid_children(cls):
        return frozenset({FigureProperty})

    def export_config(self, prefix=None):
        if prefix is None:
            prefix = []
        else:
            prefix = list(prefix)
        config = []
        export_prop_mapping = {
            v: k for k, v in six.iteritems(self.parent.STORED_LEAFS)}
        for child in self.children:
            # map the models Axis Property structure to the stored structure
            prop_s, value = child.export_config(prefix=[self.node_type])[0]
            new_prop_s = '.'.join(prefix + [export_prop_mapping[prop_s]])
            config.append((new_prop_s, value))
        return config


class XAxis(BaseAxis):
    """Definiton of an x axis."""

    icon = SvgIcon.x_axis
    node_type = 'xaxis'

    NODE_LEAFS = OrderedDict([
        ('position', {'label': 'Position',
                      'eval': 'axesposition',
                      'icon': lambda v: create_icon(
                          {'bottom': SvgIcon.x_axis_pos_bottom,
                           'top': SvgIcon.x_axis_pos_top}[v]),
                      'default': 'bottom',
                      'options': ['bottom', 'top'],
                      'description': 'Specify the position of this Axis.',
                      'editor': tree_widgets.SyComboBox}),
        ('label', SY_LABEL_PARAMS),
        ('lim', {'label': 'Limit',
                 'eval': six.text_type,
                 'icon': SvgIcon.limit,
                 'default': (None, None),
                 'options': None,
                 'description': ('Specify the lower and upper limits of '
                                 'this Axis.'),
                 'editor': tree_widgets.SyDataEdit}),
        ('scale', {'label': 'Scale',
                   'eval': six.text_type,
                   'icon': SvgIcon.scales,
                   'default': 'linear',
                   'options': ('linear', 'log'),
                   'description': ('Specify the scale (log or linear) of '
                                   'this Axis.'),
                   'editor': tree_widgets.SyComboBox}),
    ])


class YAxis(BaseAxis):
    """Definiton of an x axis."""

    icon = SvgIcon.y_axis
    node_type = 'yaxis'

    NODE_LEAFS = OrderedDict([
        ('position', {'label': 'Position',
                      'eval': 'axesposition',
                      'icon': lambda v: create_icon(
                          {'left': SvgIcon.y_axis_pos_left,
                           'right': SvgIcon.y_axis_pos_right}[v]),
                      'default': 'left',
                      'options': ['left', 'right'],
                      'description': 'Specify the position of this Axis.',
                      'editor': tree_widgets.SyComboBox}),
        ('label', SY_LABEL_PARAMS),
        ('lim', {'label': 'Limit',
                 'eval': six.text_type,
                 'icon': SvgIcon.limit,
                 'default': (None, None),
                 'options': None,
                 'description': ('Specify the lower and upper limits of '
                                 'this Axis.'),
                 'editor': tree_widgets.SyDataEdit}),
        ('scale', {'label': 'Scale',
                   'eval': six.text_type,
                   'icon': SvgIcon.scales,
                   'default': 'linear',
                   'options': ('linear', 'log'),
                   'description': ('Specify the scale (log or linear) of '
                                   'this Axis.'),
                   'editor': tree_widgets.SyComboBox}),
    ])
