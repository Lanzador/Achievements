import os

def get_game_name(appid):
    try:
        with open('games/games.txt', encoding='utf-8') as namefile:
            namelist = namefile.read()
        namelist = namelist.split('\n')
        for namepair in namelist:
            namepair = namepair.split('=')
            if len(namepair) != 2:
                continue
            if namepair[0] == str(appid):
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
            entry = entry.split('=')
            if len(entry) != 2:
                continue
            if entry[1] == alias:
                return entry[0]
        return default
    except FileNotFoundError:
        return default

def source_name(source, default):
    known_values = {('g', 'gb', 'goldberg'): 'goldberg', ('c', 'cd', 'cod', 'cdx'): 'codex'}
    for s in known_values.keys():
        if source in s:
            return known_values[s]
    return default

known_settings = {'delay': {'type': 'float', 'default': 0.5},
                  'delay_stats': {'type': 'int', 'default': 1},
                  'delay_sleep': {'type': 'float', 'default': 0.1},
                  'delay_read_change': {'type': 'float', 'default': 0.05},
                  'gamebar_length': {'type': 'int', 'default': 375},
                  'frame_size': {'type': 'int', 'default': 2},
                  'frame_color_unlock': {'type': 'color', 'default': (255, 255, 255)},
                  'frame_color_lock': {'type': 'color', 'default': (128, 128, 128)},
                  'hidden_desc': {'type': 'str', 'default': '[Hidden achievement]'},
                  'hide_secrets': {'type': 'bool', 'default': False},
                  'bar_length': {'type': 'int', 'default': 300},
                  'bar_unlocked': {'type': 'choice', 'allowed': ['show', 'full', 'hide'], 'default': 'full'},
                  'bar_hide_unsupported': {'type': 'choice', 'allowed': ['none', 'stat', 'all'], 'default': 'none'},
                  'bar_hide_secret': {'type': 'bool', 'default': True},
                  'bar_ignore_min': {'type': 'bool', 'default': False},
                  'bar_force_unlock': {'type': 'bool', 'default': False},
                  'forced_keep': {'type': 'choice', 'allowed': {'no', 'session', 'save'}, 'default': 'save'},
                  'forced_mark': {'type': 'bool', 'default': False},
                  'show_timestamps': {'type': 'bool', 'default': True},
                  'history_length': {'type': 'int&-1', 'default': 0},
                  'history_time': {'type': 'choice', 'allowed': ['real', 'action'], 'default': 'action'},
                  'history_unread': {'type': 'bool', 'default': True},
                  #'history_no_duplicates': {'type': 'choice', 'allowed': ['off', 'unlock', 'on'], 'default': 'off'},
                  #'history_save': {'type': 'choice', 'allowed': ['none', 'unlock', 'all'], 'default': 'none'},
                  'notif': {'type': 'bool', 'default': True},
                  'notif_limit': {'type': 'int', 'default': 3},
                  'notif_timeout': {'type': 'int', 'default': 3},
                  'notif_lock': {'type': 'bool', 'default': False},
                  'language': {'type': 'list', 'default': ('english')},
                  'font_general': {'type': 'str', 'default': 'Roboto/Roboto-Regular.ttf'},
                  'font_achs': {'type': 'fontlist', 'default': {'all': 'Roboto/Roboto-Regular.ttf'}},
                  'font_size_regular': {'type': 'int', 'default': 15},
                  'font_size_small': {'type': 'int', 'default': 13},
                  'font_line_distance_regular': {'type': 'int', 'default': 16},
                  'font_line_distance_small': {'type': 'int', 'default': 16},
                  'color_background': {'type': 'color', 'default': (0, 0, 0)},
                  'color_text': {'type': 'color', 'default': (255, 255, 255)},
                  'color_text_unlock': {'type': 'color', 'default': (255, 255, 255)},
                  'color_text_lock': {'type': 'color', 'default': (128, 128, 128)},
                  'color_bar_bg': {'type': 'color', 'default': (128, 128, 128)},
                  'color_bar_fill': {'type': 'color', 'default': (255, 255, 255)},
                  'color_scrollbar': {'type': 'color', 'default': (128, 128, 128)}}

def load_settings(appid, source):
    settings = {}
    for sett in known_settings.keys():
        settings[sett] = known_settings[sett]['default']
    settings = load_settings_file(settings, 'settings.txt')
    settings = load_settings_file(settings, f'settings_{source}.txt')
    settings = load_settings_file(settings, f'settings_{appid}.txt')
    return settings

def load_settings_file(settings, filename):
    filename = os.path.join('settings', filename)
    try:
        with open(filename) as stgfile:
            stgtext = stgfile.read()
        stgtext = stgtext.split('\n')
        for sett in stgtext:
            sett = sett.split('=')
            if len(sett) == 2 and sett[0] in known_settings:
                if known_settings[sett[0]]['type'] == 'str':
                    settings[sett[0]] = sett[1]
                elif known_settings[sett[0]]['type'] == 'int' and sett[1].isnumeric():
                    settings[sett[0]] = int(sett[1])
                elif known_settings[sett[0]]['type'] == 'int&-1' and (sett[1].isnumeric() or sett[1] == '-1'):
                    settings[sett[0]] = int(sett[1])
                elif known_settings[sett[0]]['type'] == 'float' and len(sett[1].split('.')) < 3 and sett[1].replace('.', '').isnumeric():
                    settings[sett[0]] = float(sett[1])
                elif known_settings[sett[0]]['type'] == 'bool' and sett[1].lower() in ('0', '1', 'false', 'true'):
                    if sett[1] == '1' or sett[1] == sett[1].lower() == 'true':
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
                elif known_settings[sett[0]]['type'] == 'list' and len(sett[1].split(',')) > 0:
                    settings[sett[0]] = sett[1].split(',')
                elif known_settings[sett[0]]['type'] == 'fontlist':
                    fonts = {}
                    spl = sett[1].split(';')
                    for s in spl:
                        s = s.split(':')
                        if len(s) == 1:
                            fonts['all'] = s[0]
                        elif len(s) == 2:
                            langs = s[0].split(',')
                            for lang in langs:
                                fonts[lang] = s[1]
                    settings[sett[0]] = fonts
    except FileNotFoundError:
        pass
    return settings