.. _recordapi:

syrecord API
============

syrecord is the builtin datatype in sympathy used for representing records. A record is
an container type of named elements whose the elements can be of different
types. For example, (x:table, y:text) is the data type for a two element record
representing a pair of a table and a text; the table being named x and the text y.

If the port type of a node contains (:,) the resulting port will contain
record type data.

.. class:: syrecord(container_type)

   Container type, for example, ``sympathy.api.types.from_string('(x:table, y:text)')``,
   this determines the type of content allowed. Note that container type
   includes the type of the record itself.

    .. method:: create()

       Return a new syrecord, not connected to any file.
       The same container type is used for the new syrecord.

    .. method:: source(other, shallow=False):

       Fill with elements from other syrecord.

    .. method:: __copy__():

       Return a shallow copy.

    .. method:: __deepcopy__(memo=None):

       Return a deep copy.

    .. method:: __getattr__(name):

       Return named item.

    .. method:: __setattr__(name, item):

       Set named item.

    .. method:: __iter__(self):

       Return iterator of item names.

    .. method:: __repr__(self):

       Return string representation.
