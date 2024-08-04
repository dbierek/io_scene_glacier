import os

from . import format as aloc_format
from .. import io_binary
import bpy
import bmesh


def read_aloc(filepath):
    prim_name = bpy.path.display_name_from_filepath(filepath)
    print("Started reading: " + str(prim_name) + "\n")
    print("Loading AIRG file " + filepath)
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


def create_new_object(aloc_name):
    mesh = bpy.data.meshes.new(aloc_name)
    obj = bpy.data.objects.new(aloc_name, mesh)
    return obj


def link_new_object(aloc_name, context):
    obj = bpy.context.active_object
    obj.name = aloc_name
    mesh = obj.data
    mesh.name = aloc_name
    context.view_layer.objects.active = obj
    obj.select_set(True)


def load_aloc(operator, context, filepath):
    """Imports an ALOC mesh from the given path"""

    print("Loading ALOC")
    aloc_name = bpy.path.display_name_from_filepath(filepath)
    aloc = read_aloc(filepath)
    collection = context.scene.collection
    if aloc.data_type == aloc_format.PhysicsDataType.CONVEX_MESH:
        obj = create_new_object(aloc_name)
        bm = bmesh.new()
        for v in aloc.convex_meshes[0].data.vertices:
            bm.verts.new(v)
        mesh = obj.data
        convex_hull(bm, mesh, obj, collection, context)
    elif aloc.data_type == aloc_format.PhysicsDataType.TRIANGLE_MESH:
        obj = create_new_object(aloc_name)
        bm = bmesh.new()
        for v in aloc.triangle_meshes[0].data.vertices:
            bm.verts.new(v)
        mesh = bpy.context.object.data
        convex_hull(bm, mesh, obj, collection, context)
    elif aloc.data_type == aloc_format.PhysicsDataType.PRIMITIVE:
        print("Primitive Type")
        print("Primitive count: " + str(aloc.primitive_count))
        print("Primitive Box count: " + str(aloc.primitive_boxes_count))
        print("Primitive Spheres count: " + str(aloc.primitive_spheres_count))
        print("Primitive Capsules count: " + str(aloc.primitive_capsules_count))
        for box in aloc.primitive_boxes:
            print("Primitive Box")
            bpy.ops.mesh.primitive_cube_add(
                location=(box.position[0], box.position[1], box.position[2]),
                rotation=(box.rotation[0], box.rotation[1], box.rotation[2]),
                scale=(box.half_extents[0] * 2, box.half_extents[1] * 2, box.half_extents[2] * 2)
            )
            link_new_object(aloc_name, context)
        for sphere in aloc.primitive_spheres:
            print("Primitive Sphere")
            bpy.ops.mesh.primitive_ico_sphere_add(
                subdivisions=2,
                radius=sphere.radius,
                location=(sphere.position[0], sphere.position[1], sphere.position[2]),
                rotation=(sphere.rotation[0], sphere.rotation[1], sphere.rotation[2]),
            )
            link_new_object(aloc_name, context)
        for capsule in aloc.primitive_capsules:
            print("Primitive Capsule")
            bpy.ops.mesh.primitive_ico_sphere_add(
                subdivisions=2,
                radius=capsule.radius,
                location=(capsule.position[0], capsule.position[1], capsule.position[2] + capsule.length),
                rotation=(capsule.rotation[0], capsule.rotation[1], capsule.rotation[2]),
            )
            link_new_object(aloc_name + "_top", context)
            bpy.ops.mesh.primitive_cylinder_add(
                radius=capsule.radius,
                depth=capsule.length,
                end_fill_type='NOTHING',
                location=(capsule.position[0], capsule.position[1], capsule.position[2]),
                rotation=(capsule.rotation[0], capsule.rotation[1], capsule.rotation[2])
            )
            link_new_object(aloc_name + "_cylinder", context)
            bpy.ops.mesh.primitive_ico_sphere_add(
                subdivisions=2,
                radius=capsule.radius,
                location=(capsule.position[0], capsule.position[1], capsule.position[2] - capsule.length),
                rotation=(capsule.rotation[0], capsule.rotation[1], capsule.rotation[2]),
            )
            link_new_object(aloc_name + "_bottom", context)

    print("Done Importing ALOC")
    return 0


