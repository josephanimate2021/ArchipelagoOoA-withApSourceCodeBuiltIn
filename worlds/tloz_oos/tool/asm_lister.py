import json
import os

from worlds.tloz_oos import patching

if __name__ == "__main__":
    dir_name = os.path.dirname(patching.__file__) + "/asm"
    asm_files = {"base": [f"asm/{filename}" for filename in os.listdir(dir_name) if filename.endswith(".yaml")]}
    for filename in os.listdir(dir_name + "/conditional"):
        asm_files[filename[:-5]] = [f"asm/conditional/{filename}"]

    with open(dir_name + "/__init__.py", "w", encoding="utf-8") as f:
        f.write('asm_files = ')
        f.write(json.dumps(asm_files, indent=4))