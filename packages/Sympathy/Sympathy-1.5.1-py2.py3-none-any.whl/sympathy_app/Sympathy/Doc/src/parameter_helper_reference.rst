.. _parameter_helper_reference:

Parameter helper reference
==========================


Adding scalar parameters
------------------------
There are four types of scalar parameters in sympathy: booleans, integers,
floats, and strings. Use the methods ``set_boolean``, ``set_integer``,
``set_float``, and ``set_string`` to add each of these types to a parameter
group. The following arguments are accepted:

``name``
  First positional argument is the name of the parameter. This is used as a key
  to get the specific parameter from the parameter group.

``value``
  Default value.

``label``
  Shown next to the parameter editor to help the user identify the different
  parameters.

``description``
  Shown as a tooltip for each parameter and can contain a longer description
  for each parameters.

``editor``
  Changes how the parameter can be edited in the configuration GUI. See
  :ref:`parameter_editors`.


Adding lists
------------
If you need a parameter which at any given time has only one value chosen from
a list of available options, you should use one of the scalar parameter types
with a combo editor. See :ref:`All parameters example` for an example of this.
On the other hand, if you actually want a parameter where the user can select
multiple options, a list parameter is what you need. The method ``set_list``
adds a list parameter. It has all the arguments of the corresponding methods
for adding scalar parameters, but it also accepts a few extra arguments:

``list`` or ``plist``
  Two synonyms for specifying all the available options in the list.

``value``
  A list of selected indices.

``value_names``
  A list of selected entries from ``list``/``plist``.

If ``list`` (or ``plist``) is specified and non-empty, but neither ``value`` nor
``value_names`` is specified, the first element of ``list`` will automatically
be selected. To avoid this behavior and leave the selection empty you can
specify ``value_names`` (or ``value``) as an empty list.


Adding groups and pages
-----------------------
To group related parameters together, use the methods ``create_group`` and
``create_page``. Creating a group and then adding parameters to that group
results in a border around those parameters in the GUI. Each page in the
parameters is shown as a tab in the configuration GUI. See
:ref:`All parameters example` for examples of how to use groups and pages.


.. _parameter_editors:

Editors
-------
The available parameter editors are:

================================ ============================================== ==============================
Editor name                      Description                                    Usable with data types
================================ ============================================== ==============================
lineedit_editor                  A single line input.                           strings, floats and integers

bounded_lineedit_editor          A single line input with upper                 floats and integers
                                 and/or lower bounds for input.

spinbox_editor                   A line with buttons for increasing and         floats and integers
                                 decreasing the value with a predefined step.

bounded_spinbox_editor           A spinbox with upper and/or lower bounds.      floats and integers

decimal_spinbox_editor           A spinbox where the number of                  floats
                                 decimals can be defined.

decimal_bounded_spinbox_editor   A spinbox both bounded and decimal.            floats

textedit_editor                  A text editor with support for multiple lines  strings
                                 of text.

code_editor                      A text edit suitable for editing code. The     strings
                                 extra argument ``language`` can be used to
                                 specify the language for syntax highlighting.

filename_editor                  A line edit and a button to browse for         strings
                                 existing files. A filter can be set to limit
                                 the types of files shown.

savename_editor                  A line edit and a button for choosing a new    strings
                                 or existing path. A filter can be set to limit
                                 the types of files shown.

directory_editor                 A line edit and a button to browse             strings
                                 for directories.

combo_editor                     A combobox, that is, a drop down list          lists, strings
                                 with a single selection.

list_editor                      A list with checkboxes for selection.          lists

multilist_editor                 A list with checkboxes for selection.          lists
                                 Multiple selection enabled.

selectionlist_editor             Deprecated. Use list_editor or                 lists
                                 multilist_editor instead.

checkbox editor                  A box which can be checked and unchecked.      boolean
                                 The default for boolean parameters.
================================ ============================================== ==============================

All editors can be found in ``synode.editors``. To set the editor of a parameter
to for example *spinbox_editor*, set the parameters editor argument to
``synode.editors.spinbox_editor()``. Once again refer to
:ref:`All parameters example` for many examples of choosing and configuring
editors.


.. Usage in custom GUIs
.. --------------------

