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
        self.view_right,
        self.view_left,
        self.clear_everything,
        self.undo,
        self.redo,
        self.add,
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

        if event.type == 'TIMER':
            try:
                cmd = read_command(self.sockfile)
            except IOError as e:
                logging.exception(e)
            else:
                if cmd:
                    func, kwargs = cmd
                    print('Here!!!')
                    print(func, kwargs)
                    print('Here Again!!')
                    if func in self.commands:
                        #self.commands[func](**kwargs)
                        self.commands[func](kwargs)

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        try:
            self.transport.connect(('localhost', 1234))
            self.transport.setblocking(False)
            self.sockfile = self.transport.makefile()

        except IOError as e:
            logging.exception(e)
            return {'CANCELLED'}

        print("Started")
        self._timer = context.window_manager.event_timer_add(0.01, context.window)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}


    def view_numpad(self, view):
        if bpy.context.area.type == 'VIEW_3D':
            bpy.ops.view3d.viewnumpad(type = view)

    def view_left(self):
        self.view_numpad('LEFT')

    def view_right(self):
        self.view_numpad('RIGHT')

    def view_top(self):
        self.view_numpad('TOP')

    def view_bottom(self):
        self.view_numpad('BOTTOM')

    def add_cube(self):
        bpy.ops.mesh.primitive_cube_add()

    def add(self, obj):
        if(obj['shape'] == 'cube'):
            bpy.ops.mesh.primitive_cube_add()
        elif (obj['shape'] == 'monkey'):
            bpy.ops.mesh.primitive_monkey_add()
        elif (obj['shape'] == 'cylinder'):
            bpy.ops.mesh.primitive_cylinder_add()
        elif (obj['shape'] == 'cone'):
            bpy.ops.mesh.primitive_cone_add()
        elif (obj['shape'] == 'circle'):
            bpy.ops.mesh.primitive_circle_add()
        else:
            pass


    def rotate(self, x, y, z):
        bpy.ops.transform.rotate(z, y, x)

    def undo(self):
        bpy.ops.ed.undo()

    def redo(self):
        bpy.ops.ed.redo()


    #TO DO
    def clear_everything(self):
        for o in bpy.context.selected_objects:
            pass

bpy.utils.register_class(TIILTOperator)
