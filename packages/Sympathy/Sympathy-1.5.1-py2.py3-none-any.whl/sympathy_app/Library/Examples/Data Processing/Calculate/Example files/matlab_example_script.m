try
    names = arg.column_names();
    price = names(1, :);
    price_value = arg.get_column_to_array(price);

    out_table = Table();
    out_table = out_table.set_column_from_array(...
        'MAX_PRICE',  max(price_value), [[], []]);
    out_table = out_table.set_column_from_array(...
        'MIN_PRICE',  min(price_value), [[], []]);
    out_table = out_table.set_table_attributes([]);
    res = out_table;
catch err
    err.message
end
