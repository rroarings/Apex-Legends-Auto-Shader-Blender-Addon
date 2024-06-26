import bpy
from . import config
from pathlib import Path
from collections import defaultdict

shader_cache = {}
def fetchNodeGroupFromCacheOrFile(name: str, blend_fpath: Path, contain_name: str):
    """
        Get a shader node group from cache (if fetched before), else search from blend file.
        The cache is `shader_cache`.

        Args:
            name: the index for the cache
            blend_fpath: blend file path if cache miss
            contain_name: will do `contain_name in group.name` when searching from the file
    """
    blend_fpath = str(blend_fpath)

    # use cached node group for the same file if already loaded from file before
    if name in shader_cache:
        print(f'Use cached node group: {name}')
        # check cache integrity in case of RSAStruct error
        # (reference will become invalid when creating / reopening a file without closing blender)
        if 'invalid' in str(shader_cache[name]):
            print(f'Cache invalid, re-import...')
        else:
            return shader_cache[name]
    
    print(f'Import node group from file: {blend_fpath}')
    with bpy.data.libraries.load(blend_fpath) as (data_from, data_to):
        data_to.node_groups = data_from.node_groups

    # just return any shader matched in there
    for group in data_to.node_groups:
        if contain_name in group.name:
            shader_cache[name] = group
            return group
    else:
        raise Exception(f'No "{contain_name}" node tree in {blend_fpath}.')

class NodeAdder:
    """
        The class used for adding image shader nodes

        Note that since the image texture might be removed by "Remove Texture",
        you must guarentee that even if the image texture is directly removed,
        the rest of nodes you add won't affect the outcome.
    """
    @staticmethod
    def getShaderNodeGroup():
        """
            Return a node group. This will become a node and will be passed
            into addImageTexture() later.

            This will be called once every time a material is shaded.

            You can also return an empty node group and don't use this in addImageTexture...
        """
        raise NotImplementedError()

    @classmethod
    def addImageTexture(cls, img_path: Path, mat, shader_node_group, location=(0.0, 0.0)):
        """
            Given an image specified by `img_path`, attach that image to its appropriate position.
            Need to handle the creation of image node.

            shader_node_group is a node that is created by the node tree from getShaderNodeGroup()
            location should be the position of the image node (but not necessarily).
        """
        raise NotImplementedError()
        
