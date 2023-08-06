.. _tupleapi:

sytuple API
===========

sytuple is the builtin datatype in sympathy used for representing tuples. A tuple is
an ordered container type whose the elements can be of different
types. For example, (table, text) is the data type for a two element tuple
representing a pair of a table and a text.

If the port type of a node contains (,) the resulting port will contain
tuple type data.

.. class:: sytuple(container_type)

   Container type, for example, ``sympathy.api.types.from_string('(table, text)')``,
   this determines the type of content allowed. Note that container type
   includes the type of the tuple itself.

    .. method:: create()

       Return a new sytuple, not connected to any file.
       The same container type is used for the new sytuple.

    .. method:: source(other, shallow=False):

       Fill with elements from other sytuple.

    .. method:: __copy__():

       Return a shallow copy.

    .. method:: __deepcopy__(memo=None):

       Return a deep copy.

    .. method:: __len__(self):

       Return the length.

    .. method:: __getitem__(index):

       Return item at index.

    .. method:: __setitem__(index, item):

       Set item at index.

    .. method:: __iter__(self):

       Return iterator of contained items.

    .. method:: __repr__(self):

       Return string representation.
