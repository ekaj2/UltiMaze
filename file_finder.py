import os
from os.path import join, getsize, dirname


def remove_suffix(string, suffix):
    if string[len(string) - len(suffix):] == suffix:
        return string[:len(string) - len(suffix)]


my_tiles_dir = join(dirname(__file__), "tiles")
# get file names
for root, dirs, files in os.walk(my_tiles_dir):
    pass
print(files)
fbx_files = []
for f in files:
    if f.endswith(".fbx"):
        fbx_files += [(f, remove_suffix(f, ".fbx"))]
print(fbx_files)
