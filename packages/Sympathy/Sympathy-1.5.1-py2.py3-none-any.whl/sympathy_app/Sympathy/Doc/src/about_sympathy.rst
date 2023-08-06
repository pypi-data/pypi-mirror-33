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

What is Sympathy for Data?
==========================
Sympathy for Data is a framework for automation of data analysis. It is free
software and is built as a layer on top of the powerful programming language:
Python.

When working in Sympathy you build *workflows*. Workflows are both visual
presentations of the steps that need to be taken in order to perform your
specific data analysis task, but under the surface it also contains all the
code necessary to perform that data analysis. This makes the actual process
more transparent.

It allows for different user groups to use the tool in different ways. Some
will simply run existing workflows, others will create workflows or modify
existing ones, and yet others will create nodes, the components that are
used to build workflows.

Sympathy is built to encourage reuse and sharing at all levels. Nodes use a few
standardized data types to ensure that they will work well together. Parts of
workflows can be split into modular *linked subflows* and reused in other
workflows. And as a natural step, Sympathy for Data and its standard library are
both free software, distributed under `GPL`_ and `BSD`_ licences respectively.

.. _GPL: http://www.gnu.org/copyleft/gpl.html
.. _BSD: http://opensource.org/licenses/BSD-3-Clause

Sympathy is built on top of a powerful stack of technologies for doing
scientific computing.

.. figure:: sympathy_stack.png
   :alt: Output example and data viewer
   :align: center


.. Why use Sympathy for Data?
.. ==========================
.. - Cross platform.
.. - Free software.
.. - Support available.


.. When to use Sympathy for Data?
.. ==============================
.. - All data is available (not streaming).
.. -
