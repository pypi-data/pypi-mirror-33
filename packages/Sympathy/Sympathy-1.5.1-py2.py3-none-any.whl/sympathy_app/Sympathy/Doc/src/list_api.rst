.. _listapi:

sylist API
==========

sylist is the builtin datatype in sympathy used for representing lists. A list
is an ordered sequence of elements with the same type.

If the port type of a node contains [] the resulting port will contain list type
data. Some port constructors have special names like: Tables which simply
translates to [Table].

There are three different modes which determine the operations that can be used:
Normal, Read through and Write through.

Normal
^^^^^^

Normal sylists are unconnected to any file and are cached in memory.
All operations are allowed.


Read through
^^^^^^^^^^^^

Used for port inputs to nodes whose outer type is of list type.
Only read operations are allowed and no cache is used.

Read through mode helps to reduce memory use.


Write through
^^^^^^^^^^^^^

Used for port outputs of nodes whose outer type is of list type.
Only write operations are allowed and no cache is used.
Write operations take place immediately after, for example, append or extend
and cannot be undone.

Write through mode helps to reduce memory use.


.. class:: sylist(container_type)

   Container type, for example, ``sympathy.api.types.from_string('[table]')``,
   this determines the type of content allowed. Note that container type
   includes the type of the list itself.

    .. method:: create()

       Return a new, normal, sylist, not connected to any file.
       The same container type is used for the new sylist.

    .. method:: append(item):

       Append an item.

    .. method:: extend(other_list):

       Extend with elements from other sylist

    .. method:: source(other, shallow=False):

       Fill with elements from other sylist.

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

    .. method:: __delitem__(index):

       Remove item at index.

    .. method:: __repr__(self):

       Return string representation.
