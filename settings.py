import os
import zlib

def get_game_name(appid):
    try:
        with open('games/games.txt', encoding='utf-8') as namefile:
            namelist = namefile.read()
        if len(namelist) > 0 and namelist[-1] != '\n':
            with open('games/games.txt', 'a', encoding='utf-8') as gamestxt:
                gamestxt.write('\n')
        namelist = namelist.split('\n')
        for namepair in namelist:
            namepair = namepair.split('=', 1)
            if len(namepair) > 1 and namepair[0] == appid:
                return namepair[1]
        return appid
    except FileNotFoundError:
        return appid

def check_alias(alias, default=None):
    if default == None:
        default = alias

    try:
        with open('games/alias.txt', encoding='utf-8') as aliaslistf:
            aliaslist = aliaslistf.read()
        aliaslist = aliaslist.split('\n')
        for entry in aliaslist:
            entry = entry.split('=', 1)
            if len(entry) > 1 and entry[1] == alias:
                return entry[0]
        return default
    except FileNotFoundError:
        return default

def source_name(source):
    known_values = {('g', 'gb', 'goldberg'): 'goldberg',
                    ('c', 'cd', 'cod', 'cdx', 'codex'): 'codex',
                    ('a', 'ali', 'ali213', '213', 'a213'): 'ali213',
                    ('s', 'sse', 'smartsteamemu', 'smart'): 'sse',
                    ('st', 'steam'): 'steam'}
    for s in known_values.keys():
        if source in s:
            return known_values[s]
    return None

def get_save_dir(appid, source, extra):
    d = 'save/' + source
    if source == 'codex' and extra == True:
        d += '/appdata'
    elif source in ('ali213', 'sse'):
        if extra == None:
            if source == 'ali213':
                d += '/Player'
        elif (not extra[:5] == 'path:'):
            d += f'/{extra}'
        else:
            path = os.path.abspath(extra[5:]).lower().replace('\\', '/')
            path_crc = zlib.crc32(bytes(path, 'utf-8'))
            d += f'/path/{appid}_{path_crc}'
    elif source == 'steam':
        d += f'/{extra}'
    return d

