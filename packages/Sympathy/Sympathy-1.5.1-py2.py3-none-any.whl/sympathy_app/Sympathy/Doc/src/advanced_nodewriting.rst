.. This file is part of Sympathy for Data.
..
..  Copyright (c) 2010-2012 System Engineering Software Society
..
..     Sympathy for Data is free software: you can redistribute it and/or modify
..     it under the terms of the GNU General Public License as published by
..     the Free Software Foundation, either version 3 of the License, or
..     (at your option) any later version.
..
..     Sympathy for Data is distributed in the hope that it will be useful,
..     but WITHOUT ANY WARRANTY; without even the implied warranty of
..     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
..     GNU General Public License for more details.
..     You should have received a copy of the GNU General Public License
..     along with Sympathy for Data. If not, see <http://www.gnu.org/licenses/>.

.. _advanced_nodewriting:

Advanced node writing
=====================


.. _adjust_parameters:

Adjust parameters
-----------------
Sometimes you want to adjust the configuration parameters to the input data
that your node receives. This is especially useful to update the choices in a
list parameter.

As an example let us consider a node that takes a table as input. The node has
among its parameters a list of all the columns in the input table. In this list
the user can choose which column the node will operate on. To make sure that
the list is always updated when the columns in the input data change, it could
implement ``adjust_parameters`` something like this::

    def adjust_parameters(self, node_context):
        """Update the configuration with current input table columns."""
        synode.adjust(node_context.parameters['chosen_column'],
                      node_context.input['input_port'])

The ``adjust`` function picks up names from the input depending on its data
type. See the ``names()`` method of each :ref:`data type<datatypeapis>`.

This method will be called before opening the GUI, but after
:ref:`update_parameters`. See also :ref:`All parameters example` for other
examples of ``adjust_parameters``.


.. _controllers:

Controllers
-----------
To make the GUI of your nodes easier to use, you can add controllers that
clarify the interconnection between different parameters. Controllers can make
sure that when some option is chosen some other option becomes
available/unavailable. For example::

    from sympathy.api import node as synode


    class HelloWorldNode(synode.Node):
        """Prints a custom greeting to the node output."""

        name = 'Hello world!'
        nodeid = 'com.example.boblib.helloworld'
        author = 'Bob <bob@example.com>'
        copyright = '(C) 2014 Example Organization'
        version = '3.0'

        parameters = synode.parameters()
        parameters.set_boolean(
            'use_custom_greeting',
            value=False,
            label='Use custom greeting',
            description='While unchecked the node will always print '
                        '"Hello World!" ignoring any custom greeting.')
        parameters.set_string(
            'greeting',
            value='Hello World!',
            label='Greeting:',
            description='Choose what kind of greeting the node will print.')

        controllers = synode.controller(
            when=synode.field('use_custom_greeting', 'checked'),
            action=synode.field('greeting', 'enabled'))

        def execute(self, node_context):
            if node_context.parameters['use_custom_greeting'].value:
                greeting = node_context.parameters['greeting'].value
            else:
                greeting = "Hello World!"
            print(greeting)

By disabling elements of the GUI that are not relevant to the current
configuration you can make the configuration GUI easier to understand.

Each controller can have multiple actions and multiple controllers can be added
by simply wrapping them in a tuple. The code below, which contains multiple controllers, is
not directly compatible with the controller example above::

        controllers = (
            synode.controller(
                when=synode.field('use_regex', state='checked'),
                action=(synode.field('regex_pattern', state='enabled'),
                        synode.field('wildcard_pattern', state='disabled'))),
            synode.controller(
                when=synode.field('use_magic', state='checked'),
                action=synode.field('more_magic', state='enabled')))

For another example of how to use controllers, see :ref:`Controller Example`.


.. _custom_ports:

Using custom port types
-----------------------
Previously we learned how to add input and output ports to your nodes::

    inputs = Ports([Port.Table('Input Table', name='foo')])
    outputs = Ports([Port.Table('Table with some added bar', name='foobar')])

