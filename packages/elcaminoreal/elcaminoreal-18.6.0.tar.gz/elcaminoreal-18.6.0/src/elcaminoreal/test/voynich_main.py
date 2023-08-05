"""
Run the pseduo-voynich examples.
"""
import sys

from elcaminoreal.test import voynich_skeleton

if __name__ != '__main__':
    raise ImportError("Module should not be imported", __name__)

voynich_skeleton.COMMANDS.run(sys.argv[1:])
