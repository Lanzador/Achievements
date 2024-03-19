import os
import sys
import requests

group_by_game = '-g' in sys.argv
subgroup_by_game = '-eg' in sys.argv or '-eg2' in sys.argv
subgroup_by_game_alt = '-eg2' in sys.argv

saves = {}
appids = set()
if not group_by_game:
    saves['Goldberg'] = {}
    saves['Codex'] = {}
    saves['ALi213'] = {}
    saves['SmartSteamEmu'] = {}

def add_save(appid, emu, user=None):
    appid = str(int(appid))
    if not group_by_game:
        if subgroup_by_game:
            if not appid in saves[emu]:
                saves[emu][appid] = []
            saves[emu][appid].append(user)
        else:
            if not user in saves[emu]:
                saves[emu][user] = []
            saves[emu][user].append(appid)
    else:
        if not appid in saves:
            saves[appid] = []
        saves[appid].append((emu, user))
    appids.add(appid)

def scan_for_appids(path, emu, user=None):
    for f in os.scandir(path):
        if f.is_dir():
            if emu == 'SmartSteamEmu':
                if f.name.isnumeric():
                    add_save(f.name, 'SmartSteamEmu', user)
                elif user == None:
                    scan_for_appids(os.path.join(path, f.name), 'SmartSteamEmu', f.name)
            elif not f.name.isnumeric():
                continue
            elif emu == 'ALi213':
                for f2 in os.scandir(os.path.join(path, f.name)):
                    add_save(f.name, 'ALi213', f2.name)
            else:
                add_save(f.name, emu, user)

p = os.path.join(os.environ['APPDATA'], 'Goldberg SteamEmu Saves')
scan_for_appids(p, 'Goldberg')

p = 'C:/Users/Public/Documents/Steam/CODEX/'
scan_for_appids(p, 'Codex', 'Documents')

p = os.path.join(os.environ['APPDATA'], 'Steam/CODEX')
scan_for_appids(p, 'Codex', 'AppData')

p = os.path.join(os.environ['USERPROFILE'], 'Documents/VALVE')
scan_for_appids(p, 'ALi213')

p = os.path.join(os.environ['APPDATA'], 'SmartSteamEmu')
scan_for_appids(p, 'SmartSteamEmu')

app_names = {}
try:
    app_list = requests.get('https://api.steampowered.com/ISteamApps/GetAppList/v2')
    if int(app_list.status_code / 100) != 4:
        app_list = app_list.json()['applist']['apps']
        for app in app_list:
            if str(app['appid']) in appids:
                app_names[str(app['appid'])] = app['name']
    else:
        print(f' ! Failed to download app names ({r.status_code})')
except requests.exceptions.ConnectionError:
    print(' ! Failed to download app names (Connection error)')

def get_name_str(appid):
    name_str = appid
    if appid in app_names:
        name_str += ' - ' + app_names[appid]
    return name_str

if group_by_game:
    for i in saves:
        print(get_name_str(i))
        for s in saves[i]:
            if s[1] != None:
                print(f'  {s[0]} ({s[1]})')
            else:
                print(f'  {s[0]}')
else:
    for e in saves:
        if len(saves[e]) > 0:
            print(e)
        if not subgroup_by_game:
            for u in saves[e]:
                spaces = '  '
                if u != None:
                    print('  ' + u)
                    spaces = '    '
                for i in saves[e][u]:
                    print(spaces + get_name_str(i))
        else:
            for i in saves[e]:
                if not subgroup_by_game_alt:
                    print('  ' + get_name_str(i))
                for u in saves[e][i]:
                    if u != None:
                        if not subgroup_by_game_alt:
                            print('    ' + u)
                        else:
                            print(f'  {get_name_str(i)} ({u})')

os.system('pause')