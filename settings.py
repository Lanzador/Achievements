import os
import sys
import platform
import zlib
from experimental import *

def get_game_name(appid):
    try:
        with open('games/games.txt', encoding='utf-8') as namefile:
            namelist = namefile.read()
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
    known_values = {'goldberg': ('g', 'gb', 'goldberg'),
                    'codex': ('c', 'cd', 'cod', 'cdx', 'codex'),
                    'ali213': ('a', 'ali', 'ali213', '213', 'a213'),
                    'sse': ('s', 'sse', 'smartsteamemu', 'smart'),
                    'steam': ('st', 'steam')}
    for s in known_values:
        if source in known_values[s]:
            return s
    return None

def get_save_dir(appid, source, extra):
    d = 'save/' + source
    if source == 'goldberg' and extra == 'f':
        d += '/GSE Saves'
    elif source == 'codex' and extra == True:
        d += '/appdata'
    elif source in ('ali213', 'sse'):
        if extra != None and (not extra[:5] == 'path:'):
            d += f'/{extra}'
    elif source == 'steam':
        d += f'/{extra}'
    if source in ('goldberg', 'ali213', 'sse') and extra != None and (extra[:5] == 'path:'):
        path = os.path.abspath(extra[5:]).replace('\\', '/')
        if platform.uname().system == 'Windows':
            path = path.lower()
        path_crc = zlib.crc32(bytes(path, 'utf-8'))
        d += f'/path/{appid}_{path_crc}'
    return d

def load_emulator_defaults():
    defaults = {'emulator': 'g',
                'goldberg': None,
                'codex': None,
                'ali213': None,
                'sse': None,
                'steam': None}
    if os.path.isfile('games/defaults.txt'):
        with open('games/defaults.txt') as f:
            txt = f.read().split('\n')
        for l in txt:
            l = l.split('=', 1)
            if len(l) < 2: continue
            if l[0] in defaults:
                if l[1] == '':
                    defaults[l[0]] = None
                else:
                    defaults[l[0]] = l[1]
    if defaults['emulator'] == None:
        defaults['emulator'] = 'g'
    defaults['emulator'] = source_name(defaults['emulator'])
    return defaults

def load_game(inp, from_args=False):
    if from_args:
        if len(inp) > 1:
            inp[0] = check_alias(inp[0]).split()[0]
        else:
            inp = check_alias(inp[0])
            from_args = False
    else:
        inp1 = inp
        inp = check_alias(inp)
        if inp == inp1:
            spl = inp.split(None, 1)
            if len(spl) > 1:
                inp = check_alias(spl[0]).split()[0] + ' ' + spl[1]
    if not from_args:
        inp = inp.split(None, 2)

    if len(inp) == 0 or not inp[0].isnumeric():
        print('Invalid AppID')
        sys.exit()
    inp[0] = str(int(inp[0]))

    defaults = load_emulator_defaults()

    if len(inp) > 1:
        inp[1] = source_name(inp[1])
    else:
        inp.append(defaults['emulator'])

    if inp[1] == None:
        print('Invalid emulator name')
        sys.exit()

    if len(inp) == 2:
        inp.append(defaults[inp[1]])

    if inp[2] == '/':
        inp[2] = None

    if inp[1] == 'codex':
        inp[2] = inp[2] == 'a'
    elif inp[1] == 'ali213':
        if inp[2] == None:
            inp[2] = 'Player'
    elif inp[1] == 'steam':
        inp[2] = check_alias(inp[2])
        if inp[2] == None or not inp[2].isnumeric():
            print('Invalid Steam user ID')
            sys.exit()

    return inp

