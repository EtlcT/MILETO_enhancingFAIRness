import tkinter as tk
import customtkinter as ctk
import re
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

def get_sub_item_id(data, ancestor_id, sub_item_name):
    """ Return sub_item index value based on
    ancestor index and sub_item name

    Example: get_sub_item_id(DC_TERMS, 2, "nameIdentifier") return 2.4
    
    """
    for item_idx, item_info in data.items():
        if re.match(f"{ancestor_id}(?!\d)", item_idx) and item_info.get("name") is not None:
            if sub_item_name == item_info.get("name"):
                return item_idx
          
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
