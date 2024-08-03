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

def convert_aloc_to_ply(aloc, filepath):
    vertex_count = 0
    if aloc.data_type == aloc_format.PhysicsDataType.CONVEX_MESH:
        vertex_count = aloc.convex_meshes[0].vertex_count
    ply_file = open(filepath, "w")
    ply_file.writelines(
        [
            "ply\n",
            "format ascii 1.0\n",
            "element vertex " + str(vertex_count) + "\n",
            "property float x\n",
            "property float y\n",
            "property float z\n",
            "end_header\n"
        ]
    )
    if aloc.data_type == aloc_format.PhysicsDataType.CONVEX_MESH:
        for vertex in aloc.convex_meshes[0].data.vertices:
            ply_file.writelines(str(vertex[0]) + " " + str(vertex[1]) + " " + str(vertex[2]) + "\n")
    ply_file.close()


def load_aloc(operator, context, collection, filepath):
    """Imports an aloc mesh from the given path"""

    print("Loading ALOC")
    aloc_name = bpy.path.display_name_from_filepath(filepath)

    aloc = read_aloc(filepath)

    new_mesh = bpy.data.meshes.new(aloc_name)
    obj = bpy.data.objects.new("mesh_name", new_mesh)  # add a new object using the mesh

    scene = context.scene
    scene.collection.objects.link(obj)  # put the object into the scene (link)
    context.view_layer.objects.active = obj
    obj.select_set(True)

    mesh = bpy.context.object.data
    bm = bmesh.new()

    for v in aloc.convex_meshes[0].data.vertices:
        bm.verts.new(v)  # add a new vert

    bm.from_mesh(mesh)
    copy = obj.copy()

    me = bpy.data.meshes.new("%s convexhull" % mesh.name)
    ch = bmesh.ops.convex_hull(bm, input=bm.verts)
    bmesh.ops.delete(
        bm,
        geom=ch["geom_unused"] + ch["geom_interior"],
        context='VERTS',
    )
    # make the bmesh the object's mesh
    bm.to_mesh(mesh)

    copy.name = "%s (convex hull)" % obj.name
    copy.data = me

    scene.collection.objects.link(copy)

    bm.free()  # always do this when finished

    print("Done Importing ALOC")


