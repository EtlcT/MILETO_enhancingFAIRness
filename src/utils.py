import logging
import traceback
import json
import sys
import os
import pandas as pd
import base64
from PIL import Image

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
    else: raise TypeError(f"fields should be of type list or string but has type {type(fields)}")

def checks_pipeline(check_funcs: list):
    """
    Execute a list of function produce log if errors are raised
    """

    errors = []
    for check in check_funcs:
        try:
            check()
        except Exception as e:
            logging.error(f"Exception occurred in {check.__name__}: {str(e)}", exc_info=True)
            logging.error(traceback.format_exc(), exc_info=True)
            errors.append(f"Exception in {check.__name__}: {str(e)}")
    
    if errors:
        logging.info("Errors occurred:")
        for error in errors:
            logging.info(f"- {error}")
    else:
        logging.info("All checks passed successfully.")

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

def html_formatted_sql(raw_sql: str) -> str:
        """Return readable sql statement from sqlite_master statement"""

        formatted_sql = (
            raw_sql
            .replace('    ', '&emsp;')
            .replace('\n', '<br>')
        )

        return formatted_sql

def rotate_image(image_path):
    """Rotate image from 90°"""
    
    with Image.open(image_path) as image:
        rotated_image = image.rotate(-90, expand=True)
        rotated_image.save(image_path)
    
    return