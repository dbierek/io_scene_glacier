import os
import json

from . import bl_import_aloc
import mathutils
from mathutils import Euler
import math


def load_scenario(operator, context, collection, path_to_alocs_json):
    f = open(path_to_alocs_json, "r")
    data = json.loads(f.read())
    f.close()
    transforms = {}
    for hash_and_entity in data['entities']:
        aloc_hash = hash_and_entity['hash']
        entity = hash_and_entity['entity']
        transform = {"position": entity["position"], "rotate": entity["rotation"],
                     "scale": entity["scale"]["data"]}

        if aloc_hash not in transforms:
            transforms[aloc_hash] = []
        transforms[aloc_hash].append(transform)

    path_to_aloc_dir = "%s\\%s" % (os.path.dirname(path_to_alocs_json), "aloc")
    print("Path to aloc dir:")
    print(path_to_aloc_dir)
    file_list = sorted(os.listdir(path_to_aloc_dir))
    aloc_list = [item for item in file_list if item.lower().endswith('.aloc')]
    for aloc_filename in aloc_list:
        aloc_hash = aloc_filename[:-5]
        if aloc_hash not in transforms:
            continue
        aloc_path = os.path.join(path_to_aloc_dir, aloc_filename)

        print("Loading aloc:")
        print(aloc_hash)
        objects = bl_import_aloc.load_aloc(
            None, context, aloc_path
        )
        if not objects:
            print("Error Loading aloc:")
            print(aloc_hash)
            return 1

        t = transforms[aloc_hash]
        t_size = len(t)
        for i in range(0, t_size):
            transform = transforms[aloc_hash][i]
            p = transform["position"]
            r = transform["rotate"]
            s = transform["scale"]
            r["roll"] = math.pi * 2 - r["roll"]
            print("Transforming aloc:" + aloc_hash + " #" + str(i))
            for obj in objects:
                if i != 0:
                    cur = obj.copy()
                else:
                    cur = obj
                collection.objects.link(cur)
                cur.select_set(True)
                cur.scale = mathutils.Vector((s["x"], s["y"], s["z"]))
                cur.rotation_euler = Euler((-r["yaw"], -r["pitch"], -r["roll"]), 'XYZ')
                cur.location = mathutils.Vector((p["x"], p["y"], p["z"]))
                cur.select_set(False)

    return 0
