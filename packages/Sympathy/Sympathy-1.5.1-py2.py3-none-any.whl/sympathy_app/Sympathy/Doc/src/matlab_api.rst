.. _matlabapi:

Matlab API
==========
Class :class:`Table.Table`
---------------------------
.. class:: Table

:module: Matlab.Table

    .. function:: Table.clear()

       Clear the table. All columns and attributes will be removed.

    .. function:: Table.column_names()

        Return a list with the names of the table columns.

    .. function:: Table.column_type(column)

        Return the type of column named ``column``.

    .. function:: Table.number_of_rows()

        Return the number of rows in the table.

    .. function:: Table.number_of_columns()

       Return the number of columns in the table.

    .. function:: Table.is_empty()

        Returns ``True`` if the table is empty.

    .. function:: Table.from_file(filename)

        Load data from file.

        Example::

            >>> in_table = Table();
            >>> in_table = in_table.from_file(infilename);


    .. function:: Table.to_file(filename)

        Write data to file.

        Example::

            >>> out_table = Table();
            >>> out_table = out_table.set_column_from_array('MAX_PRICE',  10, {{}, {}});
            >>> out_table.to_file(outfilename)


    .. function:: Table.set_column_from_array(column, array, attributes)

        Write an array to column named by column_name.
        If the column already exists it will be replaced.

    .. function:: Table.get_column_to_array(column)

        Return named column as a array.

    .. function:: Table.set_name(name)

        Set table name. Use ``''`` to unset the name.

    .. function:: Table.get_name()

        Return table name or ``''`` if name is not set.

    .. function:: Table.get_column_attributes(column)

        Return dictionary of attributes for column_name.

    .. function::  Table.set_column_attributes(column, attributes)

        Set dictionary of scalar attributes for column_name.
        Attribute values can be any numbers or strings but attributes must be cell
        array.
        Example::

            out_table = out_table.set_column_attributes('column_name', {{'attr1', 'attr2'}, {'val1', 'val2'}}

    .. function::  Table.get_table_attributes()

        Return dictionary of attributes for table.

    .. function::  Table.set_table_attributes(attributes)

        Set table attributes to those in dictionary attributes.
        Example::

            out_table = out_table.set_table_attributes({'attr1', 'attr2'; 'val1', 'val2'})


    .. function::  Table.get_attributes()

        Get all table attributes and all column attributes.

    .. function::  Table.set_attributes(attributes)

        Set table attributes and column attributes at the same time.

    .. function::  Table.has_column(key)

        Return True if table contains a column named key.


    .. function::  Table.update(other_table)

        Updates the columns in the table with columns from other table keeping
        the old ones. If a column exists in both tables the one from
        other_table is used.

    .. function:: Table.update_column(column_name, other_table, other_name)

        Updates a column from a column in another table. The column other_name
        from other_table will be copied into column_name. If column_name
        already exists it will be replaced. When other_name is not used, then
        column_name will be used instead.

    .. function:: Table.hjoin(other_table)

        Add the columns from other_table. Analoguous to :meth:`update`.

    .. function:: Table.source(other_table)
       Fill a table with the contents of another.

    .. function:: Table.attr(name)

       Get the tables attribute with `name`.

    .. function:: Table.attrs(name)

       Return dictionary of attributes for table.

The MAT format
---------------------------
Although the above API tries to emulate the Sympathy (Python) Table API it
has some restrictions:


* Only tables where all columns are the same type are fully supported. If
  there are mixed types the resulting .mat file  will convert all columns to
  a type that accommodates all. E.g., ints and floats will all be floats,
  floats and strings will all be strings.

The represenation in MATLAB is a struct which you can access freely. This is
not recommended however, since it can be changed at any time, and should
be considered an implementation detail. The above API should be used at all
times to ensure compatibility.
