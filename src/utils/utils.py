import logging
import traceback
import json
import sys
import os
import pandas as pd
import base64
from PIL import Image
import re
import shutil

from conf.config import *

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
    """Read a json file and return it as a python dictionnary
    """

    with open(resource_path(json_filepath)) as json_file:
        json_data = json_file.read()
    
    return json.loads(json_data)

def resource_path(relative_path):
    """ Get absolute path to resource for PyInstaller executable """
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.normpath(os.path.join(base_path, relative_path))

def img_base64(img_path):
        
        with open(img_path, "rb") as image_file:
            img_base64_encoded = base64.b64encode(image_file.read())
        
        return img_base64_encoded.decode('utf-8')

def rotate_image(image_path):
    """Rotate image from 90°"""
    
    with Image.open(image_path) as image:
        rotated_image = image.rotate(-90, expand=True)
        rotated_image.save(image_path)
    
    return

def file_exists(file_path):
    """Return true if file exists, False if not"""

    return os.path.isfile(file_path)

def output_exist(output_dir, output_basename):
        """For all potential generated output, check if one already exists
        return True if output already exist else False
        """
        outputs = [
            os.path.join(output_dir, output_basename + ".json"),
            os.path.join(output_dir, output_basename + ".sqlite"),
            os.path.join(output_dir, output_basename + ".pdf"),
            os.path.join(output_dir, "ERD_" + output_basename + ".svg"),
            os.path.join(output_dir, "ERD_" + output_basename + ".png")
            ]
        exists = []

        for o in outputs:
            if os.path.isfile(o):
                exists.append(True)
            else:
                exists.append(False)
        #TODO give info about the file that already exists
        return any(exists) 

def save_spreadsheet(sheets_dict, filepath, format):
    """Save changes applied to the spreadsheet"""
    if format== "ods":
            engine = "odf"
    else:
        engine = "openpyxl"
    with pd.ExcelWriter(filepath, engine=engine) as doc:
        for table_name, table in sheets_dict.items():
            table.to_excel(doc, sheet_name=table_name, index=False)

def get_relative_items(dc_dict, dc_id, required=None):
    """Return key: value from dc_meta_terms relative to dc_id
    
    Example: dc_id=2 would return key: value for keys from 2.1 to 2.5
    including sub properties
    """
    dc_terms = dc_dict["properties"]
    return {key:value for key, value in dc_terms.items() if re.match(f"{dc_id}(?!\d)", key)}

def format_as_json(text: str):
    parsed_json = json.loads(text, )
    return json.dumps(parsed_json, indent=4)

def get_name_id_pairs(data):
    result = {}
    for key, values in data.items():
        name = values.get('name')
        if name:
            result[name] = key
    return result

def parse_json(value):
    if pd.isna(value):
        # if value is np.nan return None to get valid value null in json
        return None
    try:
        # Try to parse the value as JSON
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        # if fails return the value as it is
        return value

def move_metadata_json(input_path, output_path, output_name):
    """Move json file that contain metadata for actual database"""
    src = f"{input_path}.json"
    dst = os.path.join(output_path, f"metadata_{output_name}.json")
    shutil.move(
        src=src,
        dst=dst
    )