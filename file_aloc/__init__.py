import bpy
import os
from bpy.utils import register_class
from bpy.utils import unregister_class
from . import bl_import_aloc

from .. import BlenderUI
from bpy_extras.io_utils import ImportHelper, ExportHelper

from bpy.props import (
    StringProperty,
    BoolProperty,
    BoolVectorProperty,
    CollectionProperty,
    PointerProperty,
    IntProperty,
    EnumProperty,
    FloatProperty,
    FloatVectorProperty,
    IntVectorProperty,
)

from bpy.types import (
    Context,
    Panel,
    Operator,
    PropertyGroup,
)


class ImportALOC(bpy.types.Operator, ImportHelper):
    """Load a collision .aloc file"""

    bl_idname = "import_collision.aloc"
    bl_label = "Import Collision ALOC"
    filename_ext = ".aloc"

    filter_glob: StringProperty(
        default="*.aloc",
        options={"HIDDEN"},
    )

    files: CollectionProperty(
        name="File Path",
        type=bpy.types.OperatorFileListElement,
    )

    def draw(self, context):
        if ".aloc" not in self.filepath.lower():
            return

        layout = self.layout

        layout.row(align=True)

    def execute(self, context):
        aloc_paths = [
            "%s\\%s" % (os.path.dirname(self.filepath), aloc_paths.name)
            for aloc_paths in self.files
        ]
        for aloc_path in aloc_paths:
            collection = bpy.data.collections.new(
                bpy.path.display_name_from_filepath(aloc_path)
            )
            context.scene.collection.children.link(collection)

            scenario = bl_import_aloc.load_aloc(
                self, context, collection, aloc_path
            )

            if scenario == 1:
                BlenderUI.MessageBox(
                    'Failed to import scenario "%s"' % aloc_path, "Importing error", "ERROR"
                )
                return {"CANCELLED"}

            layer = bpy.context.view_layer
            layer.update()

        return {"FINISHED"}

# ------------------------------------------------------------------------
#    Registration
# ------------------------------------------------------------------------


classes = [ImportALOC]


def register():
    for cls in classes:
        register_class(cls)

    bpy.types.TOPBAR_MT_file_import.append(menu_func_import_aloc)


def unregister():
    for cls in classes:
        unregister_class(cls)


def menu_func_import_aloc(self, context):
    self.layout.operator(ImportALOC.bl_idname, text="Glacier Collision Mesh (.aloc)")

if __name__ == "__main__":
    register()
