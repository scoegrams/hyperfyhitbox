bl_info = {
    "name": "Hyperfy HitBox",
    "blender": (2, 80, 0),  # Compatible with Blender 2.80+
    "category": "Object",
    "version": (1, 8, 0),
    "author": "bitmato",
    "description": "Creates matobody with Hiro-cube, bogie-collider, and adds colliders to existing objects.",
}

import bpy

# Function to create a collider for an existing object without hierarchy
def add_collider_to_existing_object():
    """Create a bogie-collider around an existing object."""
    selected_objects = bpy.context.selected_objects
    if not selected_objects or len(selected_objects) != 1:
        return "Please select exactly one object to create a collider around."

    # Get the selected object
    target_object = selected_objects[0]

    # Ensure the selected object is a mesh
    if target_object.type != 'MESH':
        return "Selected object is not a valid polygon or mesh."

    # Create the collider
    collider = bpy.data.objects.new("bogie-collider", bpy.data.meshes.new("Collider_Mesh"))
    bpy.context.scene.collection.objects.link(collider)
    collider.display_type = 'WIRE'  # Set to wireframe for visualization
    
    # Add custom properties to the collider
    collider["node"] = "collider"
    collider["type"] = "hitbox"

    # Match the position and dimensions of the target object
    collider.location = target_object.location
    collider.scale = target_object.scale

    # Add a basic cube mesh for the collider
    bpy.context.view_layer.objects.active = collider
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.primitive_cube_add(size=2)  # Default collider size
    bpy.ops.object.mode_set(mode='OBJECT')

    return "Collider created around the selected object (pre-hierarchy)."

# Function to create the Empty and Collider hierarchy
def create_rigidbody_hierarchy():
    """Create a game-ready hierarchy: matobody -> bogie-collider."""
    
    # Step 1: Create the Empty (matobody root object)
    empty = bpy.data.objects.new("matobody", None)
    bpy.context.scene.collection.objects.link(empty)
    empty["node"] = "rigidbody"
    empty["type"] = "static"
    empty.location = bpy.context.scene.cursor.location  # Place at the 3D cursor

    # Step 2: Create the Collider Object
    collider = bpy.data.objects.new("bogie-collider", bpy.data.meshes.new("Collider_Mesh"))
    bpy.context.scene.collection.objects.link(collider)
    collider.parent = empty  # Parent to the matobody
    collider.display_type = 'WIRE'  # Set to wireframe for easy visualization
    
    # Add custom properties to the collider
    collider["node"] = "collider"
    collider["type"] = "hitbox"

    # Add a basic cube mesh for the collider
    bpy.context.view_layer.objects.active = collider
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.primitive_cube_add(size=2)  # Set cube size (e.g., 2 meters)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    return empty, collider

# Function to add a smaller Hiro cube under the matobody
def add_model_cube():
    """Add a smaller Hiro-cube under the matobody hierarchy."""
    # Find the matobody
    matobody = None
    for obj in bpy.context.scene.objects:
        if obj.name == "matobody":
            matobody = obj
            break

    if not matobody:
        return "No matobody found. Create it first!"

    # Create the Hiro Cube
    model_cube = bpy.data.objects.new("Hiro-cube", bpy.data.meshes.new("ModelCube_Mesh"))
    bpy.context.scene.collection.objects.link(model_cube)
    model_cube.parent = matobody  # Parent to the matobody

    # Add custom properties to the Hiro cube
    model_cube["node"] = "model"
    model_cube["type"] = "dynamic"

    # Add a basic smaller cube mesh
    bpy.context.view_layer.objects.active = model_cube
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.primitive_cube_add(size=1.5)  # Smaller cube (1.5 meters)
    bpy.ops.object.mode_set(mode='OBJECT')

    return "Hiro-cube added under matobody!"

# Operator to create the matobody hierarchy
class OBJECT_OT_CreateGameHierarchy(bpy.types.Operator):
    """Create a matobody with a bogie-collider object."""
    bl_idname = "object.create_game_hierarchy"
    bl_label = "Create Game Hierarchy"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Create the matobody hierarchy
        create_rigidbody_hierarchy()
        self.report({'INFO'}, "Game hierarchy created successfully!")
        return {'FINISHED'}

# Operator to add the Hiro cube
class OBJECT_OT_AddModelCube(bpy.types.Operator):
    """Add a smaller Hiro-cube under the matobody hierarchy."""
    bl_idname = "object.add_model_cube"
    bl_label = "Add Hiro Cube"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        result = add_model_cube()
        self.report({'INFO'}, result)
        return {'FINISHED'}

# Operator to add a collider for an existing object
class OBJECT_OT_AddColliderToExisting(bpy.types.Operator):
    """Add a bogie-collider to an existing object."""
    bl_idname = "object.add_collider_to_existing"
    bl_label = "Add Collider to Existing Object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        result = add_collider_to_existing_object()
        self.report({'INFO'}, result)
        return {'FINISHED'}

# Panel to access the tools
class OBJECT_PT_CustomToolsPanel(bpy.types.Panel):
    """Custom Tools Panel"""
    bl_label = "Hyperfy HitBox Tools"
    bl_idname = "OBJECT_PT_custom_tools_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Hyperfy HitBox"  # Blender Add-on Tab Name

    def draw(self, context):
        layout = self.layout
        layout.operator(OBJECT_OT_CreateGameHierarchy.bl_idname, text="Build Game Hierarchy")
        layout.operator(OBJECT_OT_AddModelCube.bl_idname, text="Add Hiro Cube")
        layout.operator(OBJECT_OT_AddColliderToExisting.bl_idname, text="Add Collider to Existing Object")

# Registration
def register():
    bpy.utils.register_class(OBJECT_OT_CreateGameHierarchy)
    bpy.utils.register_class(OBJECT_OT_AddModelCube)
    bpy.utils.register_class(OBJECT_OT_AddColliderToExisting)
    bpy.utils.register_class(OBJECT_PT_CustomToolsPanel)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_CreateGameHierarchy)
    bpy.utils.unregister_class(OBJECT_OT_AddModelCube)
    bpy.utils.unregister_class(OBJECT_OT_AddColliderToExisting)
    bpy.utils.unregister_class(OBJECT_PT_CustomToolsPanel)

if __name__ == "__main__":
    register()
