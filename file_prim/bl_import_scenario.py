import os
import bpy
import json

from . import format as prim_format
from ..file_borg import format as borg_format
from .. import io_binary
from . import bl_import_prim
from .. import BlenderUI
import mathutils
from mathutils import Euler
import math


def load_scenario(operator, context, collection, path_to_prims_json):
    f = open(path_to_prims_json, "r")
    data = json.loads(f.read())
    f.close()
    print("Printing hashes and transforms")
    transforms = {}
    for hash_and_entity in data['entities']:
        prim_hash = hash_and_entity['primHash']
        entity = hash_and_entity['entity']
        print(prim_hash + ":")
        transform = {"position": entity["position"], "rotate": entity["rotation"],
                     "scale": entity["scale"]["data"]}
        print(json.dumps(transform))

        if prim_hash not in transforms:
            transforms[prim_hash] = []
        transforms[prim_hash].append(transform)

    path_to_prim_dir = "%s\\%s" % (os.path.dirname(path_to_prims_json), "prim")
    print("Path to prim dir:")
    print(path_to_prim_dir)
    file_list = sorted(os.listdir(path_to_prim_dir))
    print("File list:")
    print(file_list)
    prim_list = [item for item in file_list if item.lower().endswith('.prim')]
    print("Prim List:")
    print(prim_list)
    for prim_filename in prim_list:
        print("Prim File name:")
        print(prim_filename)
        prim_path = os.path.join(path_to_prim_dir, prim_filename)
        print("Prim Path:")
        print(prim_path)
        prim_hash = prim_filename[:-5]
        print("Prim hash:")
        print(prim_hash)
        if prim_hash not in transforms:
            continue
        for i in range(0, len(transforms[prim_hash])):
            print("Loading prim:")
            print(prim_hash)
            objects = bl_import_prim.load_prim(
                None, context, collection, prim_path, False, None
            )
            if not objects:
                print("Error Loading prim:")
                print(prim_hash)
                return 1
            transform = transforms[prim_hash][i]
            p = transform["position"]
            r = transform["rotate"]
            s = transform["scale"]
            r["roll"] = math.pi * 2 - r["roll"]
            print("Transforming prim:")
            print(prim_hash + " #" + str(i))
            print("Prim Transforms:")
            print(transform)
            for obj in objects:
                collection.objects.link(obj)
                obj.select_set(True)
                bpy.ops.transform.resize(value=(s["x"], s["y"], s["z"]), orient_type="LOCAL")
                bpy.ops.transform.rotate(value=r["yaw"], orient_axis='X', orient_type="LOCAL")
                bpy.ops.transform.rotate(value=r["pitch"], orient_axis='Y', orient_type="LOCAL")
                bpy.ops.transform.rotate(value=r["roll"], orient_axis='Z', orient_type="LOCAL")
                bpy.ops.transform.translate(value=(p["x"], p["y"], p["z"]), orient_type="LOCAL")
                obj.select_set(False)

    return 0
