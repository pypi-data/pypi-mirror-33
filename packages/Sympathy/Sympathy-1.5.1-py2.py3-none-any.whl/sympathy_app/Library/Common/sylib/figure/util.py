# Copyright (c) 2016, System Engineering Software Society
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

import copy
import itertools
from collections import defaultdict, OrderedDict, Iterable
from datetime import datetime

import numpy as np
import six
import matplotlib
from matplotlib import collections as mpl_collections
from matplotlib import container as mpl_container
from matplotlib import dates as mpl_dates
from matplotlib import gridspec
from matplotlib import image as mpl_image
from matplotlib import lines as mpl_lines
from matplotlib import patches as mpl_patches
from matplotlib.text import Text
from matplotlib.ticker import FixedLocator
from matplotlib.transforms import IdentityTransform

from sylib.figure import colors, models, mpl_utils, common
from sympathy.platform.exceptions import sywarn, SyConfigurationError
from sympathy.typeutils import figure
from sympathy.typeutils.figure import SyAxes


def gen_config_by_prefix(config, prefix):
    """
    Return a generator returning (key, value) where the key
    starts with the given prefix + '.'.
    """
    prefix += '.'
    return ((k.lower(), v) for k, v in config
            if k.lower().startswith(prefix.lower()))


def fill_in_global_parameters(global_params, local_params):
    """
    Update the local parameters with existing global parameters
    without overriding existing ones.
    """
    for key, value in six.iteritems(global_params):
        for local in local_params.values():
            if key not in local:
                local[key] = value


def add_layer_to_axes(config, layer_cls, axes, default_axes_id,
                      container_dict):
    """
    Parse the parameters of a plot type (line/scatter/bar etc.).

    The parsed configurations get added to the appropriate axes.

    Parameters
    ----------
    config : list of tuples
        A list of (parameter, value) pairs, where each parameter is defined as
        <layer_type>.<type_id>.<type_parameter>.
    layer_cls : class
        The model class of the given layer type, either
        `models.BasePlot` or `models.BasePlotContainer`.
    axes : dict
        A dictionary with all parsed axes.
    default_axes_id : str
        The axes_id in `axes` of the default 'x1,y1' axis.
    container_dict : OrderedDict
    """
    # global_layer_params = {}
    layers = OrderedDict()

    item_leafs = layer_cls.NODE_LEAFS

    for key, value in config:
        key_splitted = key.lower().split('.')
        sub_param = []
        num_keys = len(key_splitted)

        if num_keys == 3 and key_splitted[1] not in item_leafs.keys():
            identifier, param = key_splitted[1:]
        elif num_keys == 3 and key_splitted[1] in item_leafs.keys():
            identifier = None
            param = key_splitted[1]
            sub_param = key_splitted[2:]
        elif num_keys == 2:
            identifier, param = None, key_splitted[1]
        else:
            identifier = key_splitted[1]
            param = key_splitted[2]
            sub_param = key_splitted[3:]

        if identifier is not None:
            if identifier not in layers:
                layers[identifier] = copy.deepcopy(layer_cls.default_data)
                layers[identifier]['type'] = layer_cls.node_type
            working_d = layers[identifier]
        else:
            continue
            # currently disabled, since not used
            # working_d = global_layer_params

        if models.NodeTags.is_container in layer_cls.cls_tags:
            container_dict[identifier] = working_d
        child_nodes = {c.node_type: c for c in layer_cls.valid_children() if
                       not c.is_leaf}
        if param in child_nodes:
            param_cls = child_nodes[param]
            sub_props = param_cls.NODE_LEAFS

            if param not in working_d:
                if param_cls.default_data is not None:
                    working_d[param] = copy.deepcopy(param_cls.default_data)
                else:
                    working_d[param] = OrderedDict()
            if len(sub_param) == 1 and sub_param[0] in sub_props:
                prop = sub_param[0]
                if prop is not None and value is not None:
                    working_d[param][prop] = value
        else:
            if param == 'axes' and identifier is not None:
                if value == '_default_':
                    value = default_axes_id
                working_d['axes'] = value
            elif param == 'container' and identifier is not None:
                working_d['container'] = value
            elif param not in item_leafs:
                continue
            else:
                working_d[param] = value

    # add the layers to the appropriate axes
    for id_, layer in six.iteritems(layers):
        container_id = layer.pop('container', None)
        # if axes_id does not exist, take default one
        if container_id is None or container_id not in container_dict:
            axes_id = layer.pop('axes', default_axes_id)
            if axes_id not in axes:
                axes_id = default_axes_id
            axes[axes_id]['plots'].append(layer)
        else:
            # remove link to axes from plot, its already given by the container
            axes_id = layer.pop('axes', None)
            container_dict[container_id]['plots'].append(layer)
    return axes


def parse_config_axes(config):
    """Parse the axes parameters."""
    # global_axes = {}
    axes = OrderedDict()

    item_properties = models.Axes.STORED_LEAFS

    for key, value in config:
        key_splitted = key.lower().split('.')
        sub_param = []
        num_keys = len(key_splitted)

        if num_keys == 3 and key_splitted[1] not in item_properties.keys():
            identifier, param = key_splitted[1:]
        elif num_keys == 3 and key_splitted[1] in item_properties.keys():
            identifier = None
            param = key_splitted[1]
            sub_param = key_splitted[2:]
        elif num_keys == 2:
            identifier, param = None, key_splitted[1]
        else:
            identifier = key_splitted[1]
            param = key_splitted[2]
            sub_param = key_splitted[3:]

        # special case handling to convert old style axis positions
        if param == 'xaxis':
            param = 'xaxis_position'
            if value in common.REPLACE_AXIS_TYPE:
                value = common.REPLACE_AXIS_TYPE[value]
        if param == 'yaxis':
            param = 'yaxis_position'
            if value in common.REPLACE_AXIS_TYPE:
                value = common.REPLACE_AXIS_TYPE[value]

        # set default data for identifier and
        # assign dict to add parameters to as 'working_d'
        if identifier is not None:
            if identifier not in axes:
                axes[identifier] = copy.deepcopy(models.Axes.default_data)
            working_d = axes[identifier]
        else:
            continue
            # currently not used
            # working_d = global_axes

        mapping = item_properties.get(param, None)
        if mapping is None:
            continue

        child_nodes = {c.node_type: c for c in models.Axes.valid_children() if
                       not issubclass(c, models.FigureProperty)}
        if param in child_nodes:
            sub_cls = child_nodes[param]
            sub_props = sub_cls.NODE_LEAFS

            if param not in working_d:
                if sub_cls.default_data is not None:
                    working_d[param] = copy.deepcopy(sub_cls.default_data)
                else:
                    working_d[param] = OrderedDict()
            if len(sub_param) == 1 and sub_param[0] in sub_props:
                prop = sub_param[0]
                if prop is not None and value is not None:
                    working_d[param][prop] = value
        else:
            # parsed_value = common.parse_type(value, t, o)
            # a[param] = value  # parsed_value

            subdirs = mapping.split('.')
            for subdir in subdirs[:-1]:
                if subdir not in working_d:
                    working_d[subdir] = OrderedDict()
                working_d = working_d[subdir]
            working_d[subdirs[-1]] = value  # parsed_value

    # get all defined x and y axes
    # defined_yaxis = set(
    #     [a['yaxis'] for a in axes.values() if 'yaxis' in a])

    # get required parameters
    # required_parameters = [k for k, v in six.iteritems(AXES) if
    #                        not isinstance(v, dict) and v[3]]

    # TODO(Bene): update line parameters from global parameters if missing and
    # defined in global line parameter
    # for axis_id, params in six.iteritems(axes):
    #     for required_param in required_parameters:
    #         if required_param in params.keys():
    #             continue
    #         if required_param in global_axes.keys():
    #             value = global_axes[required_param]
    #         else:
    #             value = AXES[required_param][1]
    #             if required_param == 'yaxis':
    #                 if value in defined_yaxis:
    #                     value = 'right'
    #         axes[axis_id][required_param] = value
    # fill_in_global_parameters(global_axes, axes)
    return axes


def parse_config_figure(config):
    """Parse the figure parameters."""
    figure = OrderedDict()

    item_leafs = models.Figure.NODE_LEAFS

    for key, value in config:
        key_splitted = key.lower().split('.')
        num_keys = len(key_splitted)

        if num_keys == 2 and key_splitted[1] in item_leafs:
            param = key_splitted[1]
            type_ = item_leafs[param]['eval']
            options = item_leafs[param]['options']
            parsed_value = common.parse_type(value, type_, options)
            figure[param] = parsed_value
        elif num_keys == 3 and key_splitted[1] in [models.Legend.node_type]:
            param = key_splitted[1]
            sub_param = key_splitted[2]
            if param not in figure:
                figure[param] = OrderedDict()
            figure[param][sub_param] = value
    # TODO: reordering of items
    return figure


def get_default_axes_id(axes):
    """Get the default axes_id."""
    for axes_id, ax in six.iteritems(axes):
        if (ax['xaxis']['position'] == 'bottom' and
                ax['yaxis']['position'] == 'left'):
            return axes_id
    return None


