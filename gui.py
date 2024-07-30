# main.py
from src.gui.view import View
from src.gui.model import Model
from src.gui.controller import Controller

def main_gui():
    model = Model()
    view = View()
    controller = Controller(model, view)
    # open in fullscreen mode
    view._state_before_windows_set_titlebar_color = 'zoomed'
    view.set_controller(controller)
    # root element have width 100%
    view.columnconfigure(0, weight=1)
    view.mainloop()

if __name__ == "__main__":
    main_gui()
