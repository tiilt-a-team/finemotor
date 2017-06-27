import sys
sys.path.append('.')
import bpy
import bgl
import socket
import json
import math
import logging
import mathutils
import bpy_extras.view3d_utils
import pickle



def read_command(transport):
    try:
        line = transport.recv(2048)
        data = pickle.loads(line)
        print('Data has been received')
        if not line:
            return
        #data = json.loads(line)

    except ValueError as e:
        logging.exception(e)
        raise IOError()

    try:
        cmd = data['verb']
        del data['verb']
    except KeyError as e:
        logging.exception(e)
        raise IOError()

    return cmd, data


'''Calculates the correct coordinates for placing the cursor location based on a command that specifies
pixel quantity and a direction'''

def coord_calc(quantity, direction):
    if direction == 'top':
        return (bpy.data.screens['Default'].scene.cursor_location[0], quantity)
    elif direction == 'bottom':
        return (bpy.data.screens['Default'].scene.cursor_location[0], -(quantity))
    elif direction == 'right':
        return (quantity, bpy.data.screens['Default'].scene.cursor_location[1])
    elif direction == 'left':
        return (-(quantity), bpy.data.screens['Default'].scene.cursor_location[1])

'''Calculates the distance betweent two points on the screen'''

def calc_min_distance(obj1_loc, obj2_loc):
    dist = (obj1_loc[0]-obj2_loc[0])**2 + (obj1_loc[1]-obj2_loc[1])**2 + (obj1_loc[2]-obj2_loc[2])**2
    return math.sqrt(dist)


def find_object(obj_specifier, obj_location):
    scene = bpy.context.scene

    if obj_location is None:
        obj_counter = 0;
        for ob in scene.objects:
            if ob.name.startswith(obj_specifier):
                obj_counter = obj_counter + 1

        if obj_counter > 1:
            print('Please specify which ' + obj_specifier + ' you want.')
        else:
            return ob.name
    

    prev_dist = 100000000
    found_obj_name = '' 
    
    for ob in scene.objects:
        if ob.name.startswith(obj_specifier):
            obj_name = ob.name

            ob_location = (bpy.data.objects[obj_name].location[0],bpy.data.objects[obj_name].location[1],bpy.data.objects[obj_name].location[2])

            dist = calc_min_distance(ob_location, obj_location)

            if dist < prev_dist:
                prev_dist = dist
                found_obj_name = obj_name


    return found_obj_name

'''Selects an object and makes it the active object
    obj_name : The name of the object as stored in blender
'''
def select_object(obj_name):
    curr_obj = bpy.context.selected_objects
    
    if len(curr_obj) > 0:
        bpy.ops.object.select_all(action = 'TOGGLE')
    
    bpy.context.scene.objects.active = bpy.data.objects[obj_name]
    bpy.data.objects[obj_name].select = True




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
        self.view,
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
            bpy.ops.view3d.viewnumpad(type='TOP')
            try:
                cmd = read_command(self.transport)
            except IOError as e:
                logging.exception(e)
            else:
                if cmd:
                    func, kwargs = cmd
                    if func in self.commands:
                        #self.commands[func](**kwargs)
                        self.commands[func](kwargs)

        '''
        if event.type == 'TAB':
            mouse_vector = bpy_extras.view3d_utils.region_2d_to_origin_3d(bpy.context.region, 
                bpy.context.space_data.region_3d, (event.mouse_region_x, event.mouse_region_y), mathutils.Vector((0,0,0)))

            print(str(mouse_vector[0]) + ' ' + str(mouse_vector[1]) + ' ' + str(mouse_vector[2]))
            bpy.ops.mesh.primitive_cube_add(location = mouse_vector)
        '''

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        try:
            self.transport.connect(('localhost', 8888))
            #self.transport.setblocking(False)
            self.sockfile = self.transport.makefile()

        except IOError as e:
            logging.exception(e)
            return {'CANCELLED'}

        print("Started")
        self._timer = context.window_manager.event_timer_add(0.01, context.window)
        context.window_manager.modal_handler_add(self)
        bpy.ops.view3d.viewnumpad(type='TOP')
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


    def view(self, obj):
        direction = obj['specifier']
        self.view_numpad(direction.upper())

    def add(self, dict):
        shape = dict['object']
        object_position = dict['quantity']
        if(object_position != 'NULL'):
            pos = (object_position,0,0)
            logging.debug('These are the coordinates: ')
            logging.debug(pos)
        else:
            pos = [0,0,0]

        bpy.context.scene.cursor_location = (pos[0], pos[1], pos[2])
        if(shape == 'cube'):
            bpy.ops.mesh.primitive_cube_add()
        elif (shape == 'monkey'):
            bpy.ops.mesh.primitive_monkey_add()
        elif (shape == 'cylinder'):
            bpy.ops.mesh.primitive_cylinder_add()
        elif (shape == 'cone'):
            bpy.ops.mesh.primitive_cone_add()
        elif (shape == 'circle'):
            bpy.ops.mesh.primitive_circle_add()
        else:
            pass


    def move_object(self, dict):
        #Moves an object from one location to another
        obj_specifier = dict['object']
        obj_location = dict['coord']

        find_object(obj_specifier, obj_location)

        pass

    def rotate(self, x, y, z):
        bpy.ops.transform.rotate(z, y, x)

    def undo(self, dict):
        bpy.ops.ed.undo()

    def redo(self, dict):
        bpy.ops.ed.redo()

    def clear_everything(self):
        if not bpy.context.selected_objects:
            bpy.ops.object.select_all(actions = 'TOGGLE') 
        bpy.ops.object.select_all(actions = 'TOGGLE')
        bpy.ops.object.delete(use_global = False)

    def delete_object(self, dict):
        #Find object with given properties, delete object
        obj_name = dict['object']
        obj_location = dict['coord']
        obj_name = find_object(obj_name, obj_location)
        select_object(obj_name)

        bpy.ops.object.delete(use_global)

        print('Object has been deleted')

    def resize_object(self):
        #find object with given properties, resize to new scale
        pass


bpy.utils.register_class(TIILTOperator)

