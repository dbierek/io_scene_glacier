import os

from . import format as aloc_format
from .format import PhysicsCollisionLayerType, PhysicsCollisionType, PhysicsDataType, PhysicsCollisionPrimitiveType
from .. import io_binary
import bpy
import bmesh
import math


def read_aloc(filepath):
    prim_name = bpy.path.display_name_from_filepath(filepath)
    print("Started reading: " + str(prim_name) + "\n")
    print("Loading ALOC file " + filepath)
    fp = os.fsencode(filepath)
    file = open(fp, "rb")
    br = io_binary.BinaryReader(file)
    aloc = aloc_format.Physics()
    aloc.read(filepath)
    br.close()

    return aloc


def convex_hull(bm, mesh, obj, collection, context):
    bm.from_mesh(mesh)
    ch = bmesh.ops.convex_hull(bm, input=bm.verts)
    # bmesh.ops.delete(
    #     bm,
    #     geom=ch["geom_unused"] + ch["geom_interior"],
    #     context='VERTS',
    # )
    bm.to_mesh(mesh)
    obj.data = mesh
    bm.free()
    collection.objects.link(obj)
    context.view_layer.objects.active = obj
    obj.select_set(True)


def set_mesh_aloc_properties(mesh, collision_type, data_type, sub_data_type):
    mask = []
    for col_type in PhysicsCollisionType:
        mask.append(collision_type == col_type.value)
    mesh.aloc_properties.collision_type = mask
    mesh.aloc_properties.aloc_type = str(PhysicsDataType(data_type))
    mesh.aloc_properties.aloc_subtype = str(PhysicsCollisionPrimitiveType(sub_data_type))


def create_new_object(aloc_name, collision_type, data_type):
    mesh = bpy.data.meshes.new(aloc_name)
    set_mesh_aloc_properties(mesh, collision_type, data_type, PhysicsCollisionPrimitiveType.NONE)
    obj = bpy.data.objects.new(aloc_name, mesh)
    return obj


def link_new_object(aloc_name, context):
    obj = bpy.context.active_object
    obj.name = aloc_name
    mesh = obj.data
    mesh.name = aloc_name
    context.view_layer.objects.active = obj
    obj.select_set(True)


def rot(x, y, z):
    return x * math.pi / 2, z * math.pi / 2, y * math.pi / 2


def collidable_layer(collision_layer):
    excluded_collision_layer_types = [
        # PhysicsCollisionLayerType.SHOT_ONLY_COLLISION,
        # PhysicsCollisionLayerType.ACTOR_DYN_BODY,
        # PhysicsCollisionLayerType.ACTOR_PROXY,
        # PhysicsCollisionLayerType.ACTOR_RAGDOLL,
        # PhysicsCollisionLayerType.AI_VISION_BLOCKER,
        # PhysicsCollisionLayerType.AI_VISION_BLOCKER_AMBIENT_ONLY,
        # PhysicsCollisionLayerType.COLLISION_VOLUME_HITMAN_OFF,
        # PhysicsCollisionLayerType.DYNAMIC_COLLIDABLES_ONLY,
        # PhysicsCollisionLayerType.DYNAMIC_COLLIDABLES_ONLY_NO_CHARACTER,
        # PhysicsCollisionLayerType.DYNAMIC_COLLIDABLES_ONLY_NO_CHARACTER_TRANSPARENT,
        # PhysicsCollisionLayerType.DYNAMIC_TRASH_COLLIDABLES,
        # PhysicsCollisionLayerType.HERO_DYN_BODY,
        # PhysicsCollisionLayerType.ITEMS,
        # PhysicsCollisionLayerType.KINEMATIC_COLLIDABLES_ONLY,
        # PhysicsCollisionLayerType.KINEMATIC_COLLIDABLES_ONLY_TRANSPARENT,
        # PhysicsCollisionLayerType.WEAPONS
    ]
    return collision_layer not in excluded_collision_layer_types