known_settings = {'window_size_x': {'type': 'int', 'default': 800},
                  'window_size_y': {'type': 'int', 'default': 600},
                  'delay': {'type': 'float', 'default': 0.5},
                  'delay_stats': {'type': 'int', 'default': 1},
                  'delay_sleep': {'type': 'float', 'default': 0.1},
                  'delay_read_change': {'type': 'float', 'default': 0.05},
                  'gamebar_length': {'type': 'int', 'default': 375},
                  'gamebar_position': {'type': 'choice', 'allowed': ['normal', 'repname', 'under', 'hide'], 'default': 'normal'},
                  'frame_size': {'type': 'int', 'default': 2},
                  'frame_color_unlock': {'type': 'color', 'default': (255, 255, 255)},
                  'frame_color_lock': {'type': 'color', 'default': (128, 128, 128)},
                  'frame_color_rare': {'type': 'color', 'default': None},
                  'frame_color_rare_lock': {'type': 'color', 'default': None},
                  'rare_below': {'type': 'float', 'default': 10.0},
                  'hidden_desc': {'type': 'str', 'default': '[Hidden achievement]'},
                  'secrets': {'type': 'choice', 'allowed': ['normal', 'hide', 'bottom'], 'default': 'normal'},
                  'unlocks_on_top': {'type': 'bool', 'default': False},
                  'unlocks_timesort': {'type': 'bool', 'default': False},
                  'sort_by_rarity': {'type': 'bool', 'default': False},
                  'bar_length': {'type': 'int', 'default': 300},
                  'bar_unlocked': {'type': 'choice', 'allowed': ['show', 'full', 'hide', 'zerolen'], 'default': 'full'},
                  'bar_hide_unsupported': {'type': 'choice', 'allowed': ['none', 'stat', 'all'], 'default': 'none'},
                  'bar_hide_secret': {'type': 'bool', 'default': True},
                  'bar_ignore_min': {'type': 'bool', 'default': False},
                  'bar_force_unlock': {'type': 'bool', 'default': True},
                  'forced_keep': {'type': 'choice', 'allowed': ['no', 'session', 'save'], 'default': 'save'},
                  'forced_mark': {'type': 'bool', 'default': False},
                  'forced_time_load': {'type': 'choice', 'allowed': ['now', 'filechange'], 'default': 'now'},
                  'show_timestamps': {'type': 'bool', 'default': True},
                  'strftime': {'type': 'str', 'default': '%d %b %Y %H:%M:%S'},
                  'history_length': {'type': 'int&-1', 'default': 0},
                  'history_time': {'type': 'choice', 'allowed': ['real', 'action'], 'default': 'action'},
                  'history_unread': {'type': 'bool', 'default': True},
                  'notif': {'type': 'bool', 'default': True},
                  'notif_limit': {'type': 'int', 'default': 3},
                  'notif_timeout': {'type': 'int', 'default': 3},
                  'notif_lock': {'type': 'bool', 'default': False},
                  'notif_icons': {'type': 'bool', 'default': True},
                  'language': {'type': 'list', 'default': ['english']},
                  'language_requests': {'type': 'str', 'default': None},
                  'unlockrates': {'type': 'choice', 'allowed': ['none', 'load', 'name', 'desc'], 'default': 'name'},
                  'unlockrates_expire': {'type': 'time', 'default': 3600},
                  'font_general': {'type': 'str', 'default': 'Roboto/Roboto-Regular.ttf'},
                  'font_achs': {'type': 'fontlist', 'default': {'all': 'Roboto/Roboto-Regular.ttf'}},
                  'font_achs_desc': {'type': 'fontlist', 'default': {}},
                  'font_size_general': {'type': 'int', 'default': 15},
                  'font_size_regular': {'type': 'fontlist', 'default': {'all': 15}},
                  'font_size_small': {'type': 'fontlist', 'default': {'all': 13}},
                  'font_line_distance_regular': {'type': 'int', 'default': 16},
                  'font_line_distance_small': {'type': 'int', 'default': 16},
                  'color_background': {'type': 'color', 'default': (0, 0, 0)},
                  'color_text': {'type': 'color', 'default': (255, 255, 255)},
                  'color_text_unlock': {'type': 'color', 'default': (255, 255, 255)},
                  'color_text_lock': {'type': 'color', 'default': (128, 128, 128)},
                  'color_bar_bg': {'type': 'color', 'default': (128, 128, 128)},
                  'color_bar_fill': {'type': 'color', 'default': (255, 255, 255)},
                  'color_bar_completed': {'type': 'color', 'default': None},
                  'color_scrollbar': {'type': 'color', 'default': (128, 128, 128)},
                  'color_achbg_unlock': {'type': 'color', 'default': None},
                  'color_achbg_lock': {'type': 'color', 'default': None},
                  'color_achbg_rare': {'type': 'color', 'default': None},
                  'color_achbg_rare_lock': {'type': 'color', 'default': None},
                  'color_achbg_hover': {'type': 'color', 'cbn': '', 'default': (64, 64, 64)},
                  'save_timestamps': {'type': 'bool', 'default': True},
                  'savetime_shown': {'type': 'choice', 'allowed': ['normal', 'first', 'earliest'], 'default': 'first'},
                  'savetime_mark': {'type': 'bool', 'default': False},
                  'savetime_keep_locked': {'type': 'bool', 'default': False},
                  'smooth_scale': {'type': 'bool', 'default': True},
                  'stat_display_names': {'type': 'bool', 'default': True},
                  'api_key': {'type': 'str', 'default': ''}}

def load_settings(appid, source):
    settings = {}
    for sett in known_settings.keys():
        settings[sett] = known_settings[sett]['default']
    settings = load_settings_file(settings, 'settings.txt')
    settings = load_settings_file(settings, f'settings_{source}.txt')
    settings = load_settings_file(settings, f'settings_{appid}.txt')
    settings = load_settings_file(settings, f'settings_{appid}_{source}.txt')
    return settings

