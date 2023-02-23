# Apex Legends Auto Shader

Blender addon that auto-shades Apex Legends characters.

## How To Use
Video: https://youtu.be/p-CK_bYSK4Y

For mesh and armatures, this addon can find and import all other textures based on the auto-imported albedo texture.

`Right-click (on armature or mesh) > Apex Shader` to access the menu.

**Make sure to `Apex Shader > Set Core Apex Shader blender file path` first, to use the pre-existing `Cores Apex Shader` from `Apex Shader.blend` !**

## Notes
+ This will delete existing shader nodes from active material. Should use on newly imported model / material.
+ FYI, This auto shader is done by getting the image directory by looking into material's `Image Texture`. Some requirements are:
  + (All armature's) mesh's active material have at least one `Image Texture` inside, and it should have a image file attached to it.
    + If there are multiple `Image Texture`, pick one randomly.
  + The `Image Texture`'s file path must be in the format auto-generated by Legion+.
    + e.g. `bloodhound_lgnd_v20_ascension_body_albedoTexture.png`, i.e. `<meshName>_<textureName>.<fileType>`
    + That means unnamed texture files (e.g. `0x53237a2cdd03344e.png`) cannot be imported this way.
  + It will search through that directory (which the image file resides in) and import all similarly-named textures.
    + e.g. `bloodhound_lgnd_v20_ascension_body_cavityTexture.png`, i.e. `<meshName>_*` in wildcard.
+ If the auto-shading failed and the shader nodes are ruined, you can add one `Image Texture` satisfying the above condition and try to shade it again.
+ Currently supported Legion-labeled textures are:
```
[O] albedoTexture
[O] aoTexture
[O] cavityTexture
[O] emissiveTexture
[O] glossTexture
[O] normalTexture
[O] specTexture
[O] opacityMultiplyTexture
  -> (ref. https://youtu.be/dMqk0jz749U?t=1108, may fail on some case)
[?] scatterThicknessTexture
  -> strange result in some cases, e.g. octane_base_body_scatterThicknessTexture
[X] anisoSpecDirTexture
[X] transmittanceTintTexture
[X] emissiveMultiplyTexture
[X] uvDistortionTexture

... (there may be other textures not listed here)
```

## Installation
Should be the same as any other addons on Github. ref. [dtzxporter/io_model_semodel](https://github.com/dtzxporter/io_model_semodel)

1. Clone this repository and zip it, or just download as zip file on Github. (`Code -> Download ZIP`)
2. `Edit -> Preferences -> Add-ons -> Install..` and choose the zip file.
3. Activate the addon by checking the box. 
   + You might have to search the addon if it is not shown automatically. (by the string `apex` or `Apex Legends Auto Shader Addon`).
4. `Save Preferences`.

## Problem
Some of the problem that may occur. Do note that this is just a helper addon, you should check the result and modify shader nodes when needed.

+ When shading `bloodhound_v21_heroknight_w` (Feral's Future legendary skin), the whole model would look invisible.
  + This is because their `opacityMultiplyTexture` is not like other model's opacity multiply texture, so the auto-shade method failed. This may also occur on other models.
  + Use option `Shade Selected Apex Legend (Without Opacity Multiplier)` instead, or if you already auto-shaded, use `Remove Texture From Selected Legends > Remove opacityMultiplyTexture` on armature.
+ When shading a lot of meshes all at once, blender may stop responding.
  + This is normal, it's just the addon took too long processing those textures. **DON'T CLOSE BLENDER** and wait a while longer, it will be good soon enough... (or do close blender if you give up waiting.)
  + Open console before shading (`Window > Toggle System Console`) to track progress.
+ Octane's skin looked orange-ish.
  + Its `octane_base_body_scatterThicknessTexture` does not look like it is properly exported...?
  + Use `Remove Texture From Selected Legends > Remove scatterThicknessTexture` on armature to remove that texture if you want.