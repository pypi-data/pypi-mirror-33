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

.. _batch:

Using Sympathy from the command line
====================================

You can run Sympathy from the command line by running python with *launch.py*
syg or sy and a workflow path as arguments. For the relevant startup options,
see :ref:`start_options`. For more information about *launch.py* see
:ref:`launch_options`. Use the `-h` option to get more information about the
arguments.


Run *Sympathy for Data GUI* on Windows or Unix:

.. code-block:: bash

   python launch.py syg


Run *Sympathy for Data CLI* on Windows or Unix:

.. code-block:: bash

   python launch.py sy filename


On Windows it is often useful to launch Sympathy in this way, using python.exe
instead of pythonw.exe to get terminal output. If you also have access to
RunSympathyGUI.exe and RunSympathyCLI.exe that we bundle with our installers
they can be used to run *Sympathy for Data*. These two basically run
*pythonw.exe launch.py syg* and *python.exe launch.py sy* respectively.


Run *Sympathy for Data GUI* on Windows:

.. code-block:: bat

   RunSympathyGUI.exe


Run *Sympathy for Data CLI* on Windows:

.. code-block:: bat

   RunSympathyCLI.exe filename


On Unix syg.sh and sy.sh provide the same convenience.


Run *Sympathy for Data GUI* on UNIX:

.. code-block:: bat

   ./syg.sh


Run *Sympathy for Data CLI* on UNIX:

.. code-block:: bat

   ./sy.sh filename


.. _start_options:

Sympathy Start options
----------------------
``--loglevel=X`` or ``-LX``
  Set log level to X which should be a number between 0 and 5 inclusive. 0
  means no logging and higher number corresponds to more verbose logging. The
  log is printed to standard output.

``--node-loglevel=X`` or ``-NX``
  Set node log level to X which should be a number between 0 and 5 inclusive. 0
  means no logging and higher number corresponds to more verbose logging. The
  node log is printed to standard output.

``--configfile <FILELIST>`` or ``-C <FILELIST>``
  Use config files from comma separated <FILELIST>. See :ref:`config_files` for
  more info about config files.

``--inifile INIFILE`` or ``-I INIFILE``
  Specify preferences file.

``--exit-after-exception {0,1}``
  If set to 1, exit after uncaught exception occurs in a signal handler. 1 is
  default for non-GUI execution and 0 is default for GUI.

``--num-worker-processes N``
  Specifies the number worker processes that Sympathy uses. 0 means
  that the system's default number of CPUs will be used.

``--generate-documentation``
  Generate documentation files for Sympathy.

``--nocapture``
  Write output directly to stdout and stderr without platform
  interception. Useful for debugging.

``--benchmark=filename``
  Generate an HTML report of the execution to filename. Use this option together
  with -L5 and -N5 to get as much information as possible.

``--help`` or ``-h``
  Print usage message and exit.

``--version`` or ``-v``
  Show the version of Sympathy for Data.


.. _launch_options:

launch.py Start options
-----------------------

Besides sy and syg, launch.py has a few other options that can be useful.

``sy``
  Run Sympathy for Data CLI. For usable arguments see :ref:`start_options`.

``syg``
  Run Sympathy for Data GUI. For usable arguments see :ref:`start_options`.

``viewer``
  Run Sympathy for Data Viewer. It can be supplied with an optional filename
  argument.

``tests``
  Run all unit tests and test workflows for the sympathy platform and for all
  configured node libraries. See :ref:`lib_tests` for an introduction to
  library tests.

``benchmark``
  Run Sympathy for the Data Benchmark suite. It generates an HTML report
  to supplied filename argument.

``spyder``
  Run Spyder with the environment (PYTHONPATH) set up.

``ipython``
  Run ipython with the environment (PYTHONPATH) set up.

``nosetests``
  Run nose with the environment (PYTHONPATH) set up.

``install``
  Install Sympathy. On Windows, this includes creating file associations
  and start menu entries. This action requires write permissions
  in the folder where Sympathy is installed.

``uninstall``
  Uninstall Sympathy. On Windows, this includes removing file associations
  and start menu entries. This action requires write permissions
  in the folder where Sympathy is installed. Besides the ones previously
  mentioned, uninstall does not remove any files. To perform a full uninstall
  of Sympathy installed in a python environment, afterwards, run
  `python -m pip uninstall Sympathy`.
  
``nosetests``
  Run nose with the environment (PYTHONPATH) set up.

``clear``
  Clear up cache files, session files and other files generated by Sympathy.


``--help`` or ``-h``
  Print usage message and exit.


.. _env_vars:

Using environment variables
---------------------------
Environment variable expansion is useful in node configurations where the node
should behave differently depending on the environment where it is executed.
A simple example would be a workflow that always loads a certain file from the
current user's home directory. To achieve that you can simply configure a
:ref:`Datasource` node to point to *$(HOME)/somefile.txt* and it will point to
the file *somefile.txt* in the user's home directory.

