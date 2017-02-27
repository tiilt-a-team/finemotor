import sys
sys.path.append('.')
import bpy
import bgl
import socket
import json
import math
import logging
import mathutils


def read_command(transport):
    try:
        line = transport.readline()
        if not line:
            return
        data = json.loads(line)

    except ValueError as e:
        logging.exception(e)
        raise IOError()

    try:
        cmd = data['__cmd__']
        del data['__cmd__']
    except KeyError as e:
        logging.exception(e)
        raise IOError()

    return cmd, data



class TIILTOperator(bpy.types.Operator):
    bl_idname = "object.tiilt"
    bl_label = "TIILT Operator"

    # TODO use Blender's Properties
    # sock_addr = bpy.props.StringProperty(name="Server address")

    def __init__(self):
        print("Starting")
        self.transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sockfile = None

        _commands = [
        self.view_top,
        self.view_bottom,
        self.add_cube,
        ]

        self.commands = {f.__name__:f for f in _commands}
        self._timer = None

        self.current_mode = 'OBJECT'

    def __del__(self):
        print("Ending")
        self.transport.close()

        if self.sockfile:
            self.sockfile.close()

        print("End")

    @classmethod
    def poll(cls, context):
        return context.area.type == 'VIEW_3D'

    def execute(self, context):
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        if event.type == 'ESC':
            context.window_manager.event_timer_remove(self._timer)
            return {'FINISHED'}

        if event.type == 'A':
            #PART THAT NEEDS TO BE MODIFIED FOR TESTING
            self.add_cube()
        if event.type == 'TIMER':
            try:
                cmd = read_command(self.sockfile)
            except IOError as e:
                logging.exception(e)
            else:
                if cmd:
                    func, kwargs = cmd
                    print(func, kwargs)
                    if func in self.commands:
                        self.commands[func](**kwargs)

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        try:
            self.transport.connect(('', 1234))
            self.transport.setblocking(False)
            self.sockfile = self.transport.makefile()

        except IOError as e:
            logging.exception(e)
            return {'CANCELLED'}

        print("Started")
        self._timer = context.window_manager.event_timer_add(0.01, context.window)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}
        # return context.window_manager.invoke_props_dialog(self)

    def view_front(self):
        self.view_numpad('FRONT')

    def view_top(self):
        self.view_numpad('TOP')

    def view_bottom(self):
        self.view_numpad('BOTTOM')

    def add_cube(self):
        bpy.ops.mesh.primitive_cube_add()

    def render(self):
        bpy.ops.render.render()

bpy.utils.register_class(TIILTOperator)
