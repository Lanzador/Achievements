import os
import sys

if len(sys.argv) > 1:
    appid = sys.argv[1]
else:
    appid = input('Enter AppID:')

alias = []
try:
    with open('games/alias.txt') as aliasfile:
        alias = aliasfile.read()
    alias = alias.split('\n')
except FileNotFoundError:
    pass

for l in alias:
    spl = l.split('=', 1)
    if len(spl) > 1 and spl[1] == appid:
        appid = spl[0].split()[0]

if os.path.isdir(os.path.join(os.environ['APPDATA'], 'Goldberg SteamEmu Saves', appid)):
    print('Goldberg')

if os.path.isdir(f'C:/Users/Public/Documents/Steam/CODEX/{appid}'):
    print('Codex (Documents)')
if os.path.isdir(os.path.join(os.environ['APPDATA'], 'Steam/CODEX', appid)):
    print('Codex (AppData)')

p = os.path.join(os.environ['USERPROFILE'], 'Documents/VALVE', appid)
if os.path.isdir(p):
    for f in os.scandir(p):
        if f.is_dir():
            print(f'ALi213 ({f.name})')

if os.path.isdir(os.path.join(os.environ['APPDATA'], 'SmartSteamEmu', appid)):
    print('SmartSteamEmu')
p = os.path.join(os.environ['APPDATA'], 'SmartSteamEmu')
if os.path.isdir(p):
    for f in os.scandir(p):
        if f.is_dir() and os.path.isdir(os.path.join(p, f.name, appid)):
            print(f'SmartSteamEmu ({f.name})')

os.system('pause')