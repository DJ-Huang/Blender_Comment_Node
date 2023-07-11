# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####
# Author Linus Yng
#
# pep8


bl_info = {
    "name": "Comment Node",
    "description": "A Comment Node",
    "author": "Dejhon",
    "version": (0, 2, 0),
    "blender": (2, 90, 0),
    "location": "Node Editor, N-Panel or menu Layout",
    "category": "Node",
}

import bpy
from bpy.props import StringProperty
import textwrap

TW = textwrap.TextWrapper()


def get_lines(text_file):
    for line in text_file.lines:
        yield line.body

class GenericNoteNode(bpy.types.Node):
    ''' Note '''
    bl_idname = 'GenericNoteNode'
    bl_label = 'Comment'
    bl_icon = 'OUTLINER_OB_EMPTY'

    text: StringProperty(
        name='Text',
        default='',
        description="Text to show, if set will override file"
    )

    text_file: StringProperty(
        name='Text File',
        description="Text file to show"
    )

    def format_text(self):
        global TW
        out = []
        if self.text:
            lines = self.text.splitlines()
        elif self.text_file:
            text_file = bpy.data.texts.get(self.text_file)
            if text_file:
                lines = get_lines(text_file)
            else:
                return []
        else:
            return []

        width = self.width
        TW.width = int(width) // 8  # Assuming each character has a width of 6
        for t in lines:
            out.extend(TW.wrap(t))
            out.append("")
        return out

    def init(self, context):
        self.width = 200
        pref = bpy.context.preferences.addons[__name__].preferences
        self.color = pref.note_node_color[:]
        self.use_custom_color = True

    def draw_buttons(self, context, layout):
        has_text = self.text or self.text_file
        if has_text:
            col = layout.column(align=True)
            text_lines = self.format_text()
            for l in text_lines:
                if l:
                    col.label(text=l)
        else:
            col = layout.column(align=True)
            col.prop(self, "text", text="Text")
            col.prop_search(self, 'text_file', bpy.data, 'texts', text='Text file', icon='TEXT')
            col.operator("node.generic_note_from_clipboard", text="From clipboard")

    def draw_buttons_ext(self, context, layout):
        layout.prop(self, "text", text="Text")
        layout.prop_search(self, 'text_file', bpy.data, 'texts', text='Text file', icon='TEXT')
        layout.operator("node.generic_note_from_clipboard", text="From clipboard")
        layout.operator("node.generic_note_to_text", text="To text editor")
        layout.operator("node.generic_note_clear")

    def clear(self):
        self.text = ""
        self.text_file = ""

    def to_text(self):
        text_name = "Generic Note Text"
        text = bpy.data.texts.get(text_name)
        if not text:
            text = bpy.data.texts.new(text_name)
        text.clear()
        text.write(self.text)

def add_node_menu_func(self, context):
    self.layout.operator_context = 'INVOKE_REGION_WIN'
    self.layout.operator("node.add_generic_note_node", text="Generic Note")


class AddGenericNoteNode(bpy.types.Operator):
    bl_idname = "node.add_generic_note_node"
    bl_label = "Add Generic Note Node"

    def execute(self, context):
        bpy.ops.node.add_node(type="GenericNoteNode")
        return {'FINISHED'}


class GenericNoteTextFromClipboard(bpy.types.Operator):
    """
    Update note text from clipboard
    """
    bl_idname = "node.generic_note_from_clipboard"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        text = bpy.context.window_manager.clipboard
        if not text:
            self.report({"INFO"}, "No text selected")
            return {'CANCELLED'}
        node = context.node
        node.text = text
        return {'FINISHED'}


class GenericNoteClear(bpy.types.Operator):
    """
    Clear Note Node
    """
    bl_idname = "node.generic_note_clear"
    bl_label = "Clear"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        node = context.node
        node.clear()
        return {'FINISHED'}


class GenericNoteNodeToText(bpy.types.Operator):
    """
    Put note into a text buffer
    """
    bl_idname = "node.generic_note_to_text"
    bl_label = "To text"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        node = context.node
        text = node.text
        if not text:
            self.report({"INFO"}, "No text in node")
            return {'CANCELLED'}
        node.to_text()
        self.report({"INFO"}, "See text editor: Generic Note Text")
        return {'FINISHED'}

classes = (
    GenericNoteNode,
    AddGenericNoteNode,
    GenericNoteTextFromClipboard,
    GenericNoteClear,
    GenericNoteNodeToText,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.NODE_MT_add.append(add_node_menu_func)


def unregister():
    bpy.types.NODE_MT_add.remove(add_node_menu_func)
    
    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
