import os
import sys
import json
from PIL import Image

if len(sys.argv) > 1 and not (len(sys.argv) == 2 and sys.argv[1] == '-s'):
    appids = set(sys.argv[1:])
else:
    appids = set(input('Enter AppID(s): ').split())

if '*' in appids:
    appids = set()
    for f in os.scandir('games'):
        if f.is_dir() and f.name.isnumeric():
            appids.add(f.name)
else:
    with open('games/alias.txt') as aliasfile:
        alias = aliasfile.read()
    alias = alias.split('\n')
    for l in alias:
        spl = l.split('=')
        if len(spl) > 1 and spl[1] in appids:
            appids.discard(spl[1])
            appids.add(spl[0].split()[0])

    numeric = set()
    for appid in appids:
        if appid.isnumeric():
            numeric.add(appid)
    appids = numeric

done_apps = 0
errors = {}
for appid in appids:
    with open(f'games/{appid}/achievements.json') as achsfile:
        achs = json.load(achsfile)

    icons = set()
    for ach in achs:
        if 'icon' in ach:
            icons.add(ach['icon'])
        if 'icon_gray' in ach:
            icons.add(ach['icon_gray'])

    if not os.path.isdir(f'games/ico/{appid}'):
        os.makedirs(f'games/ico/{appid}')

    done = 0
    errors[appid] = 0
    for icon in icons:
        done += 1
        if not os.path.isfile(f'games/ico/{appid}/{icon}.ico'):
            try:
                img = Image.open(f'games/{appid}/achievement_images/{icon}')
                img.save(f'games/ico/{appid}/{icon}.ico')
            except Exception:
                errors[appid] += 1
        if not '-s' in sys.argv:
            print(f'{done_apps}/{len(appids)} {appid} {done}/{len(icons)}')
    
    done_apps += 1

for app in errors:
    if errors[app] > 0:
        print(f'{app} - {errors[app]} error(s)')