import sys
import os

# Prepend the root directory of the file into sys.path
project_root = os.path.abspath(os.path.dirname(__file__))
# print("Project root:", project_root)
folders = ['tasks', 'scripts', "tests", "visualisation", "draft"]

def _in(project_root):
    for folder in folders:
        if folder in project_root:
            return True
    return False

while _in(project_root):
    project_root = os.path.abspath(os.path.join(project_root, ".."))
    
sys.path.insert(0, project_root)
