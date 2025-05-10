import os
import sys
import json
import time
from PIL import Image

silent = '-s' in sys.argv
check = '-c' in sys.argv

if len(set(sys.argv)) - int(silent) - int(check) > 1:
    appids = set(sys.argv[1:])
else:
    appids = set(input('Enter AppID(s): ').split())
    silent = max(silent, '-s' in appids)
    check = max(check, '-c' in appids)

t = time.time()

folderless = set()
if '*' in appids:
    appids = set()
    for f in os.scandir('games'):
        if f.is_dir() and f.name.isnumeric() and os.path.isfile(f'games/{f.name}/achievements.json'):
            appids.add(f.name)
else:
    alias = []
    try:
        with open('games/alias.txt') as aliasfile:
            alias = aliasfile.read()
        alias = alias.split('\n')
    except FileNotFoundError:
        pass

    for l in alias:
        spl = l.split('=', 1)
        if len(spl) > 1 and spl[1] in appids:
            appids.discard(spl[1])
            appids.add(spl[0].split()[0])

    numeric = set()
    for appid in appids:
        if appid.isnumeric():
            if os.path.isfile(f'games/{appid}/achievements.json'):
                numeric.add(appid)
            else:
                folderless.add(appid)
    appids = numeric

done_apps = 1
total_conv = 0
errors = {}
check_result = []
for appid in appids:
    config_from_fork = os.path.isdir(f'games/{appid}/img')
    icons_path = f'games/{appid}/achievement_images'
    if config_from_fork:
        icons_path = f'games/{appid}/img'
    conv_path = icons_path + '/ico'

    if check:
        if not os.path.isdir(conv_path):
            check_result.append(appid)
        continue

    with open(f'games/{appid}/achievements.json') as achsfile:
        achs = json.load(achsfile)

    icons = set()
    for ach in achs:
        if 'icon' in ach:
            icons.add(ach['icon'])
        if 'icon_gray' in ach:
            icons.add(ach['icon_gray'])

    if not os.path.isdir(conv_path):
        os.makedirs(conv_path)

    done = 0
    errors[appid] = 0
    for icon in icons:
        done += 1
        extra_text = ''

        if config_from_fork and icon[:4] == 'img/':
            icon = icon[4:]

        if not os.path.isfile(os.path.join(conv_path, icon + '.ico')):
            try:
                img = Image.open(os.path.join(icons_path, icon))
                img.save(os.path.join(conv_path, icon + '.ico'))
                total_conv += 1
            except Exception as ex:
                errors[appid] += 1
                extra_text = f' - Error: {type(ex).__name__}'
        else:
            extra_text = ' - Already exists'
        if not silent:
            print(f'{done_apps}/{len(appids)} {appid} {done}/{len(icons)}' + extra_text)
    
    done_apps += 1

print(f'Converted {total_conv} icons')
for appid in errors:
    if errors[appid] > 0:
        print(f'{appid} - {errors[appid]} error(s)')
for appid in folderless:
    print(f'{appid} - No achievements.json')
if check and len(check_result) > 0:
    print('"ico" folder missing:')
    print(' '.join(check_result))
print(f'Time taken: {time.time() - t} seconds')