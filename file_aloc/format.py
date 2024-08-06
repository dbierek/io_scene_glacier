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
    SHATTER_LINKED = 144
    KINEMATIC_LINKED = 132
    KINEMATIC_LINKED_2 = 192


class PhysicsCollisionType(enum.IntEnum):
    NONE = 0
    STATIC = 1
    RIGIDBODY = 2
    SHATTER_LINKED = 16
    KINEMATIC_LINKED = 32
    BACKWARD_COMPATIBLE = 2147483647


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
        self.has_grb_data = 0
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


class Shatter:
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
        self.shatters = []
        self.shatter_count = 0
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
        print("Loading aloc file " + filepath)

        fp = os.fsencode(filepath)
        file = open(fp, "rb")
        br = io_binary.BinaryReader(file)
        # Header + MeshType Header: sizeof = 23
        self.data_type = br.readUInt()
        self.collision_type = br.readUInt()
        br.readUByteVec(11)  # "ID\0\0\0\u{5}PhysX"
        br.readUByteVec(4)  # Mesh Type ("CVX ", "TRI ", "ICP ", "BCP ")
        if self.data_type == PhysicsDataType.CONVEX_MESH:
            self.convex_mesh_count = br.readUInt()
            # Current position = 23
            for convex_mesh_index in range(self.convex_mesh_count):
                print("Loading mesh " + str(convex_mesh_index) + " of " + str(self.convex_mesh_count))
                # ---- Fixed header for each Convex Mesh sizeof = 80
                # CollisionLayer, position, rotation: sizeof = 36
                convex_mesh = ConvexMesh()
                self.convex_meshes.append(convex_mesh)
                convex_mesh.collision_layer = br.readUInt()
                convex_mesh.position = br.readFloatVec(3)
                convex_mesh.rotation = br.readFloatVec(4)
                # "\0\0.?NXS.VCXM\u{13}\0\0\0\0\0\0\0ICE.CLCL\u{8}\0\0\0ICE.CVHL\u{8}\0\0\0" sizeof = 44
                br.readUByteVec(44)
                # For first mesh, current position = 103 = 0x67
                # ---- Variable data for each Convex Mesh Hull
                # sizeof = 16 + 3*vertex_count + 20*polygon_count + polygons_vertex_count + 2*edge_count + 3*vertex_count + (if (has_grb_data) then 8*edge_count else 0)
                # Example: 00C87539307C6091:
                #  vertex_count: 8
                #  has_grb_data: false
                #  edge_count: 12
                #  polygon_count: 6
                #  polygons_vertex_count: 24
                #  sizeof variable data (no grb) = 16 + 24 + 120 + 24 + 24 + 24 + 0 = 232 = 0xE8
                #  sizeof variable data (with grb) = 16 + 24 + 120 + 24 + 24 + 24 + 96 = 328 = 0x148
                #  Total size (no grb) = 103 + 232 = 0x67 + 0xE8 = 335 = 0x14F
                #  Total size (with grb) = 103 + 328 = 0x67 + 0x148 = 431 = 0x1AF
                print("Starting to read variable convex mesh hull data. Current offset: " + str(br.tell()))
                convex_mesh.vertex_count = br.readUInt()
                print("Num vertices " + str(convex_mesh.vertex_count))

                grb_flag_and_edge_count = br.readUInt()
                convex_mesh.has_grb_data = 0x8000 & grb_flag_and_edge_count
                print("Has_grb_data " + str(convex_mesh.has_grb_data))

                convex_mesh.edge_count = 0x7FFF & grb_flag_and_edge_count
                print("edge_count " + str(convex_mesh.edge_count))
                convex_mesh.polygon_count = br.readUInt()
                print("polygon_count " + str(convex_mesh.polygon_count))
                convex_mesh.polygons_vertex_count = br.readUInt()
                print("polygons_vertex_count " + str(convex_mesh.polygons_vertex_count))
                vertices = []
                for _vertex_index in range(convex_mesh.vertex_count):
                    vertices.append(br.readFloatVec(3))
                convex_mesh.data.vertices = vertices
                print("Finished reading vertices and metadata. Reading convex main hull data")

                # Unused because Blender can build the convex hull
                hull_polygon_data = 0
                for _polygon_index in range(convex_mesh.polygon_count):
                    print("Reading 20 characters of HullPolygonData. Current offset: " + str(br.tell()))
                    hull_polygon_data = br.readUByteVec(20)  # HullPolygonData
                    print(len(hull_polygon_data))
                    # TODO: <------------------ Read past EOF Here on second convex mesh!
                    if len(hull_polygon_data) < 20:
                        break
                if len(hull_polygon_data) < 20:
                    break
                mHullDataVertexData8 = br.readUByteVec(convex_mesh.polygons_vertex_count)  # mHullDataVertexData8 for each polygon's vertices
                print("mHullDataVertexData8 " + str(mHullDataVertexData8))
                mHullDataFacesByEdges8 = br.readUByteVec(convex_mesh.edge_count * 2)  # mHullDataFacesByEdges8
                print("mHullDataFacesByEdges8 " + str(mHullDataVertexData8))
                mHullDataFacesByVertices8 = br.readUByteVec(convex_mesh.vertex_count * 3)  # mHullDataFacesByVertices8
                print("mHullDataFacesByVertices8 " + str(mHullDataVertexData8))
                if convex_mesh.has_grb_data == 1:
                    print("has_grb_data true. Reading edges. Current offset: " + str(br.tell()))
                    mEdges = br.readUByteVec(4 * 2 * convex_mesh.edge_count)  # mEdges
                else:
                    print("has_grb_data false. No edges to read. Current offset: " + str(br.tell()))
                print("Finished reading main convex hull data. Reading remaining convex hull data. Current offset: " + str(br.tell()))
                # ---- End of Variable data for each Convex Mesh Hull

                # Remaining convex hull data
                zero = br.readFloat()  # 0
                print("This should be zero: " + str(zero) + " Current offset: " + str(br.tell()))
                # Local bounds
                bbox_min_x = br.readFloat()  # mHullData.mAABB.getMin(0)
                print("Bbox min x: " + str(bbox_min_x) + " Current offset: " + str(br.tell()))
                bbox_min_y = br.readFloat()  # mHullData.mAABB.getMin(1)
                bbox_min_z = br.readFloat()  # mHullData.mAABB.getMin(2)
                bbox_max_x = br.readFloat()  # mHullData.mAABB.getMax(0)
                bbox_max_y = br.readFloat()  # mHullData.mAABB.getMax(1)
                bbox_max_z = br.readFloat()  # mHullData.mAABB.getMax(2)
                # Mass Info
                mass = br.readFloat()  # mMass
                print("Mass: " + str(mass) + " Current offset: " + str(br.tell()))
                br.readFloatVec(9)  # mInertia
                br.readFloatVec(3)  # mCenterOfMass.x
                gauss_map_flag = br.readFloat()
                print("Gauss Flag: " + str(gauss_map_flag))

                if gauss_map_flag == 1.0:
                    print("Gauss Flag is 1.0, reading Gauss Data")
                    br.readUByteVec(24)  # ICE.SUPM....ICE.GAUS....
                    mSubdiv = br.readInt()  # mSVM->mData.mSubdiv
                    print("mSubdiv: " + str(mSubdiv))

                    num_samples = br.readInt()  # mSVM->mData.mNbSamples
                    print("num_samples: " + str(num_samples))
                    br.readUByteVec(num_samples * 2)
                    br.readUByteVec(8)  # VALE....
                    num_svm_verts = br.readInt()  # mSVM->mData.mNbVerts
                    print("num_svm_verts: " + str(num_svm_verts))
                    num_svm_adj_verts = br.readInt()  # mSVM->mData.mNbAdjVerts
                    print("num_svm_adj_verts: " + str(num_svm_adj_verts))
                    svm_max_index = br.readInt()  # maxIndex
                    print("svm_max_index: " + str(svm_max_index))
                    if svm_max_index <= 0xff:
                        print("svm_max_index <= 0xff. File offset: " + str(br.tell()))
                        br.readUByteVec(num_svm_verts)
                    else:
                        print("svm_max_index > 0xff. File offset: " + str(br.tell()))
                        br.readUByteVec(num_svm_verts * 2)
                    br.readUByteVec(num_svm_adj_verts)
                else:
                    print("Gauss Flag is " + str(gauss_map_flag) + " No Gauss Data")
                print("Finished reading Convex mesh. File offset: " + str(br.tell()))
                mRadius = br.readFloat()
                mExtents_0 = br.readFloat()
                mExtents_1 = br.readFloat()
                mExtents_2 = br.readFloat()


        elif self.data_type == PhysicsDataType.TRIANGLE_MESH:
            self.triangle_mesh_count = br.readUInt()
            for _ in range(self.triangle_mesh_count):
                triangle_mesh = TriangleMesh()
                triangle_mesh.collision_layer = br.readUInt()
                br.seek(55)
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
                br.readUByteVec(1)
                if primitive_type == "BOX":
                    print("Found Primitive Box")
                    self.primitive_boxes_count += 1
                    primitive_box = PrimitiveBox()
                    primitive_box.half_extents = br.readFloatVec(3)
                    primitive_box.collision_layer = br.readUInt64()
                    primitive_box.position = br.readFloatVec(3)
                    primitive_box.rotation = br.readFloatVec(4)
                    self.primitive_boxes.append(primitive_box)
                    print(
                        "Primitive Box: Pos: " + str(primitive_box.position[0]) + str(primitive_box.position[1]) + str(
                            primitive_box.position[2]))
                    print("Primitive Box: half_extents: " + str(primitive_box.half_extents[0]) + str(
                        primitive_box.half_extents[1]) + str(primitive_box.half_extents[2]))
                    print("Primitive Box: rotation: " + str(primitive_box.rotation[0]) + str(
                        primitive_box.rotation[1]) + str(primitive_box.rotation[2]) + str(primitive_box.rotation[3]))
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
        elif self.data_type == PhysicsDataType.SHATTER_LINKED:
            self.shatter_count = br.readUInt()

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
