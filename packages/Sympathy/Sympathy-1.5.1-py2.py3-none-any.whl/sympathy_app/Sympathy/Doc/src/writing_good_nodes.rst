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

How to create reusable nodes
============================

Follow these simple guidelines to make sure that your node is as reusable as
possible.

- Break down the task into the smallest parts that are useful by themselves and
  write nodes for each of those, instead of writing one monolithic "fix
  everything" node. Take some inspiration from the Unix philosophy; every node
  should "do only one thing, and do it well".
- Try to work on the most natural data type for the problem that you are trying
  to solve. When in doubt go with Table since it is the simplest and most
  widely applicable data type.
- Do not hard code site specific stuff into your nodes. Instead add
  preprocessing steps or configuration options as needed.
- Add documentation for your node, describing what the node does, what the
  configuration options are, and whether there any constraints on the input
  data.
- When you write the code for your node, remember that how you write it can
  make a huge difference. If others can read and easily understand what your
  code does it can continue to be developed by others. As a starting point you
  should try to follow the Python style guide (PEP8_) as much as possible.

.. _PEP8: http://legacy.python.org/dev/peps/pep-0008/

If your nodes are very useful and do not include any secrets you may be able to
donate it to SysESS_ for inclusion in the standard library. This is only
possible if the node is considered reusable.

.. _SysESS: http://www.sysess.org


Add extra modules to your library
---------------------------------
If your node code is starting to become too big to keep it all in a single file
or if you created some nice utility functions that you want to use in several
different node files you can place them in the subfolder to the folder *Common*
that we created way back in :ref:`library_structure`. But first we need to make
a package out of that subfolder by placing an empty *__init__.py* file in it::

    > touch boblib/Common/boblib/__init__.py

Now you can add modules to the package by adding the python files to the folder::

    > spyder boblib/Common/boblib/mymodule.py

The *Common* folder will automatically be added to ``sys.path`` so you will now
be able to import modules from that package in your node code::

    from boblib import mymodule
