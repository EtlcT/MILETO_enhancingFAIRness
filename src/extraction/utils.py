def checkUniqueness(field, table) -> bool:
    """
        Check that a field or group of fields verify uniqueness constraint

        inputs:
            field must be a string or a list of string
            table is a pandas.Dataframe object
    """
    if isinstance(field, str):
        return table[field].is_unique
    elif isinstance(field, list):
        if len(field)>1:
            count_combination = (
                table
                .groupby(by=field)
                .size()
                .reset_index(name='count')
                            
            )
            return (count_combination['count']==1).all()
        else:
            return table[field[0]].is_unique