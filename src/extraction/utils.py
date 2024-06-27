import json

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

def checks_pipeline(funcs: list):
    """
    Execute a list of function
    """
    for func in funcs:
        func()

def json2dict(json_filepath) -> dict :
    """Read a json file and return it as a python dict
    """

    with open(json_filepath) as json_file:
        json_data = json_file.read()
    
    return json.loads(json_data)