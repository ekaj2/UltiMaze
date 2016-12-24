import bpy
import os


def append_objs(path, prefix="", suffix="", case_sens=False, ignore="IGNORE"):
    """Appends all objects into scene from .blend if they meet argument criteria."""

    scene = bpy.context.scene

    with bpy.data.libraries.load(path) as (data_from, data_to):
        if not case_sens:
            data_to.objects = [name for name in data_from.objects if
                               name.lower().startswith(prefix.lower()) and name.lower().endswith(suffix.lower()) and ignore.upper() not in name.upper()]
        else:
            data_to.objects = [name for name in data_from.objects if name.startswith(prefix) and name.endswith(suffix) and ignore.upper() not in name.upper()]

    for obj in data_to.objects:
        if obj is not None:
            scene.objects.link(obj)


def make_absolute(key):
    addon_prefs = bpy.context.user_preferences.addons['maze_gen'].preferences
    if key in addon_prefs and addon_prefs[key].startswith('//'):
        # must use a[x] notation instead of a.x so it doesn't trigger update callbacks infinitely
        addon_prefs[key] = os.path.abspath(bpy.path.abspath(addon_prefs[key]))
