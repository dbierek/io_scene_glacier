import enum
import os
import sys
import ctypes

from .. import io_binary


class PhysicsDataType(enum.IntEnum):
    NONE = 0
    CONVEX_MESH = 1
    TRIANGLE_MESH = 2
    CONVEX_MESH_AND_TRIANGLE_MESH = 3
    PRIMITIVE = 4
    CONVEX_MESH_AND_PRIMITIVE = 5
    TRIANGLE_MESH_AND_PRIMITIVE = 6


class PhysicsCollisionType(enum.IntEnum):
    NONE = 0
    STATIC = 1
    RIGIDBODY = 2


class PhysicsCollisionLayerType(enum.IntEnum):
    COLLIDE_WITH_ALL = 0
    STATIC_COLLIDABLES_ONLY = 1
    DYNAMIC_COLLIDABLES_ONLY = 2
    STAIRS = 3
    SHOT_ONLY_COLLISION = 4
    DYNAMIC_TRASH_COLLIDABLES = 5
    KINEMATIC_COLLIDABLES_ONLY = 6
    STATIC_COLLIDABLES_ONLY_TRANSPARENT = 7
    DYNAMIC_COLLIDABLES_ONLY_TRANSPARENT = 8
    KINEMATIC_COLLIDABLES_ONLY_TRANSPARENT = 9
    STAIRS_STEPS = 10
    STAIRS_SLOPE = 11
    HERO_PROXY = 12
    ACTOR_PROXY = 13
    HERO_VR = 14
    CLIP = 15
    ACTOR_RAGDOLL = 16
    CROWD_RAGDOLL = 17
    LEDGE_ANCHOR = 18
    ACTOR_DYN_BODY = 19
    HERO_DYN_BODY = 20
    ITEMS = 21
    WEAPONS = 22
    COLLISION_VOLUME_HITMAN_ON = 23
    COLLISION_VOLUME_HITMAN_OFF = 24
    DYNAMIC_COLLIDABLES_ONLY_NO_CHARACTER = 25
    DYNAMIC_COLLIDABLES_ONLY_NO_CHARACTER_TRANSPARENT = 26
    COLLIDE_WITH_STATIC_ONLY = 27
    AI_VISION_BLOCKER = 28
    AI_VISION_BLOCKER_AMBIENT_ONLY = 29
    UNUSED_LAST = 30


class PhysicsCollisionPrimitiveType(enum.IntEnum):
    BOX = 0
    CAPSULE = 1
    SPHERE = 2


class PhysicsCollisionSettings(ctypes.Structure):
    _fields_ = [
        ("data_type", ctypes.c_uint32),
        ("collider_type", ctypes.c_uint32),
    ]


class ConvexMeshData:
    def __init__(self):
        self.vertices = []


class ConvexMesh:
    def __init__(self):
        self.collision_layer = 0
        self.position = [0.0, 0.0, 0.0]
        self.rotation = [0.0, 0.0, 0.0, 0.0]
        self.vertex_count = 0
        self.edge_count = 0
        self.polygon_count = 0
        self.polygons_vertex_count = 0
        self.data = ConvexMeshData()


class TriangleMeshData:
    def __init__(self):
        self.vertices = []


class TriangleMesh:
    def __init__(self):
        self.collision_layer = 0
        self.vertex_count = 0
        self.triangle_count = 0
        self.data = TriangleMeshData()


class PrimitiveBox:
    def __init__(self):
        self.half_extents = [0.0, 0.0, 0.0]
        self.collision_layer = 0
        self.position = [0.0, 0.0, 0.0]
        self.rotation = [0.0, 0.0, 0.0, 0.0]


class PrimitiveCapsule:
    def __init__(self):
        self.radius = 0.0
        self.length = 0.0
        self.collision_layer = 0
        self.position = [0.0, 0.0, 0.0]
        self.rotation = [0.0, 0.0, 0.0, 0.0]


class PrimitiveSphere:
    def __init__(self):
        self.radius = 0.0
        self.collision_layer = 0
        self.position = [0.0, 0.0, 0.0]
        self.rotation = [0.0, 0.0, 0.0, 0.0]


