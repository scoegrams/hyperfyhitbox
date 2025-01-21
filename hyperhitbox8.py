bl_info = {
    "name": "Hyperfy HitBox",
    "blender": (2, 80, 0),
    "category": "Object",
    "version": (2, 2, 0),
    "author": "bitmato",
    "description": "Creates matobody with Hiro-cube, bogie-collider, and dynamic UI for custom properties.",
}

import bpy

# Function to dynamically update custom properties
def update_custom_property(obj, property_name, value):
    """Set or update a custom property for an object."""
    if obj:
        obj[property_name] = value
        return f"Set {property_name} to {value} for {obj.name}."
    return "No object selected."

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

# Function to create a collider for an existing object
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

# Operator to set a custom property
class OBJECT_OT_SetCustomProperty(bpy.types.Operator):
    """Set a custom property for the selected object."""
    bl_idname = "object.set_custom_property"
    bl_label = "Set Custom Property"
    bl_options = {'REGISTER', 'UNDO'}

    property_name: bpy.props.StringProperty()
    property_value: bpy.props.StringProperty()

    def execute(self, context):
        obj = context.object
        if obj:
            msg = update_custom_property(obj, self.property_name, self.property_value)
            self.report({'INFO'}, msg)
        else:
            self.report({'WARNING'}, "No object selected.")
        return {'FINISHED'}

# Operator to create the matobody hierarchy
class OBJECT_OT_CreateGameHierarchy(bpy.types.Operator):
    """Create a matobody with a bogie-collider object."""
    bl_idname = "object.create_game_hierarchy"
    bl_label = "Create Game Hierarchy"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
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

# Main Panel
class OBJECT_PT_CustomToolsPanel(bpy.types.Panel):
    """Custom Tools Panel"""
    bl_label = "Hyperfy HitBox Tools"
    bl_idname = "OBJECT_PT_custom_tools_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Hyperfy HitBox"

    def draw(self, context):
        layout = self.layout
        obj = context.object

        layout.operator(OBJECT_OT_CreateGameHierarchy.bl_idname, text="Build Game Hierarchy")
        layout.operator(OBJECT_OT_AddModelCube.bl_idname, text="Add Hiro Cube")
        layout.operator(OBJECT_OT_AddColliderToExisting.bl_idname, text="Add Collider to Selected")

        if obj:
            layout.label(text=f"Selected: {obj.name}")
            current_type = obj.get("type", "None")
            layout.label(text=f"Type: {current_type}")

            layout.label(text="Type:")
            row = layout.row()
            row.operator("object.set_custom_property", text="RigidBody").property_name = "type"
            row.operator("object.set_custom_property", text="Collider").property_name = "type"
            row.operator("object.set_custom_property", text="LOD Group").property_name = "type"

            if current_type == "rigidbody":
                layout.label(text="Options (RigidBody):")
                row = layout.row()
                row.operator("object.set_custom_property", text="Static").property_name = "node"
                row.operator("object.set_custom_property", text="Kinematic").property_name = "node"
                row.operator("object.set_custom_property", text="Dynamic").property_name = "node"
            elif current_type == "collider":
                layout.label(text="Options (Collider):")
                row = layout.row()
                row.operator("object.set_custom_property", text="Convex").property_name = "node"
                row.operator("object.set_custom_property", text="Concave").property_name = "node"

# Registration
classes = [
    OBJECT_OT_SetCustomProperty,
    OBJECT_OT_CreateGameHierarchy,
    OBJECT_OT_AddModelCube,
    OBJECT_OT_AddColliderToExisting,
    OBJECT_PT_CustomToolsPanel,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
