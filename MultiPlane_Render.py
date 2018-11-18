bl_info = {
    "name": "Multi Plane Render | alpha",
    "description":"Save render times by rendering by choosing what render layer to render each frame and which render layer render just once, I'm planning to add the functionalty to choose what layer is going to be your static enviroment and maybe use multiple layers for the animated characters. Also i would like to make de render update and render the background again if there is a camera movement.",
    "author": "Dziban",
    "version": (0, 7),
    "location": "Properties > Render > Multi Plane Render",
    "warning": "", # used for warning icon and text in addons panel
    "support": "COMMUNITY",
    "category": "Render"
}
import bpy

class Multiplanne_List(bpy.types.UIList):    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layer = item
        row=layout.row()
        print(dir(layer))
        row.split(align=True, percentage=1).prop(layer, 'name', text='')
        row.split(align=True, percentage=0.5).prop(layer, 'StaticBool', text='Animated')
        row.prop(layer, 'use', text = '',icon='VISIBLE_IPO_ON')

class RenderPanel(bpy.types.Panel):
    bl_idname = "Multiplane Render"
    bl_label = "Multiplane Render | alpha"
    bl_space_type ='PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"
    
    def draw (self, context):
        row = self.layout.row()
        col = self.layout.column()
        col.label(text="Manage and Prepare Render Layers:")
        ##
        row = col.row(align=True)
        row.template_list('Multiplanne_List', 'RenderLayers', context.scene.render, 'layers', context.scene, "testindex")
        row = col.row(align=True)
        split = row.split(align=True, percentage=0.5)
        ##
        split.operator('new.layer',icon = 'ZOOMIN', text="Add Render Layer")
        split.operator('delete.layer',icon = 'ZOOMOUT', text="Delete Render Layer")
        ##
        col.label (text=(""))
        col.prop(context.scene.my_settings, "my_bool", text="Render World's Material ( Enviroment Texture )")   
        col.label (text=(""))
        ##
        row = col.row(align=True)
        split = row.split(align=True, percentage=0.5)
        split.operator(MakeNow.bl_idname,icon = 'NODETREE', text="Make Compositor Tree")
        split.operator(RenderNow.bl_idname,icon = 'RENDER_ANIMATION', text="Render Now")
        col = self.layout.column(align=True)
        col.operator(AutoRenderNow.bl_idname,icon = 'RENDER_ANIMATION', text="Auto Render")
        col.label (text=(""))
        
class MySettings(bpy.types.PropertyGroup):
    my_bool = bpy.props.BoolProperty(
        name="bool1",
        description="Checked:Render World's Material.|| Unchked render World Material as alpha layer.",
        default = True)
    
class NewLayer(bpy.types.Operator):
    bl_idname = "new.layer"
    bl_label = "Add a New Render Layer"
    bl_options ={'REGISTER', 'UNDO'}
    def execute(self, context):
        bpy.ops.scene.render_layer_add()
        return {"FINISHED"}
    
class DeleteLayer(bpy.types.Operator):
    bl_idname = "delete.layer"
    bl_label = "Add a New Render Layer"
    bl_options ={'REGISTER', 'UNDO'}
    def execute(self, context):
        bpy.ops.scene.render_layer_remove()
        return {"FINISHED"}
    
