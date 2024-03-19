import os
import sys
import time
import json
import zlib
import requests
from datetime import datetime
from random import randint

from settings import get_game_name, check_alias, source_name, load_settings, get_save_dir
from filechanges import get_player_achs_path, get_stats_path
from achievements import convert_achs_format
from stats import Stat, convert_stats_format

def send_steam_request(name, link):
    if not name in ('appdetails', 'GetGlobalAchievementPercentagesForApp', 'GetSchemaForGame'):
        global url_random
        url_random += 1
        link += f'&__random?={url_random}'
    try:
        r = requests.get(link)
        if int(r.status_code / 100) != 4:
            try:
                r = r.json()
            except requests.exceptions.JSONDecodeError:
                print(f'JSON decode error ({name})')
                return None
            try:
                skey = 'playerstats'
                if name == 'appdetails':
                    skey = appid
                if r[skey]['success']:
                    return r
                else:
                    print(f'Request unsuccessful ({name})')
            except KeyError:
                return r
        else:
            print(f'Got status code {r.status_code} ({name})')
    except requests.exceptions.ConnectionError:
        print(f'Connection error ({name})')
    return None

known_args = ['-u', '-l', '-h', '-sn', '-sh', '-sb', '-s', '-r', '-uot', '-t']
args_count = len(sys.argv)
for a in known_args:
    args_count -= int(a in sys.argv)

appid, achdata_source, source_extra = (None, None, None)
if args_count > 1:
    appid = check_alias(sys.argv[1])
    if len(appid.split()) > 1:
        if args_count > 2:
            appid = appid.split()[0]
        else:
            achdata_source = source_name(appid.split()[1])
            if achdata_source == 'codex':
                source_extra = len(appid.split()) > 2 and appid.split()[2] in ('a', 'appdata')
            elif achdata_source in ('ali213', 'sse') and len(appid.split()) > 2:
                source_extra = ' '.join(appid.split(' ')[2:])
            elif achdata_source == 'steam' and len(appid.split()) > 2:
                source_extra = appid.split()[2]
            elif achdata_source == None:
                print('Invalid emulator name')
                sys.exit()
            appid = appid.split()[0]
    
    if achdata_source == None and args_count > 2:
        achdata_source = source_name(sys.argv[2])
        if achdata_source == 'codex':
            source_extra = args_count > 3 and sys.argv[3] in ('a', 'appdata')
        elif achdata_source in ('ali213', 'sse', 'steam') and args_count > 3:
            source_extra = sys.argv[3]
        elif achdata_source == None:
            print('Invalid emulator name')
            sys.exit()
    elif achdata_source == None:
        achdata_source = 'goldberg'
else:
    inp = input('Enter AppID: ').split(' ')
    for i in inp.copy():
        if i in known_args:
            sys.argv.append(i)
            inp.remove(i)
    inp = ' '.join(inp)
    appid = check_alias(inp)
    if len(appid.split()) > 1:
        if appid == inp:
            appid = check_alias(appid.split()[0]).split()[0] + ' ' + ' '.join(appid.split(' ')[1:])
        achdata_source = source_name(appid.split()[1])
        if achdata_source == 'codex':
            source_extra = len(appid.split()) > 2 and appid.split()[2] in ('a', 'appdata')
        elif achdata_source in ('ali213', 'sse') and len(appid.split()) > 2:
            source_extra = ' '.join(appid.split(' ')[2:])
        elif achdata_source == 'steam' and len(appid.split()) > 2:
            source_extra = appid.split()[2]
        elif achdata_source == None:
            print('Invalid emulator name')
            sys.exit()
        appid = appid.split()[0]
    else:
        achdata_source = 'goldberg'

if not appid.isnumeric():
    print('Invalid AppID')
    sys.exit()

stg = load_settings(appid, achdata_source)
save_dir = get_save_dir(appid, achdata_source, source_extra)

date = datetime.now()

achs = []
achs_crc32 = {}
unlocks = {}
stats = {}
stats_crc32 = {}
values = {}
timestamps = {}
forced = {}
dnames = {}
percentages = {}

path_achs = f'games/{appid}/achievements.json'
path_stats = f'games/{appid}/stats.txt'
if achdata_source != 'steam':
    path_unlocks = get_player_achs_path(achdata_source, appid, source_extra)
    path_values = get_stats_path(achdata_source, appid, source_extra)
path_force = f'{save_dir}/{appid}_force.json'
path_time = f'{save_dir}/{appid}_time.json'
path_dnames = f'games/{appid}/statdisplay.json'
path_percentages = f'games/{appid}/unlockrates.json'

url_random = randint(0, 10000000)

if os.path.isfile(path_achs):
    with open(path_achs) as f:
        achs = json.load(f)

if stg['stat_display_names'] and os.path.isfile(path_dnames):
    with open(path_dnames) as f:
        dnames = json.load(f)
