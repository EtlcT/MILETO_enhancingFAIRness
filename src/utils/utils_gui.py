import tkinter as tk
import customtkinter as ctk
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