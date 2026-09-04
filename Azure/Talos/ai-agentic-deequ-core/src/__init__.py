import os
import sys

# Parche Táctico de Nivel Elite para subprocesos efímeros en Python 3.14
root_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)
