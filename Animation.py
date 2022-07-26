import bpy
import json
from . import Bone
from . import MJBA
from . import MRTR

class Animation:
	def import_mjba(self, object):
		bpy.ops.object.mode_set(mode='POSE')
		self.object = object
		self.bones = {}
		if self.object.animation_data == None:
			self.object.animation_data_create()
		elif self.object.animation_data.action != None:
			print(self.object.animation_data.action)
			bpy.data.actions.remove(self.object.animation_data.action)
			bpy.context.scene.frame_start = 1
			bpy.context.scene.frame_end = 1
			bpy.context.scene.frame_current = 1
		self.mjba = MJBA.MJBA()
		self.mjba.import_json("R:\\0090CB9A79180160.MJBA.JSON")
		bpy.context.scene.render.fps = self.mjba.get_fps()
		bpy.context.scene.frame_end = self.mjba.get_frame_count()
		bone_list = self.mjba.get_used_bone_list()
		print(bone_list)
		for bone in bone_list:
			print(bone, "added to self bones")
			self.bones[bone] = Bone.Bone(object, bone)
		for bone1 in object.pose.bones:
			for bone2 in bone_list:
				if bone1.name.lower() == bone2.lower():
					bone1.name = bone2
					print(bone1.name, "was changed to", bone2)
		for frame in range(bpy.context.scene.frame_start, bpy.context.scene.frame_end + 1):
			bpy.context.scene.frame_set(frame)
			for bone in object.pose.bones:
				print(bone.name, "in pose bones")
				if bone.name in self.bones:
					print(bone.name, "in self bones")
					self.bones[bone.name].location = self.mjba.get_bone_location(frame - 1, bone.name)
					object.pose.bones[bone.name].location = self.bones[bone.name].location
					object.pose.bones[bone.name].keyframe_insert(data_path = "location")
					self.bones[bone.name].rotation_quaternion = self.mjba.get_bone_rotation(frame - 1, bone.name)
					object.pose.bones[bone.name].rotation_quaternion = self.bones[bone.name].rotation_quaternion
					object.pose.bones[bone.name].keyframe_insert(data_path = "rotation_quaternion")
	
	def export_mjba(self, object):
		bpy.ops.object.mode_set(mode='POSE')
		self.object = object
		self.bones = {}		
		for fcurve in self.object.animation_data.action.fcurves:
			animation_type = fcurve.data_path[fcurve.data_path.rfind('.') + 1:]
			bone = fcurve.data_path.split('"')[1]
			if bone not in self.bones:
				self.bones[bone] = Bone.Bone(object, bone)
			for keyframe in fcurve.keyframe_points:
				if keyframe.co[0] >= bpy.context.scene.frame_start and keyframe.co[0] <= bpy.context.scene.frame_end:
					if animation_type == "location":
						self.bones[bone].set_position_animated()
					elif animation_type == "rotation_euler":
						self.bones[bone].set_rotation_animated()
					elif animation_type == "rotation_quaternion":
						self.bones[bone].set_rotation_animated()
					elif animation_type == "scale":
						self.bones[bone].set_scale_animated()
		for frame in range(bpy.context.scene.frame_start, bpy.context.scene.frame_end + 1):
			bpy.context.scene.frame_set(frame)
			for bone in object.pose.bones:
				if bone in self.bones:
					self.bones[bone].set_matrix(frame, bone.matrix)