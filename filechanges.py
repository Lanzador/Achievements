import os
import sys
import platform
import json
import time
import struct
from experimental import *

if platform.uname().system == 'Windows':
    import ctypes
    from ctypes.wintypes import MAX_PATH
    dll = ctypes.windll.shell32

def get_player_achs_path(source, appid, extra=None):
    if source == 'goldberg':
        if (extra != None and len(extra) > 5 and extra[:5] == 'path:'):
            return os.path.join(extra[5:], appid, 'achievements.json')
        dir_name = 'Goldberg SteamEmu Saves'
        if extra == 'f':
            dir_name = 'GSE Saves'
        if platform.uname().system == 'Windows':
            return os.path.join(os.environ['APPDATA'], dir_name, appid, 'achievements.json')
        elif platform.uname().system == 'Linux':
            if os.environ.get('XDG_DATA_HOME') is not None:
                return os.path.join(os.path.expandvars('$XDG_DATA_HOME'), dir_name, appid, 'achievements.json')
            else:
                return os.path.join(os.path.expandvars('$HOME/.local/share'), dir_name, appid, 'achievements.json')
        else:
            print('Unable to determine location of player progress')
            sys.exit()
    elif source == 'codex' and platform.uname().system == 'Windows':
        if extra == False:
            buf = ctypes.create_unicode_buffer(MAX_PATH + 1)
            if not dll.SHGetSpecialFolderPathW(None, buf, 46, False):
                print('Failed to get path to documents folder')
            return os.path.join(buf.value, 'Steam/CODEX', appid, 'achievements.ini')
        else:
            return os.path.join(os.environ['APPDATA'], 'Steam/CODEX', appid, 'achievements.ini')
    elif source == 'ali213' and platform.uname().system == 'Windows':
        if not (extra != None and len(extra) > 5 and extra[:5] == 'path:'):
            buf = ctypes.create_unicode_buffer(MAX_PATH + 1)
            if not dll.SHGetSpecialFolderPathW(None, buf, 5, False):
                print('Failed to get path to documents folder')
            return os.path.join(buf.value, 'VALVE', appid, extra, 'Stats/Achievements.Bin')
        else:
            return os.path.join(extra[5:], 'Stats/Achievements.Bin')
    elif source == 'sse' and platform.uname().system == 'Windows':
        if extra == None:
            return os.path.join(os.environ['APPDATA'], 'SmartSteamEmu', appid, 'stats.bin')
        elif not (len(extra) > 5 and extra[:5] == 'path:'):
            return os.path.join(os.environ['APPDATA'], 'SmartSteamEmu', extra, appid, 'stats.bin')
        else:
            return os.path.join(extra[5:], appid, 'stats.bin')
    else:
        print('Unable to determine location of player progress')
        sys.exit()
        
def get_stats_path(source, appid, extra=None):
    if source == 'goldberg':
        if (extra != None and len(extra) > 5 and extra[:5] == 'path:'):
            return os.path.join(extra[5:], appid, 'stats')
        dir_name = 'Goldberg SteamEmu Saves'
        if extra == 'f':
            dir_name = 'GSE Saves'
        if platform.uname().system == 'Windows':
            return os.path.join(os.environ['APPDATA'], dir_name, appid, 'stats')
        elif platform.uname().system == 'Linux':
            if os.environ.get('XDG_DATA_HOME') is not None:
                return os.path.join(os.path.expandvars('$XDG_DATA_HOME'), dir_name, appid, 'stats')
            else:
                return os.path.join(os.path.expandvars('$HOME/.local/share'), dir_name, appid, 'stats')
    elif source == 'codex' and platform.uname().system == 'Windows':
        if extra == False:
            buf = ctypes.create_unicode_buffer(MAX_PATH + 1)
            if not dll.SHGetSpecialFolderPathW(None, buf, 46, False):
                print('Failed to get path to documents folder')
            return os.path.join(buf.value, 'Steam/CODEX', appid, 'stats.ini')
        else:
            return os.path.join(os.environ['APPDATA'], 'Steam/CODEX', appid, 'stats.ini')
    elif source == 'ali213' and platform.uname().system == 'Windows':
        if not (extra != None and len(extra) > 5 and extra[:5] == 'path:'):
            buf = ctypes.create_unicode_buffer(MAX_PATH + 1)
            if not dll.SHGetSpecialFolderPathW(None, buf, 5, False):
                print('Failed to get path to documents folder')
            return os.path.join(buf.value, 'VALVE', appid, extra, 'Stats/Stats.Bin')
        else:
            return os.path.join(extra[5:], 'Stats/Stats.Bin')
    elif source == 'sse' and platform.uname().system == 'Windows':
        if extra == None:
            return os.path.join(os.environ['APPDATA'], 'SmartSteamEmu', appid, 'stats.bin')
        elif not (len(extra) > 5 and extra[:5] == 'path:'):
            return os.path.join(os.environ['APPDATA'], 'SmartSteamEmu', extra, appid, 'stats.bin')
        else:
            return os.path.join(extra[5:], appid, 'stats.bin')
    else:
        print('Unable to determine location of player stats')
        sys.exit()