if os.path.isfile(path_stats):
    with open(path_stats) as f:
        stats = f.read()
    lines = stats.split('\n')
    stats = {}
    for l in lines:
        spl = l.split('=')
        if len(spl) == 3:
            locinfo = {'source': achdata_source, 'appid': appid, 'name': spl[0]}
            locinfo['source_extra'] = source_extra
            if achdata_source == 'sse':
                stats_crc32[zlib.crc32(bytes(spl[0], 'utf-8'))] = spl[0]
            stats[spl[0]] = Stat(locinfo, spl[1], spl[2], stg['delay_read_change'], dnames)

if os.path.isfile(path_time):
    with open(path_time) as f:
        timestamps = json.load(f)
if os.path.isfile(path_force):
    with open(path_force) as f:
        forced = json.load(f)

if os.path.isfile(path_percentages):
    with open(path_percentages) as f:
        percentages = json.load(f)
        percentages = percentages['achievements']

if achdata_source == 'goldberg':
    if os.path.isfile(path_unlocks):
        with open(path_unlocks) as f:
            unlocks = json.load(f)
    # for s in stats:
        # p = os.path.join(path_stats, s)
        # if os.path.isfile(p):
            # with open(p) as f:
                # if stats[s].type == 'int':
                    # stats[s].value = struct.unpack('i', changed_file.read(4))[0]
                # elif stats[s].type == 'float':
                    # stats[s].value = struct.unpack('f', changed_file.read(4))[0]
elif achdata_source != 'steam':
    m = 'rt'
    if achdata_source == 'sse':
        m = 'rb'
        for a in achs:
            achs_crc32[zlib.crc32(bytes(a['name'], 'utf-8'))] = a['name']

    if os.path.isfile(path_unlocks):
        with open(path_unlocks, m) as f:
            unlocks = f.read()
        unlocks = convert_achs_format(unlocks, achdata_source, achs_crc32)

    if os.path.isfile(path_values):
        with open(path_values, m) as f:
            values = f.read()
        values = convert_stats_format(stats, values, achdata_source, stats_crc32)
        for s in stats:
            if stats[s].type in ('int', 'float') and s in values:
                stats[s].value = values[s]
else:
    if len(stg['api_key']) == 0:
        print('An API key is required to track achievements from Steam')
        sys.exit()

    source_extra = check_alias(source_extra)
    if source_extra == None or not source_extra.isnumeric():
        print('Invalid Steam user ID')
        sys.exit()

    steam_req = send_steam_request('GetPlayerAchievements', f"https://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v0001/?appid={appid}&key={stg['api_key']}&steamid={source_extra}")
    if steam_req != None:
        unlocks = steam_req['playerstats']['achievements']
        unlocks = convert_achs_format(unlocks, achdata_source)

    steam_req = send_steam_request('GetUserStatsForGame', f"https://api.steampowered.com/ISteamUserStats/GetUserStatsForGame/v0002/?appid={appid}&key={stg['api_key']}&steamid={source_extra}")
    if steam_req != None and 'stats' in steam_req['playerstats']:
        for s in steam_req['playerstats']['stats']:
            if s['name'] in stats.keys():
                stats[s['name']].value = s['value']

def only_float_for_decimals(v):
    if isinstance(v, str):
        v = float(v)
    if v % 1 == 0:
        return(int(v))
    return(float(v))

class Achievement():
    def __init__(self, a, u, s, t, p):
        self.name = a['name']
        self.display_name = a['displayName']
        self.description = a['description']
        self.hidden = a['hidden'] == '1'

        self.has_desc = isinstance(self.display_name, str) or 'english' in self.description

        if not isinstance(self.display_name, str):
            for l in stg['language'] + ['english']:   
                if l in self.display_name:
                    self.display_name = self.display_name[l]
                    if self.has_desc:
                        self.description = self.description[l]
                    break

        self.unlock = False
        self.time = 0.0
        if self.name in u:
            self.unlock = u[self.name]['earned']
            self.time = u[self.name]['earned_time']

        if self.name in forced:
            self.unlock = True
            self.time = forced[self.name]

        if stg['savetime_shown'] != 'normal' and self.name in t and t[self.name][stg['savetime_shown']] != None:
            self.time = t[self.name][stg['savetime_shown']]

        self.progress_f = None
        self.progress_0 = 0
        self.progress_v = 0
        self.progress_1 = 1
        if 'progress' in a:
            ap = a['progress']
            self.progress_f = ap['value']
            self.progress_1 = only_float_for_decimals(ap['max_val'])
            if len(ap['value']) == 2 and ap['value']['operation'] == 'statvalue' and ap['value']['operand1'] in s and s[ap['value']['operand1']].type in ('int', 'float'):
                self.progress_0 = s[ap['value']['operand1']].to_stat_type(ap['min_val'])
                self.progress_1 = s[ap['value']['operand1']].to_stat_type(ap['max_val'])
                self.progress_v = s[ap['value']['operand1']].value
                self.progress_v = min(self.progress_v, self.progress_1)
                if not stg['bar_ignore_min']:
                    self.progress_v = max(self.progress_v, self.progress_0)
            else:
                self.progress_v = 'Error'
            # self.progress_v = only_float_for_decimals(self.progress_v)
            # self.progress_1 = only_float_for_decimals(self.progress_1)
            if self.unlock:
                self.progress_v = self.progress_1

        self.rarity = -1.0
        self.rarity_text = ''
        if self.name in p:
            self.rarity = round(p[self.name] * 10) / 10
            self.rarity_text = str(self.rarity)
            if not '.' in self.rarity_text:
                self.rarity_text += '.0'
            self.rarity_text = f' ({self.rarity_text}%)'
            if stg['unlockrates'] == 'name':
                self.display_name += self.rarity_text
            elif stg['unlockrates'] == 'desc':
                self.description += self.rarity_text
