def check_uniqueness(fields, table) -> bool:
    """
        Check that a fields or group of fieldss verify uniqueness constraint

        inputs:
            fields must be a string or a list of string
            table is a pandas.Dataframe object
    """
    if isinstance(fields, str):
        return table[fields].is_unique
    elif isinstance(fields, list):
        if len(fields)>1:
            count_combination = (
                table
                .groupby(by=fields)
                .size()
                .reset_index(name='count')
                            
            )
            return (count_combination['count']==1).all()
        else:
            return table[fields[0]].is_unique