class CoresNodeAdder(NodeAdder):
    """
        Cores Apex Shader from `Apex Shader.blend`
        credits `CoReArtZz` 
        ref. https://www.reddit.com/r/apexlegends/comments/jtg4a7/basic_guide_to_render_apex_legends_models_in/
    """

    @staticmethod
    def _addAlbedo(img_path, mat, cas_node_group, location):
        img_node = mat.node_tree.nodes.new(type='ShaderNodeTexImage')
        img_node.hide = True
        img_node.location = location
        img_node.image = bpy.data.images.load(str(img_path))
        mat.node_tree.links.new(img_node.outputs['Color'], cas_node_group.inputs['Albedo'])

    @staticmethod
    def _addNormal(img_path, mat, cas_node_group, location):
        img_node = mat.node_tree.nodes.new(type='ShaderNodeTexImage')
        img_node.hide = True
        img_node.location = location
        img_node.image = bpy.data.images.load(str(img_path))
        img_node.image.colorspace_settings.name = 'Non-Color'
        mat.node_tree.links.new(img_node.outputs['Color'], cas_node_group.inputs['Normal'])

    @staticmethod
    def _addAO(img_path, mat, cas_node_group, location):
        img_node = mat.node_tree.nodes.new(type='ShaderNodeTexImage')
        img_node.hide = True
        img_node.location = location
        img_node.image = bpy.data.images.load(str(img_path))
        mat.node_tree.links.new(img_node.outputs['Color'], cas_node_group.inputs['AO'])

    @staticmethod
    def _addGlossy(img_path, mat, cas_node_group, location):
        img_node = mat.node_tree.nodes.new(type='ShaderNodeTexImage')
        img_node.hide = True
        img_node.location = location
        img_node.image = bpy.data.images.load(str(img_path))
        mat.node_tree.links.new(img_node.outputs['Color'], cas_node_group.inputs['Glossy'])

    @staticmethod
    def _addEmmisive(img_path, mat, cas_node_group, location):
        img_node = mat.node_tree.nodes.new(type='ShaderNodeTexImage')
        img_node.hide = True
        img_node.location = location
        img_node.image = bpy.data.images.load(str(img_path))
        mat.node_tree.links.new(img_node.outputs['Color'], cas_node_group.inputs['Emission'])
        mat.node_tree.links.new(img_node.outputs['Color'], cas_node_group.inputs['Emission Color'])
    
    @staticmethod
    def _addCavity(img_path, mat, cas_node_group, location):
        img_node = mat.node_tree.nodes.new(type='ShaderNodeTexImage')
        img_node.hide = True
        img_node.location = location
        img_node.image = bpy.data.images.load(str(img_path))
        mat.node_tree.links.new(img_node.outputs['Color'], cas_node_group.inputs['Cavity'])

    @staticmethod
    def _addSpec(img_path, mat, cas_node_group, location):
        img_node = mat.node_tree.nodes.new(type='ShaderNodeTexImage')
        img_node.hide = True
        img_node.location = location
        img_node.image = bpy.data.images.load(str(img_path))
        mat.node_tree.links.new(img_node.outputs['Color'], cas_node_group.inputs['Specular'])

    @staticmethod
    def _addSubsurface(img_path, mat, cas_node_group, location):
        # scatterThicknessTexture is possibly just subsurface, so that texture will use this function for now
        img_node = mat.node_tree.nodes.new(type='ShaderNodeTexImage')
        img_node.hide = True
        img_node.location = location
        img_node.image = bpy.data.images.load(str(img_path))
        mat.node_tree.links.new(img_node.outputs['Color'], cas_node_group.inputs['Subsurface'])
        mat.node_tree.links.new(img_node.outputs['Color'], cas_node_group.inputs['Subsurface Color'])
    
    @staticmethod
    def _addAnisoSpecDir(img_path, mat, cas_node_group, location):
        pass
    
    @staticmethod
    def _addTransmittanceTint(img_path, mat, cas_node_group, location):
        pass
    
    @staticmethod
    def _addOpacityMultiply(img_path, mat, cas_node_group, location):
        img_node = mat.node_tree.nodes.new(type='ShaderNodeTexImage')
        img_node.hide = True
        img_node.location = location
        img_node.image = bpy.data.images.load(str(img_path))

        transparent_node = mat.node_tree.nodes.new(type='ShaderNodeBsdfTransparent')
        transparent_node.location = (200, 200)
        
        mix_shader_node = mat.node_tree.nodes.new(type='ShaderNodeMixShader')
        mix_shader_node.inputs[0].default_value = 1     # so if there's no image node as input it is no-op
        mix_shader_node.location = (400, 200)

        # find output node
        output_node = [node for node in mat.node_tree.nodes.values() if node.type == 'OUTPUT_MATERIAL'][0]

        # ref. https://youtu.be/dMqk0jz749U?t=1108
        img_node.image.colorspace_settings.name = 'Non-Color'
        mat.node_tree.links.new(img_node.outputs['Color'], mix_shader_node.inputs[0])
        mat.node_tree.links.new(transparent_node.outputs[0], mix_shader_node.inputs[1])

        # should actually take whatever is linked to output_node.inputs['Surface'] as input
        # but may not be the best to assume that. oh well.
        mat.node_tree.links.new(cas_node_group.outputs[0], mix_shader_node.inputs[2])
        mat.node_tree.links.new(mix_shader_node.outputs[0], output_node.inputs['Surface'])
        mat.blend_method = 'CLIP'
        
    
    method = {
        'albedoTexture': _addAlbedo,
        'aoTexture': _addAO,
        'cavityTexture': _addCavity,
        'emissiveTexture': _addEmmisive,
        'glossTexture': _addGlossy,
        'normalTexture': _addNormal,
        'specTexture': _addSpec,
        'opacityMultiplyTexture': _addOpacityMultiply,
        'scatterThicknessTexture': _addSubsurface,

        # those are things I don't even know how to deal with
        # (or so hard to deal with I just quitted)
        'anisoSpecDirTexture': _addAnisoSpecDir,
        'transmittanceTintTexture': _addTransmittanceTint,
    }

    @staticmethod
    def getShaderNodeGroup():
        filepath = config.CORE_APEX_SHADER_BLENDER_FILE
        return fetchNodeGroupFromCacheOrFile('CoresApexShader_cache', filepath, 'Cores Apex Shader')

    @classmethod
    def addImageTexture(cls, img_path, mat, cas_node_group, location=(0.0, 0.0)):
        # get name
        texture_name = img_path.stem[img_path.stem.rindex('_')+1:]
        if texture_name not in cls.method.keys():
            return False
        # add texture
        cls.method[texture_name](img_path, mat, cas_node_group, location)
        return True
        
