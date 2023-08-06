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

.. _higher_order_functions:


.. _lambda_function:

Lambda
-------
A Lambda is like a subflow but when executing it the nodes inside are not executed directly.
Instead they are packaged into a data type that is sent to the output port on the outside of
the Lambda to be executed at a later time.

Lambdas can be used to reduce duplication, to work with nested lists, and allow
for conditional execution of nodes. They are created by right-clicking on an empty area of a
workflow and choosing *Create Lambda*. To execute the contents of the Lambda use either
:ref:`Apply` or :ref:`Map`.

A Lambda has only a single output on the outside. The type of the
output is a function with argument types depending on the types connected to
the input ports on the inside. Like with any other data type the output from
Lambda can be used with any nodes that handle generic types, such
as list or tuple operations.

If input data is needed to properly configure the Lambda, the input ports can be
shown on the outside of the Lambda by right-clicking on an input port and selecting *Show Input
Port -> Port[n]*. These ports can then be used to connect data to be used for
configuration.

Some advanced use cases are also possible using Lambdas, for example putting Lambdas in lists
to be executed using a :ref:`Map`.

See also the nodes :ref:`Extract Lambdas` and :ref:`Extract Flows as Lambdas`
for a way to import Lambda functions from workflow files.