def load_aloc(operator, context, filepath, include_non_collidable_layers):
    """Imports an ALOC mesh from the given path"""

    print("Loading ALOC")
    aloc_name = bpy.path.display_name_from_filepath(filepath)
    aloc = read_aloc(filepath)
    collection = context.scene.collection
    objects = []
    if aloc.data_type == aloc_format.PhysicsDataType.CONVEX_MESH:
        for mesh_index in range(aloc.convex_mesh_count):
            obj = create_new_object(aloc_name, aloc.collision_type, aloc.data_type)
            bm = bmesh.new()
            m = aloc.convex_meshes[mesh_index]
            if include_non_collidable_layers or collidable_layer(m.collision_layer):
                for v in m.vertices:
                    bm.verts.new(v)
            else:
                print(
                    "+++++++++++++++++++++ Skipping Non-collidable ALOC mesh: " + aloc_name + " with mesh index: " + str(mesh_index) + " and collision layer type: " + str(
                        m.collision_layer) + " +++++++++++++")
            mesh = obj.data
            convex_hull(bm, mesh, obj, collection, context)
            objects.append(obj)
    elif aloc.data_type == aloc_format.PhysicsDataType.TRIANGLE_MESH:
        for mesh_index in range(aloc.triangle_mesh_count):
            obj = create_new_object(aloc_name, aloc.collision_type, aloc.data_type)
            bm = bmesh.new()
            m = aloc.triangle_meshes[mesh_index]
            if include_non_collidable_layers or collidable_layer(m.collision_layer):
                for v in m.vertices:
                    bm.verts.new(v)
            else:
                print(
                    "+++++++++++++++++++++ Skipping Non-collidable ALOC mesh: " + aloc_name + " with mesh index: " + str(mesh_index) + " and collision layer type: " + str(
                        m.collision_layer) + " +++++++++++++")

            mesh = obj.data
            convex_hull(bm, mesh, obj, collection, context)
            objects.append(obj)
    elif aloc.data_type == aloc_format.PhysicsDataType.PRIMITIVE:
        print("Primitive Type")
        print("Primitive count: " + str(aloc.primitive_count))
        print("Primitive Box count: " + str(aloc.primitive_boxes_count))
        print("Primitive Spheres count: " + str(aloc.primitive_spheres_count))
        print("Primitive Capsules count: " + str(aloc.primitive_capsules_count))
        for mesh_index, box in enumerate(aloc.primitive_boxes):
            if include_non_collidable_layers or collidable_layer(box.collision_layer):
                print("Primitive Box")
                bpy.ops.mesh.primitive_cube_add(
                    location=(box.position[0], box.position[1], box.position[2]),
                    rotation=rot(box.rotation[0], box.rotation[1], box.rotation[2]  ),
                    scale=(box.half_extents[0], box.half_extents[1], box.half_extents[2])
                )
                link_new_object(aloc_name, context)
                obj = bpy.context.active_object
                set_mesh_aloc_properties(obj.data, aloc.collision_type, aloc.data_type, PhysicsCollisionPrimitiveType.BOX)
                objects.append(obj)
            else:
                print(
                    "+++++++++++++++++++++ Skipping Non-collidable ALOC mesh: " + aloc_name + " with mesh index: " + str(mesh_index) + " and collision layer type: " + str(
                        box.collision_layer) + " +++++++++++++")

        for mesh_index, sphere in enumerate(aloc.primitive_spheres):
            if include_non_collidable_layers or collidable_layer(sphere.collision_layer):
                print("Primitive Sphere")
                bpy.ops.mesh.primitive_ico_sphere_add(
                    subdivisions=2,
                    radius=sphere.radius,
                    location=(sphere.position[0], sphere.position[1], sphere.position[2]),
                    rotation=(sphere.rotation[0], sphere.rotation[1], sphere.rotation[2]),
                )
                link_new_object(aloc_name, context)
                obj = bpy.context.active_object
                set_mesh_aloc_properties(obj.data, aloc.collision_type, aloc.data_type, PhysicsCollisionPrimitiveType.SPHERE)
                objects.append(obj)
            else:
                print(
                    "+++++++++++++++++++++ Skipping Non-collidable ALOC mesh: " + aloc_name + " with mesh index: " + str(
                        mesh_index) + " and collision layer type: " + str(
                        sphere.collision_layer) + " +++++++++++++")
        for mesh_index, capsule in enumerate(aloc.primitive_capsules):
            if include_non_collidable_layers or collidable_layer(capsule.collision_layer):
                print("Primitive Capsule")
                bpy.ops.mesh.primitive_ico_sphere_add(
                    subdivisions=2,
                    radius=capsule.radius,
                    location=(capsule.position[0], capsule.position[1], capsule.position[2] + capsule.length),
                    rotation=(capsule.rotation[0], capsule.rotation[1], capsule.rotation[2]),
                )
                link_new_object(aloc_name + "_top", context)
                obj = bpy.context.active_object
                set_mesh_aloc_properties(obj.data, aloc.collision_type, aloc.data_type, PhysicsCollisionPrimitiveType.CAPSULE)
                objects.append(obj)
                bpy.ops.mesh.primitive_cylinder_add(
                    radius=capsule.radius,
                    depth=capsule.length,
                    end_fill_type='NOTHING',
                    location=(capsule.position[0], capsule.position[1], capsule.position[2]),
                    rotation=(capsule.rotation[0], capsule.rotation[1], capsule.rotation[2])
                )
                link_new_object(aloc_name + "_cylinder", context)
                obj = bpy.context.active_object
                set_mesh_aloc_properties(obj.data, aloc.collision_type, aloc.data_type, PhysicsCollisionPrimitiveType.CAPSULE)
                objects.append(obj)
                bpy.ops.mesh.primitive_ico_sphere_add(
                    subdivisions=2,
                    radius=capsule.radius,
                    location=(capsule.position[0], capsule.position[1], capsule.position[2] - capsule.length),
                    rotation=(capsule.rotation[0], capsule.rotation[1], capsule.rotation[2]),
                )
                link_new_object(aloc_name + "_bottom", context)
                obj = bpy.context.active_object
                set_mesh_aloc_properties(obj.data, aloc.collision_type, aloc.data_type, PhysicsCollisionPrimitiveType.CAPSULE)
                objects.append(obj)
            else:
                print(
                    "+++++++++++++++++++++ Skipping Non-collidable ALOC mesh: " + aloc_name + " with mesh index: " + str(mesh_index) + " and collision layer type: " + str(
                        capsule.collision_layer) + " +++++++++++++")

    print("Done Importing ALOC")
    return aloc.collision_type, objects


