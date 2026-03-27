import json
import os

def fetch_asm_files():
    dir_name = os.path.dirname(patching.__file__) + "/asm/base" # if not dir_name else dir_name
    asm_files = []
    for filename in os.listdir(dir_name):
        if filename.endswith(".yaml"):
            asm_files.append(os.path.join(dir_name, filename))
    return asm_files