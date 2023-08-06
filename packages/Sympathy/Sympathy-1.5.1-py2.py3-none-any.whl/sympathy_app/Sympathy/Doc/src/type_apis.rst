.. _datatypeapis:

Data type APIs
==============
Sympathy stores data internally as a few different data types.
Learning how to use the APIs for those data types is essential when writing
your own nodes or when using the :ref:`F(x) nodes <F(x)>`.


Built in Types
^^^^^^^^^^^^^^

The built in types are all subclasses of sygroup:

.. class:: sygroup(container_type)

   Abstract base class for builtin types. 

    .. method:: create()

       Return a new sygroup, not connected to any file.
       The same container type is used for the new sygroup.

    .. method:: source(other, shallow=False):

       Fill with elements from other sygroup.

    .. method:: __copy__():

       Return a shallow copy.

    .. method:: __deepcopy__(memo=None):

       Return a deep copy.


Methods and fields that are not documented can be considered internal and should not
be used in third party nodes.

The following builtin container types are available.

.. toctree::
   :maxdepth: 2

   dict_api.rst
   lambda_api.rst
   list_api.rst
   record_api.rst
   tuple_api.rst


Built in TypeAliases
^^^^^^^^^^^^^^^^^^^^

The built in typealiases are all subclasses of TypeAlias:

.. autoclass:: sympathy.api.typeutil.TypeAlias
   :members: viewer, icon, names, source, sync, __deepcopy__, init

Methods and fields that are not documented can be considered internal and should not
be used in third party nodes.

The following builtin type aliases.

.. toctree::
   :maxdepth: 2

   table_api.rst
   adaf_api.rst
   dsrc_api.rst
   text_api.rst
   plot_api.rst
   json_api.rst



Other data types
^^^^^^^^^^^^^^^^

.. toctree::
   :maxdepth: 2
   
   matlab_api.rst