def parse_configuration(config):
    """
    Parse a configuration table with a parameter and value column.
    """
    figure = parse_config_figure(gen_config_by_prefix(config, 'figure'))
    axes = parse_config_axes(gen_config_by_prefix(config, 'axes'))

    # get a default axes_id to use
    # if layer parameters define axes as "_default_"
    default_axes_id = get_default_axes_id(axes)

    # handle containers first, so plots can be added appropriately
    valid_layer_types = OrderedDict(
        [(i.node_type, i) for i in [
            models.BarContainer,
            models.HistogramContainer,
            models.Iterator,
            models.LinePlot,
            models.ScatterPlot,
            models.BarPlot,
            models.HistogramPlot,
            models.HeatmapPlot,
        ]])

    container_dict = OrderedDict()
    for layer_type, layer_cls in six.iteritems(valid_layer_types):
        layer_cfg = gen_config_by_prefix(config, layer_type)
        axes = add_layer_to_axes(
            layer_cfg, layer_cls, axes, default_axes_id, container_dict)

    figure['axes'] = list(axes.values())  # remove the axes ids
    return OrderedDict([('figure', figure)])


def export_config(model):
    """
    Export the models node and properties to list of (parameter, value) pairs.

    Parameters
    ----------
    model : models.DataModel

    Returns
    -------
    list
        A list of (parameter, value) tuples.
    """
    return model.root.export_config()


def reconstruct_twin_axes(start_axes, axes):
    """Reconstruct the relationship between overlaying twin axes."""
    sibling_axes = {start_axes: (1, 1)}
    shared_ax = {ax: (ax._sharex, ax._sharey) for ax in axes}

    for ax in axes:
        if ax in sibling_axes.keys():
            continue
        has_shared = shared_ax.get(ax)
        if has_shared is not None and has_shared != (None, None):
            sharex, sharey = has_shared
            if sharex is not None and sharey is None:
                x_parent_pos = sibling_axes.get(sharex)
                pos = x_parent_pos[0], x_parent_pos[1] + 1
            elif sharex is None and sharey is not None:
                y_parent_pos = sibling_axes.get(sharey)
                pos = y_parent_pos[0] + 1, y_parent_pos[1]
            else:
                raise ValueError('Unknown axes configuration')
            sibling_axes[ax] = pos
    return sibling_axes


def get_twin_axes(axes_dict, xaxis, yaxis):
    """
    Return the twin axes given by `xaxis`, `yaxis`.

    Parameters
    ----------
    axes_dict : dict
        A dictionary containing at least the default axes
        with xaxis='bottom' and yaxis='left'.
    xaxis : unicode
        The name of the xaxis. Supported values are 'bottom' and 'top'.
    yaxis : unicode
        The name of the yaxis. Supported values are 'left' and 'right'.

    Returns
    -------
    ax : matplotlib.axes._subplots.AxesSubplot
    """
    ax = axes_dict.get((xaxis, yaxis), None)
    default_axes = axes_dict[('bottom', 'left')]
    if isinstance(default_axes, figure.SyAxes):
        default_axes = default_axes.get_mpl_axes()
    if ax is None:
        if xaxis == 'bottom' and yaxis == 'right':
            ax = default_axes.twinx()
        elif xaxis == 'top' and yaxis == 'left':
            ax = default_axes.twiny()
        elif xaxis == 'top' and yaxis == 'right':
            x1y2axes = get_twin_axes(axes_dict, 'bottom', 'right')
            ax = x1y2axes.twiny()
        else:
            raise ValueError('The axes type "{}, {}" is not '
                             'supported.'.format(xaxis, yaxis))
        axes_dict[(xaxis, yaxis)] = ax
    return ax


def classify_axes(axes):
    """
    Classify the axes in the scheme ('bottom', 'left').

    The axes get stored with a (x,y) key in a dictionary
    depending on their shared x or y axes. The first axes
    will always be set as ('bottom', 'left').
    """
    if len(axes):
        classed_axes = reconstruct_twin_axes(axes[0], axes)
        xaxis_options = ['bottom', 'top']
        yaxis_options = ['left', 'right']
        return {(xaxis_options[v[0]-1], yaxis_options[v[1]-1]): k
                for k, v in six.iteritems(classed_axes)}
    return {}


def get_sorted_axes(axes_dict):
    """Sort axes dictionary."""
    order = [('bottom', 'left'),
             ('bottom', 'right'),
             ('top', 'left'),
             ('top', 'right')]
    return OrderedDict([(ax_id, axes_dict.get(ax_id))
                        for ax_id in order
                        if axes_dict.get(ax_id) is not None])


def _get_mpl_axes(source, target):
    if isinstance(target, figure.SyAxes):
        target = target.get_mpl_axes()
    if isinstance(source, figure.SyAxes):
        source = source.get_mpl_axes()
    return source, target


def _get_colorbar_axes(axes):
    """
    Helper function which returns all axes of colorbars linked to artists.

    Parameters
    ----------
    axes : list
        A list of matplotlib Axes.

    Returns
    -------
    cb_axes : set
    """
    cb_axes = []
    for ax in axes:
        for artist_type in ['images', 'collections']:
            for artist in getattr(ax, artist_type):
                if artist.colorbar is not None:
                    cb_axes.append(artist.colorbar.ax)
    return cb_axes


def _move_lines_to(source, target, existing_colors, auto_recolor=True):
    """
    Move a line artist from a source to a target axes.

    Remove the line artist from the source mpl.axes and
    add it to the target axes.
    """
    source, target = _get_mpl_axes(source, target)
    for i, line in enumerate(source.lines):
        # create new Line2D object
        x, y = line.get_data()
        new_line = mpl_lines.Line2D(x, y)
        new_line.update_from(line)
        # extend the label if same already exists
        label = line.get_label()
        used_labels = [l.get_label() for l in target.lines]
        if label in used_labels:
            i = 2
            while '{}_{}'.format(label, i) in used_labels:
                i += 1
            new_line.set_label('{}_{}'.format(label, i))
        # this is a bit of a hack to remove axes specific properties
        new_line.set_transform(IdentityTransform())
        new_line._transformed_path = None
        new_line._transformSet = False
        new_line._xy = None
        new_line._x = None
        new_line._y = None

        # auto assign new color from mpl color_cycle
        if auto_recolor:
            count_cols, unique_cols, unused_cols = _get_unique_n_unused_colors(
                existing_colors)
            current_color = colors.color2hex(new_line.get_color())
            if current_color in unique_cols:
                # assign a new color
                if len(unused_cols):
                    new_color = unused_cols[0]
                else:
                    least_occuring_color = unique_cols[
                        np.argsort(count_cols)[0]]
                    if len(least_occuring_color):
                        new_color = least_occuring_color
                    else:
                        new_color = mpl_utils.color_cycle[0]()
            else:
                new_color = current_color
            new_line.set_color(new_color)
        target.add_line(new_line)
        existing_colors.append(new_line.get_color())


def _move_images_to(source, target):
    """
    Move image artists from a source to a target axes.

    Parameters
    ----------
    source : SyAxes or matplotlib.axes.Axes
        The source axes from which artists are copied.
    target : SyAxes or matplotlib.axes.Axes
        The target axes into which artists are pasted.

    Returns
    -------
    cbs : list
        A list of tuples (artist, colorbar properties dict).
    """
    source, target = _get_mpl_axes(source, target)
    cbs = []
    for i, image in enumerate(source.images):
        target.set_aspect(source.get_aspect())

        im = mpl_image.AxesImage(target,
                                 image.get_cmap(),
                                 image.norm,
                                 image.get_interpolation(),
                                 image.origin,
                                 image.get_extent(),
                                 filternorm=image.get_filternorm(),
                                 filterrad=image.get_filterrad(),
                                 resample=image.get_resample())
        im.set_data(image.get_array())
        im.set_alpha(image.get_alpha())

        if im.get_clip_path() is None:
            im.set_clip_path(target.patch)
        vmin, vmax = image.get_clim()
        if vmin is not None or vmax is not None:
            im.set_clim(vmin, vmax)
        else:
            im.autoscale_None()
        im.set_url(image.get_url())

        extent = im.get_extent()
        im.set_extent(extent)
        target.add_image(im)
        colorbar_params = _get_colorbar_properties(image)
        cbs.append((im, colorbar_params))
    return cbs


def _move_collections_to(source, target, existing_colors, auto_recolor=True):
    """
    Move collection artists from a source to a target axes.

    Currently PathCollections and PolyCollections are supported.

    Parameters
    ----------
    source : SyAxes or matplotlib.axes.Axes
        The source axes from which artists are copied.
    target : SyAxes or matplotlib.axes.Axes
        The target axes into which artists are pasted.
    existing_colors : list
        A list of colors used by artists of the target axes. New used colors
        get appended to the list to be available to other '_move__to' helper
        functions.
    auto_recolor : bool, optional
        Set True if artists should be automatically recolored.

    Returns
    -------
    cbs : list
        A list of tuples (artist, colorbar properties dict).
    """
    source, target = _get_mpl_axes(source, target)
    cbs = []
    for i, collection in enumerate(source.collections):
        if isinstance(collection, mpl_collections.PathCollection):
            new_collection, kwargs = _move_path_collection(collection, target)
        elif isinstance(collection, mpl_collections.PolyCollection):
            new_collection, kwargs = _move_poly_collection(collection, target)
        else:
            new_collection, kwargs = None, {}

        if new_collection is not None:
            # auto assign new color from mpl color_cycle
            if auto_recolor:
                _set_unique_collection_color(new_collection, existing_colors)
            target.add_collection(new_collection, **kwargs)
            colorbar_params = _get_colorbar_properties(collection)
            cbs.append((new_collection, colorbar_params))
            target.autoscale_view()
    return cbs