This is the most convenient way to add ports with the most common data types
like Table, Datasource, ADAF, and so on. If you want add a generic type, lambda, or
any other type which does not have its own :class:`Port` method you need to use
the method :meth:`Custom`. As its first argument :meth:`Custom` takes a textual
representation of the port type. The other two arguments are the same as in the
other :class:`Port` methods. The textual representation of the port type can
contain combinations of the following:

* type aliases (e.g. ``adaf`` or ``table``)
* lists (e.g. ``[table]``, meaning a list of tables)
* lambdas (represented as an arrow from input type to output type, e.g. ``table
  -> adaf`` meaning a lambda with ``table`` input and ``adaf`` output)
* generic types (e.g. ``<a>`` meaning any type or ``[<a>]`` meaning a list of
  arbitrary items)

Here are some examples of valid port types:

* ``[table]`` (a list of tables)
* ``[[table]]`` (a list of lists of tables)
* ``adaf -> [adaf]`` (a lambda whose input is an adaf and whose output is a
  list of adafs)
* ``[adaf -> [adaf]]`` (a list of such lambdas)
* ``<a>`` (Any type)
* ``<a> -> <a>`` (a lambda whose output is of the same type as its input)
* ``<a> -> <b>`` (a lambda with arbitrary input and output)
* ``[<a> -> <a>]`` (a list of such lambdas)
* ``(<a>, <a>) -> <b>`` (a lambda where the input is a tuple in which both elements are of the same type)

If you use generic types, all ports with the same identifier (the ``a`` in
``<a>``) have to be of the same type. For example in the node :ref:`Append List`::

    inputs = Ports([Port.Custom('<a>', 'Item', name='item'),
                    Port.Custom('[<a>]', 'List', name='list')])
    outputs = Ports([Port.Custom('[<a>]', 'List', name='list')])

The two input ports can be, for example, Table and [Table], or ADAF and [ADAF], but not
Table and [ADAF]. Another example of this is in the :ref:`Map` node::

    inputs = Ports([
        Port.Custom('<a> -> <b>', 'Lambda Function', name='Function'),
        Port.Custom('[<a>]', 'Argument List', name='List')])
    outputs = Ports([
        Port.Custom('[<b>]', 'Output List', name='List')])

Where the input and output type of the lambda determine what type the other
ports must have. Or, if you connect the other ports first, they determine what
types the lambda's input and output must have.


Port.Custom accepts n as an optional keyword argument to create a range of ports
from the same definition::

    # Exactly 3 ports.
    inputs = Ports([
        Port.Custom('[<a>]', 'Argument List', name='List', n=3)])


    # Minimum of 3 ports with no upper bound, though 6 ports in total is
    # The current limit.
    inputs = Ports([
        Port.Custom('[<a>]', 'Argument List', name='List', n=(3,))])


    # Minimum of 3 ports up to a maximum of 5 ports.
    inputs = Ports([
        Port.Custom('[<a>]', 'Argument List', name='List', n=(3,5))])


    # Minimum of 0 ports up to a maximum of 5 ports, starting out with a
    # default of 2 ports.
    inputs = Ports([
        Port.Custom('[<a>]', 'Argument List', name='List', n=(0,5,2))])

As you can see, n accepts either a single integer or a tuple of up to 3 integer
components: minimum, maximum, and default. When maximum and default are not supplied,
they assume the same value as minimum.

When the n argument is used, a name is also required and all port names need to be
unique. This is a good practice, in general.

In order to make nodes reasonably compatible between different versions of
Sympathy it is important that the default ports remains the same. If the default
ports (which you will get by dragging a new node from the library into a
workflow) change, consider changing the nodeid and start a new node.


.. _update_parameters:

Managing node updates
---------------------
When developing a node over time it is not uncommon that the set of node
parameters change slightly from one version of the node to the next.

Default value (the arguments ``value``, ``value_names``, ``list``, ``plist``)
can always be updated without risk of breaking old workflows. The change simply
wont affect old workflows at all.

