import os
import sys
import platform
import json
import time
import pygame
from plyer import notification
from showtext import *
from achievements import *
from stats import *
from filechanges import *
from settings import *

def round_down(number, leave_dec):
    number = str(number)
    dot = number.find('.')
    if dot == -1 or dot >= len(number) - 1 - leave_dec:
        return number
    else:
        return number[:dot + leave_dec + 1]
        
def draw_progressbar(x, y, w, h, c1, c2, p1, p2):
    pygame.draw.rect(screen, c1, pygame.Rect(x, y, w, h))
    if p1 > p2:
        p1 = p2
    if p2 != 0:
        pygame.draw.rect(screen, c2, pygame.Rect(x, y, p1 * w // p2, h))

def draw_game_progress(max_name_length):
    long_text(screen, max_name_length, font_general, gamename, (10, 10), stg['color_text'])
    draw_progressbar(10, 30, stg['gamebar_length'], 13, stg['color_bar_bg'], stg['color_bar_fill'], achs_unlocked, len(achs))
    game_progress_str = f'{achs_unlocked}/{len(achs)}'
    if len(achs) > 0:
        game_progress_str += f' ({achs_unlocked * 100 // len(achs)}%)'
    else:
        game_progress_str += ' (0%)'
    show_text(screen, font_general, game_progress_str, (stg['gamebar_length'] + 20, 28), stg['color_text'])

def draw_achs():
    screen.fill(stg['color_background'])

    draw_game_progress(518)
    if stg['history_length'] != -1:
        screen.blit(historybutton, (538, 10))
    if len(history) > 0 and history[0]['unread'] == 1:
        screen.blit(unreadicon, (620, 24))
    screen.blit(filter_buttons[state_filter], (638, 10))
    screen.blit(statsbutton, (722, 10))

    if len(achs_f) == 0:
        show_text(screen, font_general, 'No achievements found', (10, 58), stg['color_text'])

    for i in range(scroll, scroll + achs_to_show + 1):
        if i < len(achs_f):
            font_regular = font_achs_regular[achs_f[i].language]
            font_small = font_achs_small[achs_f[i].language]
            desc_max_lines = 3
            if achs_f[i].progress != None or (achs_f[i].earned and stg['show_timestamps']):
                desc_max_lines = 2
            if hover_ach == i - scroll:
                desc_max_lines = 3
            
            if achs_f[i].earned:
                pygame.draw.rect(screen, stg['frame_color_unlock'], pygame.Rect(10 - stg['frame_size'], 58 - stg['frame_size'] + (i - scroll) * 74, 64 + stg['frame_size'] * 2, 64 + stg['frame_size'] * 2))
                if achs_f[i].icon != None:
                    screen.blit(ach_icons[achs_f[i].icon], (10, 58 + (i - scroll) * 74))
                else:
                    pygame.draw.rect(screen, stg['color_background'], pygame.Rect(10, 58 + (i - scroll) * 74, 64, 64))
                long_text(screen, 706, font_regular, achs_f[i].display_name_l, (84, 58 + (i - scroll) * 74), stg['color_text_unlock'])
                if achs_f[i].has_desc:
                    multiline_text(screen, desc_max_lines, stg['font_line_distance_small'], 706, font_small, achs_f[i].description_l, (84, 75 + (i - scroll) * 74), stg['color_text_unlock'])
                if hover_ach != i - scroll or not achs_f[i].long_desc:
                    if not ((achs_f[i].progress == None or (stg['bar_unlocked'] == 'hide' and achs_f[i].earned) or \
                      (stg['bar_hide_unsupported'] == 'all' and not achs_f[i].progress.support) or \
                      (stg['bar_hide_unsupported'] == 'stat' and achs_f[i].progress.support_error != "Unknown stat") or \
                      (stg['bar_hide_secret'] and achs_f[i].hidden == '1' and not achs_f[i].earned))):
                        if achs_f[i].progress.support:
                            if not (stg['bar_unlocked'] == 'hide' and achs_f[i].earned):
                                prg_str_len = font_general.size(f'{achs_f[i].progress.current_value}/{achs_f[i].progress.max_val}')[0]
                            else:
                                prg_str_len = font_general.size(f'{achs_f[i].progress.max_val}/{achs_f[i].progress.max_val}')[0]
                        else:
                            prg_str_len = font_general.size(achs[i].progress.support_error)[0]
                        if stg['show_timestamps']:
                            show_text(screen, font_general, achs_f[i].get_time(stg['forced_mark']), (stg['bar_length'] + 104 + prg_str_len, 107 + (i - scroll) * 74), stg['color_text'])
                    else:
                        if stg['show_timestamps']:
                            show_text(screen, font_general, achs_f[i].get_time(stg['forced_mark']), (84, 107 + (i - scroll) * 74), stg['color_text'])

                # ach_time = achs_f[i].get_time()
                # show_text(screen, font_regular, ach_time, (790 - font_regular.size(ach_time)[0] , 107 + (i - scroll) * 74))

                # ach_time = achs_f[i].get_time()
                # ach_time_len = font_regular.size(ach_time)
                # rrect = pygame.Rect(0, 0, ach_time_len[0], ach_time_len[1])
                # rrect.midright = (790, 90 + (i - scroll) * 74)
                # show_text(screen, font_regular, ach_time, rrect)

            else:
                pygame.draw.rect(screen, stg['frame_color_lock'], pygame.Rect(10 - stg['frame_size'], 58 - stg['frame_size'] + (i - scroll) * 74, 64 + stg['frame_size'] * 2, 64 + stg['frame_size'] * 2))
                if achs_f[i].icon_gray != None:
                    screen.blit(ach_icons[achs_f[i].icon_gray], (10, 58 + (i - scroll) * 74))
                else:
                    pygame.draw.rect(screen, stg['color_background'], pygame.Rect(10, 58 + (i - scroll) * 74, 64, 64))
                long_text(screen, 706, font_regular, achs_f[i].display_name_l, (84, 58 + (i - scroll) * 74), stg['color_text_lock'])
                if achs_f[i].hidden != '1' and achs_f[i].has_desc:
                    multiline_text(screen, desc_max_lines, stg['font_line_distance_small'], 706, font_small, achs_f[i].description_l, (84, 75 + (i - scroll) * 74), stg['color_text_lock'])
                elif achs_f[i].hidden == '1':
                    multiline_text(screen, desc_max_lines, stg['font_line_distance_small'], 706, font_small, stg['hidden_desc'], (84, 75 + (i - scroll) * 74), stg['color_text_lock'])

            if achs_f[i].progress != None and (hover_ach != i - scroll or not achs_f[i].long_desc):
                if achs_f[i].progress.support:
                    if not stg['bar_ignore_min']:
                        without_min = achs_f[i].progress.get_without_min()
                    else:
                        without_min = (achs_f[i].progress.real_value, achs_f[i].progress.max_val)
                    if not ((stg['bar_unlocked'] == 'hide' and achs_f[i].earned) or (stg['bar_hide_secret'] and achs_f[i].hidden == '1' and not achs_f[i].earned)):
                        if (stg['bar_unlocked'] == 'full' and achs_f[i].earned):
                            draw_progressbar(84, 109 + (i - scroll) * 74, stg['bar_length'], 13, stg['color_bar_bg'], stg['color_bar_fill'], 1, 1)
                            show_text(screen, font_general, f'{achs_f[i].progress.max_val}/{achs_f[i].progress.max_val}', (stg['bar_length'] + 94, 107 + (i - scroll) * 74), stg['color_text'])
                        else:
                            draw_progressbar(84, 109 + (i - scroll) * 74, stg['bar_length'], 13, stg['color_bar_bg'], stg['color_bar_fill'], without_min[0], without_min[1])
                            prg_val_to_show = round_down(achs_f[i].progress.current_value, 2)
                            if stg['bar_ignore_min']:
                                prg_val_to_show = round_down(achs_f[i].progress.real_value, 2)
                            show_text(screen, font_general, f'{prg_val_to_show}/{achs_f[i].progress.max_val}', (stg['bar_length'] + 94, 107 + (i - scroll) * 74), stg['color_text'])
                elif not (stg['bar_hide_unsupported'] == 'all' or (stg['bar_hide_unsupported'] == 'stat' and achs_f[i].progress.support_error != "Unknown stat") \
                     or (stg['bar_unlocked'] == 'hide' and achs_f[i].earned) or (stg['bar_hide_secret'] and achs_f[i].hidden == '1' and not achs_f[i].earned)):
                    if (stg['bar_unlocked'] == 'full' and achs_f[i].earned):
                        draw_progressbar(84, 109 + (i - scroll) * 74, stg['bar_length'], 13, stg['color_bar_bg'], stg['color_bar_fill'], 1, 1)
                    else:
                        draw_progressbar(84, 109 + (i - scroll) * 74, stg['bar_length'], 13, stg['color_bar_bg'], stg['color_bar_fill'], 0, 1)
                    show_text(screen, font_general, achs_f[i].progress.support_error, (stg['bar_length'] + 94, 107 + (i - scroll) * 74), stg['color_text'])

    if len(achs_f) > achs_to_show:
        scrollbar_height = 542 * 542 // (len(achs_f) * 74 - 10)
        scrollbar_position = 58 + scroll * (542 - (scrollbar_height)) // (len(achs_f) - achs_to_show)
        if scrollbar_height < 1:
            scrollbar_height = 1
        if scrollbar_position > 599:
            scrollbar_position = 599
        pygame.draw.rect(screen, stg['color_scrollbar'], pygame.Rect(790, scrollbar_position, 10, scrollbar_height))

    pygame.display.flip()

def draw_stats():
    screen.fill(stg['color_background'])

    draw_game_progress(702)
    screen.blit(achsbutton, (722, 10))

    if len(stats) == 0:
        show_text(screen, font_general, 'No stats found', (10, 58))

    already_shown = 0 - scroll_stats
    for stat in stats.values():
        if already_shown >= 0:
            short_name = long_text(screen, 780 - font_general.size(f' = {stat.value}')[0], font_general, stat.name, None, None, True)
            show_text(screen, font_general, f'{short_name} = {stat.value}', (10, 58 + already_shown * stg['font_line_distance_regular']), stg['color_text'])
        already_shown += 1
        if already_shown == stats_to_show + 1:
            break

    if len(stats) > stats_to_show:
        scrollbar_height = 542 * 542 // (len(stats) * 16)
        scrollbar_position = 58 + scroll_stats * (scrollbar_height) // (len(stats) - stats_to_show)
        if scrollbar_height < 1:
            scrollbar_height = 1
        if scrollbar_position > 599:
            scrollbar_position = 599
        pygame.draw.rect(screen, stg['color_scrollbar'], pygame.Rect(790, scrollbar_position, 10, scrollbar_height))

    pygame.display.flip()

def draw_history():
    screen.fill(stg['color_background'])

    draw_game_progress(716)
    screen.blit(backbutton, (736, 10))
    screen.blit(clearbutton, (662, 10))

    if len(history) == 0:
        show_text(screen, font_general, 'History is empty', (10, 58))

    for i in range(scroll_history, min(scroll_history + achs_to_show + 1, len(history))):
        if 'ach' in history[i]:
            font_regular = font_achs_regular[history[i]['ach'].language]
            font_small = font_achs_small[history[i]['ach'].language]

        desc_max_lines = 2
        if hover_ach == i - scroll_history or (not stg['show_timestamps'] and history[i]['type'] != 'progress_report'):
            desc_max_lines = 3
        
        if history[i]['type'] == 'unlock':
            pygame.draw.rect(screen, stg['frame_color_unlock'], pygame.Rect(10 - stg['frame_size'], 58 - stg['frame_size'] + (i - scroll_history) * 74, 64 + stg['frame_size'] * 2, 64 + stg['frame_size'] * 2))
            if history[i]['ach'].icon != None:
                screen.blit(ach_icons[history[i]['ach'].icon], (10, 58 + (i - scroll_history) * 74))
            else:
                pygame.draw.rect(screen, stg['color_background'], pygame.Rect(10, 58 + (i - scroll) * 74, 64, 64))
            long_text(screen, 706, font_regular, 'Unlocked: ' + history[i]['ach'].display_name_l, (84, 58 + (i - scroll_history) * 74), stg['color_text_unlock'])
            if history[i]['ach'].has_desc:
                multiline_text(screen, desc_max_lines, stg['font_line_distance_small'], 706, font_small, history[i]['ach'].description_l, (84, 75 + (i - scroll_history) * 74), stg['color_text_unlock'])
            if hover_ach != i - scroll_history or not history[i]['ach'].long_desc and stg['show_timestamps']:
                show_text(screen, font_general, history[i][f"time_{stg['history_time']}"], (84, 107 + (i - scroll_history) * 74), stg['color_text'])
        elif history[i]['type'] == 'lock':
            pygame.draw.rect(screen, stg['frame_color_lock'], pygame.Rect(10 - stg['frame_size'], 58 - stg['frame_size'] + (i - scroll_history) * 74, 64 + stg['frame_size'] * 2, 64 + stg['frame_size'] * 2))
            if history[i]['ach'].icon_gray != None:
                screen.blit(ach_icons[history[i]['ach'].icon_gray], (10, 58 + (i - scroll_history) * 74))
            else:
                pygame.draw.rect(screen, stg['color_background'], pygame.Rect(10, 58 + (i - scroll) * 74, 64, 64))
            long_text(screen, 706, font_regular, 'Locked: ' + history[i]['ach'].display_name_l, (84, 58 + (i - scroll_history) * 74), stg['color_text'])
            if history[i]['ach'].hidden != '1' and history[i]['ach'].has_desc:
                multiline_text(screen, desc_max_lines, stg['font_line_distance_small'], 706, font_small, history[i]['ach'].description_l, (84, 75 + (i - scroll_history) * 74), stg['color_text_lock'])
            elif history[i]['ach'].hidden == '1':
                multiline_text(screen, desc_max_lines, stg['font_line_distance_small'], 706, font_small, stg['hidden_desc'], (84, 75 + (i - scroll_history) * 74), stg['color_text_lock'])
            if hover_ach != i - scroll_history or not history[i]['ach'].long_desc and stg['show_timestamps']:
                show_text(screen, font_general, history[i][f"time_{stg['history_time']}"], (84, 107 + (i - scroll_history) * 74), stg['color_text'])
        elif history[i]['type'] == 'lock_all':
            pygame.draw.rect(screen, stg['frame_color_lock'], pygame.Rect(10 - stg['frame_size'], 58 - stg['frame_size'] + (i - scroll_history) * 74, 64 + stg['frame_size'] * 2, 64 + stg['frame_size'] * 2))
            screen.blit(lockallicon, (10, 58 + (i - scroll_history) * 74))
            show_text(screen, font_general, 'All achievements locked', (84, 58 + (i - scroll_history) * 74), stg['color_text'])
            show_text(screen, font_general_small, 'File containing achievement data was deleted', (84, 75 + (i - scroll_history) * 74)), stg['color_text']
            if stg['show_timestamps']:
                show_text(screen, font_general, history[i][f"time_{stg['history_time']}"], (84, 107 + (i - scroll_history) * 74), stg['color_text'])
        elif history[i]['type'] == 'progress_report':
            pygame.draw.rect(screen, stg['frame_color_lock'], pygame.Rect(10 - stg['frame_size'], 58 - stg['frame_size'] + (i - scroll_history) * 74, 64 + stg['frame_size'] * 2, 64 + stg['frame_size'] * 2))
            if history[i]['ach'].icon != None:
                screen.blit(ach_icons[history[i]['ach'].icon_gray], (10, 58 + (i - scroll_history) * 74))
            else:
                pygame.draw.rect(screen, stg['color_background'], pygame.Rect(10, 58 + (i - scroll) * 74, 64, 64))

            progress_str = f"{round_down(history[i]['value'][0], 2)}/{history[i]['value'][1]}"
            prg_str_len = font_regular.size(progress_str)[0]
            title_str = long_text(screen, 706 - font_regular.size(f'({progress_str})')[0], font_regular, 'Progress: ' + history[i]['ach'].display_name_l, None, (255, 255, 255), True)
            show_text(screen, font_regular, f'{title_str} ({progress_str})', (84, 58 + (i - scroll_history) * 74), stg['color_text'])

            if history[i]['ach'].hidden != '1' and history[i]['ach'].has_desc:
                multiline_text(screen, desc_max_lines, stg['font_line_distance_small'], 706, font_small, history[i]['ach'].description_l, (84, 75 + (i - scroll_history) * 74), stg['color_text_lock'])
            elif history[i]['ach'].hidden == '1':
                multiline_text(screen, desc_max_lines, stg['font_line_distance_small'], 706, font_small, stg['hidden_desc'], (84, 75 + (i - scroll_history) * 74), stg['color_text_lock'])

            if hover_ach != i - scroll_history or not history[i]['ach'].long_desc:
                # without_min = history[i]['ach'].progress.get_without_min()
                draw_progressbar(84, 109 + (i - scroll_history) * 74, stg['bar_length'], 13, stg['color_bar_bg'], stg['color_bar_fill'], history[i]['value'][0], history[i]['value'][1])
                show_text(screen, font_general, progress_str, (stg['bar_length'] + 94, 107 + (i - scroll_history) * 74), stg['color_text'])
                if stg['show_timestamps']:
                    show_text(screen, font_general, history[i][f"time_{stg['history_time']}"], (stg['bar_length'] + 104 + prg_str_len, 107 + (i - scroll_history) * 74), stg['color_text'])

        if history[i]['unread'] == 1:
            screen.blit(unreadicon, (66, 114 + (i - scroll_history) * 74))
        elif history[i]['unread'] == 2:
            screen.blit(unreadicon2, (66, 114 + (i - scroll_history) * 74))

    if len(history) > achs_to_show:
        scrollbar_height = 542 * 542 // (len(history) * 74 - 10)
        scrollbar_position = 58 + scroll_history * (542 - (scrollbar_height)) // (len(history) - 7)
        if scrollbar_height < 1:
            scrollbar_height = 1
        if scrollbar_position > 599:
            scrollbar_position = 599
        pygame.draw.rect(screen, stg['color_scrollbar'], pygame.Rect(790, scrollbar_position, 10, scrollbar_height))

    pygame.display.flip()

if platform.uname().system == 'Linux':
    os.environ['SDL_VIDEO_X11_NET_WM_BYPASS_COMPOSITOR'] = '0'

appid, achdata_source, cdx_appdata = (None, None, None)
if len(sys.argv) > 1:
    appid = check_alias(sys.argv[1])
    if len(appid.split()) > 1:
        achdata_source = source_name(appid.split()[1], 'goldberg')
        if achdata_source == 'codex':
            cdx_appdata = len(appid.split()) > 2 and appid.split()[2] in ('a', 'appdata')
        appid = appid.split()[0]
    if not appid.isnumeric:
        print('Invalid AppID')
        exit(1)
    
    if achdata_source == None and len(sys.argv) > 2:
        achdata_source = source_name(sys.argv[2], 'goldberg')
        if achdata_source == 'codex':
            cdx_appdata = len(sys.argv) > 3 and sys.argv[3] in ('a', 'appdata')
    elif achdata_source == None:
        achdata_source = 'goldberg'
else:
    appid = check_alias(input('Enter AppID: '))
    if len(appid.split()) > 1:
        achdata_source = source_name(appid.split()[1], 'goldberg')
        if achdata_source == 'codex':
            cdx_appdata = len(appid.split()) > 2 and appid.split()[2] in ('a', 'appdata')
        appid = appid.split()[0]
    else:
        achdata_source = 'goldberg'
    if not appid.isnumeric():
        print('Invalid AppID')
        exit(1)
gamename = get_game_name(appid)

stg = load_settings(appid, achdata_source)

pygame.init()

pygame.display.set_caption(f'Achievements | {gamename}')
screen = pygame.display.set_mode((800, 600))
achs_to_show = 7
stats_to_show = 33

viewing = 'achs'
scroll = 0
scroll_stats = 0
scroll_history = 0
state_filter = 0
history = []

statsbutton = pygame.image.load('images/stats.png')
achsbutton = pygame.image.load('images/achs.png')
filter_buttons = [pygame.image.load('images/filter_all.png'), pygame.image.load('images/filter_unlock.png'), pygame.image.load('images/filter_lock.png')]
historybutton = pygame.image.load('images/history.png')
backbutton = pygame.image.load('images/back.png')
clearbutton = pygame.image.load('images/clear.png')
unreadicon = pygame.image.load('images/unread.png')
unreadicon2 = pygame.image.load('images/unread2.png')
lockallicon = pygame.image.load('images/lock_all.png')

try:
    with open(os.path.join('games', appid, 'achievements.json')) as achsfile:
        achs_json = json.load(achsfile)
except FileNotFoundError:
    achs_json = {}

try:
    with open(get_player_achs_path(achdata_source, appid, cdx_appdata)) as player_achsfile:
        if achdata_source == 'goldberg':
            achieved_json = json.load(player_achsfile)
        elif achdata_source == 'codex':
            achieved_json = player_achsfile.read()
            achieved_json = convert_achs_format(achieved_json, achdata_source)
except FileNotFoundError:
    achieved_json = None

stats = {}

try:
    with open(os.path.join('games', appid, 'stats.txt')) as statslist:
        statlines = statslist.read().split('\n')
        for line in statlines:
            linespl = line.split('=')
            if len(linespl) == 3:
                locinfo = {'source': achdata_source, 'appid': appid, 'name': linespl[0]}
                if achdata_source == 'codex':
                    locinfo['cdx_appdata'] = cdx_appdata
                stats[linespl[0]] = Stat(locinfo, linespl[1], linespl[2], stg['delay_read_change'])
except FileNotFoundError:
    pass

achs = []
for ach in achs_json:
    achs.append(Achievement(ach, achieved_json, stats, stg))

achs_f, secrets_hidden = filter_achs(achs, state_filter, stg['hide_secrets'])

ach_idxs = {}
ach_icons = {}
achs_unlocked = 0
languages_used = set()
if stg['hide_secrets']:
    languages_used.add('english')
force_unlocks = {}
if stg['forced_keep'] == 'save':
    try:
        with open(f'save/{achdata_source}/force_{appid}.json') as forcefile:
            force_unlocks = json.load(forcefile)
    except FileNotFoundError:
        pass

fu_change = False
for i in range(len(achs)):
    ach_idxs[achs[i].name] = i
    if achs[i].icon != None and not achs[i].icon in ach_icons.keys():
        ach_icons[achs[i].icon] = pygame.image.load(os.path.join('games', appid, 'achievement_images', achs[i].icon))
    if achs[i].icon_gray != None and not achs[i].icon_gray in ach_icons.keys():
        ach_icons[achs[i].icon_gray] = pygame.image.load(os.path.join('games', appid, 'achievement_images', achs[i].icon_gray))
    if achs[i].earned:
        achs_unlocked += 1
    languages_used.add(achs[i].language)
    if achs[i].name in force_unlocks.keys():
        if not achs[i].earned or achs[i].force_unlock:
            achs[i].earned = True
            achs[i].force_unlock = True
            achs[i].earned_time = force_unlocks[achs[i].name]
        else:
            force_unlocks.pop(achs[i].name)
            fu_change = True
    if achs[i].force_unlock and not achs[i].name in force_unlocks:
        force_unlocks[achs[i].name] = time.time()
        fu_change = True
if fu_change and stg['forced_keep'] == 'save':
    if not os.path.isdir(f'save/{achdata_source}'):
        os.makedirs(f'save/{achdata_source}')
    with open(f'save/{achdata_source}/force_{appid}.json', 'w') as forcefile:
        json.dump(force_unlocks, forcefile)

for i in ach_icons.keys():
    if (ach_icons[i].get_width(), ach_icons[i].get_height()) != (64, 64):
        ach_icons[i] = pygame.transform.scale(ach_icons[i], (64, 64))

ach_icons['hidden_dummy_ach_icon'] = pygame.image.load('images/hidden.png')

font_general = pygame.font.Font(os.path.join('fonts', stg['font_general']), stg['font_size_regular'])
font_general_small = pygame.font.Font(os.path.join('fonts', stg['font_general']), stg['font_size_small'])
font_achs_regular = {}
font_achs_small = {}
for l in languages_used:
    try:
        if l in stg['font_achs'].keys():
            font_achs_regular[l] = pygame.font.Font(os.path.join('fonts', stg['font_achs'][l]), stg['font_size_regular'])
            font_achs_small[l] = pygame.font.Font(os.path.join('fonts', stg['font_achs'][l]), stg['font_size_small'])
        elif 'all' in stg['font_achs'].keys():
            font_achs_regular[l] = pygame.font.Font(os.path.join('fonts', stg['font_achs']['all']), stg['font_size_regular'])
            font_achs_small[l] = pygame.font.Font(os.path.join('fonts', stg['font_achs']['all']), stg['font_size_small'])
        else:
            print("Couldn't find a font to use for", l)
            exit(1)
    except FileNotFoundError:
        print('Font file not found')
        exit(1)

for ach in achs:
    if ach.has_desc:
        ach.long_desc = multiline_text(None, 2, stg['font_line_distance_small'], 706, font_achs_small[ach.language], ach.description_l, None, (0, 0, 0), True)

hover_ach = None
running = True
flip_required = True
last_update = time.time()
fchecker_achieved_locinfo = {'source': achdata_source, 'appid': appid}
if achdata_source == 'codex':
    fchecker_achieved_locinfo['cdx_appdata'] = cdx_appdata
fchecker_achieved = FileChecker('player_achs', fchecker_achieved_locinfo, stg['delay_read_change'])
stats_delay_counter = 0
mouse_scrolling = False

draw_achs()

while running:
    notifications_sent = 0
    notifications_hidden = 0
    fu_change = False

    unread_default = 1
    if viewing == 'history':
        unread_default = 2
    if not stg['history_unread']:
        unread_default = 0

    if time.time() >= last_update + stg['delay']:
        last_update = time.time()

        if stg['delay_stats'] > 1:
            stats_delay_counter += 1
        changed, newdata = fchecker_achieved.check()
        
        if changed:
            
            if achdata_source != 'goldberg' and newdata != None:
                newdata = convert_achs_format(newdata, achdata_source)

            achs, changes = update_achs(achs, newdata, fchecker_achieved, stg)
            achs_f, secrets_hidden = filter_achs(achs, state_filter, stg['hide_secrets'])
            flip_required = True

            lock_all_notified = False
            for change in changes:
                if change['type'] == 'unlock':
                    achs_unlocked += 1
                    if change['was_forced']:
                        force_unlocks.pop(change['ach_api'], None)
                    history.insert(0, {'type': 'unlock', 'ach': achs[ach_idxs[change['ach_api']]], 'time_real': change['time_real'], 'time_action': change['time_action'], 'unread': unread_default})
                    if stg['notif'] and not change['was_forced']:
                        if notifications_sent < stg['notif_limit'] or stg['notif_limit'] == 0:
                            notification.notify(title='Achievement Unlocked!', message=change['ach'], timeout=stg['notif_timeout'])
                            notifications_sent += 1
                        else:
                            notifications_hidden += 1
                elif change['type'] == 'lock':
                    achs_unlocked -= 1
                    if change['lock_all']:
                        achs_unlocked = 0
                    if stg['notif_lock']:
                        if not change['lock_all']:
                            history.insert(0, {'type': 'lock', 'ach': achs[ach_idxs[change['ach_api']]], 'time_real': change['time_real'], 'time_action': change['time_action'], 'unread': unread_default})
                            if stg['notif']:
                                if notifications_sent < stg['notif_limit'] or stg['notif_limit'] == 0:
                                    notification.notify(title='Achievement Locked', message=change['ach'], timeout=stg['notif_timeout'])
                                    notifications_sent += 1
                                else:
                                    notifications_hidden += 1
                        elif not lock_all_notified:
                            history.insert(0, {'type': 'lock_all', 'time_real': change['time_real'], 'time_action': change['time_action'], 'unread': unread_default})
                            if stg['notif']:
                                if notifications_sent < stg['notif_limit'] or stg['notif_limit'] == 0:
                                    notification.notify(title='All achievements locked', message='Achievement data not found', timeout=stg['notif_timeout'])
                                    notifications_sent += 1
                                else:
                                    notifications_hidden += 1
                            lock_all_notified = True
                elif change['type'] == 'progress_report':
                    history.insert(0, {'type': 'progress_report', 'value': change['value'], 'ach': achs[ach_idxs[change['ach_api']]], 'time_real': change['time_real'], 'time_action': change['time_action'], 'unread': unread_default})
                    if stg['notif']:
                        if notifications_sent < stg['notif_limit'] or stg['notif_limit'] == 0:
                            notification.notify(title='Achievement Progress', message=f"{change['ach']} ({change['value'][0]}/{change['value'][1]})", timeout=stg['notif_timeout'])
                            notifications_sent += 1
                        else:
                            notifications_hidden += 1
            if notifications_hidden > 0:
                notification.notify(title='Too many notifications', message=f'{notifications_hidden} more notification(s) were hidden', timeout=stg['notif_timeout'])
            flip_required = True

        if stg['delay_stats'] <= 1 or stats_delay_counter >= stg['delay_stats']:
            stats_changed = False
            for stat in stats.values():
                if stat.update_val():
                    stats_changed = True

            if stats_changed:
                for ach in achs:
                    if ach.progress != None:
                        ach.progress.calculate(stats)

                        if stg['bar_force_unlock']:
                            # actual_value = ach.progress.current_value
                            # if stg['bar_ignore_min'] or ach.progress.min_val == ach.progress.max_val:
                                # actual_value = ach.progress.real_value
                            if ach.progress.real_value >= ach.progress.max_val and not ach.earned:
                                ach.earned = True
                                ach.earned_time = time.time()
                                ach.force_unlock = True
                                force_unlocks[ach.name] = ach.earned_time
                                fu_change = True
                                achs_unlocked += 1
                                time_real = datetime.now().strftime('%d %b %Y %H:%M:%S')
                                time_action = datetime.fromtimestamp(stats[ach.progress.value['operand1']].fchecker.last_check)
                                time_action = time_action.strftime('%d %b %Y %H:%M:%S')
                                if stg['forced_mark']:
                                    time_real += ' (F)'
                                    time_action += ' (F)'
                                history.insert(0, {'type': 'unlock', 'ach': ach, 'time_real': datetime.now().strftime('%d %b %Y %H:%M:%S (F)'), 'time_action': time_action, 'unread': unread_default})
                                if stg['notif']:
                                    if notifications_sent < stg['notif_limit'] or stg['notif_limit'] == 0:
                                        notification.notify(title='Achievement Unlocked!', message=ach.display_name_l, timeout=stg['notif_timeout'])
                                        notifications_sent += 1
                                    else:
                                        notifications_hidden += 1
                            elif ach.progress.real_value < ach.progress.max_val and ach.force_unlock and stg['forced_keep'] == 'no':
                                ach.earned = False
                                ach.force_unlock = False
                                force_unlocks.pop(ach.name, None)
                                fu_change = True
                                achs_unlocked -= 1
                                if stg['notif_lock']:
                                    time_real = datetime.now().strftime('%d %b %Y %H:%M:%S')
                                    time_action = datetime.fromtimestamp(stats[ach.progress.value['operand1']].fchecker.last_check)
                                    time_action = time_action.strftime('%d %b %Y %H:%M:%S')
                                    if stg['forced_mark']:
                                        tme_real += ' (F)'
                                        time_action += ' (F)'
                                    history.insert(0, {'type': 'lock', 'ach': ach, 'time_real': datetime.now().strftime('%d %b %Y %H:%M:%S (F)'), 'time_action': time_action, 'unread': unread_default})
                                    if stg['notif']:
                                        if notifications_sent < stg['notif_limit'] or stg['notif_limit'] == 0:
                                            notification.notify(title='Achievement Unlocked!', message=ach.display_name_l, timeout=stg['notif_timeout'])
                                            notifications_sent += 1
                                        else:
                                            notifications_hidden += 1
            stats_delay_counter = 0

        if fu_change and stg['forced_keep'] == 'save':
            if not os.path.isdir(f'save/{achdata_source}'):
                os.makedirs(f'save/{achdata_source}')
            with open(f'save/{achdata_source}/force_{appid}.json', 'wt') as forcefile:
                json.dump(force_unlocks, forcefile)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                if viewing == 'achs' and scroll < len(achs_f) - achs_to_show:
                    scroll += 1
                    flip_required = True
                elif viewing == 'stats' and scroll_stats < len(stats) - (stats_to_show + 1):
                    scroll_stats += 1
                    flip_required = True
                elif viewing == 'history' and scroll_history < len(history) - 7:
                    scroll_history += 1
                    flip_required = True
            elif event.key == pygame.K_UP:
                if viewing == 'achs' and scroll > 0:
                    scroll -= 1
                    flip_required = True
                elif viewing == 'stats' and scroll_stats > 0:
                    scroll_stats -= 1
                    flip_required = True
                if viewing == 'history' and scroll_history > 0:
                    scroll_history -= 1
                    flip_required = True

        elif event.type == pygame.MOUSEMOTION:
            if mouse_scrolling:
                if viewing == 'achs':
                    scroll = (event.pos[1] - 58) * (len(achs_f) - achs_to_show) // 542
                    if scroll < 0:
                        scroll = 0
                    if scroll > len(achs_f) - achs_to_show:
                        scroll = len(achs_f) - achs_to_show
                elif viewing == 'stats':
                    scroll_stats = (event.pos[1] - 58) * (len(stats) - stats_to_show) // 542
                    if scroll_stats < 0:
                        scroll_stats = 0
                    if scroll_stats > len(stats) - stats_to_show:
                        scroll_stats = len(stats) - stats_to_show
                elif viewing == 'history':
                    scroll_history = (event.pos[1] - 58) * (len(history) - achs_to_show) // 542
                    if scroll_history < 0:
                        scroll_history = 0
                    if scroll_history > len(history) - achs_to_show:
                        scroll_history = len(history) - achs_to_show
                flip_required = True
            elif viewing == 'achs' or viewing == 'history':
                old_hover_ach = hover_ach
                hover_ach = None
                for i in range(achs_to_show):
                    if pygame.Rect(10, 58 + i * 74, 780, 64).collidepoint(event.pos):
                        hover_ach = i
                        break
                if hover_ach != old_hover_ach:
                    flip_required = True

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if viewing == 'achs':
                if len(achs_f) > achs_to_show and event.pos[0] >= 790 and event.pos[1] >= 58:
                    mouse_scrolling = True
                elif pygame.Rect(638, 10, 74, 22).collidepoint(event.pos):
                    state_filter += 1
                    if state_filter > 2:
                        state_filter = 0
                    achs_f, secrets_hidden = filter_achs(achs, state_filter, stg['hide_secrets'])
                    scroll = 0
                    flip_required = True
                elif pygame.Rect(722, 10, 68, 22).collidepoint(event.pos):
                    viewing = 'stats'
                elif pygame.Rect(538, 10, 90, 22).collidepoint(event.pos) and stg['history_length'] != -1:
                    viewing = 'history'
            elif viewing == 'stats':
                if pygame.Rect(722, 10, 68, 22).collidepoint(event.pos):
                    viewing = 'achs'
                if len(stats) > stats_to_show and event.pos[0] >= 790 and event.pos[1] >= 58:
                    mouse_scrolling = True
            elif viewing == 'history':
                if len(history) > achs_to_show and event.pos[0] >= 790 and event.pos[1] >= 58:
                    mouse_scrolling = True
                elif pygame.Rect(736, 10, 54, 22).collidepoint(event.pos):
                    for entry in history:
                        entry['unread'] = 0
                    scroll_history = 0
                    viewing = 'achs'
                elif pygame.Rect(662, 10, 64, 22).collidepoint(event.pos):
                    scroll_history = 0
                    history = []

        elif event.type == pygame.MOUSEBUTTONUP:
            mouse_scrolling = False

    while stg['history_length'] != 0 and len(history) > stg['history_length'] and len(history) > 0:
        history.pop(-1)

    if flip_required:
        if viewing == 'achs':
            draw_achs()
        elif viewing == 'stats':
            draw_stats()
        elif viewing == 'history':
            draw_history()

    time.sleep(stg['delay_sleep'])