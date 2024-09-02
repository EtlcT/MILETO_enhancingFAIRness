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

class MessageBox():
    def custom_msgbox(title="success", text=None):
            pass