.. _create_type:

Creating a custom data type
===========================
The data types that are available in Sympathy include Table, ADAF, Text, and
lists of these types, but if the need should arise you can also make your own
data type.

Please keep in mind that this is an advanced operation that is not needed for
most users. Furthermore:

- Nodes can only be connected to other nodes that use the same data type. So a
  node using your own data type can only be connected to other nodes that use
  your own data type.
- Do not duplicate functionality for several different data types. For example
  Select rows operation should probably only exist for Table.
- Create paths to and from Table or some other native data type so people using
  your nodes can still benefit from the standard library and any third party
  libraries using the standard data types. See :ref:`working_with_adafs` for an
  example.

By following this guide, you should be able to create a new composite data type
out of the existing fundamental data types in sympathy. An example of such a
data type is the ADAF. Even many types of data which are not most naturally
represented as a hierarchical collection of tables can be created in this
fashion. For example an array type could be created by using a single table and
building a specialized and more restrictive typeutil interface. Even the
ubiquitous Table can be said to be a composite data type as it is a wrapper
around the more fundamental sytable type.


.. _create_type_alias:

Create typeutils class
^^^^^^^^^^^^^^^^^^^^^^
Creating a new type, requires subclassing ``sympathy.api.typeutil.TypeAlias``
and wrapping the class in the ``sympathy.api.typeutil.typeutil`` decorator.

The TypeAlias class has the following API:

.. autoclass:: sympathy.api.typeutil.TypeAlias
   :noindex:
   :members: viewer, icon, names, source, sync, __deepcopy__, init

This is the only mandatory step towards creating your own data type. Create a
new Python file anywhere in the package inside the *Common* folder of your
library. Name it as your data type, all lower case. In our example we will place
the file at *boblib/Common/boblib/twin_tables.py*. Open your new file and add a
TypeAlias subclass called ``File`` wrapped in the typeutil decorator. Use the
method ``init`` to do any initialization.

.. code-block:: python

    import os
    from sympathy.api import typeutil
    # Full path to the directory where this file is located.
    _directory = os.path.abspath(os.path.dirname(__file__))


    @typeutil.typeutil('sytypealias twin_tables = (first: table, second: table)')
    class File(typeutil.TypeAlias):
        """Twin tables."""

        def init(self):
            self.first = self._data.first
            self.second = self._data.second

        @classmethod
        def viewer(cls):
            from . import twin_tables_viewer
            return twin_tables_viewer.TwinTablesViewer

        @classmethod
        def icon(cls):
            return os.path.join(_directory, 'port_twin_tables.svg')

The argument to the decorator is the declaration of your data type. It can
contain a combination of basic data types (such as ``sytable`` or ``sytext``)
other composite types (such as ``adaf`` or ``table``), and container types
(``sylist``, ``sydict``, and ``syrecord``).

``sylist``
  Create a list of elements by surrounding the name of a type in brackets. For
  example ``[adaf]``.

``sydict``
  Create a dictionary of elements by surrounding the name of a type in curly
  braces. For example ``{sytable}``.

``syrecord``
  A record contains a few fixed elements. Create a record by surrounding
  key-value pairs with parenthesis. For example ``(projects: sytable,
  coffee_budget: sytable)``. The values must all be valid types and the keys
  must all be valid python identifiers. As seen in the example above the
  elements are available as attributes of the record.

The instance variable ``self._data`` will contain the declared data structure.
Where applicable, stuff in ``self._data`` will be wrapped in the correct
typeutil class. In the above example the tables will be wrapped in the
typeutils class :class:`typeutils.table.File`, but if the declared type had
been ``'(first: sytable, second: sytable)'``, the tables would be bare
:class:`types.sytable` objects and not wrapped in the typeutils class.

The typeutil class should contain any interface to the data that you want to
expose to nodes working with this data type. In our example the interface is
simply two instance variables called ``first`` and ``second``, but for example
the typeutils class for the table type defines many methods for reading and
writing data and the ADAF typeutil even defines several additional classes.

