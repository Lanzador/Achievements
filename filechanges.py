import os
import platform
import json
import time
import struct

def get_player_achs_path(source, appid, extra=None):
    if source == 'goldberg':
        if platform.uname().system == 'Windows':
            return os.path.join(os.environ['APPDATA'], 'Goldberg SteamEmu Saves', appid, 'achievements.json')
        elif platform.uname().system == 'Linux':
            if os.environ.get('XDG_DATA_HOME') is not None:
                return os.path.join(os.path.expandvars('$XDG_DATA_HOME/Goldberg SteamEmu Saves'), appid, 'achievements.json')
            else:
                return os.path.join(os.path.expandvars('$HOME/.local/share/Goldberg SteamEmu Saves'), appid, 'achievements.json')
        else:
            print('Unable to determine location of player progress')
            exit(1)
    elif source == 'codex' and platform.uname().system == 'Windows':
        if extra == False:
            return os.path.join('C:/Users/Public/Documents/Steam/CODEX', appid, 'achievements.ini')
        else:
            return os.path.join(os.environ['APPDATA'], 'Steam/CODEX', appid, 'achievements.ini')
    else:
        print('Unable to determine location of player progress')
        exit(1)
        
def get_stats_path(source, appid, extra=None):
    if source == 'goldberg':
        if platform.uname().system == 'Windows':
            return os.path.join(os.environ['APPDATA'], 'Goldberg SteamEmu Saves', appid, 'stats')
        elif platform.uname().system == 'Linux':
            if os.environ.get('XDG_DATA_HOME') is not None:
                return os.path.join(os.path.expandvars('$XDG_DATA_HOME/Goldberg SteamEmu Saves'), appid, 'stats')
            else:
                return os.path.join(os.path.expandvars('$HOME/.local/share/Goldberg SteamEmu Saves'), appid, 'stats')
    elif source == 'codex' and platform.uname().system == 'Windows':
        if extra == False:
            return os.path.join('C:/Users/Public/Documents/Steam/CODEX', appid, 'stats.ini')
        else:
            return os.path.join(os.environ['APPDATA'], 'Steam/CODEX', appid, 'stats.ini')

class FileChecker:
    def __init__(self, filetype, locinfo, sleep_t):

        self.locinfo = locinfo
        self.source = locinfo['source']
        self.filetype = filetype
        self.sleep_t = sleep_t
        if filetype == 'player_achs':
            if self.source == 'goldberg':
                self.path = get_player_achs_path(locinfo['source'], locinfo['appid'])
            elif self.source == 'codex':
                self.path = get_player_achs_path(locinfo['source'], locinfo['appid'], locinfo['cdx_appdata'])
        elif filetype == 'stat':
            if self.source == 'goldberg':
                self.path = os.path.join(get_stats_path(locinfo['source'], locinfo['appid']), locinfo['name'])
            elif self.source == 'codex':
                self.path = get_stats_path(locinfo['source'], locinfo['appid'], locinfo['cdx_appdata'])
        try:
            self.last_check = os.stat(self.path).st_mtime
        except FileNotFoundError:
            self.last_check = None

    def check(self, force_read = False):
        try:
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
                    if self.source == 'goldberg':
                        with open(self.path) as changed_file:
                            try:
                                newdata = json.load(changed_file)
                            except json.decoder.JSONDecodeError:
                                print('Failed to read file (player achs). Will retry on next check.')
                                self.last_check = 'Retry'
                                return False, None
                    elif self.source == 'codex':
                        with open(self.path) as changed_file:
                            newdata = changed_file.read()

                elif self.filetype == 'stat':
                    if self.source == 'goldberg':
                        with open(self.path, 'rb') as changed_file:
                            try:
                                if self.locinfo['type'] == 'int':
                                    newdata = struct.unpack('i', changed_file.read(4))
                                elif self.locinfo['type'] == 'float':
                                    newdata = struct.unpack('f', changed_file.read(4))
                            except Exception:
                                print(f"Failed to read file (stat: {self.locinfo['name']}). Will retry on next check.")
                                self.last_check = 'Retry'
                                return False, None
                    elif self.source == 'codex':
                        with open(self.path) as changed_file:
                            try:
                                for l in changed_file.read().split('\n'):
                                    spl = l.split('=')
                                    if len(spl) == 2 and spl[0] == self.locinfo['name']:
                                        if self.locinfo['type'] == 'int':
                                            newdata = int(spl[1])
                                            break
                                        elif self.locinfo['type'] == 'float':
                                            newdata = float(spl[1])
                                            break
                            except Exception:
                                print(f"Failed to read file (stat: {self.locinfo['name']}). Will retry on next check.")
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