def load_settings_file(settings, filename):
    filename = os.path.join('settings', filename)
    try:
        with open(filename, encoding='utf-8') as stgfile:
            stgtext = stgfile.read()
        stgtext = stgtext.split('\n')
        for sett in stgtext:
            sett = sett.split('=', 1)
            if len(sett) > 1 and sett[0] in known_settings:
                if (known_settings[sett[0]]['default'] == None or 'cbn' in known_settings[sett[0]]) and sett[1] == '':
                    settings[sett[0]] = None
                elif known_settings[sett[0]]['type'] == 'str':
                    settings[sett[0]] = sett[1]
                elif known_settings[sett[0]]['type'] == 'int' and sett[1].isnumeric():
                    settings[sett[0]] = int(sett[1])
                elif known_settings[sett[0]]['type'] == 'int&-1' and (sett[1].isnumeric() or sett[1] == '-1'):
                    settings[sett[0]] = int(sett[1])
                elif known_settings[sett[0]]['type'] == 'float' and len(sett[1].split('.')) < 3 and sett[1].replace('.', '').isnumeric():
                    settings[sett[0]] = float(sett[1])
                elif known_settings[sett[0]]['type'] == 'bool' and sett[1].lower() in ('0', '1', 'false', 'true'):
                    if sett[1] == '1' or sett[1].lower() == 'true':
                        settings[sett[0]] = True
                    else:
                        settings[sett[0]] = False
                elif known_settings[sett[0]]['type'] == 'choice' and sett[1] in known_settings[sett[0]]['allowed']:
                    settings[sett[0]] = sett[1]
                elif known_settings[sett[0]]['type'] == 'color' and len(sett[1].split(',')) == 3 and sett[1].replace(',', '').isnumeric():
                    spl = sett[1].split(',')
                    as_color = (int(spl[0]), int(spl[1]), int(spl[2]))
                    if as_color[0] <= 255 or as_color[1] <= 255 or as_color[2] <= 255:
                        settings[sett[0]] = as_color
                elif known_settings[sett[0]]['type'] == 'list':
                    if len(sett[1]) > 0:
                        settings[sett[0]] = sett[1].split(',')
                    else:
                        settings[sett[0]] = list()
                elif known_settings[sett[0]]['type'] == 'fontlist':
                    fonts = {}
                    if 'all' in known_settings[sett[0]]['default']:
                        fonts['all'] = known_settings[sett[0]]['default']['all']
                    spl = sett[1].split(';')
                    for s in spl:
                        if len(s) == 0:
                            continue
                        s = s.split(':')
                        if len(s) == 1:
                            fonts['all'] = s[0]
                        elif len(s) == 2:
                            langs = s[0].split(',')
                            for lang in langs:
                                fonts[lang] = s[1]
                    settings[sett[0]] = fonts
                elif known_settings[sett[0]]['type'] == 'time' and len(sett[1]) > 0:
                    units = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}
                    num = sett[1]
                    if sett[1][-1] in units:
                        if len(sett[1]) > 1:
                            num = num[:-1]
                        else:
                            continue
                        unit = sett[1][-1]
                    else:
                        unit = 's'                    
                    if len(num.split('.')) < 3 and num.replace('.', '').isnumeric():
                        settings[sett[0]] = float(num) * units[unit]
            elif sett[0] == 'add_file' and len(sett) > 1 and len(sett[1]) > 0:
                settings = load_settings_file(settings, sett[1])
    except FileNotFoundError:
        pass
    return settings

if __name__ == '__main__':
    s = ''
    for n in known_settings.keys():
        s += n
        s += '='
        if known_settings[n]['default'] == None:
            s += '\n'
            continue
        if known_settings[n]['type'] == 'bool':
            s += str(int(known_settings[n]['default']))
        elif known_settings[n]['type'] == 'color':
            s += ','.join(map(str, known_settings[n]['default']))
        elif known_settings[n]['type'] == 'list':
            s += ','.join(known_settings[n]['default'])
        elif known_settings[n]['type'] == 'fontlist':
            try:
                s += str(known_settings[n]['default']['all'])
            except (KeyError, TypeError):
                pass
        elif known_settings[n]['type'] == 'time':
            if known_settings[n]['default'] == 3600:
                s += '1h'
            else:
                s += str(known_settings[n]['default']) + 's'
        else:
            s += str(known_settings[n]['default'])
        s += '\n'
    s = s[:-1]
    with open('settings/settings_default.txt', 'w', encoding='utf-8') as def_file:
        def_file.write(s)