Locate port type
^^^^^^^^^^^^^^^^

In order for the type to be fully usable, Sympathy needs to be able to locate it.
It is located using a function called library_types() that should be present in
the __init__.py file of your package under Common.

Example from the standard library:

.. code-block:: python

    # Filename Library/Common/sylib/__init__.py

    import sympathy.api

    def library_types():
        return [
            sympathy.api.adaf.File,
            sympathy.api.datasource.File,
            sympathy.api.figure.File,
            sympathy.api.report.File,
            sympathy.api.table.File,
            sympathy.api.text.File,
        ]

For TwinTables it would look something like::

    # Filename boblib/Common/boblib/__init__.py

    from . import twin_tables

    def library_types():
        return [twin_tables.File]


Create port type
^^^^^^^^^^^^^^^^
This step is not strictly necessary but will make it easier to create nodes
that use your data type. Add a new port type function to the same file as your
typeutils class. It should be similar to the static methods of the ``Port``
class of ``utils.port``.

Example:

.. code-block:: python

    from sympathy.utils import port


    def TwinTables(description, name=None):
        return port.CustomPort('twin_tables', description, name=name)

Create an example node
^^^^^^^^^^^^^^^^^^^^^^
Create a node that uses the new port type:

.. code-block:: python

    import numpy as np

    from sympathy.api import node as synode
    from sympathy.api.nodeconfig import Ports

    from boblib.twin_tables import TwinTables


    class TwinTablesExample(synode.Node):
        """
        Outputs a twin table with one column in the first table with values 1-99.
        """
        name = 'Twin tables example'
        description = 'Outputs a twin table with one column in first table with values 1-99.'
        icon = 'example.svg'

        nodeid = 'org.sysess.sympathy.examples.twintablesexample'
        author = 'Magnus Sanden <magnus.sanden@combine.se>'
        copyright = '(c) 2014 System Engineering Software Society'
        version = '1.0'

        outputs = Ports([TwinTables('Output', name='port1')])

        def execute(self, node_context):
            """Execute node"""
            tablefile = node_context.output['port1'].first
            data = np.arange(1, 101, dtype=int)
            tablefile.set_name('Output Example')
            tablefile.set_column_from_array('Enumeration', data)

Look at the data on the out port by right-clicking on it and choosing *Copy
File Path To Clipboard* and pasting the path into HDF5View.

Adding an icon
^^^^^^^^^^^^^^
To customize your new type by adding an icon, first create an svg icon for
TwinTables. See the icons in *Sympathy/Gui/Resources/icons/ports* for more
details about what the platform icons look like.

Icons should have a width and height of 16. Use an existing platform icon as
a template if you are uncertain. If this criteria is not met, the icon will be
scaled and cropped to a width and height of 16 automatically.

Once the icon is created, copy it to *boblib/Common/boblib/port_twin_tables.svg*.
The free software Inkscape can be used to create the icons.

Extend the data viewer
^^^^^^^^^^^^^^^^^^^^^^
To be able to view the data on ports of type twin_tables, a new viewer needs to
be created.

Add a module called *twin_tables_viewer.py* to
*boblib/Common/boblib/twin_tables_viewer.py* with the following code:

.. code-block:: python

    import PySide.QtGui as QtGui

    from sympathy.api import table
    from sympathy.api.typeutil import ViewerBase


    class TwinTablesViewer(ViewerBase):
        def __init__(self, data=None, console=None, parent=None):
            super(TwinTablesViewer, self).__init__(parent)

            TableViewer = table.File.viewer()
            self._table1_viewer = TableViewer()
            self._table2_viewer = TableViewer()

            layout = QtGui.QVBoxLayout()
            layout.addWidget(self._table1_viewer)
            layout.addWidget(self._table2_viewer)
            self.setLayout(layout)

            self.update_data(data)

        def data(self):
            return self._data

        def update_data(self, data):
            self._data = data
            if data is not None:
                self._table1_viewer.update_data(data.first)
                self._table2_viewer.update_data(data.second)
