.. This file is part of Sympathy for Data.
..
..  Copyright (c) 2015 System Engineering Software Society
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

.. _interactive_mode:


Using library nodes from python
-------------------------------

If you want to work with Library nodes from python code, use the interactive
module. The interactive module is intended for experimentation, scripting, and
test and aims to make it convenient to work in IPython or similar.

The code example below demonstrates how to load the interactive module.

.. code-block:: python

   from Gui import interactive

Interactive relies on sympathy.api in order to produce port data such as ADAF or Table,
but using sympathy.api explicitly is not required.


Loading the Library
^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from Gui import interactive

   library = interactive.load_library()

``load_library`` may produce warnings similarly to the ones produced when
running Sympathy for Data as GUI or CLI.

Loading nodes
^^^^^^^^^^^^^

When the Library has been loaded you are ready to begin loading nodes. The nodes
can be loaded by nodeid or name and if no match is found the method will also
attempt to do a fuzzy match of the provided name. If more than one node is
matched, then a ``KeyError`` is produced listing which nodes that match the
given name. Matching the node name is often good enough, it should certainly be
unique within a library and is easy to read compared to the full nodeid.

.. code-block:: python

   random_table = library.node('Random Table')


Working with configurations
^^^^^^^^^^^^^^^^^^^^^^^^^^^

There are two different ways of configuring nodes: graphical and
programmatic. When working interactively it is often a good start to use the
graphical interface, the programmatic interface is more useful for automation
and tests. Some nodes have very complex configurations that can be hard to get
right and, for those cases, the graphical interface is recommended.

Graphical interface
"""""""""""""""""""

The code example below demonstrates how to launch the configuration GUI for a
Random Table node. The node remembers its configuration and the changes will
have effect when the node is executed and in other cases when its configuration
is used.

.. code-block:: python

   random_table = library.node('Random Table')
   random_table.configure()


Programmatic interface
""""""""""""""""""""""

The code example below demonstrates how to set the column_entries attributes of a
Random Table node to the value 3. This change will make the node produce 3
random columns of the default column_length which is 1000, when executed.

.. code-block:: python

   random_table = library.node('Random Table')
   random_table.parameters.attributes.column_entries.value = 3

The parameters, when accessed via attributes, have a similar interface
node_context.parameters wrapped in sympathy.api.parameters or ParameterRoot, but
allows you to index the elements using dot notation. This way is more convenient when
used from the CLI since it allows for code completion. If you instead wish to
work with the same interface as is used by nodes, then use random_table.parameters.data.

Working with nodes
^^^^^^^^^^^^^^^^^^

Nodes store the changes made during configure and when the parameters are
changed. They produce a list of data elements when executed and expect a list of
data elements as input, this makes it possible to easily connect the data
between nodes. Note that the ordering of inputs and outputs is important and
should match the declaration order in the node definition.

The code example below demonstrates how to use the result produced by one node as
input for another.

.. code-block:: python

   random_table = library.node('Random Table')
   rt_output = random_table.execute()

   table_to_tables = library.node('Table to Tables')
   ttt_output = table_to_tables.execute(rt_output)

   assert(ttt_output[0][0] == rt_output)

The code example below demonstrates how to use the result produced by multiple
nodes as input for another.

.. code-block:: python

   random_table0 = library.node('Random Table')
   rt_output0 = random_table.execute()

   random_table1 = library.node('Random Table')
   rt_output1 = random_table.execute()

   vjoin_table = library.node('VJoin Table')
   vj_output = vjoin_table.execute(rt_output0 + rt_output1)
