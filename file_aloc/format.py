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
    KINEMATIC_LINKED = 132
    SHATTER_LINKED = 144
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


class ConvexMesh:
    def __init__(self):
        self.collision_layer = 0
        self.position = [0.0, 0.0, 0.0]
        self.rotation = [0.0, 0.0, 0.0, 0.0]
        self.vertex_count = 0
        self.vertices = []
        self.has_grb_data = 0
        self.edge_count = 0
        self.polygon_count = 0
        self.polygons_vertex_count = 0


class TriangleMesh:
    def __init__(self):
        self.collision_layer = 0
        self.serial_flags = 0
        self.vertex_count = 0
        self.triangle_count = 0
        self.vertices = []
        self.triangle_data = []


class Shatter:
    def __init__(self):
        self.collision_layer = 0
        self.vertex_count = 0
        self.triangle_count = 0


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


def read_convex_mesh(br):
    # Start of first convex mesh, offset = 27
    # ---- Fixed header for each Convex Mesh sizeof = 80
    # CollisionLayer, position, rotation: sizeof = 36
    convex_mesh = ConvexMesh()
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
    convex_mesh.vertices = vertices
    print("Finished reading vertices and metadata. Reading convex main hull data")

    # Unused because Blender can build the convex hull
    hull_polygon_data = 0
    for _polygon_index in range(convex_mesh.polygon_count):
        # print("Reading 20 characters of HullPolygonData. Current offset: " + str(br.tell()))
        hull_polygon_data = br.readUByteVec(20)  # HullPolygonData
        # print(len(hull_polygon_data))
        # TODO: <------------------ Read past EOF Here on second convex mesh!
        if len(hull_polygon_data) < 20:
            break
    if len(hull_polygon_data) < 20:
        return
    mHullDataVertexData8 = br.readUByteVec(
        convex_mesh.polygons_vertex_count)  # mHullDataVertexData8 for each polygon's vertices
    # print("mHullDataVertexData8 " + str(mHullDataVertexData8))
    mHullDataFacesByEdges8 = br.readUByteVec(convex_mesh.edge_count * 2)  # mHullDataFacesByEdges8
    # print("mHullDataFacesByEdges8 " + str(mHullDataVertexData8))
    mHullDataFacesByVertices8 = br.readUByteVec(convex_mesh.vertex_count * 3)  # mHullDataFacesByVertices8
    # print("mHullDataFacesByVertices8 " + str(mHullDataVertexData8))
    if convex_mesh.has_grb_data == 1:
        print("has_grb_data true. Reading edges. Current offset: " + str(br.tell()))
        mEdges = br.readUByteVec(4 * 2 * convex_mesh.edge_count)  # mEdges
    else:
        print("has_grb_data false. No edges to read. Current offset: " + str(br.tell()))
    print(
        "Finished reading main convex hull data. Reading remaining convex hull data. Current offset: " + str(br.tell()))
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
    return convex_mesh


