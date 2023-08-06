.. _dictapi:

sydict API
==========

sydict is the builtin datatype in sympathy used for representing dicts. A dict
is an unordered map of elements with the same type.

If the port type of a node contains {} the resulting port will contain dict type
data.


.. class:: sydict(container_type)

   Container type, for example, ``sympathy.api.types.from_string('{table}')``,
   this determines the type of content allowed. Note that container type
   includes the type of the dict itself.

    .. method:: create()

       Return a new sydict not connected to any file.
       The same container type is used for the new sydict.

    .. method:: source(other, shallow=False):

       Fill with elements from other sydict.

    .. method:: __copy__():

       Return a shallow copy.

    .. method:: __deepcopy__(memo=None):

       Return a deep copy.

    .. method:: __len__(self):

       Return the length.

    .. method:: __getitem__(key):

       Return item with key.

    .. method:: __setitem__(key, item):

       Set item with key.

    .. method:: __iter__(self):

       Return iterator of item keys.

    .. method:: __delitem__(index):

       Remove item at index.

    .. method:: __repr__(self):

       Return string representation.