known_settings = {'window_size_x': {'type': 'int', 'default': 800},
                  'window_size_y': {'type': 'int', 'default': 600},
                  'delay': {'type': 'float', 'default': 0.5},
                  'delay_stats': {'type': 'int', 'default': 1},
                  'delay_sleep': {'type': 'float', 'default': 0.03},
                  'delay_read_change': {'type': 'float', 'default': 0.05},
                  'gamebar_length': {'type': 'int', 'default': 375},
                  'gamebar_position': {'type': 'choice', 'allowed': ['normal', 'repname', 'under', 'hide'], 'default': 'normal'},
                  'frame_size': {'type': 'int', 'default': 2},
                  'frame_color_unlock': {'type': 'color', 'default': (255, 255, 255)},
                  'frame_color_lock': {'type': 'color', 'default': (128, 128, 128)},
                  'frame_color_rare': {'type': 'color', 'default': None},
                  'frame_color_rare_lock': {'type': 'color', 'default': None},
                  'frame_color_hover': {'type': 'color', 'default': None},
                  'rare_below': {'type': 'float', 'default': 10.0},
                  'rare_below_relative': {'type': 'bool', 'default': False},
                  'rare_guaranteed': {'type': 'int', 'default': 0},
                  'language': {'type': 'list', 'default': ['english']},
                  'language_requests': {'type': 'str', 'default': None},
                  'ctrl_click': {'type': 'bool', 'default': False},
                  'hidden_title': {'type': 'str', 'default': '??????????'},
                  'hidden_desc': {'type': 'str', 'default': '[Hidden achievement]'},
                  'secrets': {'type': 'choice', 'allowed': ['normal', 'hide', 'bottom'], 'default': 'hide'},
                  'secrets_listhide': {'type': 'bool', 'default': False},
                  'secrets_bottom_count': {'type': 'bool', 'default': True},
                  'reveal_icons_hover': {'type': 'bool', 'default': False},
                  'reveal_icons_revsecr': {'type': 'choice', 'allowed': ['never', 'hover', 'always'], 'default': 'hover'},
                  'unlocks_on_top': {'type': 'bool', 'default': False},
                  'unlocks_timesort': {'type': 'bool', 'default': False},
                  'sort_by_rarity': {'type': 'bool', 'default': False},
                  'bar_length': {'type': 'int', 'default': 300},
                  'bar_unlocked': {'type': 'choice', 'allowed': ['show', 'full', 'hide', 'zerolen'], 'default': 'full'},
                  'bar_hide_unsupported': {'type': 'choice', 'allowed': ['none', 'stat', 'all'], 'default': 'none'},
                  'bar_hide_secret': {'type': 'bool', 'default': True},
                  'bar_ignore_min': {'type': 'bool', 'default': False},
                  'bar_percentage': {'type': 'choice', 'allowed': ['no', 'show', 'only'], 'default': 'no'},
                  'bar_images': {'type': 'bool', 'default': False},
                  'bar_force_unlock': {'type': 'bool', 'default': True},
                  'forced_keep': {'type': 'choice', 'allowed': ['no', 'session', 'save'], 'default': 'save'},
                  'forced_mark': {'type': 'bool', 'default': False},
                  'forced_time_load': {'type': 'choice', 'allowed': ['now', 'filechange'], 'default': 'now'},
                  'show_timestamps': {'type': 'bool', 'default': True},
                  'strftime': {'type': 'str', 'default': '%d %b %Y %H:%M:%S'},
                  'history_length': {'type': 'int', 'negative': None, 'default': 0},
                  'history_time': {'type': 'choice', 'allowed': ['real', 'action'], 'default': 'action'},
                  'history_unread': {'type': 'bool', 'default': True},
                  'history_clearable': {'type': 'bool', 'default': True},
                  'notif': {'type': 'bool', 'default': True},
                  'notif_desc': {'type': 'bool', 'default': False},
                  'notif_unlock_count': {'type': 'bool', 'default': False},
                  'notif_limit': {'type': 'int', 'default': 3},
                  'notif_timeout': {'type': 'int', 'default': 3},
                  'notif_lock': {'type': 'bool', 'default': True},
                  'notif_icons': {'type': 'bool', 'default': True},
                  'notif_icons_no_ico': {'type': 'choice', 'allowed': ['ignore', 'warn', 'convert'], 'default': 'convert'},
                  'sound': {'type': 'bool', 'default': True},
                  'sound_unlock': {'type': 'str', 'default': ''},
                  'sound_rare': {'type': 'str', 'default': ''},
                  'sound_progress': {'type': 'str', 'default': ''},
                  'sound_multi': {'type': 'str', 'default': ''},
                  'sound_complete': {'type': 'str', 'default': ''},
                  'sound_rare_over_multi': {'type': 'bool', 'default': False},
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
                  'font_time_general': {'type': 'bool', 'default': False},
                  'images': {'type': 'list', 'default': []},
                  'color_background': {'type': 'color', 'default': (0, 0, 0)},
                  'color_text': {'type': 'color', 'default': (255, 255, 255)},
                  'color_text_unlock': {'type': 'color', 'default': (255, 255, 255)},
                  'color_text_lock': {'type': 'color', 'default': (128, 128, 128)},
                  'color_text_rare': {'type': 'color', 'default': None},
                  'color_text_rare_lock': {'type': 'color', 'default': None},
                  'color_text_hover': {'type': 'color', 'default': None},
                  'color_time_general': {'type': 'bool', 'default': False},
                  'color_progress_report': {'type': 'choice', 'allowed': ['mixed', 'unlock', 'lock'], 'default': 'mixed'},
                  'color_bar_bg': {'type': 'color', 'default': (128, 128, 128)},
                  'color_bar_fill': {'type': 'color', 'default': (255, 255, 255)},
                  'color_bar_completed': {'type': 'color', 'default': None},
                  'color_scrollbar': {'type': 'color', 'default': (128, 128, 128)},
                  'color_achbg_unlock': {'type': 'color', 'default': None},
                  'color_achbg_lock': {'type': 'color', 'default': None},
                  'color_achbg_rare': {'type': 'color', 'default': None},
                  'color_achbg_rare_lock': {'type': 'color', 'default': None},
                  'color_achbg_hover': {'type': 'color', 'cbn': None, 'default': (64, 64, 64)},
                  'achbg_rarity': {'type': 'choice', 'allowed': ['no', 'sort', 'yes'], 'default': 'no'},
                  'achbg_rarity_relative': {'type': 'bool', 'default': False},
                  'save_timestamps': {'type': 'bool', 'default': True},
                  'savetime_shown': {'type': 'choice', 'allowed': ['normal', 'first', 'earliest'], 'default': 'first'},
                  'savetime_mark': {'type': 'bool', 'default': False},
                  'savetime_keep_locked': {'type': 'bool', 'default': False},
                  'smooth_scale': {'type': 'bool', 'default': True},
                  'stat_display_names': {'type': 'bool', 'default': True},
                  'generator_path': {'type': 'str', 'default': ''},
                  'api_key': {'type': 'str', 'default': ''},
                  'exp_console_max_lines': {'type': 'int', 'default': 0},
                  'exp_no_cmd_input': {'type': 'bool', 'default': False},
                  'exp_sound_console': {'type': 'str', 'default': ''},
                  'exp_allow_wiping': {'type': 'bool', 'default': False},
                  'exp_confirm_wiping': {'type': 'bool', 'default': True},
                  'exp_history_location': {'type': 'str', 'default': '*'},
                  'exp_history_autosave': {'type': 'bool', 'default': False},
                  'exp_history_autosave_clear': {'type': 'choice', 'allowed': ['save', 'disable', 'ignore'], 'default': 'save'},
                  'exp_history_autosave_auto': {'type': 'bool', 'default': False},
                  'exp_grid_default': {'type': 'bool', 'default': False},
                  'exp_grid_bar_height': {'type': 'int', 'default': 10},
                  'exp_grid_bar_hover_hide': {'type': 'bool', 'default': False},
                  'exp_grid_empty_line': {'type': 'bool', 'default': True},
                  'exp_grid_show_extra_line': {'type': 'bool', 'default': False},
                  'exp_grid_reserve_last_line': {'type': 'bool', 'default': False}}