class AutoRenderNow(bpy.types.Operator):
    bl_idname = "execute.auto_render"
    bl_label = "Auto Render without preset Compositor Node Tree  editing"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context) :
        #storing user settings and setting up Variables
        fp = bpy.data.scenes['Scene'].render.filepath # get existing output path
        outp = bpy.data.scenes['Scene'].render.image_settings.file_format
        alpha = bpy.context.scene.cycles.film_transparent
        exp_format = 'OPEN_EXR'
        wx=bpy.context.scene.render.resolution_x
        hy=bpy.context.scene.render.resolution_y
        act_l = []
        cc=0
        iii = 0
        l_19 =[19]
        render_layers = bpy.context.scene.render.layers
        scene=bpy.context.scene
        counter1 = 0
        counterx = 0
        counter2 = 2
        for layer in bpy.context.scene.layers:
            if layer==True:
                act_l.append(iii)
            iii+=1
        rlayer_list=[]
        for rlayer_name in bpy.context.scene.render.layers:
            rlayer_list.append(rlayer_name.name)
        #Render World
        if bpy.context.scene.my_settings.my_bool == True:
            bpy.context.scene.cycles.film_transparent = False
            for obj_name in obj_list:
                bpy.data.objects[obj_name].hide_render = True
            bpy.context.scene.layers = [x in l_19 for x in range(20)] 
            bpy.data.scenes['Scene'].render.filepath = '/tmp/bk'
            bpy.data.scenes['Scene'].render.image_settings.file_format = exp_format
            bpy.data.scenes['Scene'].render.image_settings.use_zbuffer = True
            bpy.ops.render.render(write_still=True,layer=rlayer_list[0])
            #going back to user settings
            bpy.data.scenes['Scene'].render.filepath = fp
            bpy.data.scenes['Scene'].render.image_settings.file_format = outp
            bpy.context.scene.cycles.film_transparent = alpha
            bpy.context.scene.layers = [ww in act_l for ww in range(20)]
            for obj_name in obj_list:
                bpy.data.objects[obj_name].hide_render = False
            #loading/reloading bacground image
            for i in bpy.data.images:
                bpy.context.scene.use_nodes = True
                tree = bpy.context.scene.node_tree
                for node in tree.nodes:
                    tree.nodes.remove(node)
                for block in bpy.data.images:
                    if block.users == 0:
                        bpy.data.images.remove(block)
                if i.name=="bk.exr":
                    i.reload()
                if not i.name=="bk.exr":
                    bpy.data.images.load("/tmp/bk.exr", check_existing=True)
        if bpy.context.scene.my_settings.my_bool == False:
            bpy.context.scene.use_nodes = True
            tree = bpy.context.scene.node_tree
            for node in tree.nodes:
                tree.nodes.remove(node)
            for block in bpy.data.images:
                if block.users == 0:
                    bpy.data.images.remove(block)
            for i in bpy.data.images:
                if not i.name=="bk.exr":
                    bpy.data.images.new(name="bk.exr",width=wx,height=hy,alpha=True)
                    bpy.data.images['bk.exr'].generated_color = (0,0,0,0)
                    bpy.context.scene.layers = [ww in act_l for ww in range(20)]   
        #setting up compositor nodes
        # switch on nodes and get reference
        bpy.context.scene.use_nodes = True
        tree = bpy.context.scene.node_tree
        # clear default nodes
        for node in tree.nodes:
            tree.nodes.remove(node)
        #Rendering Static Layers as images
        output_node =tree.nodes.new(type='CompositorNodeOutputFile')
        render_node = tree.nodes.new(type='CompositorNodeRLayers')
        tree.links.new(tree.nodes['Render Layers'].outputs['Image'],tree.nodes['File Output'].inputs['Image'])
        for count, layer in enumerate(render_layers):
            if bpy.context.scene.render.layers[rlayer_list[count]].StaticBool==False:
                render_node.layer = layer.name
                bpy.context.scene.cycles.film_transparent = True
                bpy.data.scenes['Scene'].render.filepath = '/tmp/img_'+str(layer.name)
                bpy.data.scenes['Scene'].render.image_settings.file_format = exp_format
                bpy.data.scenes['Scene'].render.image_settings.use_zbuffer = True
                bpy.ops.render.render(write_still=True,layer=str(bpy.context.scene.render.layers[layer.name].name))
                for i in bpy.data.images:
                    if i.name=="img_"+str(rlayer_list[cc])+".exr":
                        i.reload()
                    if not i.name=="img_"+str(rlayer_list[cc])+".exr":
                        bpy.data.images.load('/tmp/img_'+str(layer.name)+".exr", check_existing=True)
                cc+=1
        #going back to user settings
        bpy.data.scenes['Scene'].render.filepath = fp
        bpy.data.scenes['Scene'].render.image_settings.file_format = outp
        bpy.context.scene.cycles.film_transparent = alpha
        for node in tree.nodes:
            tree.nodes.remove(node)
        #SETTING UP NODES
        comp_node = tree.nodes.new('CompositorNodeComposite')
        comp_node.location = 500,100
        comp_node.use_alpha = True
        view_node = tree.nodes.new('CompositorNodeViewer')
        view_node.location = 500,250
        view_node.use_alpha = True
        #setting up BK node
        ##Bk node.
        image_node = tree.nodes.new(type='CompositorNodeImage')
        image_node.image = bpy.data.images['bk.exr']
        image_node.location = 0,0
        ## Image node(Static) or Render node (Animated)
        for count, layer in enumerate(render_layers):
            if bpy.context.scene.render.layers[count].StaticBool==True:
                render_node = tree.nodes.new(type='CompositorNodeRLayers')
                render_node.location = [0,300]
                if "." in render_node.name:
                    suffix = render_node.name[-3:]
                    stripp = render_node.name.strip(suffix)
                    render_node.name = stripp+ str(counter1+2)
                    if counter1 <= len(render_layers):
                        counter1 += 1
                    render_node.layer = layer.name
                else:  
                    render_node.name = "Render Layers."+str(counter1+1)
                    if counter1 < len(render_layers)-1:
                        counter1 += 1
                    render_node.layer = layer.name
            if bpy.context.scene.render.layers[count].StaticBool==False:
                imager_node = tree.nodes.new(type='CompositorNodeImage')
                imager_node.location = [0,300]
                if "." in imager_node.name:
                    suffix = imager_node.name[-3:]
                    stripp = imager_node.name.strip(suffix)
                    if counter1 <= len(render_layers):
                        counter1 += 1
                    imager_node.name = stripp+ str(counter1)
                    imager_node.image = bpy.data.images["img_"+rlayer_list[count]+".exr"]
            #setting up Z Combine Nodes
        for layer in render_layers:
            z_node = tree.nodes.new(type='CompositorNodeZcombine')
            z_node.location = (300,100)
            z_node.use_alpha = True
            if "." in z_node.name:
                suffix = z_node.name[-3:]
                stripp = z_node.name.strip(suffix)
                z_node.name = stripp+ str(counter2)
                if counter2 <= len(render_layers):
                    counter2 += 1
        tree.nodes["Z Combine"].name = "Z Combine.1"
        #LINKING NODES
        links = tree.links
        links.new(z_node.outputs[0], comp_node.inputs[0])
        links.new(z_node.outputs[0], view_node.inputs[0])
        z_node.inputs[3].default_value = 1e+10
        links.new(tree.nodes["Image"].outputs[0], z_node.inputs[2])
        #
        n = 1
        nn= 1
        for layer in tree.nodes:
            if n < len(render_layers):
                links.new(tree.nodes["Z Combine.%s"%str(n)].outputs[0],tree.nodes["Z Combine.%s"%str(n+1)].inputs[0])
                links.new(tree.nodes["Z Combine.%s"%str(n)].outputs[1],tree.nodes["Z Combine.%s"%str(n+1)].inputs[1])
                n +=1
            ###
            if nn < len(render_layers) and bpy.context.scene.render.layers[rlayer_list[nn]].StaticBool==True:
                links.new(tree.nodes["Render Layers.%s"%str(nn+1)].outputs[0],tree.nodes["Z Combine.%s"%str(nn)].inputs[2])
                links.new(tree.nodes["Render Layers.%s"%str(nn+1)].outputs[2],tree.nodes["Z Combine.%s"%str(nn)].inputs[3])
                nn +=1
            ###---
            if nn < len(render_layers) and bpy.context.scene.render.layers[rlayer_list[nn]].StaticBool==False:
                links.new(tree.nodes["Image.%s"%str(nn+1)].outputs[0],tree.nodes["Z Combine.%s"%str(nn)].inputs[2])
                links.new(tree.nodes["Image.%s"%str(nn+1)].outputs[2],tree.nodes["Z Combine.%s"%str(nn)].inputs[3])
                nn +=1
            ###---
        if 'Render Layers.1' in tree.nodes.keys():
            links.new(tree.nodes["Render Layers.1"].outputs[0],tree.nodes["Z Combine.1"].inputs[0])
            links.new(tree.nodes["Render Layers.1"].outputs[2],tree.nodes["Z Combine.1"].inputs[1])
        if "Image.1" in tree.nodes.keys():
            links.new(tree.nodes["Image.1"].outputs[0],tree.nodes["Z Combine.1"].inputs[0])
            links.new(tree.nodes["Image.1"].outputs[2],tree.nodes["Z Combine.1"].inputs[1])
        #Reder animation
        bpy.context.scene.cycles.film_transparent = True
        bpy.context.scene.layers[0]= True
        bpy.context.scene.layers[19]= False
        bpy.ops.render.render(animation=True)
        bpy.context.scene.cycles.film_transparent = alpha
        return {"FINISHED"}

