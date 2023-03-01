import sys
import os

# Prepend the root directory of the file into sys.path
project_root = os.path.abspath(os.path.dirname(__file__))

while 'tasks' in project_root or 'scripts' in project_root:
    project_root = os.path.abspath(os.path.join(project_root, ".."))
    
sys.path.insert(0, project_root)
