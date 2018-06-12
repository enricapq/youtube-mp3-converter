import logging as log
import os
import sys


def validate_url(url):
    # TODO or use youtube_dl
    if not url:
        raise ValueError


def validate_playlist(url):
    if not url:
        raise ValueError


def get_download_path():
    """Returns the default user's downloads path for linux, macOS or windows or the current
    dir if the OS is not one of those"""
    if sys.platform == 'darwin':
        # Mac OS X
        return os.path.join(os.path.expanduser('~'), 'downloads')
    elif sys.platform == 'linux':
        home = os.path.expanduser("~")
        return os.path.join(home, "Downloads")
    elif sys.platform in ('win32', 'cygwin') and os.name == 'nt':
        import winreg
        sub_key = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders'
        downloads_guid = '{374DE290-123F-4565-9164-39C4925E467B}'
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub_key) as key:
            location = winreg.QueryValueEx(key, downloads_guid)[0]
        return location
    else:
        log.warning(f"unknown OS {sys.platform}")
        # return current directory
        return os.getcwd()


def create_dir(path_dir):
    if not os.path.exists(path_dir):
        os.makedirs(path_dir)