Apart from using already existing OS environment variables you can also add
your own environment variables at four different levels: OS/shell, local
config, workflow, and global config. Local config or workflow level variables
are generally preferred as they do not risk affecting workflows that they
should not affect.

.. _default_workflow_vars:

Default workflow environment variables
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
A few variables are always defined in every workflow. ``$(SY_FLOW_FILEPATH)``
holds the full path to the workflow file, and ``$(SY_FLOW_DIR)`` contains the
directory of the workflow file. These variables behave just like normal workflow
variables, but they are not stored in a syx-file. Instead they are computed on the
fly when they are used. Check properties for a flow to see what values these
variables have for that flow.

.. _shell_vars:

Adding OS/shell environment variables
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Setting environment variables or shell variables is done differently depending
on operating system, version, shell, and so on. As an example let us set the shell
variable ``GREETING`` and start Sympathy in a command prompt in Windows::

    > set GREETING=Hi!
    > RunSympathyGUI.exe

.. TODO : Write about OSX and linux?

Add a :ref:`Hello world Example` node and configure it to display
``$(GREETING)``. Run the node. The output should be *Hi!*.

Adding environment variables via local config files
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
When starting Sympathy with one or more :ref:`config files <config_files>`
specified you can set environment variables in those config files. Simply add
lines like this to the config file::

    $(GREETING) = "Yo!"

.. _flow_vars:

Adding workflow environment variables
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Workflow level environment variables can be added and removed via the
preferences GUI. Right click in your flow and click *Properties* and go to the
tab *Environment variables*, where you can add, change, and remove workflow
variables. These variables are stored in the workflow file, and will only
affect that workflow, and its subflows. A subflow can always override a
variable set by one of its parent flows.

Adding environment variables to the global config file
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Just as workflow level variables, global config variables can be added and
edited under *File*->*Preferences...*->*Environment*, but they are stored in
the global config file for Sympathy so they affect all workflows.

Priority
^^^^^^^^
In case of name conflicts, environment variables are looked up in the following
order:

1. OS/shell
2. Local config files
3. Workflow (defined in current subflow)
4. Workflow (defined in a parent workflow)
5. Global config file


.. _`config_files`:

Using config files
------------------

.. warning::

   This functionality is now deprecated, please do not use it unless there is no
   other alternative.

   Using the configuration port together with some normal input should be
   possible in most cases. See :ref:`configuration_port`.  Support for config
   files will be removed in Sympathy version 1.6.0 and later.


Examples
^^^^^^^^

Config files can be used to set environment variables and for directly changing
node config parameters.

Here is an example config file::

    alias helloworld = {1679abf7-2fb9-4453-9b45-a7eb61b670ed}
    helloworld.parameters.greeting.value = "Howdy!"

The crazy string of numbers and characters on the first line is a node UUID.
This uniquely identifies a single node in a workflow. The alias command is used
to give the node a more human-readable name that can be used throughout the
rest of the config file. To find the UUID of a node right click on it and
choose *Info*.

When setting strings with non-ASCII characters note that the config file should
always be encoded using utf8::

    alias helloworld = {1679abf7-2fb9-4453-9b45-a7eb61b670ed}
    helloworld.parameters.greeting.value = "Grüß Gott!"

Or use escape sequences for any non-ASCII characters::

    alias helloworld = {1679abf7-2fb9-4453-9b45-a7eb61b670ed}
    helloworld.parameters.greeting.value = "Gr\u00FC\u00DF Gott!"

When changing parameters in parameter groups or parameter pages write the full
path to the parameter. The following example changes the parameters of an
:ref:`All parameters example` node::

    alias allparameters = {9cc8b9b8-bcc5-4218-8bb4-13cf1e249626}
    allparameters.parameters.numbers.float.spinfloat.value = 0.005
    allparameters.parameters.logics.boolflag.value = false
    allparameters.parameters.strings.lineedit.value = "some string"

All values must be valid JSON, which for instance means that ``true`` and
``false`` are lower case.

When using multiple config files in the same call the last config file has
highest priority and the first one has the lowest priority::

    > RunSympathyGUI.exe flow.syx -C low_prio.cfg,high_prio.cfg

You can also add environment variables to your config files using the following
syntax::

    $(GREETING) = "Good day!"

Environment variables defined in config files have precedence over workflow
specific and global variables. For more info on environment variables see
:ref:`env_vars`.

Whenever you start Sympathy with a config file the flow that you open will be
copied to a temporary location and modified according to the config file. This
means that any relative paths in the flow or in the config file will be
relative to this temporary location instead of being relative to the original
workflow. So when using relative paths in conjunction with config files you
should always add an output workflow filename to the command::

    > RunSympathyGUI.exe flow.syx -C rel_paths.cfg output_flow.syx

Then the workflow *flow.syx* will be copied to *output_flow.syx* instead of a
default temporary location and you can use paths relative to the output
workflow path. Note that the output workflow will be mercilessly overwritten
each time you run the command above.
