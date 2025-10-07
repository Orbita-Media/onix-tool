# utils.py
"""
Utility functions for BoD MasteringOrder Generator.
Place this file in the project root next to main.py.
"""
import os
import sys
import json

# BASE_DIR je nachdem, ob wir als EXE (PyInstaller) laufen oder als Script
if getattr(sys, 'frozen', False):
    # läuft als EXE: JSONs liegen im temporären Ordner _MEIPASS
    BASE_DIR = sys._MEIPASS
else:
    # läuft als normales Script
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def load_json(filename):
    """
    Load and return JSON data from a file in the project root.

    Args:
        filename (str): Name of the JSON file (e.g., 'warengruppe_codes.json').

    Returns:
        dict: Parsed JSON data.
    """
    path = os.path.join(BASE_DIR, filename)
    with open(path, encoding='utf-8') as f:
        return json.load(f)