achs_obj = []
unlock_count = 0
for a in achs:
    o = Achievement(a, unlocks, stats, timestamps, percentages)
    achs_obj.append(o)
    if o.unlock:
        unlock_count += 1

secrets = stg['secrets']
if '-sn' in sys.argv:
    secrets = 'normal'
elif '-sh' in sys.argv:
    secrets = 'hide'
elif '-sb' in sys.argv:
    secrets = 'bottom'
filt = None
if '-u' in sys.argv:
    filt = True
elif '-l' in sys.argv:
    filt = False
hide_descs = '-h' in sys.argv
stats_only = '-s' in sys.argv
rarity_sort = '-r' in sys.argv
unlocks_on_top = '-uot' in sys.argv
timesort = '-t' in sys.argv

if rarity_sort:
    achs_obj.sort(key=lambda a : a.rarity, reverse=True)
if unlocks_on_top:
    achs_obj.sort(key=lambda a : a.unlock, reverse=True)
if timesort:
    if filt == True:
        achs_obj.sort(key=lambda a : a.time, reverse=True)
    elif filt == None and unlocks_on_top:
        unlocked_slice = achs_obj[:unlock_count]
        unlocked_slice.reverse()
        unlocked_slice.sort(key=lambda a : a.time, reverse=True)
        achs_obj = unlocked_slice + achs_obj[unlock_count:]

gamename = get_game_name(appid)

text = appid
if gamename != appid:
    text += ' - ' + gamename
text += ' | ' + date.strftime('%d.%m.%Y %H:%M:%S')
text += f'\nUnlocked: {unlock_count}/{len(achs_obj)}'
if filt == True:
    text += ' (Unlocked only)'
elif filt == False:
    text += ' (Locked only)'
if rarity_sort:
    text += ' [%↓]'
if unlocks_on_top:
    text += ' [U↑]'
if timesort:
    text += ' [T↓]'

if stats_only and len(stats) > 0:
    text += '\n'
    for s in stats:
        text += '\n' + stats[s].dname + ' = ' + str(stats[s].value)

secrets_hidden = 0
secrets_list = []
for a in achs_obj:
    if stats_only:
        break

    if filt != None and filt != a.unlock:
        continue
    if secrets == 'hide' and a.hidden and not a.unlock:
        secrets_hidden += 1
        continue
    elif secrets == 'bottom' and a.hidden and not a.unlock:
        secrets_list.append(a)
        continue

    text += '\n\n' + a.display_name
    if not a.hidden or (a.unlock and not hide_descs):
        if a.has_desc:
            text += '\n' + a.description
    # else:
        # text += '\n' + stg['hidden_desc']

    if a.unlock:
        text += '\n' + f"[Unlocked - {datetime.fromtimestamp(a.time).strftime('%d.%m.%Y %H:%M:%S')}]"
    else:
        text += '\n[Locked]'

    if a.progress_f != None:
        text += f' ({a.progress_v}/{a.progress_1})'
if secrets == 'bottom' and len(secrets_list) > 0 and filt != True:
    if len(secrets_list) == 1:
        text += '\n\nThere is 1 more hidden achievement'
    else:
        text += f'\n\nThere are {len(secrets_list)} more hidden achievements'

    for a in secrets_list:
        text += '\n\n' + a.display_name
        # text += '\n' + stg['hidden_desc']
        text += '\n[Locked]'
elif secrets == 'hide' and secrets_hidden > 0 and filt != True:
    if secrets_hidden == 1:
        text += '\n\nThere is 1 more hidden achievement'
    else:
        text += f'\n\nThere are {secrets_hidden} more hidden achievements'

if not os.path.isdir('ach_dumper'):
    os.makedirs('ach_dumper')

filename = f"ach_dumper/{date.strftime('%Y%m%d_%H%M%S')}_{achdata_source}_{appid}"
if stats_only:
    filename += '_stats'
elif filt == True:
    filename += '_unlock'
elif filt == False:
    filename += '_lock'
filename += '.txt'

with open(filename, 'w', encoding='utf-8') as f:
    f.write(text)