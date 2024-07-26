import sys
import os

from cli import main_cli
from gui import main_gui
# access binaries
if getattr(sys, 'frozen', False):
    # If running as a PyInstaller bundle
    bundle_dir = sys._MEIPASS
    os.environ["PATH"] = (
        os.path.join(bundle_dir, "graphviz_bin")
        + os.pathsep 
        + os.path.join(bundle_dir, "wkhtml_bin") 
        + os.pathsep + os.environ["PATH"]
    )

if __name__ == "__main__":
    if len(sys.argv) > 1:
        main_cli()
    else :
        main_gui()