def read_triangle_mesh(br):
    # Start of first triangle mesh, offset = 27
    triangle_mesh = TriangleMesh()
    triangle_mesh.collision_layer = br.readUInt()
    br.readUByteVec(16)  # \0\0\0\0NXS.MESH....\u{15}\0\0\0
    # Offset: 47
    br.readUByteVec(4)  # midPhaseId
    print("Reading serial_flags. Current offset: " + str(br.tell()))

    triangle_mesh.serial_flags = br.readInt()
    # Example Serial Flag: 6 = 00000110: IMSF_FACE_REMAP | IMSF_8BIT_INDICES
    # IMSF_MATERIALS       =    (1 << 0), // ! < if set, the cooked mesh file contains per-triangle material indices
    # IMSF_FACE_REMAP      =    (1 << 1), // ! < if set, the cooked mesh file contains a remap table
    # IMSF_8BIT_INDICES    =    (1 << 2), // ! < if set, the cooked mesh file contains 8bit indices (topology)
    # IMSF_16BIT_INDICES   =    (1 << 3), // ! < if set, the cooked mesh file contains 16bit indices (topology)
    # IMSF_ADJACENCIES     =    (1 << 4), // ! < if set, the cooked mesh file contains adjacency structures
    # IMSF_GRB_DATA        =    (1 << 5)  // ! < if set, the cooked mesh file contains GRB data structures
    print("Reading Vertex_count: Current offset: " + str(br.tell()))
    triangle_mesh.vertex_count = br.readUInt()
    print("vertex_count: " + str(triangle_mesh.vertex_count))
    triangle_mesh.triangle_count = br.readUInt()
    print("triangle_count: " + str(triangle_mesh.triangle_count))
    vertices = []
    for vertex_index in range(triangle_mesh.vertex_count):
        vertex = br.readFloatVec(3)
        # print("vertex " + str(vertex_index) + ": " + str(vertex))
        vertices.append(vertex)
    triangle_mesh.vertices = vertices
    # Check serial flag
    triangle_data = []
    print("serial Flags: " + str(triangle_mesh.serial_flags))
    is_8bit = (triangle_mesh.serial_flags >> 2) & 1 == 1
    print("is_8bit: " + str(is_8bit))
    is_16bit = (triangle_mesh.serial_flags >> 3) & 1 == 1
    print("is_16bit: " + str(is_16bit))
    if is_8bit:
        print("is_8bit. Reading triangle bytes")
        for triangle_index in range(triangle_mesh.triangle_count * 3):
            triangle_byte = br.readUByte()
            # print("Triangle_byte: " + str(triangle_byte))
            triangle_data.append(triangle_byte)
    elif is_16bit:
        print("is_16bit. Reading triangle byte pairs")
        for triangle_index in range(triangle_mesh.triangle_count * 3):
            triangle_byte_pair = br.readUByteVec(2)
            # print("Triangle_byte_pair: " + str(triangle_byte_pair))
            triangle_data.append(triangle_byte_pair)
    else:
        print("Not 8 or 16 bit. Reading triangle ints")
        for triangle_index in range(triangle_mesh.triangle_count * 3):
            triangle_int = br.readInt()
            # print("Triangle_Int: " + str(triangle_int))
            triangle_data.append(triangle_int)
    triangle_mesh.triangle_data = triangle_data
    material_indices = (triangle_mesh.serial_flags >> 0) & 1 == 1
    print("material_indices: " + str(material_indices))

    if material_indices:
        br.readUByteVec(2 * triangle_mesh.triangle_count)  # material_indices
    face_remap = (triangle_mesh.serial_flags >> 1) & 1 == 1
    print("face_remap: " + str(face_remap))

    if face_remap:
        max_id = br.readInt()
        print("max_id: " + str(max_id))
        if is_8bit:
            face_remap_val = br.readUByteVec(triangle_mesh.triangle_count)
            # print("face_remap_val 8bit: " + str(face_remap_val))

        elif is_16bit:
            face_remap_val = br.readUByteVec(triangle_mesh.triangle_count * 2)
            # print("face_remap_val 16bit: " + str(face_remap_val))
        else:
            for triangle_index in range(triangle_mesh.triangle_count):
                face_remap_val = br.readInt()
                # print("face_remap_val int: " + str(face_remap_val))
    adjacencies = (triangle_mesh.serial_flags >> 4) & 1 == 1
    print("adjacencies: " + str(adjacencies))
    if adjacencies:
        for triangle_index in range(triangle_mesh.triangle_count * 3):
            br.readInt()
    # Write midPhaseStructure. Is it BV4? -> BV4TriangleMeshBuilder::saveMidPhaseStructure
    print("Reading BV4: Current offset: " + str(br.tell()))
    bv4 = br.readString(3)  # "BV4."
    br.readUByte()
    print("Should say bv4: " + str(bv4))
    bv4_version = br.readIntBigEndian()  # Bv4 Structure Version. Is always 1, so the midPhaseStructure will be bigEndian
    print("BV4 version. Should be 1: " + str(bv4_version))
    br.readFloat()  # mData.mBV4Tree.mLocalBounds.mCenter.x
    br.readFloat()  # mData.mBV4Tree.mLocalBounds.mCenter.y
    br.readFloat()  # mData.mBV4Tree.mLocalBounds.mCenter.z
    br.readFloat()  # mData.mBV4Tree.mLocalBounds.mCenter.mExtentsMagnitude
    br.readUByteVec(4)  # mData.mBV4Tree.mInitData
    # #ifdef GU_BV4_QUANTIZED_TREE
    br.readFloat()  # mData.mBV4Tree.mCenterOrMinCoeff.x
    br.readFloat()  # mData.mBV4Tree.mCenterOrMinCoeff.y
    br.readFloat()  # mData.mBV4Tree.mCenterOrMinCoeff.z
    br.readFloat()  # mData.mBV4Tree.mExtentsOrMaxCoeff.x
    br.readFloat()  # mData.mBV4Tree.mExtentsOrMaxCoeff.y
    br.readFloat()  # mData.mBV4Tree.mExtentsOrMaxCoeff.z
    # endif
    print("Reading mNbNodes: Current offset: " + str(br.tell()))
    mNbNodes = br.readIntBigEndian()  # mData.mBV4Tree.mNbNodes
    print("mNbNodes: " + str(mNbNodes))

    for _mNbNodesIndex in range(mNbNodes):
        # #ifdef GU_BV4_QUANTIZED_TREE
        br.readUByteVec(12)  # node.mAABB.mData[0].mExtents
        # else
        # br.readFloatVec(6)  # node.mAABB.mCenter.x
        # endif
        br.readUByteVec(4)  # node.mData
    # End midPhaseStructure

    br.readFloat()  # mMeshData.mGeomEpsilon
    bbox_min_x = br.readFloat()  # mMeshData.mAABB.minimum.x
    print("mMeshData.mAABB.minimum.x: " + str(bbox_min_x))
    br.readFloat()  # mMeshData.mAABB.minimum.y
    br.readFloat()  # mMeshData.mAABB.minimum.z
    br.readFloat()  # mMeshData.mAABB.maximum.x
    br.readFloat()  # mMeshData.mAABB.maximum.y
    bbox_min_z = br.readFloat()  # mMeshData.mAABB.maximum.z
    print("mMeshData.mAABB.maximum.z: " + str(bbox_min_z))

    # if(mMeshData.mExtraTrigData)
    mNbvTriangles = br.readInt()  # mMeshData.mNbTriangles
    print("mNbvTriangles: " + str(mNbvTriangles))

    br.readUByteVec(mNbvTriangles)
    # else
    # br.readUByteVec(4)  # 0
    # endif

    # GRB Write
    has_grb = (triangle_mesh.serial_flags >> 5) & 1 == 1
    print("has_grb: " + str(has_grb))

    if has_grb:
        for _triangle_index in range(triangle_mesh.triangle_count * 3):
            if is_8bit:
                br.readUByte()
            elif is_16bit:
                br.readUByteVec(2)
            else:
                br.readInt()
        br.readUIntVec(triangle_mesh.triangle_count * 4)  # mMeshData.mGRB_triAdjacencies
        br.readUIntVec(triangle_mesh.triangle_count)  # mMeshData.mGRB_faceRemap
        # Write midPhaseStructure BV3 -> BV32TriangleMeshBuilder::saveMidPhaseStructure
        bv32 = br.readString(4)  # "BV32"
        print("Reading BV32: " + str(bv32) + " File Offset: " + str(br.tell()))
        br.readUByteVec(4)  # Bv32 Structure Version. If 1, the midPhaseStructure will be bigEndian
        br.readFloat()  # mData.mBV4Tree.mLocalBounds.mCenter.x
        br.readFloat()  # mData.mBV4Tree.mLocalBounds.mCenter.y
        br.readFloat()  # mData.mBV4Tree.mLocalBounds.mCenter.z
        br.readFloat()  # mData.mBV4Tree.mLocalBounds.mCenter.mExtentsMagnitude
        br.readUByteVec(4)  # mData.mBV4Tree.mInitData
        mNbPackedNodes = br.readInt()  # mData.mBV4Tree.mNbPackedNodes
        print("mNbPackedNodes: " + str(mNbPackedNodes))
        mNbPackedNodesBE = br.readIntBigEndian()  # mData.mBV4Tree.mNbPackedNodes
        print("mNbPackedNodesBE: " + str(mNbPackedNodesBE))
        for _mNbNodesIndex in range(mNbPackedNodes):
            mNbNodes = br.readInt(4)  # node.mNbNodes
            # print("mNbNodes: " + str(mNbNodes))
            mNbNodesBE = br.readIntBigEndian(4)  # node.mNbNodes
            # print("mNbNodesBE: " + str(mNbNodesBE))
            br.readUByteVec(4 * mNbNodes)  # node.mData
            br.readFloatVec(4 * mNbNodes)  # node.mCenter[0].x
            br.readFloatVec(4 * mNbNodes)  # node.mExtents[0].x
        # End midPhaseStructure
        # End GRB Write
    return triangle_mesh

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
        # End of header. Current offset = 23
        # PhysicsDataTypes
        # NONE = 0
        # CONVEX_MESH = 1
        # TRIANGLE_MESH = 2
        # CONVEX_MESH_AND_TRIANGLE_MESH = 3
        # PRIMITIVE = 4
        # CONVEX_MESH_AND_PRIMITIVE = 5
        # TRIANGLE_MESH_AND_PRIMITIVE = 6
        # KINEMATIC_LINKED = 132
        # SHATTER_LINKED = 144
        # KINEMATIC_LINKED_2 = 192

        # Current position = 23
        if self.data_type == PhysicsDataType.CONVEX_MESH:
            self.convex_mesh_count = br.readUInt()
            for convex_mesh_index in range(self.convex_mesh_count):
                print("Loading Convex mesh " + str(convex_mesh_index) + " of " + str(self.convex_mesh_count))
                self.convex_meshes.append(read_convex_mesh(br))
        elif self.data_type == PhysicsDataType.TRIANGLE_MESH:
            self.triangle_mesh_count = br.readUInt()
            for triangle_mesh_index in range(self.triangle_mesh_count):
                print("Loading Triangle mesh " + str(triangle_mesh_index) + " of " + str(self.triangle_mesh_count))
                self.triangle_meshes.append(read_triangle_mesh(br))
        elif self.data_type == PhysicsDataType.CONVEX_MESH_AND_TRIANGLE_MESH:
            self.convex_mesh_count = br.readUInt()
            for convex_mesh_index in range(self.convex_mesh_count):
                print("Loading Convex mesh " + str(convex_mesh_index) + " of " + str(self.convex_mesh_count))
                self.convex_meshes.append(read_convex_mesh(br))
            self.triangle_mesh_count = br.readUInt()
            for triangle_mesh_index in range(self.triangle_mesh_count):
                print("Loading Triangle mesh " + str(triangle_mesh_index) + " of " + str(self.triangle_mesh_count))
                self.triangle_meshes.append(read_triangle_mesh(br))
        elif self.data_type == PhysicsDataType.PRIMITIVE:
            print("Found primitive")
            primitive_count = br.readUInt()
            # 27
            for _ in range(primitive_count):  # size of box = 52
                primitive_type = br.readString(3).decode("utf-8")
                print("Primitive type: " + primitive_type)
                br.readUByteVec(1)
                if primitive_type == "BOX":
                    print("Loading Primitive Box")
                    primitive_box = PrimitiveBox()
                    # 31
                    primitive_box.half_extents = br.readFloatVec(3)
                    # 43
                    primitive_box.collision_layer = br.readUInt64()
                    # 51
                    primitive_box.position = br.readFloatVec(3)
                    # 63
                    primitive_box.rotation = br.readFloatVec(4)
                    # 79
                    print(
                        "Primitive Box: Pos: " + str(primitive_box.position[0]) + str(primitive_box.position[1]) + str(
                            primitive_box.position[2]))
                    print("Primitive Box: half_extents: " + str(primitive_box.half_extents[0]) + str(
                        primitive_box.half_extents[1]) + str(primitive_box.half_extents[2]))
                    print("Primitive Box: rotation: " + str(primitive_box.rotation[0]) + str(
                        primitive_box.rotation[1]) + str(primitive_box.rotation[2]) + str(primitive_box.rotation[3]))
                    print("Primitive Box: collision_layer: " + str(primitive_box.collision_layer))
                    self.primitive_boxes_count += 1
                    self.primitive_boxes.append(primitive_box)

                elif primitive_type == "CAP":
                    primitive_capsule = PrimitiveCapsule()
                    primitive_capsule.radius = br.readFloat()
                    primitive_capsule.length = br.readFloat()
                    primitive_capsule.collision_layer = br.readUInt64()
                    primitive_capsule.position = br.readFloatVec(3)
                    primitive_capsule.rotation = br.readFloatVec(4)
                    self.primitive_capsules_count += 1
                    self.primitive_capsules.append(primitive_capsule)
                elif primitive_type == "SPH":
                    primitive_sphere = PrimitiveSphere()
                    primitive_sphere.radius = br.readFloat()
                    primitive_sphere.collision_layer = br.readUInt64()
                    primitive_sphere.position = br.readFloatVec(3)
                    primitive_sphere.rotation = br.readFloatVec(4)
                    self.primitive_spheres_count += 1
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
