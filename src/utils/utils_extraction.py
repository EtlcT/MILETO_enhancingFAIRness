import os
import re
import pandas as pd
import logging

def regex_exclude_meta(text) -> bool:
    """
    return True if text match one of the regex to exclude, false either

    case insensitive regex to keep only data tables
    """
    no_info = re.search(r"(?i)tables_info", text)
    no_meta = re.search(r"(?i)meta\_", text)
    no_DDict = re.search(r"(?i)datadict\_", text)
    no_extra = re.match(r"(?i)extra\_", text)

    return any([no_DDict, no_meta, no_info, no_extra])


def get_datatables_list(sheets_dict) -> list:
    """
    Return a list containing the name of table that contains effective data

    exclude extra.*, meta.* and DDict.*, tables_info
    """
    datatable_list = list()
    for sheet_name in sheets_dict:
        if(regex_exclude_meta(sheet_name) == False):
            datatable_list.append(sheet_name)
    return datatable_list

def rm_extra_tables(sheets_dict) -> dict:
    """Remove tables that start with 'extra' from the database"""

    extra_tables = [key for key in sheets_dict if re.match(r"extra", key)]
    for key in extra_tables:
        del sheets_dict[key]
    
    return sheets_dict

def img2Blob(path: str, file_dir=None) -> bytes:
    """Take a filepath to an image, read relative file
    convert content to blob

    if the file does not exists or can't be accessed,
    the path remains as it was and an error is raised

    """
    if os.path.isfile(path):
        img_path = os.path.abspath(path)
    else:
        img_path = os.path.abspath(os.path.join(file_dir, "images" , path))
    try:
        with open(img_path, 'rb') as file:
            binary = file.read()
        return binary
    
    except FileNotFoundError:
        logging.error("An error occurred ", exc_info=True)
        return path

def bytes_in_df_col(column: pd.Series) -> bool:
    """Return True if column contains bytes"""
    is_bytes = pd.Series()
    is_bytes = column.apply(lambda x: isinstance(x, bytes))
    return is_bytes.any()

def process_item(object_id, dc_terms_dict):
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
            sub_req_terms, sub_opt_terms = process_item(req_item, dc_terms_dict)
            for sub_key, sub_values in sub_req_terms.items():
                if sub_key not in req_terms:
                    req_terms[sub_key] = []
                req_terms[sub_key].extend(sub_values)  # Collect nested required terms
            opt_terms.extend(sub_opt_terms)  # Collect nested optional terms

    # Process optional sub_terms (has_o)
    if dc_terms_dict[object_id].get("has_o") is not None:
        for opt_item in dc_terms_dict[object_id].get("has_o"):
            opt_terms.append(opt_item)  # Collect optional sub-item
            sub_req_terms, sub_opt_terms = process_item(opt_item, dc_terms_dict)  # Recursively process
            for sub_key, sub_values in sub_req_terms.items():
                if sub_key not in req_terms:
                    req_terms[sub_key] = []
                req_terms[sub_key].extend(sub_values)  # Collect nested required terms
            opt_terms.extend(sub_opt_terms)  # Collect nested optional terms

    return req_terms, opt_terms  # Return both required and optional terms