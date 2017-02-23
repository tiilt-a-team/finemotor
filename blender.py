import sys
sys.path.append('.')
import bpy
import bgl
import socket
import json
import math
import logging
import mathutils


class TIILTOperator(bpy.types.Operator):
    bl_idname = "object.tiilt"
    bl_label = "TIILT Operator"

    # TODO use Blender's Properties
    # sock_addr = bpy.props.StringProperty(name="Server address")

    def __init__(self):
        print("Starting")
        self.transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.current_mode = 'OBJECT'

    def __del__(self):
        print("Ending")
        self.transport.close()
        print("End")

    @classmethod
    def poll(cls, context):
        return context.area.type == 'VIEW_3D'

    def execute(self, context):
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        if event.type == 'ESC':
            return {'FINISHED'}

        if event.type == 'A':
            data = self.transport.recv(1024).decode()

            if (data == 'add cube'):
                bpy.ops.mesh.primitive_cube_add()
                print('Cube added')
            elif (data == 'add cylinder'):
                bpy.ops.mesh.primitive_cylinder_add()
                print('Cylinder added')
            else: 
                print('Invalid command')
            
            message = input('Do you wish to enter another command?: ')
            self.transport.sendto(message.encode('utf-8'), ('',1234))



        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        try:
            self.transport.connect(('', 1234))
            self.transport.setblocking(False)
        except IOError as e:
            logging.exception(e)
            return {'CANCELLED'}

        print("Started")
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}
        # return context.window_manager.invoke_props_dialog(self)


bpy.utils.register_class(TIILTOperator)
