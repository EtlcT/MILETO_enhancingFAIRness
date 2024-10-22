import sys
import os
import logging

from cli import main_cli
from gui import main_gui

# Configure logging
logging.basicConfig(level=logging.ERROR, 
                    format='%(asctime)s %(levelname)s %(message)s',
                    handlers=[logging.FileHandler("logs"),
                              logging.StreamHandler()])

# access binaries
if getattr(sys, 'frozen', False):
    # If running as a PyInstaller bundle
    bundle_dir = sys._MEIPASS
    os.environ["PATH"] = (
        os.path.join(bundle_dir, "graphviz")
        + os.pathsep 
        + os.path.join(bundle_dir, "wkhtmltopdf") 
        + os.pathsep + os.environ["PATH"]
    )

if __name__ == "__main__":
    try:
        if len(sys.argv) > 1:
            main_cli()
        else :
            main_gui()
    except Exception as e:
        logging.error(f"An error occurred: {e}", exc_info=True)