class PlusNodeAdder(NodeAdder):
    """
        Apex Shader Plus from `Apex_Shader_Plus1.blend`
        credits `unknown` 
        ref. https://github.com/ovlack/apex-info/commit/a9ec3ff2fab88546b8f91c1d62fd399652fe23c2/
    """

    @staticmethod
    def _addAlbedo(img_path, mat, cas_node_group, location):
        img_node = mat.node_tree.nodes.new(type='ShaderNodeTexImage')
        img_node.hide = True
        img_node.location = location
        img_node.image = bpy.data.images.load(str(img_path))
        mat.node_tree.links.new(img_node.outputs['Color'], cas_node_group.inputs['Albedo'])

    @staticmethod
    def _addNormal(img_path, mat, cas_node_group, location):
        img_node = mat.node_tree.nodes.new(type='ShaderNodeTexImage')
        img_node.hide = True
        img_node.location = location
        img_node.image = bpy.data.images.load(str(img_path))
        img_node.image.colorspace_settings.name = 'Non-Color'
        mat.node_tree.links.new(img_node.outputs['Color'], cas_node_group.inputs['Normal Map'])

    @staticmethod
    def _addAO(img_path, mat, cas_node_group, location):
        img_node = mat.node_tree.nodes.new(type='ShaderNodeTexImage')
        img_node.hide = True
        img_node.location = location
        img_node.image = bpy.data.images.load(str(img_path))
        mat.node_tree.links.new(img_node.outputs['Color'], cas_node_group.inputs['AO (Ambient Occlussion)'])

    @staticmethod
    def _addGlossy(img_path, mat, cas_node_group, location):
        img_node = mat.node_tree.nodes.new(type='ShaderNodeTexImage')
        img_node.hide = True
        img_node.location = location
        img_node.image = bpy.data.images.load(str(img_path))
        mat.node_tree.links.new(img_node.outputs['Color'], cas_node_group.inputs['Glossiness'])

    @staticmethod
    def _addEmmisive(img_path, mat, cas_node_group, location):
        img_node = mat.node_tree.nodes.new(type='ShaderNodeTexImage')
        img_node.hide = True
        img_node.location = location
        img_node.image = bpy.data.images.load(str(img_path))
        mat.node_tree.links.new(img_node.outputs['Color'], cas_node_group.inputs['Emission'])
    
    @staticmethod
    def _addCavity(img_path, mat, cas_node_group, location):
        img_node = mat.node_tree.nodes.new(type='ShaderNodeTexImage')
        img_node.hide = True
        img_node.location = location
        img_node.image = bpy.data.images.load(str(img_path))
        mat.node_tree.links.new(img_node.outputs['Color'], cas_node_group.inputs['Cavity'])

    @staticmethod
    def _addSpec(img_path, mat, cas_node_group, location):
        img_node = mat.node_tree.nodes.new(type='ShaderNodeTexImage')
        img_node.hide = True
        img_node.location = location
        img_node.image = bpy.data.images.load(str(img_path))
        mat.node_tree.links.new(img_node.outputs['Color'], cas_node_group.inputs['Specular'])

    @staticmethod
    def _addSubsurface(img_path, mat, cas_node_group, location):
        # scatterThicknessTexture is possibly just subsurface, so that texture will use this function for now
        img_node = mat.node_tree.nodes.new(type='ShaderNodeTexImage')
        img_node.hide = True
        img_node.location = location
        img_node.image = bpy.data.images.load(str(img_path))
        mat.node_tree.links.new(img_node.outputs['Color'], cas_node_group.inputs['SSS (Subsurface Scattering)'])
        mat.node_tree.links.new(img_node.outputs['Alpha'], cas_node_group.inputs['SSS Alpha'])
        cas_node_group.inputs['SSS Strength'].default_value = 0.5
    
    @staticmethod
    def _addAnisoSpecDir(img_path, mat, cas_node_group, location):
        img_node = mat.node_tree.nodes.new(type='ShaderNodeTexImage')
        img_node.hide = True
        img_node.location = location
        img_node.image = bpy.data.images.load(str(img_path))
        mat.node_tree.links.new(img_node.outputs['Color'], cas_node_group.inputs['Anis-SpecDir'])
    
    @staticmethod
    def _addTransmittanceTint(img_path, mat, cas_node_group, location):
        pass
    
    @staticmethod
    def _addOpacityMultiply(img_path, mat, cas_node_group, location):
        img_node = mat.node_tree.nodes.new(type='ShaderNodeTexImage')
        img_node.hide = True
        img_node.location = location
        img_node.image = bpy.data.images.load(str(img_path))
        mat.node_tree.links.new(img_node.outputs['Color'], cas_node_group.inputs['Alpha//OpacityMult'])
        
    
    method = {
        'albedoTexture': _addAlbedo,
        'aoTexture': _addAO,
        'cavityTexture': _addCavity,
        'emissiveTexture': _addEmmisive,
        'glossTexture': _addGlossy,
        'normalTexture': _addNormal,
        'specTexture': _addSpec,
        'opacityMultiplyTexture': _addOpacityMultiply,
        'scatterThicknessTexture': _addSubsurface,

        # those are things I don't even know how to deal with
        # (or so hard to deal with I just quitted)
        'anisoSpecDirTexture': _addAnisoSpecDir,
        'transmittanceTintTexture': _addTransmittanceTint,
    }

    @staticmethod
    def getShaderNodeGroup():
        filepath = config.PLUS_APEX_SHADER_BLENDER_FILE
        return fetchNodeGroupFromCacheOrFile('PlusNodeAdder_cache', filepath, 'Apex Shader+')

    @classmethod
    def addImageTexture(cls, img_path, mat, cas_node_group, location=(0.0, 0.0)):
        # get name
        texture_name = img_path.stem[img_path.stem.rindex('_')+1:]
        if texture_name not in cls.method.keys():
            return False
        # add texture
        cls.method[texture_name](img_path, mat, cas_node_group, location)
        return True

