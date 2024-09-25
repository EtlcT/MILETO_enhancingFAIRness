import tkinter as tk
import customtkinter as ctk
import json
from json import JSONDecodeError
import textwrap

def get_zoomed_geometry():
    """Return geometry for tkinter view to set fullscreen mode on linux"""
    root = tk.Tk()
    root.update_idletasks()
    root.attributes('-zoomed', True)
    root.state('iconic')
    geometry = root.winfo_geometry()
    root.update_idletasks()
    root.destroy()
    return geometry

def get_str_max_length(items):
    """Return the lenght the longest string in items if items is a list
    of string, else the lenght of the string
    """
    if isinstance(items, list):
        return max(len(item) for item in items)
    else:
         return len(items)

def CenterWindowToDisplay(Screen: ctk, width: int, height: int, scale_factor: float = 1.0):
        """Centers the window to the main display/monitor"""
        screen_width = Screen.winfo_screenwidth()
        screen_height = Screen.winfo_screenheight()
        x = int(((screen_width/2) - (width/2)) * scale_factor)
        y = int(((screen_height/2) - (height/1.5)) * scale_factor)
        return f"{width}x{height}+{x}+{y}"

def get_authorized_type(current_type):
     """Return list of authorized sqlite type based on current type of an object"""

     match current_type:
          case "REAL":
               return ["TEXT"]
          case "INTEGER":
               return ["REAL", "TEXT"]
          case _:
               return None
          
# def recurse_str_to_dict(json_str):
#     try:
#         # Check if the input is a string, then attempt to load it as JSON
#         if isinstance(json_str, str):
#             loaded_d = json.loads(json_str)
#         elif isinstance(json_str, dict):
#             loaded_d = json_str
#         else:
#             return json_str  # If it's neither a string nor a dict, return as-is
          
#         # Recurse through the dictionary's items
#         for k, v in loaded_d.items():
#             loaded_d[k] = recurse_str_to_dict(v)
#     except (json.JSONDecodeError, TypeError):
#         return json_str  # Return the original string or object if loading fails
#     return loaded_d
            
     
# # Function to calculate the required row height
# def get_max_lines_per_row(data_frame):
#     """Calculate required row height based on break line"""
#     max_lines = 1
#     for row in data_frame.itertuples(index=False):
#         for cell in row:
#             cell_lines = str(cell).count('\n') + 1
#             max_lines = max(max_lines, cell_lines)
#     return max_lines

# def wrap(string, lenght=8):
#     return '\n'.join(textwrap.wrap(string, lenght))

    # def process_item(self, object_id, dc_terms_dict):
    #     """
    #         Collect required and optionnal terms and sub_terms (recursively) for each object_id
    #     """
    #     req_terms = {}  # Store required sub_terms id and the id of the terms that imply them to be mandatory
    #     opt_terms = []  # Store optional sub_terms id

    #     # Initialize the list for the current key in req_terms
    #     if object_id not in req_terms:
    #         req_terms[object_id] = []

    #     # Process required sub_terms (has_r)
    #     if dc_terms_dict[object_id].get("has_r") is not None:
    #         for req_item in dc_terms_dict[object_id].get("has_r"):
    #             req_terms[object_id].append(req_item)  # Collect required sub_terms
    #             # Recursively process required sub_terms
    #             sub_req_terms, sub_opt_terms = self.process_item(req_item, dc_terms_dict)
    #             for sub_key, sub_values in sub_req_terms.items():
    #                 if sub_key not in req_terms:
    #                     req_terms[sub_key] = []
    #                 req_terms[sub_key].extend(sub_values)  # Collect nested required terms
    #             opt_terms.extend(sub_opt_terms)  # Collect nested optional terms

    #     # Process optional sub_terms (has_o)
    #     if dc_terms_dict[object_id].get("has_o") is not None:
    #         for opt_item in dc_terms_dict[object_id].get("has_o"):
    #             opt_terms.append(opt_item)  # Collect optional sub-item
    #             sub_req_terms, sub_opt_terms = self.process_item(opt_item, dc_terms_dict)  # Recursively process
    #             for sub_key, sub_values in sub_req_terms.items():
    #                 if sub_key not in req_terms:
    #                     req_terms[sub_key] = []
    #                 req_terms[sub_key].extend(sub_values)  # Collect nested required terms
    #             opt_terms.extend(sub_opt_terms)  # Collect nested optional terms

    #     return req_terms, opt_terms  # Return both required and optional terms
    
    # def process_dc_json(self, dc_json_objects, dc_json_terms):
    #     """
    #     Return a dictionnary of required terms and a list of optionnal terms
    #     from conf/dc_meta_terms.json file

    #     Arguments:
    #     dc_json_object corresponds to {**DC_TERMS["items"]["required"], **DC_TERMS["items"]["other"]}
    #     dc_json_terms corresponds to DC_TERMS["properties"]

    #     req_terms dictionnary contain as object_id each term that has required sub terms
    #     and the list of those required sub_terms as value
        
    #     opt_terms is a list of all terms that are opionnals
    #     """
    #     req_terms, opt_terms = {}, []
    #     for obj, info in dc_json_objects.items():

    #         if info["id"] not in req_terms:
    #             req_terms[info["id"]] = []
    #         sub_req_terms, sub_opt_terms = self.process_item(info["id"], dc_json_terms)

    #         for sub_object_id, sub_values in sub_req_terms.items():
    #             if sub_object_id not in req_terms:
    #                 req_terms[sub_object_id] = []
    #             req_terms[sub_object_id].extend(sub_values)  # Collect nested required items
    #         opt_terms.extend(sub_opt_terms)  # Collect optional items

    #         if len(sub_req_terms.keys()) == 1:
    #             if dc_json_terms[info["id"]]["required"] == 0:
    #                 opt_terms.append(info["id"])
    #     req_terms = {k:v for k, v in req_terms.items() if v}
    #     return req_terms, opt_terms