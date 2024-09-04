import sys
from src.gui.view import View
from src.gui.model import Model
from src.gui.controller import Controller
from src.utils.utils_gui import get_zoomed_geometry

def main_gui():
    model = Model()

    # open in fullscreen mode
    if(sys.platform.startswith('linux')):
        geometry = get_zoomed_geometry()
        view = View()
        view.geometry(geometry)
    else:
        view = View()
        view._state_before_windows_set_titlebar_color = 'zoomed'

    view.after(201, lambda: view.iconbitmap("assets/logo(1).ico"))
    controller = Controller(model, view)
    view.set_controller(controller)
    # root element have width 100%
    view.columnconfigure(0, weight=1)
    view.mainloop()

if __name__ == "__main__":
    main_gui()