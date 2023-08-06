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

Debugging, profiling, and tests
===============================
Sympathy offers a few tools that will help you fix problems in your nodes,
notably interactive debugging and profiling.


Debugging nodes
---------------

.. _spyder_debug:

Debugging nodes using Spyder
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When a node is not working as expected a very handy tool to use is the node
debugger. Run a workflow up and to the node that you want to debug. Right-click
the node and choose "Debug" from the context menu.

This will bring up Spyder with the node with correct data on the input ports,
ready to be debugged simply by setting a breakpoint and pressing "play". After
running the code at least once you will also have access to the node's
``node_context`` in the interactive python prompt under the name ``dnc`` (short
for *debug node context*). See :ref:`node_context` for information on how to
use the ``dnc`` variable.

Please refer to the `Spyder manual`_ for more info on it's debugging features.

.. _`Spyder manual`: https://pythonhosted.org/spyder/debugging.html


Debugging nodes using PyCharm
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

PyCharm is an external IDE (not included in Sympathy) that can be used as
an alternative to Spyder.


https://www.jetbrains.com/pycharm/



.. _profiling:

Profiling nodes and workflows
-----------------------------
If your node or workflow is running too slow you can run the profiler on it to
see what parts are taking the most time. If you have configured Graphviz, see
:ref:`conf_gv`, you will also get a call graph.

To profile a single node simply right-click on a node that can be executed and
choose *Profile*. This will execute the node and any nodes before it that need
to be executed, but only the node for which you chose *Profile* will be
included in the profiling. To profile an entire workflow go to the *Controls*
menu and choose *Profile flow*. This will execute all nodes in the workflow
just as via the *Execute flow* command. After either execution a report of the
profiling is presented in the *Messages* view. Profiling of single subflows is
similar to profiling of single nodes but include all the executable nodes in
the subflow.

The profile report consists of a part called *Profile report files* and a part
called *Profile report summary*.


Profile report files
^^^^^^^^^^^^^^^^^^^^
The *Profile report files* part of the profile report consists of two or four
file paths. There is always a path to a txt file and a stats file, and also two
pdf files if Graphviz is configured, see :ref:`conf_gv`. The txt file is a more
verbose version of the summary but with full path names and without any limit on
the number of rows. The first pdf file contains a visualization of the
information in the summary, also called a call graph, and the second a call graph
of flows and nodes.

The function call graph contains a node for each function that has been called
in the profiled code. The color of the node gives you a hint about how much of
the total time was spent inside a specific function. Blue nodes represent
functions with low total running time and red nodes represent functions with
high total running time. The nodes have the following layout:

.. figure:: call_graph.png
   :scale: 100 %
   :alt: Part of a call graph produced by Sympathy's profiler.

First row is the name of the function. Second row is the percentage of the
running time spent in this function and all its children. Third row (in
parentheses) is the percentage of the running time spent in this function
alone. The forth row is the total number of times this function was called
(including recursive calls).

The edges of the graph represent the calls between functions and the label at
an edge tells you the percentage of the running time transferred from the
children to this parent (if available). The second row of the label tells you
the number of calls the parent function called the children.

Please note that the total running time of a function has to exceed a certain
cut-off to be added to the call graph. So some very fast workflows can produce
almost empty call graphs.

A third file will also always be provided with the file ending ".stats". This
file contains all the statistics that was used to create the summary and the
call graph. To begin digging through this file open a Python interpreter and
write::

  >>> import pstats
  >>> s = pstats.Stats('/path/to/file.stats')
  >>> s.print_stats()

For more information look at the documentation for the `Stats`_ class.

.. _Stats: https://docs.python.org/2/library/profile.html#the-stats-class


Profile report summary
^^^^^^^^^^^^^^^^^^^^^^
The summary contains a row for each function that has been called in the
profiled code. Several calls to the same function are gathered into a single
row. The first column tells you the number of times a function has been called.
The next four columns measure the time that it took to run a specific function.
In the last column you can see what function the row is about. See
https://docs.python.org/2/library/profile.html for details on how to interpret
this table.

The summary also includes up to 10 node names from nodes included in the
profiling and an indication of the number of nodes that were ommited to save
space.


.. _`conf_gv`:

Configuring Graphviz
^^^^^^^^^^^^^^^^^^^^
For the call graph file to be generated Graphviz will have to be installed and
the path to the bin folder which contains dot will have to be in either PATH or
*Graphviz install path* in Debug Preferences. Visit http://www.graphviz.org to
obtain a copy of Graphviz.

.. figure:: graphviz_setting.png
   :scale: 50%
   :alt: Setting GraphViz path in preferences.


.. _lib_tests:

Writing tests for your nodes
----------------------------
As with any other code, writing tests for your nodes is a good way of assuring
that the nodes work and continue to work as you expect.

Let us start by running the following command from a terminal or command prompt:

.. code-block:: bash

    python launch.py tests

This will run an extensive test suite on the sympathy platform and on all
configured libraries. It tests that the documentation for all nodes can be
generated without any errors or warnings and that the configuration GUIs for
all nodes can be created. But it does not run the node.


Test workflows
^^^^^^^^^^^^^^
The easiest way to test the execution of your nodes is to add them to a
workflow and put that workflow in *<library path>/Test/Workflow/*. All
workflows in that folder and subfolders are automatically run when running the
above command.

Look in *<sympathy folder>/Library/Test/Workflow/* for examples of such test
workflows.


Unit tests
^^^^^^^^^^
It is also a good idea to write unit tests to ensure the quality of your
modules. Put unit test scripts in *<library path>/Test/Unit/*. If the tests are
named correctly they will automatically be found by the Python module ``nose``.
Which is run as a part of ``launch.py tests``. See
https://nose.readthedocs.org/en/latest/finding_tests.html for more details
about how to name your unit tests.

For example a unit test script that tests the two functions :func:`foo` and
:func:`bar` in the module :mod:`boblib.bobutils` could be called
*test_bobutils.py* and look something like this::

    import numpy as np
    from nose.tools import assert_raises

    import boblib.bobutils


    def test_foo():
        """Test bobutils.foo."""
        assert boblib.bobutils.foo(1) == 2
        assert boblib.bobutils.foo(0) == None
        with assert_raises(ValueError):
            boblib.bobutils.foo(-1)


    def test_bar():
        """Test bobutils.bar."""
        input = np.array([True, False, True])
        expected = np.array([False, False, True])
        output = boblib.bobutils.bar(input)
        assert all(output == expected)

For more examples of real unit tests take a look at the scripts in *<sympathy
folder>/Library/Test/Unit/* or have a look at the documentation for the
``nose`` module at https://nose.readthedocs.org/.

You can run only the unit tests of your own library by running the following
command from a terminal or command prompt:

.. code-block:: bash

    python launch.py tests <library path>/Test/Unit
