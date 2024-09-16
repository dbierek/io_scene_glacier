import os
import json
import struct

from . import bl_import_aloc
import mathutils
from mathutils import Euler
import math
from timeit import default_timer as timer

import bpy
import bmesh
from .format import PhysicsCollisionLayerType, PhysicsCollisionType


def load_scenario(operator, context, collection, path_to_alocs_json):
    start = timer()
    print("Loading scenario.")
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

    print("Loading PfBoxes.")
    alocs_json_dir = os.path.dirname(path_to_alocs_json)
    path_to_pf_boxes_json = "%s\\%s" % (alocs_json_dir, "pfBoxes.json")
    f = open(path_to_pf_boxes_json, "r")
    pb_boxes_data = json.loads(f.read())
    f.close()
    pf_transforms = []
    print("Loading file: " + str(path_to_pf_boxes_json))

    for hash_and_entity in pb_boxes_data['entities']:
        entity = hash_and_entity['entity']
        pf_box_type = entity["type"]["data"]
        # print("PF Box Type: " + str(pf_box_type))
        if pf_box_type == "PFBT_EXCLUDE_MESH_COLLISION":
            transform = {"position": entity["position"], "rotate": entity["rotation"],
                         "scale": entity["size"]["data"], "id": entity["id"]}
            pf_transforms.append(transform)
    path_to_aloc_dir = "%s\\%s" % (alocs_json_dir, "aloc")
    print("Path to aloc dir:" + path_to_aloc_dir)
    file_list = sorted(os.listdir(path_to_aloc_dir))
    aloc_list = [item for item in file_list if item.lower().endswith('.aloc')]

    excluded_collision_types = [
        # PhysicsCollisionType.NONE,
        # PhysicsCollisionType.RIGIDBODY,
        # PhysicsCollisionType.KINEMATIC_LINKED,
        # PhysicsCollisionType.SHATTER_LINKED
    ]
    excluded_aloc_hashes = [
        # "00C47B7553348F32"
    ]
    for aloc_filename in aloc_list:
        aloc_hash = aloc_filename[:-5]
        if aloc_hash not in transforms:
            continue
        if aloc_hash in excluded_aloc_hashes:
            continue
        aloc_path = os.path.join(path_to_aloc_dir, aloc_filename)

        print("Loading aloc:" + aloc_hash)
        # try:
        collision_type, objects = bl_import_aloc.load_aloc(
            None, context, aloc_path, False
        )
        # except struct.error as err:
        #     print("=========================== Error Loading aloc: " + str(aloc_hash) + " Exception: " + str(err) + " ================")
        #     continue

        if len(objects) == 0:
            # print("No collidable objects for " + str(aloc_hash))
            continue
        if not objects:
            print("-------------------- Error Loading aloc:" + aloc_hash + " ----------------------")
            continue
        if collision_type in excluded_collision_types:
            # print("+++++++++++++++++++++ Skipping Non-collidable ALOC: " + aloc_hash + " with collision type: " + str(collision_type) + " +++++++++++++")
            continue
        t = transforms[aloc_hash]
        t_size = len(t)
        for i in range(0, t_size):
            transform = transforms[aloc_hash][i]
            p = transform["position"]
            r = transform["rotate"]
            s = transform["scale"]
            print("Transforming aloc:" + aloc_hash + " #" + str(i))
            for obj in objects:
                if i != 0:
                    cur = obj.copy()
                else:
                    cur = obj
                collection.objects.link(cur)
                cur.select_set(True)
                cur.scale = mathutils.Vector((s["x"], s["y"], s["z"]))
                cur.rotation_mode = 'QUATERNION'
                cur.rotation_quaternion = (r["w"], r["x"], r["y"], r["z"])
                cur.location = mathutils.Vector((p["x"], p["y"], p["z"]))
                cur.select_set(False)

    print("Creating PF Box")
    mesh = bpy.data.meshes.new("PF_BOX")
    pb_box_obj = bpy.data.objects.new("PF_BOX", mesh)
    bm = bmesh.new()
    bmv = []
    x = 0
    y = 0
    z = 0
    sx = .5
    sy = .5
    sz = .5
    vertices = [
        [x + sx, y + sy, z - sz],
        [x + sx, y - sy, z - sz],
        [x - sx, y - sy, z - sz],
        [x - sx, y + sy, z - sz],
        [x + sx, y + sy, z + sz],
        [x + sx, y - sy, z + sz],
        [x - sx, y - sy, z + sz],
        [x - sx, y + sy, z + sz]
    ]
    for v in vertices:
        bmv.append(bm.verts.new(v))
    bm.faces.new((bmv[0], bmv[1], bmv[2], bmv[3]))  # bottom
    bm.faces.new((bmv[4], bmv[5], bmv[6], bmv[7]))  # top
    bm.faces.new((bmv[0], bmv[1], bmv[5], bmv[4]))  # right
    bm.faces.new((bmv[2], bmv[3], bmv[7], bmv[6]))
    bm.faces.new((bmv[0], bmv[3], bmv[7], bmv[4]))
    bm.faces.new((bmv[1], bmv[2], bmv[6], bmv[5]))
    mesh = pb_box_obj.data
    bm.to_mesh(mesh)
    pb_box_obj.data = mesh
    bm.free()
    t_size = len(pf_transforms)
    for i in range(0, t_size):
        transform = pf_transforms[i]
        p = transform["position"]
        r = transform["rotate"]
        s = transform["scale"]
        print("Transforming pf box:" + " #" + str(i))

        if i != 0:
            cur = pb_box_obj.copy()
        else:
            cur = pb_box_obj
        collection.objects.link(cur)
        cur.select_set(True)
        cur.scale = mathutils.Vector((s["x"], s["y"], s["z"]))
        cur.rotation_mode = 'QUATERNION'
        cur.rotation_quaternion = (r["w"], r["x"], r["y"], r["z"])
        cur.location = mathutils.Vector((p["x"], p["y"], p["z"]))
        cur.select_set(False)
    end = timer()
    # print("PfBox Exclusion entity ids:")
    # print("[")
    # for pf_box in pf_transforms:
    #     print("   \"" + pf_box["id"] + "\",")
    # print("]")
    print("Finished loading scenario in " + str(end - start) + " seconds.")
    return 0
