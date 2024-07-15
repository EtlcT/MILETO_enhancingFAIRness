# hook-user32.py
from PyInstaller.utils.hooks import collect_submodules
import sys

if sys.platform.startswith('linux'):
    hiddenimports = collect_submodules('user32')