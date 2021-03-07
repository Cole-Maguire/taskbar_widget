# Readme.md

A collection of minor utilities/tasks that I wanted to have a shortcut on my taskbar for.

Heavily relies on nircmd, which is redistributed in `/nircmd`.

## Install

For Windows only

```powershell
pip -r requirements.txt
```

## Included functions

Obviously this is customised to my setup, but the following are the main functions, and should be able to be fairly easily adapted as necessary:

|Function|Usages|Purpose|
|-|-|-|
|`set_audio_input`|`_set_headset`, `_set_external`|Set the default audio output. May be difficult to adapt, as the naming convention used by windows/nircmd is odd|
|`toggle_wallpaper_timeout`|`toggle_wallpaper_timeout`|Pauses desktop background slideshow (to aid performance)|
| `delete_current_wallpaper`|`_delete_laptop_wallpaper`,`_delete_external_wallpaper`|Deletes the wallpaper currently displayed on a given screen|