class MakeNow(bpy.types.Operator):
    bl_idname = "make.node_tree"
    bl_label = "Build the Compositing Node tree, to edit before Render."
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context) :
        #storing user settings and setting up Variables
        fp = bpy.data.scenes['Scene'].render.filepath # get existing output path
        outp = bpy.data.scenes['Scene'].render.image_settings.file_format
        alpha = bpy.context.scene.cycles.film_transparent
        exp_format = 'OPEN_EXR'
        wx=bpy.context.scene.render.resolution_x
        hy=bpy.context.scene.render.resolution_y
        act_l = []
        iii = 0
        cc=0
        l_19 =[19]
        render_layers = bpy.context.scene.render.layers
        scene=bpy.context.scene
        counter1 = 0
        counterx = 0
        counter2 = 2
        for layer in bpy.context.scene.layers:
            if layer==True:
                act_l.append(iii)
            iii+=1
        rlayer_list=[]
        for rlayer_name in bpy.context.scene.render.layers:
            rlayer_list.append(rlayer_name.name)
        obj_list=[]
        for obj_name in bpy.data.objects:
            obj_list.append(obj_name.name)
        #Render World
        if bpy.context.scene.my_settings.my_bool == True:
            bpy.context.scene.cycles.film_transparent = False
            #bpy.context.scene.layers = [x in l_19 for x in range(20)]
            bpy.context.scene.layers=((False,)*19+(True,))
            for obj_name in obj_list:
                bpy.data.objects[obj_name].hide_render = True
            bpy.data.scenes['Scene'].render.filepath = '/tmp/bk'
            bpy.data.scenes['Scene'].render.image_settings.file_format = exp_format
            bpy.data.scenes['Scene'].render.image_settings.use_zbuffer = True
            bpy.ops.render.render(write_still=True, layer=rlayer_list[0])
            #going back to user settings
            bpy.data.scenes['Scene'].render.filepath = fp
            bpy.data.scenes['Scene'].render.image_settings.file_format = outp
            bpy.context.scene.cycles.film_transparent = alpha
            bpy.context.scene.layers = [ww in act_l for ww in range(20)]
            for obj_name in obj_list:
                bpy.data.objects[obj_name].hide_render = False
            #loading/reloading bacground image
            for i in bpy.data.images:
                bpy.context.scene.use_nodes = True
                tree = bpy.context.scene.node_tree
                for node in tree.nodes:
                    tree.nodes.remove(node)
                for block in bpy.data.images:
                    if block.users == 0:
                        bpy.data.images.remove(block)
                if i.name=="bk.exr":
                    i.reload()
                if not i.name=="bk.exr":
                    bpy.data.images.load("/tmp/bk.exr", check_existing=True)
        if bpy.context.scene.my_settings.my_bool == False:
            bpy.context.scene.use_nodes = True
            tree = bpy.context.scene.node_tree
            for node in tree.nodes:
                tree.nodes.remove(node)
            for block in bpy.data.images:
                if block.users == 0:
                    bpy.data.images.remove(block)
            for i in bpy.data.images:
                if not i.name=="bk.exr":
                    bpy.data.images.new(name="bk.exr",width=wx,height=hy,alpha=True)
                    bpy.data.images['bk.exr'].generated_color = (0,0,0,0)
                    bpy.context.scene.layers = [ww in act_l for ww in range(20)]   
        #setting up compositor nodes
        # switch on nodes and get reference
        bpy.context.scene.use_nodes = True
        tree = bpy.context.scene.node_tree
        # clear default nodes
        for node in tree.nodes:
            tree.nodes.remove(node)
        #Rendering Static Layers as images
        output_node =tree.nodes.new(type='CompositorNodeOutputFile')
        render_node = tree.nodes.new(type='CompositorNodeRLayers')
        tree.links.new(tree.nodes['Render Layers'].outputs['Image'],tree.nodes['File Output'].inputs['Image'])
        for count, layer in enumerate(render_layers):
            if bpy.context.scene.render.layers[rlayer_list[count]].StaticBool==False:
                render_node.layer = layer.name
                bpy.context.scene.cycles.film_transparent = True
                bpy.data.scenes['Scene'].render.filepath = '/tmp/img_'+str(layer.name)
                bpy.data.scenes['Scene'].render.image_settings.file_format = exp_format
                bpy.data.scenes['Scene'].render.image_settings.use_zbuffer = True
                bpy.ops.render.render(write_still=True,layer=str(bpy.context.scene.render.layers[layer.name].name))
                for i in bpy.data.images:
                    if i.name=="img_"+str(rlayer_list[cc])+".exr":
                        i.reload()
                    if not i.name=="img_"+str(rlayer_list[cc])+".exr":
                        bpy.data.images.load('/tmp/img_'+str(layer.name)+".exr", check_existing=True)
                cc+=1
        #going back to user settings
        bpy.data.scenes['Scene'].render.filepath = fp
        bpy.data.scenes['Scene'].render.image_settings.file_format = outp
        bpy.context.scene.cycles.film_transparent = True
        for node in tree.nodes:
            tree.nodes.remove(node)
        #SETTING UP NODES
        comp_node = tree.nodes.new('CompositorNodeComposite')
        comp_node.location = 500,100
        comp_node.use_alpha = True
        view_node = tree.nodes.new('CompositorNodeViewer')
        view_node.location = 500,250
        view_node.use_alpha = True
        #setting up BK node
        ##Bk node.
        image_node = tree.nodes.new(type='CompositorNodeImage')
        image_node.image = bpy.data.images['bk.exr']
        image_node.location = 0,0
        ## Image node(Static) or Render node (Animated)
        for count, layer in enumerate(render_layers):
            if bpy.context.scene.render.layers[count].StaticBool==True:
                render_node = tree.nodes.new(type='CompositorNodeRLayers')
                render_node.location = [0,300]
                if "." in render_node.name:
                    suffix = render_node.name[-3:]
                    stripp = render_node.name.strip(suffix)
                    render_node.name = stripp+ str(counter1+2)
                    if counter1 <= len(render_layers):
                        counter1 += 1
                    render_node.layer = layer.name
                else:  
                    render_node.name = "Render Layers."+str(counter1+1)
                    if counter1 < len(render_layers)-1:
                        counter1 += 1
                    render_node.layer = layer.name
            if bpy.context.scene.render.layers[count].StaticBool==False:
                imager_node = tree.nodes.new(type='CompositorNodeImage')
                imager_node.location = [0,300]
                if "." in imager_node.name:
                    suffix = imager_node.name[-3:]
                    stripp = imager_node.name.strip(suffix)
                    if counter1 <= len(render_layers):
                        counter1 += 1
                    imager_node.name = stripp+ str(counter1)
                    imager_node.image = bpy.data.images["img_"+rlayer_list[count]+".exr"]
            #setting up Z Combine Nodes
        for layer in render_layers:
            z_node = tree.nodes.new(type='CompositorNodeZcombine')
            z_node.location = (300,100)
            z_node.use_alpha = True
            if "." in z_node.name:
                suffix = z_node.name[-3:]
                stripp = z_node.name.strip(suffix)
                z_node.name = stripp+ str(counter2)
                if counter2 <= len(render_layers):
                    counter2 += 1
        tree.nodes["Z Combine"].name = "Z Combine.1"
        #LINKING NODES
        links = tree.links
        links.new(z_node.outputs[0], comp_node.inputs[0])
        links.new(z_node.outputs[0], view_node.inputs[0])
        z_node.inputs[3].default_value = 1e+10
        links.new(tree.nodes["Image"].outputs[0], z_node.inputs[2])
        #
        n = 1
        nn= 1
        for layer in tree.nodes:
            if n < len(render_layers):
                links.new(tree.nodes["Z Combine.%s"%str(n)].outputs[0],tree.nodes["Z Combine.%s"%str(n+1)].inputs[0])
                links.new(tree.nodes["Z Combine.%s"%str(n)].outputs[1],tree.nodes["Z Combine.%s"%str(n+1)].inputs[1])
                n +=1
            ###
            if nn < len(render_layers) and bpy.context.scene.render.layers[rlayer_list[nn]].StaticBool==True:
                links.new(tree.nodes["Render Layers.%s"%str(nn+1)].outputs[0],tree.nodes["Z Combine.%s"%str(nn)].inputs[2])
                links.new(tree.nodes["Render Layers.%s"%str(nn+1)].outputs[2],tree.nodes["Z Combine.%s"%str(nn)].inputs[3])
                nn +=1
            ###---
            if nn < len(render_layers) and bpy.context.scene.render.layers[rlayer_list[nn]].StaticBool==False:
                links.new(tree.nodes["Image.%s"%str(nn+1)].outputs[0],tree.nodes["Z Combine.%s"%str(nn)].inputs[2])
                links.new(tree.nodes["Image.%s"%str(nn+1)].outputs[2],tree.nodes["Z Combine.%s"%str(nn)].inputs[3])
                nn +=1
            ###---
        if 'Render Layers.1' in tree.nodes.keys():
            links.new(tree.nodes["Render Layers.1"].outputs[0],tree.nodes["Z Combine.1"].inputs[0])
            links.new(tree.nodes["Render Layers.1"].outputs[2],tree.nodes["Z Combine.1"].inputs[1])
        if "Image.1" in tree.nodes.keys():
            links.new(tree.nodes["Image.1"].outputs[0],tree.nodes["Z Combine.1"].inputs[0])
            links.new(tree.nodes["Image.1"].outputs['Depth'],tree.nodes["Z Combine.1"].inputs[1])
        return {"FINISHED"}