As of Sympathy 1.2.5 newly added parameters are automatically added to old
instances of nodes when they are configured, executed and so on. So simply add the
new parameter to the node definition and you can expect the new parameter to
always be there when you reach any node method, such as ``execute``.
As of Sympathy 1.3.0 any changes to the label or description of an existing
parameter are automatically applied to nodes.

If you need more fine-grained control you can implement the node method
``update_parameters(self, old_params)`` (available as of Sympathy
1.2.5). This method can create new parameters where the default value of the
new parameter depends on the value of some of the old parameters. You do this
by making changes to the argument ``old_params``. Any parameters that are still
missing after this method are added automatically from the parameter
definition.

Here is an example of ``update_parameters`` from :ref:`Calculator List`::

    def update_parameters(self, old_params):
        # Old nodes without the same_length_res option work the same way as if
        # they had the option, set to False.
        if 'same_length_res' not in old_params:
            old_params['same_length_res'] = self.parameters['same_length_res']
            old_params['same_length_res']['value'] = False



.. _custom_gui:

Custom GUIs
-----------
For most basic nodes the configuration GUI can be created automatically.
This is very convenient but is of course a bit limited. More advanced nodes
can also choose to implement their own custom configuration GUIs without
such limitations. All GUIs in Sympathy are created using Qt
(http://www.qt-project.org).

To create a custom GUI implement the method ``exec_parameter_view(self,
node_context)`` to return a custom widget which will be run when configuring
the node.

This is probably a good place for an example. Let us continue with the Hello
World example and add a custom GUI in which the user can not only set the
greeting, but also click a button to test it::

    from sympathy.api import node as synode
    from sympathy.api import ParameterView
    from sympathy.api import qt
    
    QtGui= qt.import_module('QtGui')
    
    
    class MyWidget(ParameterView):
        def __init__(self, parameters, parent=None):
            super(MyWidget, self).__init__(parent=parent)
            self._parameters = parameters
    
            greeting_edit = self._parameters['greeting'].gui()
    
            button = QtGui.QPushButton('Test greeting')
            button.clicked.connect(self.test_greeting)
    
            layout = QtGui.QHBoxLayout()
            layout.addWidget(greeting_edit)
            layout.addWidget(button)
            self.setLayout(layout)
    
        def test_greeting(self):
            QtGui.QMessageBox.information(
                self, 'A greeting...', self._parameters['greeting'].value,
                QtGui.QMessageBox.Ok)
    
    
    class HelloWorldNode(synode.Node):
        """Prints a custom greeting to the node output."""
    
        name = 'Hello World!'
        nodeid = 'com.example.boblib.helloworld'
        author = 'Bob <bob@example.com>'
        copyright = '(C) 2014 Example Organization'
        version = '4.0'
    
        parameters = synode.parameters()
        parameters.set_string(
            'greeting',
            value='Hello World!',
            label='Greeting:',
            description='Choose what kind of greeting the node will print.')
		    
    
        def exec_parameter_view(self, node_context):
            return MyWidget(node_context.parameters)
    
        def execute(self, node_context):
            greeting = node_context.parameters['greeting'].value
            print(greeting)

The editors/widgets created in the parameter definition can also be used in a
custom GUI, but one has to add them to the layout one by one, as it is done
with regular Qt widgets. The benefit of using widgets defined in the parameter
definition, is that the signals emitted from the widgets are taken care of, and
the parameters are updated automatically when the user makes changes in the
GUI.

If one has created a list of parameters with the name ``'combo_example'``,
the command to access its editor widget would look like::

    example_combo = self._parameters['combo_example'].gui()

Since the user might decide to open the GUI even when there is no data
ready on the input ports (e.g. when no node has been connected to the input
port), we need to check that there actually is data ready on that port before
using it. To test if the input data is available you can use the method
:meth:`is_valid` on the port. If it returns ``True`` you can safely use the
input data. 

If the widget keeps an internal model of the parameters it should define a
method called ``save_parameters`` which updates ``node_context.parameters``.
