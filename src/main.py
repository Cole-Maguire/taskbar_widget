"""A collection of minor utilities/tasks that I wanted to have a shortcut on my taskbar for."""

import winreg
import os

import send2trash
from infi.systray import SysTrayIcon
import imageio

import util


DEFAULT_TIMES = (86400000, 600000)


def toggle_wallpaper_timeout(_):
    """Switch the live wallpaper timeout, and the timeout stored in the db"""

    with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                        r'Control Panel\Personalization\Desktop Slideshow',
                        0, winreg.KEY_ALL_ACCESS) as key:

        old_interval, reg_type = winreg.QueryValueEx(key, 'Interval')
        new_interval = int(util.get_key('interval'))

        # In case state gets fucked up
        if new_interval == old_interval:
            new_interval = DEFAULT_TIMES[0] \
                if new_interval != DEFAULT_TIMES[0] else DEFAULT_TIMES[1]

        winreg.SetValueEx(key, 'Interval', 0, reg_type, new_interval)
        util.set_key('interval', old_interval)
        # Make the timeout human readable (instead of a massive number of ms)
        new_interval_min = new_interval/60000
        time_text = f"{int(new_interval_min)} minutes" if new_interval_min < 60 \
            else f"{int(new_interval_min/60)} hours"
        util.show_notification(f"Set the wallpaper timeout to {time_text}")


def delete_current_wallpaper(monitor):
    """Delete the wallpaper on the specified monitor.

    There appears to be no pratical way of simulating the "Next desktop background" native,
    so we'll just have to live with our shit wallpaper till next rotation"""

    with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                        r'Control Panel\Desktop',
                        0, winreg.KEY_READ) as key:
        result = winreg.QueryValueEx(
            key, f'TranscodedImageCache_00{monitor}')
        # Registry struct contains the path in bytes 24:544.
        # Uses \x00 as padding at the end of the string,
        # as well as between each byte of actual content (for some reason)
        wallpaper_path = result[0][24:544:2].decode().replace('\x00', '')
        # Notifies, with an image of the deleted image (meta)
        deleted_path = 'deleted.ico'
        img = imageio.imread(wallpaper_path)
        imageio.imwrite(deleted_path, img)
        util.show_notification(f"Deleted {wallpaper_path}", deleted_path)
        # Actually remove the images
        # Note that we send the wallpaper to the trash in case of misclick
        # Generated .ico is gone forever though, cause who cares
        send2trash.send2trash(wallpaper_path)
        os.remove(deleted_path)


def set_audio_output(audio_output, friendly_name):
    """Set the default audio output to a given value"""
    os.system(f'{util.NIRCMD} setdefaultsounddevice {audio_output}')
    util.show_notification(f"Set audio to {friendly_name}")


# The following could all be lambdas, but my formatter throws a hissy,
# and I can't be arsed fighting it.
def _set_headset(_):
    """Set audio to headset"""
    set_audio_output("Speakers", "headset")


def _set_external(_):
    """Set audio to 3.5mm/external"""
    set_audio_output("Speaker/Headphone", "3.5mm/external")


def _delete_laptop_wallpaper(_):
    """Delete the wallpaper currently on laptop screen"""
    delete_current_wallpaper(0)


def _delete_external_wallpaper(_):
    """Delete the wallpaper currently on external monitor"""
    delete_current_wallpaper(1)


if __name__ == '__main__':
    util.init_db()

    MENU = (("Toggle wallpaper timeout", None, toggle_wallpaper_timeout),
            ("Set audio to headset", None, _set_headset),
            ("Set audio to 3.5mm/external", None, _set_external),
            ("Delete wallpaper on laptop", None, _delete_laptop_wallpaper),
            ("Delete wallpaper on monitor", None, _delete_external_wallpaper))

    SYS_TRAY = SysTrayIcon(None, "Right click for options", MENU)
    SYS_TRAY.start()
    util.show_notification("Started taskbar_widget")