class RenderNow(bpy.types.Operator):
    bl_idname = "execute.render"
    bl_label = "Render Compositor setup"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context) :
        alpha = bpy.context.scene.cycles.film_transparent
        bpy.context.scene.cycles.film_transparent = True
        bpy.ops.render.render(animation=True)
        bpy.context.scene.cycles.film_transparent = alpha 
        return {"FINISHED"}
def register() :
    ###
    bpy.utils.register_class(MySettings)
    bpy.types.Scene.my_settings = \
        bpy.props.PointerProperty(type=MySettings)
    ####
    bpy.utils.register_class(Multiplanne_List)
    bpy.types.Scene.testindex = bpy.props.IntProperty()
    ###
    bpy.utils.register_class(NewLayer)
    bpy.utils.register_class(RenderNow)
    bpy.utils.register_class(AutoRenderNow)
    bpy.utils.register_class(MakeNow)
    bpy.utils.register_class(DeleteLayer)
    bpy.utils.register_class(RenderPanel)
    bpy.types.SceneRenderLayer.StaticBool = bpy.props.BoolProperty(
        name="StaticBool",
        description="Checked: The Render Layer,containts animated objects and will be rendered each frame || Unchecked: The Render Layer contains static objects and will be rendered just once, to save render times.",
        default = True)

def unregister() :
    bpy.utils.unregister_class(MySettings)
    bpy.utils.unregister_class(Multiplanne_List)
    bpy.utils.unregister_class(NewLayer)
    bpy.utils.unregister_class(RenderNow)
    bpy.utils.unregister_class(AutoRenderNow)
    bpy.utils.unregister_class(MakeNow)
    bpy.utils.unregister_class(DeleteLayer)
    bpy.utils.unregister_class(RenderPanel)
    del bpy.types.Scene.my_settings
    del bpy.types.SceneRenderLayer.StaticBool
    del bpy.types.Scene.testindex

    
if __name__ == "__main__":
    register()
