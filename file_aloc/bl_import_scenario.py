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


def log(level, msg, filter_field):
    enabled = ["ERROR", "WARNING", "INFO", "DEBUG"]  # Log levels are "DEBUG", "INFO", "WARNING", "ERROR"
    if level in enabled:  # and filter_field == "0031CDA11AFD98A9":
        print("[" + str(level) + "] " + str(filter_field) + ": " + str(msg))
        
        
def load_scenario(operator, context, collection, path_to_alocs_json):
    start = timer()
    log("INFO", "Loading scenario.", "load_scenario")
    log("INFO", "Alocs file: " + path_to_alocs_json, "load_scenario")
    f = open(path_to_alocs_json, "r")
    data = json.loads(f.read())
    f.close()
    transforms = {}
    for hash_and_entity in data['entities']:
        aloc_hash = hash_and_entity['hash']
        entity = hash_and_entity['entity']
        transform = {"position": entity["position"], "rotate": entity["rotation"],
                     "scale": entity["scale"]["data"], "id": entity["id"]}

        if aloc_hash not in transforms:
            transforms[aloc_hash] = []
        transforms[aloc_hash].append(transform)

    log("INFO", "Loading PfBoxes.", "load_scenario")
    alocs_json_dir = os.path.dirname(path_to_alocs_json)
    path_to_pf_boxes_json = "%s\\%s" % (alocs_json_dir, "pfBoxes.json")
    log("INFO", "PfBoxes file: " + path_to_pf_boxes_json, "load_scenario")
    f = open(path_to_pf_boxes_json, "r")
    pb_boxes_data = json.loads(f.read())
    f.close()
    pf_transforms = []
    log("INFO", "Loading file: " + str(path_to_pf_boxes_json), "load_scenario")

    for hash_and_entity in pb_boxes_data['entities']:
        entity = hash_and_entity['entity']
        pf_box_type = entity["type"]["data"]
        log("DEBUG", "PF Box Type: " + str(pf_box_type), "load_scenario")
        if pf_box_type == "PFBT_EXCLUDE_MESH_COLLISION":
            transform = {"position": entity["position"], "rotate": entity["rotation"],
                         "scale": entity["size"]["data"], "id": entity["id"]}
            pf_transforms.append(transform)
    path_to_aloc_dir = "%s\\%s" % (alocs_json_dir, "aloc")
    log("INFO", "Path to aloc dir:" + path_to_aloc_dir, "load_scenario")
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
    aloc_file_count = len(aloc_list)
    mesh_count = 0
    for aloc_i in range(0, aloc_file_count):
        aloc_filename = aloc_list[aloc_i]
        aloc_hash = aloc_filename[:-5]
        if aloc_hash in transforms:
            mesh_count += len(transforms[aloc_filename[:-5]])

    mesh_i = 0
    alocs_in_scenario_count = len(transforms)
    current_aloc_in_scene_index = 0
    for aloc_i in range(0, aloc_file_count):
        aloc_filename = aloc_list[aloc_i]
        aloc_hash = aloc_filename[:-5]
        if aloc_hash not in transforms:
            continue
        if aloc_hash in excluded_aloc_hashes:
            continue
        aloc_path = os.path.join(path_to_aloc_dir, aloc_filename)

        log("INFO", "Loading aloc: " + aloc_hash, "load_scenario")
        try:
            collision_type, objects = load_aloc(
                None, context, aloc_path, False
            )
        except struct.error as err:
            log("DEBUG", "=========================== Error Loading aloc: " + str(aloc_hash) + " Exception: " + str(err) + " ================", "load_scenario")
            continue

        if len(objects) == 0:
            log("DEBUG", "No collidable objects for " + str(aloc_hash), "load_scenario")
            continue
        if not objects:
            log("INFO", "-------------------- Error Loading aloc:" + aloc_hash + " ----------------------", "load_scenario")
            continue
        if collision_type in excluded_collision_types:
            log("DEBUG", "+++++++++++++++++++++ Skipping Non-collidable ALOC: " + aloc_hash + " with collision type: " + str(collision_type) + " +++++++++++++", "load_scenario")
            continue
        t = transforms[aloc_hash]
        current_aloc_in_scene_index += 1
        t_size = len(t)
        for i in range(0, t_size):
            transform = transforms[aloc_hash][i]
            p = transform["position"]
            r = transform["rotate"]
            s = transform["scale"]
            log("INFO", "Transforming aloc [" + str(current_aloc_in_scene_index) + "/" + str(alocs_in_scenario_count) + "]: " + aloc_hash + " #" + str(i) + " Mesh: [" + str(mesh_i + 1) + "/" + str(mesh_count) + "]", "load_scenario")
            mesh_i += 1
            for obj in objects:
                if i != 0:
                    cur = obj.copy()
                else:
                    cur = obj
                collection.objects.link(cur)
                cur.select_set(True)
                cur.name = aloc_hash + " " + transform["id"]
                cur.scale = mathutils.Vector((s["x"], s["y"], s["z"]))
                cur.rotation_mode = 'QUATERNION'
                cur.rotation_quaternion = (r["w"], r["x"], r["y"], r["z"])
                cur.location = mathutils.Vector((p["x"], p["y"], p["z"]))
                cur.select_set(False)

    if len(pf_transforms) > 0:
        log("INFO", "Creating PF Box", "load_scenario")
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
            log("DEBUG", "Transforming pf box:" + " #" + str(i), "load_scenario")

            if i != 0:
                cur = pb_box_obj.copy()
            else:
                cur = pb_box_obj
            collection.objects.link(cur)
            cur.select_set(True)
            cur.name = "PF_BOX " + transform["id"]
            cur.scale = mathutils.Vector((s["x"], s["y"], s["z"]))
            cur.rotation_mode = 'QUATERNION'
            cur.rotation_quaternion = (r["w"], r["x"], r["y"], r["z"])
            cur.location = mathutils.Vector((p["x"], p["y"], p["z"]))
            cur.select_set(False)
        log("DEBUG", "PfBox Exclusion entity ids:", "load_scenario")
        log("DEBUG", "[", "load_scenario")
        for pf_box in pf_transforms:
            log("DEBUG", "   \"" + pf_box["id"] + "\",", "load_scenario")
        log("DEBUG", "]", "load_scenario")
    end = timer()
    log("INFO", "Finished loading scenario in " + str(end - start) + " seconds.", "load_scenario")
    return 0
