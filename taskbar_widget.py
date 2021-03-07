"""A taskbar widget, for quick access to some common tasks

Mostly just ends up being a wrapper around nircmdc.exe (included)"""

import winreg
import sqlite3
import os

import send2trash
from infi.systray import SysTrayIcon
import imageio

DEFAULT_TIMES = (86400000, 600000)
NIRCMD = 'nircmd\\nircmdc.exe'
DB_PATH = ".config"


def create_db():
    """Create the db, with default values if it doesn't already exists"""
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(f"""CREATE TABLE config(key text, value text);
    INSERT INTO config VALUES ("interval", {DEFAULT_TIMES[0]});""")
    return conn.commit()


def get_key(key):
    """Get a value from the db
    We don't cache the connection because:
    1. It doesn't handle threading (which our systray library uses)
    2. It's performant enough anyway that who gives a shit for this usecase"""
    conn = sqlite3.connect(DB_PATH)
    query = conn.execute('SELECT value FROM config WHERE key LIKE ?', (key,))
    return query.fetchone()[0]


def set_key(key, value):
    """Save a value to the db
    We don't cache the connection because:
    1. It doesn't handle threading (which our systray library uses)
    2. It's performant enough anyway that who gives a shit for this usecase"""
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        'UPDATE config SET value = ? WHERE key LIKE ?', (value, key))
    return conn.commit()


def show_notification(message, image="shell32.dll,-154"):
    """Pop a tray notification with given text"""
    sanitised = message.replace('"', '\\"')
    os.system(
        f'{NIRCMD} trayballoon "taskbar_widget.py" "{sanitised}" "{image}" 3000')


def set_wallpaper_timeout(_):
    """Switch the live wallpaper timeout, and the timeout stored in the db"""

    with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                        r'Control Panel\Personalization\Desktop Slideshow',
                        0, winreg.KEY_ALL_ACCESS) as key:

        old_interval, reg_type = winreg.QueryValueEx(key, 'Interval')
        new_interval = int(get_key('interval'))

        # In case state gets fucked up
        if new_interval == old_interval:
            new_interval = DEFAULT_TIMES[0] \
                if new_interval != DEFAULT_TIMES[0] else DEFAULT_TIMES[1]

        winreg.SetValueEx(key, 'Interval', 0, reg_type, new_interval)
        set_key('interval', old_interval)
        # Make the timeout human readable (instead of a massive number of ms)
        new_interval_min = new_interval/60000
        time_text = f"{int(new_interval_min)} minutes" if new_interval_min < 60 \
            else f"{int(new_interval_min/60)} hours"
        show_notification(f"Set the wallpaper timeout to {time_text}")


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
        show_notification(f"Deleted {wallpaper_path}", deleted_path)
        # Actually remove the images
        # Note that we send the wallpaper to the trash in case of misclick
        # Generated .ico is gone forever though, cause who cares
        send2trash.send2trash(wallpaper_path)
        os.remove(deleted_path)


def set_audio_input(audio_input, friendly_name):
    """Set the default audio input to a given value"""
    os.system(f'{NIRCMD} setdefaultsounddevice {audio_input}')
    show_notification(f"Set audio to {friendly_name}")


# The following could all be lambdas, but my formatter throws a hissy,
# and I can't be arsed fighting it
def set_headset(_):
    """Set audio to headset"""
    set_audio_input("Speakers", "headset")


def set_external(_):
    """Set audio to 3.5mm/external"""
    set_audio_input("Speaker/Headphone", "3.5mm/external")


def delete_laptop_wallpaper(_):
    """Delete the wallpaper currently on laptop screen"""
    delete_current_wallpaper(0)


def delete_external_wallpaper(_):
    """Delete the wallpaper currently on external monitor"""
    delete_current_wallpaper(1)


if __name__ == '__main__':
    if not os.path.exists(DB_PATH):
        create_db()

    MENU = (("Toggle wallpaper timeout", None, set_wallpaper_timeout),
            ("Set audio to headset", None, set_headset),
            ("Set audio to 3.5mm/external", None, set_external),
            ("Delete wallpaper on laptop", None, delete_laptop_wallpaper),
            ("Delete wallpaper on monitor", None, delete_external_wallpaper))

    SYS_TRAY = SysTrayIcon(None, "Right click for options", MENU)
    SYS_TRAY.start()
    show_notification("Started taskbar_widget")
