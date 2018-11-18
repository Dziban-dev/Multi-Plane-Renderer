bl_info = {
    "name": "Multi Plane Render | alpha",
    "description":"Save render times by rendering a static eviroment only once, which is placed as the background for your animated objects/characters, like it was greenscreek. The 3d enviroment for your background must be setup in the 19th layer, and your animated characters must be in layer 0. I'm planning to add the functionalty to choose what layer is going to be your static enviroment and maybe use multiple layers for the animated characters. Also i would like to make de render update and render the background again if there is a camera movement.",
    "author": "Dziban",
    "version": (0, 2),
    "location": "Properties > Render > Multi Plane Render",
    "warning": "", # used for warning icon and text in addons panel
    "support": "COMMUNITY",
    "category": "Render"
}
import bpy
#from bpy.types import Panel

class RenderPanel(bpy.types.Panel):
    bl_idname = "Multiplane Render"
    bl_label = "Multiplane Render | alpha"
    bl_space_type ='PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"
    
    def draw (self, context):
        
        self.layout.row().label(text="Instructions:")
        self.layout.row().label(text="Place animated objects in layer 0")
        self.layout.row().label(text=" and static enviroment in layer 19")
        self.layout.row().operator(RenderNow.bl_idname,icon = 'RENDER_ANIMATION', text="Render Now")

class RenderNow(bpy.types.Operator):
    bl_idname = "execute.render"
    bl_label = "Render This Now"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context) :
        #storing user settings
        fp = bpy.data.scenes['Scene'].render.filepath # get existing output path
        outp = bpy.data.scenes['Scene'].render.image_settings.file_format
        alpha = bpy.context.scene.cycles.film_transparent 
        #rendering the static background layer
        bpy.context.scene.cycles.film_transparent = False
        bpy.context.scene.layers=((False,)*19+(True,)) 
        bpy.data.scenes['Scene'].render.filepath = '/tmp/bk'
        bpy.data.scenes['Scene'].render.image_settings.file_format = 'OPEN_EXR'
        bpy.ops.render.render(write_still=True)
        #going back to user settings
        bpy.data.scenes['Scene'].render.filepath = fp
        bpy.data.scenes['Scene'].render.image_settings.file_format = outp
        bpy.context.scene.cycles.film_transparent = alpha
        #loaading/reloading bacground image
        for i in bpy.data.images:
            if i.filepath=="/tmp/bk.exr":
                i.reload()
            else:
                bpy.data.images.load("/tmp/bk.exr", check_existing=True)
        #bpy.data.images['bk.exr.001'].name = 'bk.exr'
        #setting up compositor nodes
            # switch on nodes and get reference
        bpy.context.scene.use_nodes = True
        tree = bpy.context.scene.node_tree
            # clear default nodes
        for node in tree.nodes:
            tree.nodes.remove(node)
        # create input image node
        image_node = tree.nodes.new(type='CompositorNodeImage')
        image_node.image = bpy.data.images['bk.exr']
        image_node.location = 0,0
        render_node = tree.nodes.new(type='CompositorNodeRLayers')
        render_node.location = 0,300
        alpha_node = tree.nodes.new(type='CompositorNodeAlphaOver')
        alpha_node.location = 300,100
        comp_node = tree.nodes.new('CompositorNodeComposite')
        comp_node.location = 500,100
        # linking nodes
        links = tree.links
        link = links.new(alpha_node.outputs[0], comp_node.inputs[0])
        link = links.new(image_node.outputs[0], alpha_node.inputs[1])
        link = links.new(render_node.outputs[0], alpha_node.inputs[2])
        #Reder animation
        bpy.context.scene.cycles.film_transparent = True
        bpy.context.scene.layers[0]= True
        bpy.context.scene.layers[19]= False
        bpy.ops.render.render(animation=True)
        bpy.context.scene.cycles.film_transparent = alpha
        return {"FINISHED"}

def register() :
    bpy.utils.register_class(RenderNow)
    bpy.utils.register_class(RenderPanel)
def unregister() :
    bpy.utils.unregister_class(RenderPanel)
    bpy.utils.register_class(RenderNow)
    
if __name__ == "__main__":
    register()
    