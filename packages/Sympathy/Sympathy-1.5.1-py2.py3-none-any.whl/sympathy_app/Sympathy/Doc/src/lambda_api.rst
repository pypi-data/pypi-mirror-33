.. _lambdaapi:

sylambda API
============

sylambda is the builtin datatype in sympathy used for representing lambdas. A lambda
is a pure function with arguments constructed using the special Lambda (subflow) or 
Extract * Lambdas nodes.

If the port type of a node contains -> the resulting port will contain lambda type
data. 


.. class:: sylambda(container_type)

   For use in Map and Apply nodes only. All methods and fields can be considered internal
   and shall not be accessed in third party nodes.