def _move_poly_collection(collection, target):
    """Move a single PolyCollection to target axes."""

    verts = [p.vertices for p in collection.get_paths()]
    # TODO: remove if else when matplotlib version > 1.4.0
    if hasattr(collection, 'get_sizes'):
        sizes = collection.get_sizes()
    else:
        sizes = collection._sizes

    new_collection = mpl_collections.PolyCollection(verts, sizes)
    new_collection.update_from(collection)
    new_collection._transformSet = False

    label = collection.get_label()
    used_labels = [l.get_label() for l in target.collections]
    if label in used_labels:
        i = 2
        while '{}_{}'.format(label, i) in used_labels:
            i += 1
        new_collection.set_label('{}_{}'.format(label, i))

    # now update the datalim and autoscale
    for path in collection.get_paths():
        target.dataLim.update_from_path(
            path, ignore=target.ignore_existing_data_limits,
            updatex=True, updatey=True)

    return new_collection, {'autolim': False}


def _move_path_collection(collection, target):
    """Move a single PathCollection to target axes."""
    x, y = collection.get_offsets().T
    # create a new Collection object
    new_collection = mpl_collections.PathCollection(
        collection.get_paths(),
        collection.get_sizes(),
        offsets=collection.get_offsets(),
        transOffset=target.transData,
        alpha=collection.get_alpha())
    # extend the label if same already exists
    label = collection.get_label()
    used_labels = [l.get_label() for l in target.collections]
    if label in used_labels:
        i = 2
        while '{}_{}'.format(label, i) in used_labels:
            i += 1
        new_collection.set_label('{}_{}'.format(label, i))
    new_collection.update_from(collection)
    new_collection.set_cmap(collection.get_cmap())
    if target._xmargin < 0.05 and x.size > 0:
        target.set_xmargin(0.05)
    if target._ymargin < 0.05 and y.size > 0:
        target.set_ymargin(0.05)
    return new_collection, {}


def _set_unique_collection_color(collection, existing_colors):
    count_cols, unique_cols, unused_cols = _get_unique_n_unused_colors(
        existing_colors)
    current_color = colors.color2hex(collection.get_facecolor()[0])
    if current_color in unique_cols:
        # assign a new color
        if len(unused_cols):
            new_color = unused_cols[0]
        else:
            least_occuring_color = unique_cols[
                np.argsort(count_cols)[0]]
            if len(least_occuring_color):
                new_color = least_occuring_color
            else:
                new_color = mpl_utils.color_cycle[0]()
    else:
        new_color = current_color
    if isinstance(collection, mpl_collections.PolyCollection):
        collection.set_facecolor(new_color)
    else:
        collection.set_color(new_color)
    existing_colors.append(new_color)


def _move_containers_to(source, target):
    """
    Move a bar containers artist from a source to a target axes.
    """
    source, target = _get_mpl_axes(source, target)
    for container in source.containers:
        # currently only BarContainers are supported
        if not isinstance(container, mpl_container.BarContainer):
            continue

        patches = []
        for patch in container.patches:
            r = mpl_patches.Rectangle(
                xy=patch.get_xy(),
                width=patch.get_width(),
                height=patch.get_height(),
                facecolor=patch.get_facecolor(),
                edgecolor=patch.get_edgecolor(),
                linewidth=patch.get_linewidth(),
                linestyle=patch.get_linestyle(),
                fill=patch.get_fill(),
                hatch=patch.get_hatch(),
                alpha=patch.get_alpha())
            target.add_patch(r)
            patches.append(r)

        label = container.get_label()
        used_labels = [l.get_label() for l in target.containers]
        if label in used_labels:
            i = 2
            while '{}_{}'.format(label, i) in used_labels:
                i += 1
            new_label = '{}_{}'.format(label, i)
        else:
            new_label = label

        bar_container = mpl_container.BarContainer(patches, None,
                                                   label=new_label)
        target.add_container(bar_container)

    # Label the bins on the x axis.
    if isinstance(source.xaxis.get_major_locator(), FixedLocator):
        labels = source.get_xticklabels()
        target.set_xticks(range(len(labels)))
        target.set_xticklabels([l.get_text() for l in labels])


def _move_text_to(source, target):
    """
    Move text artist from a soruce to a target axes.
    """
    source, target = _get_mpl_axes(source, target)
    for text in source.texts:
        # get the text properties
        x, y = text.get_unitless_position()
        t = text.get_text()
        c = text.get_color()
        va = text.get_verticalalignment()
        ha = text.get_horizontalalignment()
        rot = text.get_rotation()
        rot_mode = text.get_rotation_mode()

        new_text = target.text(x, y, t, color=c, va=va, ha=ha)
        # copy font properties
        new_text.set_fontproperties(text.get_font_properties())
        # apply rotation
        new_text.set_rotation_mode(rot_mode)
        new_text.set_rotation(rot)


def _get_unique_n_unused_colors(existing_colors):
    unique_colors = np.unique(existing_colors)
    # workaround for numpy version < 1.9
    # we could use return_count in np.unique in the future
    color_count = [(np.array(existing_colors) == item).sum()
                   for item in unique_colors]
    unique_colors = list(unique_colors)  # otherwise FutureWarning
    hex_color_cycle = [colors.color2hex(c) for c in mpl_utils.color_cycle()]
    unused_colors = [c for c in hex_color_cycle if
                     c not in unique_colors]
    return color_count, unique_colors, unused_colors


parameter_list_to_copy = [
    # 'title',  # doesn't work for whichever reason
    'xscale',
    'yscale',
    'xlabel',
    'ylabel',
    'xlim',
    'ylim',
    'aspect',
]


def copy_axes_parameter(source, target):
    """
    Copy axes parameters from a source to a target axes.

    Copy the parameters defined in the ``parameter_list_to_copy``
    from the ``source`` mpl axes to the ``target`` mpl axes.
    """
    source, target = _get_mpl_axes(source, target)
    for attr in parameter_list_to_copy:
        # special case handling for FixedLocator on xaxis
        # required to keep Fixed Bar Plot lables
        if (attr == 'xscale' and
                isinstance(source.xaxis.get_major_locator(), FixedLocator)):
            continue
        value = getattr(source, 'get_{}'.format(attr))()
        setter = getattr(target, 'set_{}'.format(attr))
        setter(value)

    # has to be done manually
    target.set_title(source.get_title())

    # Copy x-axis tick labels including rotations
    if isinstance(source.xaxis.get_major_locator(), FixedLocator):
        x_ticklabels = source.xaxis.get_ticklabels()
        try:
            tick_label_kwargs = {
                'ha': x_ticklabels[0].get_ha(),
                'rotation': x_ticklabels[0].get_rotation()}
        except IndexError:
            tick_label_kwargs = {}
        target.set_xticklabels(
            [text.get_text() for text in x_ticklabels],
            **tick_label_kwargs)

    for saxis, taxis in zip([source.xaxis, source.yaxis],
                            [target.xaxis, target.yaxis]):
        grid_params = {}
        major_grid_on = saxis._major_tick_kw.get('gridOn', False)
        minor_grid_on = saxis._minor_tick_kw.get('gridOn', False)

        if major_grid_on and minor_grid_on:
            grid_params['which'] = 'both'
        elif major_grid_on:
            grid_params['which'] = 'major'
        elif minor_grid_on:
            grid_params['which'] = 'minor'

        grid_lines = saxis.get_gridlines()
        if grid_lines:
            line_properties = grid_lines[0].properties()
            for prop in ['color', 'linewidth', 'linestyle']:
                value = line_properties.get(prop, None)
                grid_params[prop] = value

        grid_params['zorder'] = 1
        if saxis._gridOnMajor or saxis._gridOnMinor:
            taxis.grid(**grid_params)