def load_settings(appid, source, ach_dumper=False):
    settings = {}
    for sett in known_settings:
        settings[sett] = known_settings[sett]['default']
    filenames = ['settings', f'settings_{source}', f'settings_{appid}', f'settings_{appid}_{source}']
    for f in filenames:
        settings = load_settings_file(settings, f + '.txt')
        if ach_dumper:
            settings = load_settings_file(settings, f + '_ad.txt')
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
                elif known_settings[sett[0]]['type'] == 'int':
                    if sett[1].isnumeric() or (sett[1].startswith('-') and sett[1][1:].isnumeric()):
                        val = int(sett[1])
                    if val >= 0 or 'negative' in known_settings[sett[0]]:
                        settings[sett[0]] = val
                elif known_settings[sett[0]]['type'] == 'float':
                    if sett[1].count('.') < 2 and sett[1].replace('.', '').isnumeric():
                        settings[sett[0]] = float(sett[1])
                elif known_settings[sett[0]]['type'] == 'bool':
                    if sett[1] == '1' or sett[1].lower() == 'true':
                        settings[sett[0]] = True
                    elif sett[1] == '0' or sett[1].lower() == 'false':
                        settings[sett[0]] = False
                elif known_settings[sett[0]]['type'] == 'choice':
                    if sett[1] in known_settings[sett[0]]['allowed']:
                        settings[sett[0]] = sett[1]
                elif known_settings[sett[0]]['type'] == 'color':
                    if sett[1].count(',') == 2 and sett[1].replace(',', '').isnumeric():
                        spl = sett[1].split(',')
                        as_color = (int(spl[0]), int(spl[1]), int(spl[2]))
                        if as_color[0] <= 255 and as_color[1] <= 255 and as_color[2] <= 255:
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
    for n in known_settings:
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
    if not os.path.isdir('settings'):
        os.makedirs('settings')
    with open('settings/settings_default.txt', 'w', encoding='utf-8') as def_file:
        def_file.write(s)