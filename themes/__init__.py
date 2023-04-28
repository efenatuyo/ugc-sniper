import os
import glob

current_dir = os.path.dirname(os.path.abspath(__file__))

module_files = glob.glob(os.path.join(current_dir, "*.py"))

for module_file in module_files:
    module_name = os.path.basename(module_file)[:-3]
    if module_name != "__init__":
        __import__(f"{__name__}.{module_name}")
