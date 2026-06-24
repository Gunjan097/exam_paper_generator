import os
import sys


def get_asset_path(relative: str) -> str:
    """Returns the absolute path to an asset file.

    Works in two contexts:
    - Dev: resolves relative to the project root (parent of src/)
    - PyInstaller bundle: resolves relative to sys._MEIPASS (the unpacked bundle dir)
    """
    if hasattr(sys, "_MEIPASS"):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(base, relative)
