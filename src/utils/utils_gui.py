import tkinter as tk

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

class MessageBox():
    def custom_msgbox(title="success", text=None):
            pass