def compress_axes(axes_of_figures, default_output_axes,
                  legends_join=False, legend_location='best',
                  copy_properties_from=0, auto_recolor=True,
                  auto_rescale=True, add_colorbars=True, add_legends=True,
                  remove_ticklabels=None):
    """
    Compress the lines and parameters from different axes into one.

    Parameters
    ----------
    axes_of_figures : array-like
        List of mpl axes
    default_output_axes : axes
        Mpl axes
    legends_join : bool, optional
        Set True if legends for different twin axes should be joined
        into one. Default False.
    legend_location : unicode or str or int, optional
        Location of the joined legend in mpl strings or int.
        Default 'best'., optional
    copy_properties_from : int, optional
        The set of twinaxes from which the axes properties should be
        copied to the resulting axes. Default 0.
    auto_recolor : bool, optional
        Set True if artists should be automatically recolored [Default: True].
    auto_rescale : bool, optional
        Automatically rescale all axes to fit the visible data.
    add_colorbars : bool, optional
        If True colorbars are added to the output axes.
        Default True
    add_legends : bool, optional
        If True legends are added to the output axes.
        Default True
    remove_ticklabels : tuple, optional
        If supplied, should be a tuple of four bool values, corresponding to
        each side of the plot (top, right, bottom, left). If a value is True
        the corresponding axis in the output figure will have its ticklabels
        removed.

    Returns
    -------
    axes_colorbars : dict
    """
    default_axes = default_output_axes

    output_axes_dict = {('bottom', 'left'): default_axes}
    if copy_properties_from >= len(axes_of_figures):
        copy_properties_from = 0
        sywarn('The figure specified as source for the new axes parameter '
               'does not exist. The first figure will be used!')

    axes_legends = {}
    axes_colorbars = {}

    last_axes_drawn_to = None
    existing_colors = []

    for idx, axes in enumerate(axes_of_figures):
        cb_axes = _get_colorbar_axes(axes)
        axes = [a for a in axes if a not in cb_axes]
        axes_dict = classify_axes(axes)

        for ax_id, source_ax in six.iteritems(get_sorted_axes(axes_dict)):
            colorbars = {}
            # save old ids, required to find last added axes
            old_axes_ids = output_axes_dict.keys()
            target_ax = get_twin_axes(output_axes_dict, ax_id[0], ax_id[1])
            source_ax, target_ax = _get_mpl_axes(source_ax, target_ax)
            # move supported artists
            _move_lines_to(source_ax, target_ax, existing_colors,
                           auto_recolor=auto_recolor)
            cbs = _move_collections_to(source_ax, target_ax, existing_colors,
                                       auto_recolor=auto_recolor)
            if cbs:
                colorbars['collections'] = cbs
            _move_containers_to(source_ax, target_ax)
            _move_text_to(source_ax, target_ax)
            cbs = _move_images_to(source_ax, target_ax)
            if cbs:
                colorbars['images'] = cbs

            # save the last added axes
            if ax_id not in old_axes_ids:
                last_axes_drawn_to = target_ax

            if idx == copy_properties_from:
                copy_axes_parameter(source_ax, target_ax)

            # set converter from source axes to format and locate datetime
            # correctly in only scatter plots
            target_ax.xaxis.converter = source_ax.xaxis.converter
            # call _update_axisinfo to reformat date axis
            target_ax.xaxis._update_axisinfo()
            target_ax.yaxis._update_axisinfo()

            if auto_rescale:
                target_ax.autoscale()

            if remove_ticklabels is not None:
                # Explicitly change the tick locator to FixedLocator to work
                # around a bug where date locators would recurse infinitely
                # during pickle if the ticklabels are cleared.
                if ax_id[0] == 'top' and remove_ticklabels[0]:
                    target_ax.set_xlabel("")
                    target_ax.set_xticklabels([])
                    target_ax.xaxis.set_major_locator(
                        FixedLocator(source_ax.xaxis.get_xticks()))
                    target_ax.xaxis.set_minor_locator(
                        FixedLocator(source_ax.xaxis.get_xticks(minor=True)))
                if ax_id[1] == 'right' and remove_ticklabels[1]:
                    target_ax.set_ylabel("")
                    target_ax.set_yticklabels([])
                    target_ax.yaxis.set_major_locator(
                        FixedLocator(source_ax.get_yticks()))
                    target_ax.xaxis.set_minor_locator(
                        FixedLocator(source_ax.get_yticks(minor=True)))
                if ax_id[0] == 'bottom' and remove_ticklabels[2]:
                    target_ax.set_xlabel("")
                    target_ax.set_xticklabels([])
                    target_ax.xaxis.set_major_locator(
                        FixedLocator(source_ax.get_xticks()))
                    target_ax.xaxis.set_minor_locator(
                        FixedLocator(source_ax.get_xticks(minor=True)))
                if ax_id[1] == 'left' and remove_ticklabels[3]:
                    target_ax.set_ylabel("")
                    target_ax.set_yticklabels([])
                    target_ax.yaxis.set_major_locator(
                        FixedLocator(source_ax.get_yticks()))
                    target_ax.xaxis.set_minor_locator(
                        FixedLocator(source_ax.get_yticks(minor=True)))

            # save if source_ax had legend
            legend = source_ax.get_legend()
            if (legend is not None and (ax_id not in axes_legends or
                                        idx == copy_properties_from)):
                # collect legends parameters
                legend_props = {}
                for prop in models.Legend.NODE_LEAFS:
                    value = None
                    if hasattr(legend, prop):
                        value = getattr(legend, prop)
                    elif hasattr(legend, '_{}'.format(prop)):
                        value = getattr(legend, '_{}'.format(prop))
                    elif hasattr(legend, 'get_{}'.format(prop)):
                        value = getattr(legend, 'get_{}'.format(prop))()
                    elif prop == 'frameon':
                        value = legend.get_frame_on()
                    if value is not None:
                        legend_props[prop] = value
                if legend_props:
                    legend_props['show'] = True
                axes_legends[ax_id] = legend_props
            elif legends_join and ax_id not in axes_legends:
                # if legend is a joined legend, it contains handles from
                # other axes which would be ignored. If joined legend is
                # specified all axes are added to the axes_legends dict
                axes_legends[ax_id] = {'show': True}

            if colorbars:
                axes_colorbars[ax_id] = colorbars

    if add_colorbars and axes_colorbars:
        for colorbars in axes_colorbars.values():
            axes_ = list(get_sorted_axes(output_axes_dict).values())
            for artist_type, artists in six.iteritems(colorbars):
                for (artist, colorbar_params) in artists:
                    _add_colorbar(colorbar_params, artist, axes=axes_)

    if add_legends and axes_legends:
        _draw_legend(default_axes, last_axes_drawn_to, axes_legends,
                     legend_location, legends_join, output_axes_dict)

    return axes_colorbars


def add_global_colorbar(axes_colorbars, figure):
    """
    Add a global colorbar to a figure.

    Parameters
    ----------
    axes_colorbars : dict
    figure : syfigure.Figure
    """
    for ax_id, colorbars in six.iteritems(axes_colorbars):
        for artist_type, artists in six.iteritems(colorbars):
            if artists:
                for (artist, colorbar_params) in artists:
                    if colorbar_params.pop('show', 'False') == 'True':
                        figure.colorbar(artist, **colorbar_params)
                        break
                break
        break


def _draw_legend(default_axes, last_axes_drawn_to, axes_legends,
                 legend_location, legends_join, axes_by_name,
                 global_legend=None):
    """Draw the Legend(s) to the given Axes."""

    lookup = {('bottom', 'left'): '$\downarrow\leftarrow$',
              ('bottom', 'right'): '$\downarrow\\rightarrow$',
              ('top', 'left'): '$\\uparrow\leftarrow$',
              ('top', 'right'): '$\\uparrow\\rightarrow$'}
    # draw legend for each axes
    legend_handles = []
    legend_labels = []
    multiple_axes = len(set(axes_legends.keys())) > 1
    for ax_name, props in six.iteritems(axes_legends):
        ax = axes_by_name[ax_name]

        if (bool(props.pop('show', False)) not in ['True', True] and
                not legends_join):
            continue
        if not legends_join:
            title = props.pop('title', None)
            if title is not None and title != 'None':
                if isinstance(title, Text):
                    title = title.get_text()
                props['title'] = title
            if 'frameon' in props:
                props['frameon'] = props['frameon'] in ['True', True]
            if 'ncol' in props:
                props['ncol'] = int(props['ncol'])
            ax.legend(**props)
        else:
            handles, labels = ax.get_legend_handles_labels()
            legend_handles.extend(handles)

            if multiple_axes:
                labels = ['{} ({})'.format(l, lookup[ax_name]) for l in labels]
            legend_labels.extend(labels)
    if legends_join:
        if global_legend is None:
            # copy legend properties from the default axes
            parent_legend_props = axes_legends.get(('bottom', 'left'), {})
            parent_legend_props.pop('loc', None)
            parent_legend_props.pop('title', None)
            parent_legend_props['loc'] = legend_location
        else:
            parent_legend_props = global_legend
        if len(legend_labels) or len(legend_handles):
            # to place the legend on top of everything else, we
            # need to add it to the last axes we added to the plot
            if last_axes_drawn_to is not None:
                ax = last_axes_drawn_to
            else:
                ax = default_axes
            if 'frameon' in parent_legend_props:
                frameon = parent_legend_props['frameon'] in ['True', True]
                parent_legend_props['frameon'] = frameon
            if 'ncol' in parent_legend_props:
                parent_legend_props['ncol'] = int(parent_legend_props['ncol'])
            ax.legend(legend_handles, legend_labels, **parent_legend_props)


def parse_values_in_dict(d, data_table, extra_vars=None):
    """Parse the values in a dict with `parse_value`."""
    extra_vars = extra_vars or {}
    return {key: (common.parse_value(value, data_table, extra_vars)
                  if isinstance(value, six.text_type) else value)
            for key, value in six.iteritems(d)}


