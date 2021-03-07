"""Utility functions that don't need to be surfaced to a future user"""
import sqlite3
import os


NIRCMD = '..\\nircmd\\nircmdc.exe'
DB_PATH = "..\\.config"


def init_db():
    """Create the db, with default values if it doesn't already exists"""
    if not os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        conn.executescript(f"""CREATE TABLE config(key text, value text);
        INSERT INTO config VALUES ("interval", 86400000);""")
        conn.commit()


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
