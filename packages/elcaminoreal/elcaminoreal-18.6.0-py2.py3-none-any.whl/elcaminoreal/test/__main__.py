"""
El Camino Real Test Main

Run the built-in test El Camino Real plugins.
"""
import sys
from elcaminoreal.test import some_plugins

if __name__ != '__main__':
    raise ImportError("main module, not importable", __name__)

some_plugins.COMMANDS.run(sys.argv[1:])