def parse_plots_container(plots_container, data_table):
    """
    Traverse a list of plots parsing all values and expanding iterators.
    """
    parsed_container = []
    for value in plots_container:
        if isinstance(value, dict):
            if value.get('type') == 'iterator':
                parsed_container.extend(
                    expand_iterator(value, data_table))
            else:
                parsed_dict = parse_values_in_dict(value, data_table)
                if 'plots' in value:
                    parsed_dict['plots'] = parse_plots_container(
                        value['plots'], data_table)
                parsed_container.append(parsed_dict)
        else:
            parsed_container.append(common.parse_value(value, data_table))
    return parsed_container


def expand_iterator(iterator_dict, data_table):
    iter_name, iter_expression = iterator_dict['iterable'].split('=', 1)
    iter_name = iter_name.strip()
    if not iter_name:
        iter_name = 'e'
    counter_name = iterator_dict.get('counter', 'i')
    iterable = common.parse_value(iter_expression.strip(), data_table)
    plots = iterator_dict['plots']
    if not plots:
        return
    plot = plots[0]

    parsed_container = []
    for i, e in enumerate(iterable):
        extra_vars = {counter_name: i, iter_name: e}
        parsed_container.append(
            parse_values_in_dict(plot, data_table, extra_vars))
    return parsed_container


def _draw_bar_labels(
        axes, x_coords, y0, values, bar_labels, bar_labels_valign,
        bar_labels_font=None):
    """Draw bar labels onto axes."""
    if y0 is None:
        y0 = np.zeros_like(values)
    y_min, y_max = axes.get_ylim()
    inside = np.logical_not(np.logical_or(y0 > y_max, y0 + values < y_min))

    # Calculate positions based on y limits or bar edges, whichever is smaller.
    y_bot = np.minimum(y0, y_max)
    y_bot = np.maximum(y_bot, y_min)
    y_top = np.minimum(y0 + values, y_max)
    y_top = np.maximum(y_top, y_min)

    if bar_labels_valign == 'over':
        y_pos = y_top
        text_valign = 'bottom'
    elif bar_labels_valign == 'top':
        y_pos = y_top
        text_valign = 'top'
    elif bar_labels_valign == 'center':
        y_pos = np.mean([y_bot, y_top], axis=0)
        text_valign = 'center'
    elif bar_labels_valign == 'bottom':
        y_pos = y_bot
        text_valign = 'bottom'
    elif bar_labels_valign == 'under':
        y_pos = y_bot
        text_valign = 'top'
    else:
        raise ValueError('Unknown value for bar_labels_valign: '
                         '{}'.format(bar_labels_valign))

    if bar_labels_font is None:
        bar_labels_font = {}
    for x, y, s, i in zip(x_coords, y_pos, bar_labels, inside):
        if i:  # Ignore bars that are entirely outside of ylimits
            axes.text(x, y, s, horizontalalignment='center',
                      verticalalignment=text_valign, **bar_labels_font)


def get_fill_coords(bin_edges, values, y0=None):
    """
    Return coordinates suitable for building a histogram using fill_between.
    """
    if y0 is None:
        y0 = np.zeros_like(values)
    fill_x = np.zeros((2*(values.size + 1),))
    fill_x[::2] = bin_edges
    fill_x[1::2] = bin_edges
    fill_y = np.zeros_like(fill_x)
    fill_y[1:-2:2] = values + y0
    fill_y[2:-1:2] = values + y0
    fill_y0 = np.zeros_like(fill_x)
    fill_y0[1:-2:2] = y0
    fill_y0[2:-1:2] = y0
    return fill_x, fill_y, fill_y0


# TODO: This could be put either in figure API or in add_barcontainer.
def barcontainer_plot(axes, values_list, labels=None, grouping='grouped',
                      **kwargs):
    if grouping not in ('grouped', 'stacked'):
        raise ValueError("Invalid value for 'grouping': {}".format(grouping))

    group = None
    last_values = None
    for i, (values, label) in enumerate(zip(values_list, labels)):
        kwargs_ = {}
        for k, v in kwargs.items():
            if v is None:
                continue
            elif isinstance(v, list):
                kwargs_[k] = v[i]
            else:
                kwargs_[k] = v

        if grouping == 'grouped':
            group = i, len(values_list)
        bar_plot(axes, values, label, group=group, y0=last_values, **kwargs_)
        if grouping == 'stacked':
            if last_values is None:
                last_values = np.array(values)
            else:
                last_values += np.array(values)


# TODO: This could be put either in figure API or in add_histcontainer.
def histcontainer_plot(axes, values_list, bin_min_edges, bin_max_edges,
                       **kwargs):
    last_values = None
    for i, values in enumerate(values_list):
        kwargs_ = {}
        for k, v in kwargs.items():
            if v is None:
                continue
            elif isinstance(v, list):
                kwargs_[k] = v[i]
            else:
                kwargs_[k] = v

        hist_plot(axes, values, bin_min_edges, bin_max_edges, y0=last_values,
                  **kwargs_)
        if last_values is None:
            last_values = np.array(values)
        else:
            last_values += np.array(values)


# TODO: I would like to put this method into typeutils/figure.py but this
# module is only working with pure mpl objects.
def bar_plot(axes, values, labels=None, histtype='bar', rwidth=0.8,
             bar_labels=None, bar_labels_valign='center',
             bar_labels_font=None, color=None, group=None, y0=None,
             rot_bin_labels=None, **kwargs):
    """Make a bar plot the way you want it."""
    if not isinstance(values, np.ndarray):
        values = np.array(values)
    if labels is None:
        labels = np.arange(len(values))
    if color is not None:
        kwargs['facecolor'] = color

    x_data = np.arange(len(values))
    left, width = x_data, rwidth

    if histtype == 'bar':
        # Assume unity bin width
        bin_width = 1
        padding = bin_width*(1 - rwidth)/2.0
        left = x_data - bin_width/2.0 + padding
        if group is not None:
            width *= bin_width/group[1]
            left += group[0]*width
        patches = axes.bar(
            left, height=values, width=width, bottom=y0, align='edge',
            **kwargs)
    else:
        # Use fill_between() instead of hist() to get around bugs in matplotlib
        # histograms with 'step' histtype.
        bin_edges = np.arange(len(values) + 1)
        fill_x, fill_y, fill_y0 = get_fill_coords(bin_edges, values, y0)

        kwargs.setdefault('facecolor', 'none')
        patches = axes.fill_between(fill_x, fill_y0, fill_y, **kwargs)

    # Draw bar labels
    if bar_labels is not None:
        x_coords = left + width/2.0
        _draw_bar_labels(axes, x_coords, y0, values, bar_labels,
                         bar_labels_valign, bar_labels_font)

    # Label the bins on the x axis.
    tick_label_kwargs = {}
    if rot_bin_labels == 'Clockwise':
        tick_label_kwargs = {'ha': 'left', 'rotation': -30}
    elif rot_bin_labels == 'Vertical':
        tick_label_kwargs = {'rotation': -90}
    elif rot_bin_labels == 'Counter clockwise':
        tick_label_kwargs = {'ha': 'right', 'rotation': 30}
    axes.set_xticks(x_data)
    axes.set_xticklabels(labels, **tick_label_kwargs)
    return patches


# TODO: I would like to put this method into typeutils/figure.py but this
# module is only working with pure mpl objects.
def hist_plot(axes, values, bin_min_edges, bin_max_edges, bar_labels=None,
              bar_labels_valign='center', bar_labels_font=None,
              histtype='bar', color=None, y0=None, **kwargs):
    """Make a histogram plot."""
    if not isinstance(values, np.ndarray):
        values = np.array(values)
    if color is not None:
        kwargs['facecolor'] = color

    if histtype == 'bar':
        width = bin_max_edges - bin_min_edges
        patches = axes.bar(
            bin_min_edges, height=values, width=width, bottom=y0,
            align='edge', **kwargs)
    else:
        # Use fill_between() instead of hist() to get around bugs in matplotlib
        # histograms with 'step' histtype.
        bin_edges = np.append(bin_min_edges, bin_max_edges[-1])
        fill_x, fill_y, fill_y0 = get_fill_coords(bin_edges, values, y0)

        kwargs.setdefault('facecolor', 'none')
        patches = axes.fill_between(fill_x, fill_y0, fill_y, **kwargs)

        try:
            sticky_edges = patches.sticky_edges
        except AttributeError:
            # sticky_edges don't exist prior to matplotlib 2.0
            pass
        else:
            sticky_edges.y[:] = (0,)
            axes.autoscale_view()

    # Draw bar labels
    if bar_labels is not None:
        x_coords = (bin_min_edges + bin_max_edges)/2.0
        _draw_bar_labels(axes, x_coords, y0, values, bar_labels,
                         bar_labels_valign, bar_labels_font)

    return patches