class Physics:
    def __init__(self):
        self.data_type = PhysicsDataType.NONE
        self.collision_type = PhysicsCollisionType.NONE
        self.convex_meshes = []
        self.convex_mesh_count = 0
        self.triangle_meshes = []
        self.triangle_mesh_count = 0
        self.primitive_count = []
        self.primitive_boxes = []
        self.primitive_boxes_count = 0
        self.primitive_capsules = []
        self.primitive_capsules_count = 0
        self.primitive_spheres = []
        self.primitive_spheres_count = 0
        if not os.environ["PATH"].startswith(
            os.path.abspath(os.path.dirname(__file__))
        ):
            os.environ["PATH"] = (
                os.path.abspath(os.path.dirname(__file__))
                + os.pathsep
                + os.environ["PATH"]
            )
        self.lib = ctypes.CDLL(
            os.path.abspath(os.path.join(os.path.dirname(__file__), "alocgen.dll")),
            winmode=0,
        )
        self.lib.AddConvexMesh.argtypes = (
            ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_float),
            ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.c_uint64,
        )
        self.lib.AddConvexMesh.restype = ctypes.c_int
        self.lib.AddTriangleMesh.argtypes = (
            ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_float),
            ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.c_uint64,
        )
        self.lib.AddTriangleMesh.restype = ctypes.c_int
        self.lib.AddPrimitiveBox.argtypes = (
            ctypes.POINTER(ctypes.c_float),
            ctypes.c_uint64,
            ctypes.POINTER(ctypes.c_float),
            ctypes.POINTER(ctypes.c_float),
        )
        self.lib.AddPrimitiveBox.restype = ctypes.c_int
        self.lib.AddPrimitiveCapsule.argtypes = (
            ctypes.c_float,
            ctypes.c_float,
            ctypes.c_uint64,
            ctypes.POINTER(ctypes.c_float),
            ctypes.POINTER(ctypes.c_float),
        )
        self.lib.AddPrimitiveCapsule.restype = ctypes.c_int
        self.lib.AddPrimitiveSphere.argtypes = (
            ctypes.c_float,
            ctypes.c_uint64,
            ctypes.POINTER(ctypes.c_float),
            ctypes.POINTER(ctypes.c_float),
        )
        self.lib.AddPrimitiveSphere.restype = ctypes.c_int
        self.lib.SetCollisionSettings.argtypes = (
            ctypes.POINTER(PhysicsCollisionSettings),
        )
        self.lib.SetCollisionSettings.restype = ctypes.c_int
        self.lib.NewPhysics()

    def write(self, filepath):
        self.lib.Write(filepath)

    def read(self, filepath):
        fp = os.fsencode(filepath)
        file = open(fp, "rb")
        br = io_binary.BinaryReader(file)
        self.data_type = br.readUInt()
        self.collision_type = br.readUInt()
        br.seek(23)
        if self.data_type == PhysicsDataType.CONVEX_MESH:
            self.convex_mesh_count = br.readUInt()
            for _ in range(self.convex_mesh_count):
                convex_mesh = ConvexMesh()
                convex_mesh.collision_layer = br.readUInt()
                convex_mesh.position = br.readFloatVec(3)
                convex_mesh.rotation = br.readFloatVec(4)
                br.seek(103)
                convex_mesh.vertex_count = br.readUInt()
                convex_mesh.edge_count = br.readUInt()
                convex_mesh.polygon_count = br.readUInt()
                convex_mesh.polygons_vertex_count = br.readUInt()
                vertices = []
                for __ in range(convex_mesh.vertex_count):
                    vertices.append(br.readFloatVec(3))
                convex_mesh.data.vertices = vertices
                self.convex_meshes.append(convex_mesh)
        elif self.data_type == PhysicsDataType.TRIANGLE_MESH:
            self.triangle_mesh_count = br.readUInt()
            br.seek(55)
            for _ in range(self.triangle_mesh_count):
                triangle_mesh = TriangleMesh()
                triangle_mesh.collision_layer = br.readUInt()
                triangle_mesh.vertex_count = br.readUInt()
                triangle_mesh.triangle_count = br.readUInt()
                vertices = []
                for __ in range(triangle_mesh.vertex_count):
                    vertices.append(br.readFloatVec(3))
                triangle_mesh.data.vertices = vertices
                self.triangle_meshes.append(triangle_mesh)
        elif self.data_type == PhysicsDataType.PRIMITIVE:
            print("Found primitive")
            primitive_count = br.readUInt()
            for _ in range(primitive_count):
                primitive_type = br.readString(3).decode("utf-8")
                print("Primitive type: " + primitive_type)
                br.readString(1)
                if primitive_type == "BOX":
                    print("Found Primitive Box")
                    self.primitive_boxes_count += 1
                    primitive_box = PrimitiveBox()
                    primitive_box.half_extents = br.readFloatVec(3)
                    primitive_box.collision_layer = br.readUInt64()
                    primitive_box.position = br.readFloatVec(3)
                    primitive_box.rotation = br.readFloatVec(4)
                    self.primitive_boxes.append(primitive_box)
                    print("Primitive Box: Pos: " + str(primitive_box.position[0]) + str(primitive_box.position[1]) + str(primitive_box.position[2]))
                    print("Primitive Box: half_extents: " + str(primitive_box.half_extents[0]) + str(primitive_box.half_extents[1]) + str(primitive_box.half_extents[2]))
                    print("Primitive Box: rotation: " + str(primitive_box.rotation[0]) + str(primitive_box.rotation[1]) + str(primitive_box.rotation[2]) + str(primitive_box.rotation[3]))
                    print("Primitive Box: collision_layer: " + str(primitive_box.collision_layer))

                elif primitive_type == "CAP":
                    self.primitive_capsules_count += 1
                    primitive_capsule = PrimitiveCapsule()
                    primitive_capsule.radius = br.readFloat()
                    primitive_capsule.length = br.readFloat()
                    primitive_capsule.collision_layer = br.readUInt64()
                    primitive_capsule.position = br.readFloatVec(3)
                    primitive_capsule.rotation = br.readFloatVec(4)
                    self.primitive_capsules.append(primitive_capsule)
                elif primitive_type == "SPH":
                    self.primitive_spheres_count += 1
                    primitive_sphere = PrimitiveSphere()
                    primitive_sphere.radius = br.readFloat()
                    primitive_sphere.collision_layer = br.readUInt64()
                    primitive_sphere.position = br.readFloatVec(3)
                    primitive_sphere.rotation = br.readFloatVec(4)
                    self.primitive_spheres.append(primitive_sphere)
            self.primitive_count = self.primitive_capsules_count + self.primitive_boxes_count + self.primitive_spheres_count

        br.close()

    def set_collision_settings(self, settings):
        self.lib.SetCollisionSettings(ctypes.byref(settings))

    def add_convex_mesh(self, vertices_list, indices_list, collider_layer):
        vertices = (ctypes.c_float * len(vertices_list))(*vertices_list)
        indices = (ctypes.c_uint32 * len(indices_list))(*indices_list)
        self.lib.AddConvexMesh(
            len(vertices_list),
            vertices,
            int(len(indices_list) / 3),
            indices,
            collider_layer,
        )

    def add_triangle_mesh(self, vertices_list, indices_list, collider_layer):
        vertices = (ctypes.c_float * len(vertices_list))(*vertices_list)
        indices = (ctypes.c_uint32 * len(indices_list))(*indices_list)
        self.lib.AddTriangleMesh(
            len(vertices_list),
            vertices,
            int(len(indices_list) / 3),
            indices,
            collider_layer,
        )

    def add_primitive_box(
        self, half_extents_list, collider_layer, position_list, rotation_list
    ):
        half_extents = (ctypes.c_float * len(half_extents_list))(*half_extents_list)
        position = (ctypes.c_float * len(position_list))(*position_list)
        rotation = (ctypes.c_float * len(rotation_list))(*rotation_list)
        self.lib.AddPrimitiveBox(half_extents, collider_layer, position, rotation)

    def add_primitive_capsule(
        self, radius, length, collider_layer, position_list, rotation_list
    ):
        position = (ctypes.c_float * len(position_list))(*position_list)
        rotation = (ctypes.c_float * len(rotation_list))(*rotation_list)
        self.lib.AddPrimitiveCapsule(radius, length, collider_layer, position, rotation)

    def add_primitive_sphere(
        self, radius, collider_layer, position_list, rotation_list
    ):
        position = (ctypes.c_float * len(position_list))(*position_list)
        rotation = (ctypes.c_float * len(rotation_list))(*rotation_list)
        self.lib.AddPrimitiveSphere(radius, collider_layer, position, rotation)
