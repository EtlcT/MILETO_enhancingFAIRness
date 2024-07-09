import logging
import traceback
import json
import sys
import os
import pandas as pd
import base64

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
    """Read a config files
    """

    with open(resource_path(json_filepath)) as json_file:
        json_data = json_file.read()
    
    return json.loads(json_data)

def resource_path(relative_path):
    """ Get absolute path to resource for PyInstaller executable """
    try:
        # PyInstaller creates a temporary folder and stores the path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def file2Blob(absolute_path: str) -> bytes:
    """Take an absolute filepath, read relative file
    convert content to blob

    if the file does not exists orcan't be accessed,
    let the absolute_path as it was and print error

    """

    try:
        with open(absolute_path, 'rb') as file:
            binary = file.read()

        return binary
    
    except FileNotFoundError:
        logging.error("An error occurred ", exc_info=True)
        traceback.print_exc()

        return absolute_path
    
def bytes_in_df_col(column: pd.Series) -> bool:
    is_bytes = pd.Series()
    is_bytes = column.apply(lambda x: isinstance(x, bytes))
    return is_bytes.any()

def img_base64(img_path):
        
        with open(img_path, "rb") as image_file:
            img_base64_encoded = base64.b64encode(image_file.read())
        
        return img_base64_encoded.decode('utf-8')

def prettier_sql(raw_sql: list) -> str:
        """Return readable sql statement from sqlite_master statement"""

        formatted_sql = str()
        for row in raw_sql:
            formatted_row = (
                row[0]
                .replace('(', '(<br>&emsp;', 1) # brak line after
                .replace(',\n', ',<br>&emsp;')
                .rstrip(row[0][-1]) # remove last ) and break line
            )
                          
            formatted_sql += formatted_row + "<br>)<br><br>"

        return formatted_sql