def heatmap_plot(axes, xdata, ydata, zdata, colormap='auto',
                 normalization='linear', vmin=None, vmax=None, aspect='auto',
                 zlabels=None):
    """Create a heatmap."""
    # TODO: Check integrity of xdata and ydata! There should be no reoccuring
    # and no missing indices (x,y).
    unique_x = np.unique(xdata)
    unique_y = np.unique(ydata)
    masked_z = np.ma.masked_all(zdata.shape, zdata.dtype)
    finite_mask = np.isfinite(zdata)
    if isinstance(zdata, np.ma.MaskedArray):
        finite_mask = finite_mask.filled(False)
    masked_z[finite_mask] = zdata[finite_mask]
    if normalization == 'log':
        non_positive_mask = (masked_z <= 0).filled(False)
        if np.any(non_positive_mask):
            sywarn("Ignoring non-positive z-values when using log scale.")
            masked_z.mask = np.logical_or(masked_z.mask, non_positive_mask)

    if len(unique_x) == 1:
        next_x = unique_x[0] + 1
    else:
        x_step = np.median(np.diff(unique_x))
        next_x = max(unique_x) + x_step
    if len(unique_y) == 1:
        next_y = unique_y[0] + 1
    else:
        y_step = np.median(np.diff(unique_y))
        next_y = max(unique_y) + y_step
    x_to_index = dict(zip(unique_x, range(len(unique_x))))
    y_to_index = dict(zip(unique_y, range(len(unique_y))))
    extent = (min(unique_x), next_x, min(unique_y), next_y)
    Z = np.ma.masked_all((len(unique_y), len(unique_x)), dtype=float)
    for x, y, z in zip(xdata, ydata, masked_z):
        xi = x_to_index[x]
        yi = y_to_index[y]
        Z[yi, xi] = z

    # Set up colormap
    colormap = colors.COLORMAPS[colormap]
    if colormap is None:
        if np.any(masked_z < 0) and np.any(masked_z > 0):
            # Use diverging colormap
            colormap = 'BrBG'
        else:
            # Use sequential colormap
            colormap = 'viridis'

    if np.all(masked_z.mask):
        # There are no finite values in zdata. z-scale doesn't matter.
        if normalization == 'linear':
            vmin, vmax = 0, 1
        elif normalization == 'log':
            vmin, vmax = 1, 10
    else:
        if colormap in list(colors.DIVERGING_COLORMAPS.values()):
            zabsmax = max(np.abs(np.min(masked_z)), np.abs(np.max(masked_z)))
            if vmin is None:
                vmin = -zabsmax
            if vmax is None:
                vmax = zabsmax
        else:
            if vmin is None:
                vmin = np.min(masked_z)
            if vmax is None:
                vmax = np.max(masked_z)

    if normalization == 'linear':
        norm = matplotlib.colors.Normalize()
    elif normalization == 'log':
        norm = matplotlib.colors.LogNorm()
    heatmap = axes.imshow(
        Z, cmap=colormap, norm=norm, interpolation='none', aspect=aspect,
        extent=extent, vmin=vmin, vmax=vmax, origin='lower')

    # Draw zlabels if selected
    if zlabels is not None:
        for x, y, zlabel in zip(xdata, ydata, zlabels):
            # Never print masked values
            if zlabel is np.ma.masked:
                continue

            # Position in center of bin
            xpos = x + x_step/2
            ypos = y + y_step/2

            # Find a good text color for this bin, choosing white if the
            # bin color is dark and black if the bin color is bright.
            c = heatmap.cmap
            n = heatmap.norm
            xi = x_to_index[x]
            yi = y_to_index[y]
            bg_color_tuple = c(n(Z[yi, xi]))
            bg_brightness = sum(bg_color_tuple[:3]) / 3.0
            if bg_brightness > 0.5:
                text_color = '#000000'
            else:
                text_color = '#FFFFFF'

            axes.text(xpos, ypos, six.text_type(zlabel),
                      horizontalalignment='center',
                      verticalalignment='center',
                      color=text_color, fontsize='small')

    return heatmap


def make_axes_gridspec(parents, **kw):
    """
    Resize and reposition a parent axes, and return a child axes
    suitable for a colorbar. This function is similar to
    make_axes. Primary differences are

     * *make_axes_gridspec* only handles the *orientation* keyword
       and cannot handle the "location" keyword.

     * *make_axes_gridspec* should only be used with a subplot parent.

     * *make_axes* creates an instance of Axes. *make_axes_gridspec*
        creates an instance of Subplot.

     * *make_axes* updates the position of the
        parent. *make_axes_gridspec* replaces the grid_spec attribute
        of the parent with a new one.

    While this function is meant to be compatible with *make_axes*,
    there could be some minor differences.::

        cax, kw = make_axes_gridspec(parent, **kw)

    Keyword arguments may include the following (with defaults):

        *orientation*
            'vertical' or 'horizontal'

    %s

    All but the first of these are stripped from the input kw set.

    Returns (cax, kw), the child axes and the reduced kw dictionary to be
    passed when creating the colorbar instance.
    """

    orientation = kw.setdefault('orientation', 'vertical')
    kw['ticklocation'] = 'auto'

    fraction = kw.pop('fraction', 0.15)
    shrink = kw.pop('shrink', 1.0)
    aspect = kw.pop('aspect', 20)

    x1 = 1.0 - fraction

    # for shrinking
    pad_s = (1. - shrink) * 0.5
    wh_ratios = [pad_s, shrink, pad_s]

    gs_from_subplotspec = gridspec.GridSpecFromSubplotSpec
    parent = parents[0]

    if orientation == 'vertical':
        pad = kw.pop('pad', 0.05)
        if any([p.yaxis.get_ticks_position() == 'right' for p in parents]):
            pad += 0.10

        wh_space = 2 * pad / (1 - pad)

        gs = gs_from_subplotspec(1, 2,
                                 subplot_spec=parent.get_subplotspec(),
                                 wspace=wh_space,
                                 width_ratios=[x1 - pad, fraction]
                                 )

        gs2 = gs_from_subplotspec(3, 1,
                                  subplot_spec=gs[1],
                                  hspace=0.,
                                  height_ratios=wh_ratios,
                                  )

        anchor = (0.0, 0.5)
        panchor = (1.0, 0.5)
    else:
        pad = kw.pop('pad', 0.15)
        wh_space = 2 * pad / (1 - pad)

        gs = gs_from_subplotspec(2, 1,
                                 subplot_spec=parent.get_subplotspec(),
                                 hspace=wh_space,
                                 height_ratios=[x1 - pad, fraction]
                                 )

        gs2 = gs_from_subplotspec(1, 3,
                                  subplot_spec=gs[1],
                                  wspace=0.,
                                  width_ratios=wh_ratios,
                                  )

        aspect = 1.0 / aspect
        anchor = (0.5, 1.0)
        panchor = (0.5, 0.0)

    for parent_ in parents:
        parent_.set_subplotspec(gs[0])
        parent_.update_params()
        parent_.set_position(parent_.figbox)
        parent_.set_anchor(panchor)

    fig = parent.get_figure()
    cax = fig.add_subplot(gs2[1])
    cax.set_aspect(aspect, anchor=anchor, adjustable='box')
    return cax, kw


def _add_colorbar(colorbar, artist, axes=None):
    """
    Add a colorbar for given artist to the figure.

    Parameters
    ----------
    colorbar : dict
        Dictionary of parameters.
    artist : matplotlib.artist.Artist
        The artist which should be linked to the colorbar.
    axes : matplotlib.axes.Axes or list, optional
        None | parent axes object(s) from which space for a new colorbar axes
        will be stolen. If a list of axes is given they will all be resized to
        make room for the colorbar axes.

    Returns
    -------
    cb : matplotlib.colorbar.Colorbar
    """
    figure = artist.get_figure()

    if colorbar is not None and colorbar.get('show') == 'True':
        orientation = colorbar.get('orientation', 'vertical')
        ax = axes if axes is not None else figure.axes
        if isinstance(axes, Iterable):
            cax, kw = make_axes_gridspec(ax, orientation=orientation)
            cb = figure.colorbar(artist, cax=cax, **kw)
        else:
            cb = figure.colorbar(artist, ax=ax, orientation=orientation)
        cb_label = colorbar.get('label')
        if cb_label:
            cb.set_label(cb_label)
        return cb
    return None


def _recreate_colorbar(old_artist, new_artist):
    colorbar_params = _get_colorbar_properties(old_artist)
    _add_colorbar(colorbar_params, new_artist)


def _get_colorbar_properties(old_artist):
    """
    Returns the parameters for recreating the colorbar.

    Parameters
    ----------
    old_artist : matplotlib.artist.Artist
        The artist whose colorbar to copy.

    Returns
    -------
    colorbar : dict
        Dictionary of parameters.
    """
    cb = getattr(old_artist, 'colorbar')
    if cb is not None:
        colorbar = {'show': 'True',
                    'orientation': cb.orientation}
        if hasattr(cb, '_label') and cb._label:
            colorbar['label'] = cb._label
        return colorbar


