import os

def remove_suffix(string, suffix):
    if string[len(string) - len(suffix):] == suffix:
        return string[:len(string) - len(suffix)]


my_tiles_dir = os.path.join(os.path.dirname(__file__), "tiles")
# get file names
tile_fbxs = [a for a in os.listdir(my_tiles_dir) if a[-4:] == '.fbx']
