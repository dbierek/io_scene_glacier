import os
import json

from . import bl_import_prim
import mathutils
from mathutils import Euler
import math


def load_scenario(operator, context, collection, path_to_prims_json):
    f = open(path_to_prims_json, "r")
    data = json.loads(f.read())
    f.close()
    transforms = {}
    for hash_and_entity in data['entities']:
        prim_hash = hash_and_entity['hash']
        entity = hash_and_entity['entity']
        transform = {"position": entity["position"], "rotate": entity["rotation"],
                     "scale": entity["scale"]["data"]}

        if prim_hash not in transforms:
            transforms[prim_hash] = []
        transforms[prim_hash].append(transform)

    path_to_prim_dir = "%s\\%s" % (os.path.dirname(path_to_prims_json), "prim")
    print("Path to prim dir:")
    print(path_to_prim_dir)
    file_list = sorted(os.listdir(path_to_prim_dir))
    prim_list = [item for item in file_list if item.lower().endswith('.prim')]
    for prim_filename in prim_list:
        prim_hash = prim_filename[:-5]
        if prim_hash not in transforms:
            continue
        prim_path = os.path.join(path_to_prim_dir, prim_filename)

        print("Loading prim:")
        print(prim_hash)
        objects = bl_import_prim.load_prim(
            None, context, collection, prim_path, False, None
        )
        if not objects:
            print("Error Loading prim:")
            print(prim_hash)
            return 1
        highest_lod = -1
        for obj in objects:
            for j in range(0, 8):
                if obj.data['prim_properties']['lod'][j] == 1 and highest_lod < j:
                    highest_lod = j

        t = transforms[prim_hash]
        t_size = len(t)
        for i in range(0, t_size):
            transform = transforms[prim_hash][i]
            p = transform["position"]
            r = transform["rotate"]
            s = transform["scale"]
            r["roll"] = math.pi * 2 - r["roll"]
            print("Transforming prim:" + prim_hash + " #" + str(i))
            for obj in objects:
                if obj.data['prim_properties']['lod'][highest_lod] == 0:
                    continue
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