class PathfinderEmoteNodeAdder(CoresNodeAdder):
    """
        Translate UV map for emote's albedo texture to use different emote.
        TextureCoordinate.UV + (x, y, 0) to access all 12 emotes, where
        - x in [0, 0.25, 0.5, 0.75]
        - y in [0, 0.375, 0.63]

        The actual node group's specification are:

        value = getValueInput()             # increment 0.1
        v1 = truncate((value + 24) * 10)    # +24 because if value start at 0 then some emotes will
                                            # repeat frequently, for unknown reason
        x = (v1 % 4) * 0.25
        v2 = truncate(v1 / 4) % 3
        y = (v2 > 0.1) * 0.375 + (v2 > 1.1) * 0.255
        output = getTexCoordUVInput() + (x, y, 0)

        connect output to albedo texture's vector input.
    """
    @staticmethod
    def getPathfinderUVTransformNodeGroup():
        # the node group spec above is from a built-in node.
        filepath = config.PATHFINDER_EMOTE_SHADER_BLENDER_FILE
        return fetchNodeGroupFromCacheOrFile('PathfinderEmoteNodeAdder_cache', filepath, 'Pathfinder Emote UV Transform Node')
        
    @staticmethod
    def _addAlbedo(img_path, mat, cas_node_group, location):
        img_node = mat.node_tree.nodes.new(type='ShaderNodeTexImage')
        img_node.hide = True
        img_node.location = location
        img_node.image = bpy.data.images.load(str(img_path))
        mat.node_tree.links.new(img_node.outputs['Color'], cas_node_group.inputs['Albedo'])

        path_node_group = mat.node_tree.nodes.new(type='ShaderNodeGroup')
        path_node_group.node_tree = PathfinderEmoteNodeAdder.getPathfinderUVTransformNodeGroup()
        path_node_group.hide = True
        path_node_group.location = (-200 + location[0], location[1])

        texture_coord_node = mat.node_tree.nodes.new(type='ShaderNodeTexCoord')
        texture_coord_node.hide = True
        texture_coord_node.location = (-400 + location[0], location[1] + 50)

        value_node = mat.node_tree.nodes.new(type='ShaderNodeValue')
        value_node.label = 'Value (Click its left & right button to rotate emote)'
        value_node.width = 300
        value_node.location = (-590 + location[0], location[1] - 50)

        mat.node_tree.links.new(texture_coord_node.outputs['UV'], path_node_group.inputs[0])
        mat.node_tree.links.new(value_node.outputs[0], path_node_group.inputs[1])

        mat.node_tree.links.new(path_node_group.outputs[0], img_node.inputs[0])
        return 


    method = CoresNodeAdder.method.copy()
    method['albedoTexture'] = _addAlbedo
 
