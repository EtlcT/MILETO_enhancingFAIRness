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
    name_id_dict = {}
    id_name_dict = {}
    for key, values in data.items():
        name = values.get('name')
        if name:
            name_id_dict[name] = key
            id_name_dict[key] = name
    return name_id_dict, id_name_dict

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

def process_item(self, object_id, dc_terms_dict):
    """
        Collect required and optionnal terms and sub_terms (recursively) for each object_id
    """
    req_terms = {}  # Store required sub_terms id and the id of the terms that imply them to be mandatory
    opt_terms = []  # Store optional sub_terms id

    # Initialize the list for the current key in req_terms
    if object_id not in req_terms:
        req_terms[object_id] = []

    # Process required sub_terms (has_r)
    if dc_terms_dict[object_id].get("has_r") is not None:
        for req_item in dc_terms_dict[object_id].get("has_r"):
            req_terms[object_id].append(req_item)  # Collect required sub_terms
            # Recursively process required sub_terms
            sub_req_terms, sub_opt_terms = self.process_item(req_item, dc_terms_dict)
            for sub_key, sub_values in sub_req_terms.items():
                if sub_key not in req_terms:
                    req_terms[sub_key] = []
                req_terms[sub_key].extend(sub_values)  # Collect nested required terms
            opt_terms.extend(sub_opt_terms)  # Collect nested optional terms

    # Process optional sub_terms (has_o)
    if dc_terms_dict[object_id].get("has_o") is not None:
        for opt_item in dc_terms_dict[object_id].get("has_o"):
            opt_terms.append(opt_item)  # Collect optional sub-item
            sub_req_terms, sub_opt_terms = self.process_item(opt_item, dc_terms_dict)  # Recursively process
            for sub_key, sub_values in sub_req_terms.items():
                if sub_key not in req_terms:
                    req_terms[sub_key] = []
                req_terms[sub_key].extend(sub_values)  # Collect nested required terms
            opt_terms.extend(sub_opt_terms)  # Collect nested optional terms

    return req_terms, opt_terms  # Return both required and optional terms

def process_dc_json(self, dc_json_objects, dc_json_terms):
    """
    Return a dictionnary of required terms and a list of optionnal terms
    from conf/dc_meta_terms.json file

    Arguments:
    dc_json_object corresponds to {**DC_TERMS["items"]["required"], **DC_TERMS["items"]["other"]}
    dc_json_terms corresponds to DC_TERMS["properties"]

    req_terms dictionnary contain as object_id each term that has required sub terms
    and the list of those required sub_terms as value
    
    opt_terms is a list of all terms that are opionnals
    """
    req_terms, opt_terms = {}, []
    for obj, info in dc_json_objects.items():

        if info["id"] not in req_terms:
            req_terms[info["id"]] = []
        sub_req_terms, sub_opt_terms = self.process_item(info["id"], dc_json_terms)

        for sub_object_id, sub_values in sub_req_terms.items():
            if sub_object_id not in req_terms:
                req_terms[sub_object_id] = []
            req_terms[sub_object_id].extend(sub_values)  # Collect nested required items
        opt_terms.extend(sub_opt_terms)  # Collect optional items

        if len(sub_req_terms.keys()) == 1:
            if dc_json_terms[info["id"]]["required"] == 0:
                opt_terms.append(info["id"])
    req_terms = {k:v for k, v in req_terms.items() if v}
    return req_terms, opt_terms