"""Utilities for detecting and handling .app bundle mode."""
import os
import sys


def is_frozen():
    """Return True if running inside a py2app bundle."""
    return getattr(sys, 'frozen', False)


def get_resource_path(relative_path):
    """Get absolute path to a resource, works in dev and bundled mode."""
    if is_frozen():
        base = os.path.join(os.path.dirname(sys.executable), '..', 'Resources')
    else:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, relative_path)


def get_data_dir():
    """Get ~/Library/Application Support/Philoquent/."""
    path = os.path.expanduser('~/Library/Application Support/Philoquent')
    os.makedirs(path, exist_ok=True)
    return path


def get_model_cache_dir():
    """Get model cache directory."""
    path = os.path.join(get_data_dir(), 'models')
    os.makedirs(path, exist_ok=True)
    return path