class CreateFigure(object):
    """
    This :class:`CreateFigure` class is used to create a populate a
    ``matplotlib`` figure with data from `date_table` as defined in
    `parsed_param`.
    """
    def __init__(self, data_table, figure, parsed_param):

        self.data_table = data_table
        self.figure = figure
        self.parsed_param = copy.deepcopy(parsed_param)
        self.axes = {
            ('bottom', 'left'): self.figure.first_subplot().get_mpl_axes()}
        self.axes_by_name = {('bottom', 'left'): self.axes[('bottom', 'left')]}
        self.axes_legends = {}
        self.global_legend_properties = None
        self.join_legends = False
        self.last_axes_drawn_to = None
        self.xaxes_with_dates = {}

    def create_figure(self):
        fig_param = self.parsed_param['figure']
        self.apply_figure_parameters(fig_param)
        ax_params = fig_param.get('axes', {})
        self.apply_axes_parameters(ax_params)

        for axes_param in ax_params:
            xaxis = axes_param.get('xaxis', {})
            yaxis = axes_param.get('yaxis', {})
            xaxis_pos = xaxis.get('position', 'bottom')
            yaxis_pos = yaxis.get('position', 'left')
            ax = self.axes[(xaxis_pos, yaxis_pos)]
            plots = parse_plots_container(
                axes_param.get('plots', []), self.data_table)
            for plot_param in plots:
                plot_type = plot_param.pop('type')
                if plot_type == 'line':
                    self.add_lines(ax, plot_param)
                elif plot_type == 'scatter':
                    self.add_scatter(ax, plot_param)
                elif plot_type == 'bar':
                    self.add_bars(ax, plot_param)
                elif plot_type == 'barcontainer':
                    self.add_barcontainer(ax, plot_param)
                elif plot_type == 'hist':
                    self.add_hist(ax, plot_param)
                elif plot_type == 'histcontainer':
                    self.add_histcontainer(ax, plot_param)
                elif plot_type == 'heatmap':
                    self.add_heatmap(ax, plot_param)
            self.last_axes_drawn_to = ax

        self.draw_legends()

        for axes, xlim in six.iteritems(self.xaxes_with_dates):
            axes.set_xlim(xlim)
        return self.figure

    def update_date_axes_xlimits(self, axes, xlim):
        old_xlim = self.xaxes_with_dates.get(axes)
        if old_xlim:
            xlim = (min(old_xlim[0], xlim[0]), max(old_xlim[1], xlim[1]))
        self.xaxes_with_dates[axes] = xlim

    def apply_axes_parameters(self, parameters):
        """Create all defined axes."""
        for axes_params in parameters:
            axes_params = copy.deepcopy(axes_params)
            axes_params.pop('type')
            # add a grid if specified
            grid_params = axes_params.pop('grid', None)

            # create the defined axes
            xaxis = axes_params.pop('xaxis', {})
            yaxis = axes_params.pop('yaxis', {})
            xaxis_pos = xaxis.get('position', 'bottom')
            yaxis_pos = yaxis.get('position', 'left')
            for l, axis in zip('xy', [xaxis, yaxis]):
                for key in ['label', 'scale', 'lim']:
                    value = axis.get(key)
                    if value is not None:
                        axes_params[l+key] = value

            # save legend parameters for later handling
            self.axes_legends[(xaxis_pos, yaxis_pos)] = axes_params.pop(
                'legend', {'show': False})

            # evaluate parameters
            axes_params = parse_values_in_dict(axes_params, self.data_table)

            ax = get_twin_axes(self.axes, xaxis_pos, yaxis_pos)
            self.axes_by_name[(xaxis_pos, yaxis_pos)] = ax

            if grid_params is not None:
                self.apply_axes_grid_parameters(ax, grid_params)

            # set the remaining parameters
            axes_params.pop('plots', None)
            if isinstance(ax, SyAxes):
                ax = ax.get_mpl_axes()
            color_cycle_name = axes_params.pop('color_cycle', 'default')
            color_cycle = colors.COLOR_CYCLES.get(color_cycle_name, 'default')

            ax.set(**axes_params)
            mpl_utils.set_color_cycle(ax, color_cycle)

    def add_bars(self, axes, bar):
        ydata = bar.pop('ydata')

        # get the column data if data is specified as string
        if (isinstance(ydata, six.text_type) and
                ydata in self.data_table.column_names()):
            ydata = self.data_table.get_column_to_array(ydata)

        if not isinstance(ydata, np.ndarray):
            sywarn('The data for bar plot is not accessible and '
                   'will not be plotted!')
            return

        bin_labels = bar.pop('bin_labels', None)
        bar_plot(axes, ydata, bin_labels, **bar)

    def add_barcontainer(self, axes, barcontainer):
        """Add a list of bar plots (stacked or grouped)."""
        plots = barcontainer.pop('plots')

        bar_list_params = defaultdict(list)
        listable_params = [
            # Mandatory:
            'ydata',
            # Very reasonable ones:
            'label', 'bar_labels', 'color', 'edgecolor',
            # Slightly less reasonable ones:
            'bar_labels_valign', 'linewidth', 'linestyle', 'alpha', 'zorder',
            'bin_labels', 'bar_labels_font'
            # Not allowed:
            # 'axes'
        ]

        color_cycle = itertools.cycle(mpl_utils.color_cycle(axes))

        # Create lists of parameters
        for i, bar in enumerate(plots):
            for k in listable_params:
                value = bar.get(k, None)
                if k == 'color' and value is None:
                    value = six.next(color_cycle)
                elif k == 'ydata' and not isinstance(value, np.ndarray):
                    sywarn('The data for Bar plot in the Bar Container '
                           'is not accessible and will not be plotted!')
                    value = None
                bar_list_params[k].append(value)

        # Remove lists with only None
        for k, v in list(bar_list_params.items()):
            if all(e is None for e in v):
                del bar_list_params[k]
        bar_list_params = {k: v for k, v in bar_list_params.items()
                           if any(e is not None for e in v)}

        barcontainer.update(bar_list_params)
        ydata = barcontainer.pop('ydata', None)
        bin_labels = barcontainer.pop('bin_labels', None)
        grouping = barcontainer.pop('grouping', None)
        if ydata is None:
            sywarn('No y-data specified. Please check the configuration.')
        else:
            barcontainer_plot(axes, ydata, bin_labels, grouping=grouping,
                              **barcontainer)

    def add_hist(self, axes, hist):
        bin_min_edges = hist.pop('bin_min_edges')
        bin_max_edges = hist.pop('bin_max_edges')
        ydata = hist.pop('ydata')

        # get the column data if data is specified as string
        if (isinstance(bin_min_edges, six.text_type) and
                bin_min_edges in self.data_table.column_names()):
            bin_min_edges = self.data_table.get_column_to_array(
                bin_min_edges)
        if (isinstance(bin_max_edges, six.text_type) and
                bin_max_edges in self.data_table.column_names()):
            bin_max_edges = self.data_table.get_column_to_array(
                bin_max_edges)
        if (isinstance(ydata, six.text_type) and
                ydata in self.data_table.column_names()):
            ydata = self.data_table.get_column_to_array(ydata)

        if (not isinstance(bin_min_edges, np.ndarray) or
                not isinstance(bin_max_edges, np.ndarray) or
                not isinstance(ydata, np.ndarray)):
            sywarn('The data for hist plot is not accessible and '
                   'will not be plotted!')
            return
        # # TODO: Handle datetimes, at least for x data
        # xdate = xdata.dtype.kind == 'M'
        # ydate = ydata.dtype.kind == 'M'
        # if xdate or ydate:
        #     if xdate:
        #         xdata = xdata.astype(datetime)
        #     if ydate:
        #         ydata = ydata.astype(datetime)
        #     hist['xdate'] = xdate
        #     hist['ydate'] = ydate

        #     axes.plot_date(xdata, ydata, **hist)
        hist_plot(axes, ydata, bin_min_edges, bin_max_edges, **hist)

    def add_histcontainer(self, axes, histcontainer):
        """Add a list of hist stacked plots."""
        plots = histcontainer.pop('plots')

        # axes_desc = histcontainer.pop('axes', '_default_')
        # axes = self.axes_by_name.get(axes_desc)
        hist_list_params = defaultdict(list)
        listable_params = [
            # Mandatory:
            'ydata',
            # Very resonable ones:
            'label', 'bar_labels', 'color', 'edgecolor', 'bar_labels_font',
            # Slightly less resonable ones:
            'hist_labels_valign', 'linewidth', 'linestyle', 'alpha', 'zorder'
            # Not allowed:
            # 'bin_min_edges', 'bin_max_edges', 'axes', 'histtype'
        ]

        possible_glob_params = [
            'bin_min_edges', 'bin_max_edges',
        ]

        color_cycle = itertools.cycle(mpl_utils.color_cycle(axes))

        # Create lists of parameters
        for hist in plots:
            for k in listable_params:
                value = hist.get(k, histcontainer.get(k, None))
                if k == 'color' and value is None:
                    value = six.next(color_cycle)
                elif (k in ['bin_min_edges', 'bin_max_edges', 'ydata'] and
                      not isinstance(value, np.ndarray)):
                    sywarn('The data for Histogram plot in the '
                           'Histogram Container is not '
                           'accessible and will not be plotted!')
                    value = None
                hist_list_params[k].append(value)

            for k in possible_glob_params:
                if k not in histcontainer:
                    value = hist.get(k, None)
                    if value is not None:
                        histcontainer[k] = value

        # Remove lists with only None
        for k, v in list(hist_list_params.items()):
            if all(e is None for e in v):
                del hist_list_params[k]
        hist_list_params = {k: v for k, v in hist_list_params.items()
                            if any(e is not None for e in v)}

        histcontainer.update(hist_list_params)
        bin_min_edges = histcontainer.pop('bin_min_edges', None)
        bin_max_edges = histcontainer.pop('bin_max_edges', None)
        ydata = histcontainer.pop('ydata', None)
        if bin_max_edges is None or bin_min_edges is None or ydata is None:
            if bin_min_edges is None:
                sywarn('"Bin min edges" are incorrect defined. '
                       'Check configuration.')
            if bin_max_edges is None:
                sywarn('"Bin max edges" are incorrect defined. '
                       'Check configuration.')
            if ydata is None:
                sywarn('"y-data" is incorrect defined. Check configuration.')
        else:
            histcontainer_plot(axes, ydata, bin_min_edges, bin_max_edges,
                               **histcontainer)

    def add_lines(self, axes, line):
        xdata = line.pop('xdata')
        ydata = line.pop('ydata')

        # get the column data if data is specified as string
        if (isinstance(xdata, six.text_type) and
                xdata in self.data_table.column_names()):
            xdata = self.data_table.get_column_to_array(xdata)
        if (isinstance(ydata, six.text_type) and
                ydata in self.data_table.column_names()):
            ydata = self.data_table.get_column_to_array(ydata)

        if (not isinstance(xdata, np.ndarray) or
                not isinstance(ydata, np.ndarray)):
            sywarn('The data for line plot is not accessible and '
                   'will not be plotted!')
            return

        if 'marker' in line:
            marker = line.pop('marker')
            for key, value in six.iteritems(mpl_utils.MARKERS):
                if marker == key:
                    break
                elif marker == value:
                    marker = key
                    break
            line['marker'] = marker

        # cleanup parameters
        if 'linestyle' in line.keys() and line['linestyle'] is None:
            line['linestyle'] = 'none'
        # required to plot as lines and not as markers
        if 'linestyle' not in line.keys():
            line['linestyle'] = '-'
        if 'marker' not in line.keys():
            line['marker'] = ''
        # make sure color values are given in correct format
        for color_key in ['color', 'markeredgecolor', 'markerfacecolor']:
            if color_key in line:
                line[color_key] = colors.parse_to_mpl_color(line[color_key])

        xdate = xdata.dtype.kind == 'M'
        ydate = ydata.dtype.kind == 'M'
        if xdate or ydate:
            if xdate:
                xdata = xdata.astype(datetime)
            if ydate:
                ydata = ydata.astype(datetime)
            line['xdate'] = xdate
            line['ydate'] = ydate

            axes.plot_date(xdata, ydata, **line)

            if xdate:
                self.update_date_axes_xlimits(axes, axes.get_xlim())
        else:
            axes.plot(xdata, ydata, **line)

    def add_scatter(self, axes, scatter):
        xdata = scatter.pop('xdata')
        ydata = scatter.pop('ydata')
        colorbar = scatter.pop('colorbar', None)

        # get the column data if data is specified as string
        if (isinstance(xdata, six.text_type) and
                xdata in self.data_table.column_names()):
            xdata = self.data_table.get_column_to_array(xdata)
        if (isinstance(ydata, six.text_type) and
                ydata in self.data_table.column_names()):
            ydata = self.data_table.get_column_to_array(ydata)

        if (not isinstance(xdata, np.ndarray) or
                not isinstance(ydata, np.ndarray)):
            sywarn('The data for line plot is not accessible and '
                   'will not be plotted!')
            return

        xdate = xdata.dtype.kind == 'M'
        ydate = ydata.dtype.kind == 'M'
        if xdate or ydate:
            if xdate:
                xdata = xdata.astype(datetime)
            if ydate:
                ydata = ydata.astype(datetime)

        # make sure color values are given in correct format
        if 'color' in scatter:
            color = scatter.pop('color')
            if (isinstance(color, six.text_type) and
                    color in self.data_table.column_names()):
                color = self.data_table.get_column_to_array(color)
            elif isinstance(color, np.ndarray):
                pass
            else:
                color = colors.parse_to_mpl_color(color)
            scatter['c'] = color

        vmin = scatter.get('vmin')
        vmax = scatter.get('vmax')

        if 'cmap' in scatter:
            if 'c' not in scatter:
                scatter['c'] = np.arange(len(xdata))
            colormap = scatter['cmap']
            # Set up colormap
            colormap = colors.COLORMAPS[colormap]
            if colormap is None:
                if np.any(scatter['c'] < 0) and np.any(scatter['c'] > 0):
                    # Use diverging colormap
                    colormap = 'BrBG'
                else:
                    # Use sequential colormap
                    colormap = 'magma'

            if colormap in list(colors.DIVERGING_COLORMAPS.values()):
                c_abs_max = max(abs(min(scatter['c'])), abs(max(scatter['c'])))
                if vmin is None:
                    vmin = -c_abs_max
                if vmax is None:
                    vmax = c_abs_max
            else:
                if vmin is None:
                    vmin = min(scatter['c'])
                if vmax is None:
                    vmax = max(scatter['c'])
            scatter['cmap'] = colormap

        if 'marker' in scatter:
            marker = scatter.pop('marker', 'circle')
            for key, value in six.iteritems(mpl_utils.MARKERS):
                if marker == key:
                    break
                elif marker == value:
                    marker = key
                    break
            scatter['marker'] = marker

        # plot scatter
        scatter['vmin'] = vmin
        scatter['vmax'] = vmax
        artist = axes.scatter(xdata, ydata, **scatter)

        if xdate:
            axes.xaxis_date(tz=None)
        if ydate:
            axes.yaxis_date(tz=None)

        axes.autoscale_view()

        if xdate:
            # fix autoscaling for scatter plots
            # the datetime must be converted to floats to be comparable
            xmin = mpl_dates.date2num(xdata.min())
            xmax = mpl_dates.date2num(xdata.max())
            xr = xmax - xmin
            xlim = (xmin - xr * axes._xmargin, xmax + xr * axes._xmargin)
            self.update_date_axes_xlimits(axes, xlim)

        _add_colorbar(colorbar, artist,
                      axes=list(get_sorted_axes(self.axes_by_name).values()))

    def add_heatmap(self, axes, heatmap):
        xdata = heatmap.pop('xdata')
        ydata = heatmap.pop('ydata')
        zdata = heatmap.pop('zdata')
        colorbar = heatmap.pop('colorbar', None)

        # get the column data if data is specified as string
        if (isinstance(xdata, six.text_type) and
                xdata in self.data_table.column_names()):
            xdata = self.data_table.get_column_to_array(xdata)
        if (isinstance(ydata, six.text_type) and
                ydata in self.data_table.column_names()):
            ydata = self.data_table.get_column_to_array(ydata)
        if (isinstance(zdata, six.text_type) and
                zdata in self.data_table.column_names()):
            zdata = self.data_table.get_column_to_array(zdata)

        if (not isinstance(xdata, np.ndarray) or
                not isinstance(ydata, np.ndarray) or
                not isinstance(zdata, np.ndarray)):
            sywarn('The data for heatmap plot is not accessible and '
                   'will not be plotted!')
            return

        diverging = heatmap.get('colormap') in list(
            colors.DIVERGING_COLORMAPS.keys())
        log_scale = heatmap.get('normalization') == 'log'
        if diverging and log_scale:
            raise SyConfigurationError(
                "Can't use diverging colormaps with logarithmic colormap "
                "scale.")

        xdate = xdata.dtype.kind == 'M'
        ydate = ydata.dtype.kind == 'M'
        if xdate or ydate:
            if xdate:
                xdata = xdata.astype(datetime)
            if ydate:
                ydata = ydata.astype(datetime)

        artist = heatmap_plot(axes, xdata, ydata, zdata, **heatmap)
        _add_colorbar(colorbar, artist,
                      axes=list(get_sorted_axes(self.axes_by_name).values()))

        if xdate:
            axes.xaxis_date(tz=None)
        if ydate:
            axes.yaxis_date(tz=None)

        axes.autoscale_view()

        if xdate:
            # fix autoscaling for scatter plots
            # the datetime must be converted to floats to be comparable
            xmin = mpl_dates.date2num(xdata.min())
            xmax = mpl_dates.date2num(xdata.max())
            xr = xmax - xmin
            xlim = (xmin - xr * axes._xmargin, xmax + xr * axes._xmargin)
            self.update_date_axes_xlimits(axes, xlim)

    def draw_legends(self):
        _draw_legend(self.axes.get(('bottom', 'left')),
                     self.last_axes_drawn_to,
                     self.axes_legends,
                     'best',
                     self.join_legends,
                     self.axes,
                     self.global_legend_properties)

    def apply_figure_parameters(self, parameters):
        parameters = parse_values_in_dict(parameters, self.data_table)
        for param, value in six.iteritems(parameters):
            if param == 'title':
                self.figure.set_title(value)
                # set the default tight layout to false
                # if figure suptitle is set
                self.figure.get_mpl_figure().set_tight_layout(False)
                self.figure.subplots_adjust(top=0.85)
            elif param == 'legend':
                if value.pop('show', False):
                    self.global_legend_properties = value
                    self.join_legends = True

    def apply_axes_grid_parameters(self, axes, params):
        parsed_params = parse_values_in_dict(params, self.data_table)
        if parsed_params.pop('show', False):
            axes.grid(**parsed_params)

    def apply_axes_legend_parameters(self, axes, params):
        parsed_params = parse_values_in_dict(params, self.data_table)
        if parsed_params.pop('show', False):
            axes.legend(**parsed_params)