class FileChecker:
    def __init__(self, filetype, locinfo, sleep_t):

        self.locinfo = locinfo
        self.source = locinfo['source']
        self.filetype = filetype
        self.sleep_t = sleep_t
        if filetype == 'player_achs':
            self.path = get_player_achs_path(locinfo['source'], locinfo['appid'], locinfo['source_extra'])
        elif filetype == 'stat':
            if self.source == 'goldberg':
                self.path1 = os.path.join(get_stats_path(locinfo['source'], locinfo['appid']), locinfo['name'].lower())
                self.path2 = os.path.join(get_stats_path(locinfo['source'], locinfo['appid']), locinfo['name'])
                self.path = self.path1 if os.path.isfile(self.path1) else self.path2
            else:
                self.path = get_stats_path(locinfo['source'], locinfo['appid'], locinfo['source_extra'])
        try:
            self.last_check = os.stat(self.path).st_mtime
        except FileNotFoundError:
            self.last_check = None

    def check(self, force_read = False):
        try:
            if self.source == 'goldberg' and self.filetype == 'stat':
                self.path = self.path1
                if not os.path.isfile(self.path):
                    self.path = self.path2

            stamp = os.stat(self.path).st_mtime
            if stamp != self.last_check or force_read:
                if self.sleep_t > 0:
                    time.sleep(self.sleep_t)
                    currtime = time.time()
                    loop_counter = 0
                    while currtime < os.stat(self.path).st_mtime + self.sleep_t:
                        loop_counter += 1
                        if loop_counter > 9:
                            print('File change was ignored because the file kept changing')
                            return False, None
                        time.sleep(self.sleep_t)
                        currtime = time.time()

                self.last_check = stamp
                newdata = None

                if self.filetype == 'player_achs':
                    m = 'rt'
                    if self.source == 'sse':
                        m = 'rb'
                    with open(self.path, m) as changed_file:
                        try:
                            if self.source == 'goldberg':
                                newdata = json.load(changed_file)
                            else:
                                newdata = changed_file.read()
                        except Exception as ex:
                            print(f'Failed to read file (player achs) - {type(ex).__name__}')
                            self.last_check = 'Retry'
                            return False, None

                elif self.filetype == 'stat':
                    if self.source == 'goldberg':
                        with open(self.path, 'rb') as changed_file:
                            try:
                                if self.locinfo['type'] == 'int':
                                    newdata = struct.unpack('i', changed_file.read(4))[0]
                                elif self.locinfo['type'] == 'float':
                                    newdata = struct.unpack('f', changed_file.read(4))[0]
                            except Exception as ex:
                                print(f"Failed to read file (stat: {self.locinfo['name']}) - {type(ex).__name__}")
                                self.last_check = 'Retry'
                                return False, None
                    elif self.source in ('codex', 'ali213'):
                        with open(self.path) as changed_file:
                            try:
                                newdata = changed_file.read()
                            except Exception as ex:
                                print(f'Failed to read file (stats) - {type(ex).__name__}')
                                self.last_check = 'Retry'
                                return False, None
                    elif self.source == 'sse':
                        with open(self.path, 'rb') as changed_file:
                            try:
                                newdata = changed_file.read()
                            except Exception as ex:
                                print(f'Failed to read file (stats) - {type(ex).__name__}')
                                self.last_check = 'Retry'
                                return False, None
                return True, newdata
            else:
                return False, None
        except FileNotFoundError:
            if self.last_check != None:
                self.last_check = None
                return True, None
            return False, None
        except Exception as ex:
            t = 'player achs'
            if self.filetype == 'stat':
                t = 'stats'
                if self.source == 'goldberg':
                    t = f"stat: {self.locinfo['name']}"
            print(f'Failed to open file ({t}) - {type(ex).__name__}')
            self.last_check = 'Retry'
            return False, None