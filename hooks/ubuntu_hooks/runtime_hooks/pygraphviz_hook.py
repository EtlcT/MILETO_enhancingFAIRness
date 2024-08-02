import os
import sys
import pygraphviz

# Save the original _which method
original_which = pygraphviz.AGraph._which

def custom_which(name):
    """
    Custom implementation of the _which method that searches in sys._MEIPASS.
    """
    if hasattr(sys, '_MEIPASS'):
        meipass_path = sys._MEIPASS
        custom_path = os.path.join(meipass_path, name)
        if os.path.isfile(custom_path) and os.access(custom_path, os.X_OK):
            return custom_path
    # Fallback to the original _which method if not found in _MEIPASS
    return original_which(name)

# Override the _which method with the custom implementation
pygraphviz.AGraph._which = staticmethod(custom_which)