class TitanfallSGNodeAdder(NodeAdder):
    """
        SG Shader from `SG_Shader.blend`
        credits `unknown?` 
        ref. 
            - https://noskill.gitbook.io/titanfall2/r2-ripping/model-ripping
            - https://github.com/Wanty5883/Titanfall2/blob/master/tools/SG_Shader.blend
    """

    @staticmethod
    def _addDiffuse(img_path, mat, cas_node_group, location):
        img_node = mat.node_tree.nodes.new(type='ShaderNodeTexImage')
        img_node.hide = True
        img_node.location = location
        img_node.image = bpy.data.images.load(str(img_path))
        mat.node_tree.links.new(img_node.outputs['Color'], cas_node_group.inputs['Diffuse map'])

    @staticmethod
    def _addNormal(img_path, mat, cas_node_group, location):
        img_node = mat.node_tree.nodes.new(type='ShaderNodeTexImage')
        img_node.hide = True
        img_node.location = location
        img_node.image = bpy.data.images.load(str(img_path))
        img_node.image.colorspace_settings.name = 'Non-Color'
        mat.node_tree.links.new(img_node.outputs['Color'], cas_node_group.inputs['Normal map'])

    @staticmethod
    def _addAO(img_path, mat, cas_node_group, location):
        img_node = mat.node_tree.nodes.new(type='ShaderNodeTexImage')
        img_node.hide = True
        img_node.location = location
        img_node.image = bpy.data.images.load(str(img_path))
        mat.node_tree.links.new(img_node.outputs['Color'], cas_node_group.inputs['AO map'])

    @staticmethod
    def _addGlossy(img_path, mat, cas_node_group, location):
        img_node = mat.node_tree.nodes.new(type='ShaderNodeTexImage')
        img_node.hide = True
        img_node.location = location
        img_node.image = bpy.data.images.load(str(img_path))
        mat.node_tree.links.new(img_node.outputs['Color'], cas_node_group.inputs['Glossiness map'])

    @staticmethod
    def _addEmmisive(img_path, mat, cas_node_group, location):
        img_node = mat.node_tree.nodes.new(type='ShaderNodeTexImage')
        img_node.hide = True
        img_node.location = (location[0] - 500, location[1])
        img_node.image = bpy.data.images.load(str(img_path))

        # add mix color node
        # s.t. if you want pilot emission to shine cyan, just make fac = 1
        mix_rgb_node = mat.node_tree.nodes.new(type='ShaderNodeMixRGB')
        mix_rgb_node.blend_type = 'MULTIPLY'
        mix_rgb_node.inputs['Fac'].default_value = 0
        mix_rgb_node.inputs['Color2'].default_value = [0, 1, 1, 1]  # cyan color
        mix_rgb_node.location = (location[0] - 200, location[1])
        mix_rgb_node.label = 'Emission Mix Node'

        mat.node_tree.links.new(img_node.outputs['Color'], mix_rgb_node.inputs['Color1'])
        mat.node_tree.links.new(mix_rgb_node.outputs['Color'], cas_node_group.inputs['Emission input'])
    
    @staticmethod
    def _addCavity(img_path, mat, cas_node_group, location):
        img_node = mat.node_tree.nodes.new(type='ShaderNodeTexImage')
        img_node.hide = True
        img_node.location = location
        img_node.image = bpy.data.images.load(str(img_path))
        mat.node_tree.links.new(img_node.outputs['Color'], cas_node_group.inputs['Cavity map'])

    @staticmethod
    def _addSpec(img_path, mat, cas_node_group, location):
        img_node = mat.node_tree.nodes.new(type='ShaderNodeTexImage')
        img_node.hide = True
        img_node.location = location
        img_node.image = bpy.data.images.load(str(img_path))
        mat.node_tree.links.new(img_node.outputs['Color'], cas_node_group.inputs['Specular map'])

    @staticmethod
    def _addOpacityMultiply(img_path, mat, cas_node_group, location):
        img_node = mat.node_tree.nodes.new(type='ShaderNodeTexImage')
        img_node.hide = True
        img_node.location = location
        img_node.image = bpy.data.images.load(str(img_path))

        transparent_node = mat.node_tree.nodes.new(type='ShaderNodeBsdfTransparent')
        transparent_node.location = (200, 200)
        
        mix_shader_node = mat.node_tree.nodes.new(type='ShaderNodeMixShader')
        mix_shader_node.inputs[0].default_value = 1     # so if there's no image node as input it is no-op
        mix_shader_node.location = (400, 200)

        # find output node
        output_node = [node for node in mat.node_tree.nodes.values() if node.type == 'OUTPUT_MATERIAL'][0]

        # ref. https://youtu.be/dMqk0jz749U?t=1108
        img_node.image.colorspace_settings.name = 'Non-Color'
        mat.node_tree.links.new(img_node.outputs['Color'], mix_shader_node.inputs[0])
        mat.node_tree.links.new(transparent_node.outputs[0], mix_shader_node.inputs[1])

        # should actually take whatever is linked to output_node.inputs['Surface'] as input
        # but may not be the best to assume that. oh well.
        mat.node_tree.links.new(cas_node_group.outputs[0], mix_shader_node.inputs[2])
        mat.node_tree.links.new(mix_shader_node.outputs[0], output_node.inputs['Surface'])
        mat.blend_method = 'CLIP'
        
    
    method = {
        'col': _addDiffuse,
        'ao': _addAO,
        'cav': _addCavity,
        'ilm': _addEmmisive,
        'gls': _addGlossy,
        'nml': _addNormal,
        'spc': _addSpec,
        'opa': _addOpacityMultiply,
    }

    @staticmethod
    def getShaderNodeGroup():
        filepath = config.SG_TITANFALL_SHADER_BLENDER_FILE
        return fetchNodeGroupFromCacheOrFile('TitanfallSGNodeAdder_cache', filepath, 'S/G-Blender')

    @classmethod
    def addImageTexture(cls, img_path, mat, cas_node_group, location=(0.0, 0.0)):
        # get name
        texture_name = img_path.stem[img_path.stem.rindex('_')+1:]
        if texture_name not in cls.method.keys():
            return False
        # add texture
        cls.method[texture_name](img_path, mat, cas_node_group, location)
        return True
        