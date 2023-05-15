import os
import sys
import platform
import json
import time
import zlib
from random import randint
from threading import Timer
import pygame
import requests
from PIL import Image as PILimg
from showtext import *
from achievements import *
from stats import *
from filechanges import *
from settings import *

if platform.uname().system == 'Windows':
    from plyer import notification
elif platform.uname().system == 'Linux':
    import unotify as notification
    os.environ['SDL_VIDEO_X11_NET_WM_BYPASS_COMPOSITOR'] = '0'
else:
    from plyer import notification

def round_down(number, leave_dec):
    number = str(number)
    dot = number.find('.')
    if dot == -1 or dot >= len(number) - 1 - leave_dec:
        return number
    else:
        return number[:dot + leave_dec + 1]

def convert_ico(name):
    p = f"games/ico/{appid}/{name.split('/')[-1]}.ico"
    if not os.path.isfile(f"games/ico/{appid}/{name.split('/')[-1]}.ico"):
        p = f"games/{appid}/{name.split('/')[-1]}.ico"
        img = PILimg.open(name)
        img.save(p)
        Timer(1, os.remove, (p, )).start()
    return p

def send_notification(title, message, app_icon=None):
    kwargs = {
        'app_name': gamename,
        'title': title,
        'message': message,
        'timeout': stg['notif_timeout']
    }
    if platform.uname().system == 'Windows':
        if app_icon != None and stg['notif_icons']:
            try:
                kwargs['app_icon'] = convert_ico(app_icon)
            except Exception:
                pass
    else:
        # Set urgency to display notification on top of fullscreen apps
        kwargs['urgency'] = notification.urgencies.HIGH
        if app_icon != None and stg['notif_icons']:
            kwargs['app_icon'] = app_icon
    return notification.notify(**kwargs)

def send_steam_request(name, link):
    if name != 'appdetails':
        global url_random
        url_random += 1
        link += f'&__random?={url_random}'
    try:
        r = requests.get(link)
        if int(r.status_code / 100) != 4:
            r = r.json()
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
        
def draw_progressbar(x, y, w, h, p1, p2):
    if w <= 0:
        return
    pygame.draw.rect(screen, stg['color_bar_bg'], pygame.Rect(x, y, w, h))
    if p1 > p2:
        p1 = p2
    c2 = stg['color_bar_fill']
    if p1 == p2:
        c2 = stg['color_bar_completed']
    if p2 != 0:
        pygame.draw.rect(screen, c2, pygame.Rect(x, y, p1 * w // p2, h))

def draw_scrollbar(scr, maxscr, total_height):
    scrollbar_height = (stg['window_size_y'] - header_h) ** 2 // total_height
    scrollbar_position = header_h + scr * (stg['window_size_y'] - header_h - (scrollbar_height)) // maxscr
    if scrollbar_height < 1:
        scrollbar_height = 1
    if scrollbar_position > stg['window_size_y'] - 1:
        scrollbar_position = stg['window_size_y'] - 1
    pygame.draw.rect(screen, stg['color_scrollbar'], pygame.Rect(stg['window_size_x'] - 10, scrollbar_position, 10, scrollbar_height))

def draw_game_progress(max_name_length):
    positions = {'normal': 30, 'repname': 15, 'under': 42, 'hide': None}
    y = positions[stg['gamebar_position']]
    if stg['gamebar_position'] != 'repname' and max_name_length > 0:
        ty = 10
        if stg['gamebar_position'] in ('under', 'hide') and stg['font_size_regular'] <= 22:
            ty += round((22 - stg['font_size_regular']) / 2)
        long_text(screen, max_name_length, font_general, gamename, (10, ty), stg['color_text'])
    if stg['gamebar_position'] == 'hide':
        return
    draw_progressbar(10, y, stg['gamebar_length'], 13, achs_unlocked, len(achs))
    game_progress_str = f'{achs_unlocked}/{len(achs)}'
    if len(achs) > 0:
        game_progress_str += f' ({achs_unlocked * 100 // len(achs)}%)'
    else:
        game_progress_str += ' (0%)'
    show_text(screen, font_general, game_progress_str, (stg['gamebar_length'] + 20, y - 2), stg['color_text'])

def draw_achs():
    screen.fill(stg['color_background'])

    if stg['history_length'] != -1:
        screen.blit(historybutton, (stg['window_size_x'] - 264, 10))
        draw_game_progress(stg['window_size_x'] - 284)
    else:
        draw_game_progress(stg['window_size_x'] - 184)
    if len(history) > 0 and history[0]['unread'] == 1:
        screen.blit(unreadicon, (stg['window_size_x'] - 182, 24))
    screen.blit(filter_buttons[state_filter], (stg['window_size_x'] - 164, 10))
    screen.blit(statsbutton, (stg['window_size_x'] - 78, 10))

    if len(achs_f) == 0:
        show_text(screen, font_general, 'No achievements found', (10, header_h), stg['color_text'])

    for i in range(scroll, scroll + achs_to_show + 1):
        if i < len(achs_f):
            font_regular = font_achs_regular[achs_f[i].language]
            font_small = font_achs_small[achs_f[i].language]

            bar_shown = not (achs_f[i].progress == None or (stg['bar_unlocked'] == 'hide' and achs_f[i].earned) or \
                            (stg['bar_hide_unsupported'] == 'all' and not achs_f[i].progress.support) or \
                            (stg['bar_hide_unsupported'] == 'stat' and achs_f[i].progress.support_error != "Unknown stat") or \
                            (stg['bar_hide_secret'] and achs_f[i].hidden and not achs_f[i].earned))

            desc_max_lines = 3
            if bar_shown or (achs_f[i].earned and stg['show_timestamps']):
                desc_max_lines = 2
            if hover_ach == i - scroll:
                desc_max_lines = 3
            
            if achs_f[i].earned:
                pygame.draw.rect(screen, stg['frame_color_unlock'], pygame.Rect(10 - stg['frame_size'], header_h - stg['frame_size'] + (i - scroll) * 74, 64 + stg['frame_size'] * 2, 64 + stg['frame_size'] * 2))
                if achs_f[i].icon != None and achs_f[i].icon in ach_icons:
                    screen.blit(ach_icons[achs_f[i].icon], (10, header_h + (i - scroll) * 74))
                else:
                    pygame.draw.rect(screen, stg['color_background'], pygame.Rect(10, header_h + (i - scroll) * 74, 64, 64))
                long_text(screen, stg['window_size_x'] - 94, font_regular, achs_f[i].display_name_l, (84, header_h + (i - scroll) * 74), stg['color_text_unlock'])
                if achs_f[i].has_desc:
                    multiline_text(screen, desc_max_lines, stg['font_line_distance_small'], stg['window_size_x'] - 94, font_small, achs_f[i].description_l, (84, header_h + 17 + (i - scroll) * 74), stg['color_text_unlock'])
                if hover_ach != i - scroll or not (achs_f[i].long_desc or (long_hidden_desc[achs_f[i].language] and achs_f[i].hidden and not achs_f[i].earned)):
                    if bar_shown:
                        if achs_f[i].progress.support:
                            if not (stg['bar_unlocked'] == 'full' and achs_f[i].earned):
                                prg_str_len = font_general.size(f'{achs_f[i].progress.current_value}/{achs_f[i].progress.max_val}')[0]
                            else:
                                prg_str_len = font_general.size(f'{achs_f[i].progress.max_val}/{achs_f[i].progress.max_val}')[0]
                        else:
                            prg_str_len = font_general.size(achs[i].progress.support_error)[0]
                        if stg['show_timestamps']:
                            show_text(screen, font_general, achs_f[i].get_time(stg['savetime_shown'], stg['forced_mark'], stg['savetime_mark']),
                                     (stg['bar_length'] + 104 + prg_str_len, header_h + 49 + (i - scroll) * 74), stg['color_text'])
                    else:
                        if stg['show_timestamps']:
                            show_text(screen, font_general, achs_f[i].get_time(stg['savetime_shown'], stg['forced_mark'], stg['savetime_mark']),
                                     (84, header_h + 49 + (i - scroll) * 74), stg['color_text'])

                # ach_time = achs_f[i].get_time()
                # show_text(screen, font_regular, ach_time, (790 - font_regular.size(ach_time)[0] , 107 + (i - scroll) * 74))

                # ach_time = achs_f[i].get_time()
                # ach_time_len = font_regular.size(ach_time)
                # rrect = pygame.Rect(0, 0, ach_time_len[0], ach_time_len[1])
                # rrect.midright = (790, 90 + (i - scroll) * 74)
                # show_text(screen, font_regular, ach_time, rrect)

            else:
                pygame.draw.rect(screen, stg['frame_color_lock'], pygame.Rect(10 - stg['frame_size'], header_h - stg['frame_size'] + (i - scroll) * 74, 64 + stg['frame_size'] * 2, 64 + stg['frame_size'] * 2))
                if achs_f[i].icon_gray != None and achs_f[i].icon_gray in ach_icons:
                    screen.blit(ach_icons[achs_f[i].icon_gray], (10, header_h + (i - scroll) * 74))
                else:
                    pygame.draw.rect(screen, stg['color_background'], pygame.Rect(10, header_h + (i - scroll) * 74, 64, 64))
                long_text(screen, stg['window_size_x'] - 94, font_regular, achs_f[i].display_name_l, (84, header_h + (i - scroll) * 74), stg['color_text_lock'])
                if not achs_f[i].hidden and achs_f[i].has_desc:
                    multiline_text(screen, desc_max_lines, stg['font_line_distance_small'], stg['window_size_x'] - 94, font_small, achs_f[i].description_l, (84, header_h + 17 + (i - scroll) * 74), stg['color_text_lock'])
                elif achs_f[i].hidden:
                    multiline_text(screen, desc_max_lines, stg['font_line_distance_small'], stg['window_size_x'] - 94, font_small, stg['hidden_desc'], (84, header_h + 17 + (i - scroll) * 74), stg['color_text_lock'])

            if achs_f[i].progress != None and (hover_ach != i - scroll or not (achs_f[i].long_desc or (long_hidden_desc[achs_f[i].language] and achs_f[i].hidden and not achs_f[i].earned))):
                if achs_f[i].progress.support:
                    if not stg['bar_ignore_min']:
                        without_min = achs_f[i].progress.get_without_min()
                    else:
                        without_min = (achs_f[i].progress.real_value, achs_f[i].progress.max_val)
                    if not ((stg['bar_unlocked'] == 'hide' and achs_f[i].earned) or (stg['bar_hide_secret'] and achs_f[i].hidden and not achs_f[i].earned)):
                        if (stg['bar_unlocked'] == 'full' and achs_f[i].earned):
                            draw_progressbar(84, header_h + 51 + (i - scroll) * 74, stg['bar_length'], 13, 1, 1)
                            show_text(screen, font_general, f'{achs_f[i].progress.max_val}/{achs_f[i].progress.max_val}', (stg['bar_length'] + 94, header_h + 49 + (i - scroll) * 74), stg['color_text'])
                        else:
                            draw_progressbar(84, header_h + 51 + (i - scroll) * 74, stg['bar_length'], 13, without_min[0], without_min[1])
                            prg_val_to_show = round_down(achs_f[i].progress.current_value, 2)
                            if stg['bar_ignore_min']:
                                prg_val_to_show = round_down(achs_f[i].progress.real_value, 2)
                            show_text(screen, font_general, f'{prg_val_to_show}/{achs_f[i].progress.max_val}', (stg['bar_length'] + 94, header_h + 49 + (i - scroll) * 74), stg['color_text'])
                elif not (stg['bar_hide_unsupported'] == 'all' or (stg['bar_hide_unsupported'] == 'stat' and achs_f[i].progress.support_error != "Unknown stat") \
                     or (stg['bar_unlocked'] == 'hide' and achs_f[i].earned) or (stg['bar_hide_secret'] and achs_f[i].hidden and not achs_f[i].earned)):
                    if (stg['bar_unlocked'] == 'full' and achs_f[i].earned):
                        draw_progressbar(84, header_h + 51 + (i - scroll) * 74, stg['bar_length'], 13, 1, 1)
                    else:
                        draw_progressbar(84, header_h + 51 + (i - scroll) * 74, stg['bar_length'], 13, 0, 1)
                    show_text(screen, font_general, achs_f[i].progress.support_error, (stg['bar_length'] + 94, header_h + 49 + (i - scroll) * 74), stg['color_text'])

    if len(achs_f) > achs_to_show:
        draw_scrollbar(scroll, len(achs_f) - achs_to_show, len(achs_f) * 74 - 10)

    pygame.display.flip()

def draw_stats():
    screen.fill(stg['color_background'])

    draw_game_progress(stg['window_size_x'] - 98)
    screen.blit(achsbutton, (stg['window_size_x'] - 78, 10))

    if len(stats) == 0:
        show_text(screen, font_general, 'No stats found', (10, header_h))

    already_shown = 0 - scroll_stats
    for stat in stats.values():
        if already_shown >= 0:
            short_name = long_text(screen, stg['window_size_x'] - 20 - font_general.size(f' = {stat.value}')[0], font_general, stat.name, None, None, True)
            show_text(screen, font_general, f'{short_name} = {stat.value}', (10, header_h + already_shown * stg['font_line_distance_regular']), stg['color_text'])
        already_shown += 1
        if already_shown == stats_to_show + 1:
            break

    if len(stats) > stats_to_show:
        draw_scrollbar(scroll_stats, len(stats) - stats_to_show, len(stats) * stg['font_line_distance_regular'])

    pygame.display.flip()

def draw_history():
    screen.fill(stg['color_background'])

    draw_game_progress(stg['window_size_x'] - 158)
    screen.blit(backbutton, (stg['window_size_x'] - 64, 10))
    screen.blit(clearbutton, (stg['window_size_x'] - 138, 10))

    if len(history) == 0:
        show_text(screen, font_general, 'History is empty', (10, header_h))

    for i in range(scroll_history, min(scroll_history + achs_to_show + 1, len(history))):
        l = 'english'
        if 'ach' in history[i]:
            l = history[i]['ach'].language
        font_regular = font_achs_regular[l]
        font_small = font_achs_small[l]

        desc_max_lines = 2
        if hover_ach == i - scroll_history or (not stg['show_timestamps'] and history[i]['type'] != 'progress_report'):
            desc_max_lines = 3
        
        if history[i]['type'] == 'unlock':
            pygame.draw.rect(screen, stg['frame_color_unlock'], pygame.Rect(10 - stg['frame_size'], header_h - stg['frame_size'] + (i - scroll_history) * 74, 64 + stg['frame_size'] * 2, 64 + stg['frame_size'] * 2))
            if history[i]['ach'].icon != None and history[i]['ach'].icon in ach_icons:
                screen.blit(ach_icons[history[i]['ach'].icon], (10, header_h + (i - scroll_history) * 74))
            else:
                pygame.draw.rect(screen, stg['color_background'], pygame.Rect(10, header_h + (i - scroll) * 74, 64, 64))
            long_text(screen, stg['window_size_x'] - 94, font_regular, 'Unlocked: ' + history[i]['ach'].display_name_l, (84, header_h + (i - scroll_history) * 74), stg['color_text_unlock'])
            if history[i]['ach'].has_desc:
                multiline_text(screen, desc_max_lines, stg['font_line_distance_small'], stg['window_size_x'] - 94, font_small, history[i]['ach'].description_l,
                              (84, header_h + 17 + (i - scroll_history) * 74), stg['color_text_unlock'])
            if hover_ach != i - scroll_history or not (history[i]['ach'].long_desc or (long_hidden_desc[history[i]['ach'].language] and history[i]['ach'].hidden and not history[i]['ach'].earned)) and stg['show_timestamps']:
                show_text(screen, font_general, history[i][f"time_{stg['history_time']}"], (84, header_h + 49 + (i - scroll_history) * 74), stg['color_text'])
        elif history[i]['type'] == 'lock':
            pygame.draw.rect(screen, stg['frame_color_lock'], pygame.Rect(10 - stg['frame_size'], header_h - stg['frame_size'] + (i - scroll_history) * 74, 64 + stg['frame_size'] * 2, 64 + stg['frame_size'] * 2))
            if history[i]['ach'].icon_gray != None and history[i]['ach'].icon_gray in ach_icons:
                screen.blit(ach_icons[history[i]['ach'].icon_gray], (10, header_h + (i - scroll_history) * 74))
            else:
                pygame.draw.rect(screen, stg['color_background'], pygame.Rect(10, header_h + (i - scroll) * 74, 64, 64))
            long_text(screen, stg['window_size_x'] - 94, font_regular, 'Locked: ' + history[i]['ach'].display_name_l, (84, header_h + (i - scroll_history) * 74), stg['color_text'])
            if not history[i]['ach'].hidden and history[i]['ach'].has_desc:
                multiline_text(screen, desc_max_lines, stg['font_line_distance_small'], stg['window_size_x'] - 94, font_small, history[i]['ach'].description_l,
                              (84, header_h + 17 + (i - scroll_history) * 74), stg['color_text_lock'])
            elif history[i]['ach'].hidden:
                multiline_text(screen, desc_max_lines, stg['font_line_distance_small'], stg['window_size_x'] - 94, font_small, stg['hidden_desc'], (84, header_h + 17 + (i - scroll_history) * 74), stg['color_text_lock'])
            if hover_ach != i - scroll_history or not (history[i]['ach'].long_desc or (long_hidden_desc[history[i]['ach'].language] and history[i]['ach'].hidden and not history[i]['ach'].earned)) and stg['show_timestamps']:
                show_text(screen, font_general, history[i][f"time_{stg['history_time']}"], (84, header_h + 49 + (i - scroll_history) * 74), stg['color_text'])
        elif history[i]['type'] == 'lock_all':
            pygame.draw.rect(screen, stg['frame_color_lock'], pygame.Rect(10 - stg['frame_size'], header_h - stg['frame_size'] + (i - scroll_history) * 74, 64 + stg['frame_size'] * 2, 64 + stg['frame_size'] * 2))
            screen.blit(lockallicon, (10, header_h + (i - scroll_history) * 74))
            show_text(screen, font_regular, 'All achievements locked', (84, header_h + (i - scroll_history) * 74), stg['color_text'])
            show_text(screen, font_small, 'File containing achievement data was deleted', (84, header_h + 17 + (i - scroll_history) * 74)), stg['color_text']
            if stg['show_timestamps']:
                show_text(screen, font_general, history[i][f"time_{stg['history_time']}"], (84, header_h + 49 + (i - scroll_history) * 74), stg['color_text'])
        elif history[i]['type'] == 'progress_report':
            pygame.draw.rect(screen, stg['frame_color_lock'], pygame.Rect(10 - stg['frame_size'], header_h - stg['frame_size'] + (i - scroll_history) * 74, 64 + stg['frame_size'] * 2, 64 + stg['frame_size'] * 2))
            if history[i]['ach'].icon != None and history[i]['ach'].icon in ach_icons:
                screen.blit(ach_icons[history[i]['ach'].icon_gray], (10, header_h + (i - scroll_history) * 74))
            else:
                pygame.draw.rect(screen, stg['color_background'], pygame.Rect(10, header_h + (i - scroll) * 74, 64, 64))

            progress_str = f"{round_down(history[i]['value'][0], 2)}/{history[i]['value'][1]}"
            prg_str_len = font_regular.size(progress_str)[0]
            title_str = long_text(screen, stg['window_size_x'] - 94 - font_regular.size(f'({progress_str})')[0], font_regular, 'Progress: ' + history[i]['ach'].display_name_l, None, (255, 255, 255), True)
            show_text(screen, font_regular, f'{title_str} ({progress_str})', (84, header_h + (i - scroll_history) * 74), stg['color_text'])

            if not history[i]['ach'].hidden and history[i]['ach'].has_desc:
                multiline_text(screen, desc_max_lines, stg['font_line_distance_small'], stg['window_size_x'] - 94, font_small, history[i]['ach'].description_l,
                              (84, header_h + 17 + (i - scroll_history) * 74), stg['color_text_lock'])
            elif history[i]['ach'].hidden:
                multiline_text(screen, desc_max_lines, stg['font_line_distance_small'], stg['window_size_x'] - 94, font_small, stg['hidden_desc'], (84, header_h + 17 + (i - scroll_history) * 74), stg['color_text_lock'])

            if hover_ach != i - scroll_history or not (history[i]['ach'].long_desc or (long_hidden_desc[history[i]['ach'].language] and history[i]['ach'].hidden and not history[i]['ach'].earned)):
                # without_min = history[i]['ach'].progress.get_without_min()
                draw_progressbar(84, header_h + 51 + (i - scroll_history) * 74, stg['bar_length'], 13, history[i]['value'][0], history[i]['value'][1])
                show_text(screen, font_general, progress_str, (stg['bar_length'] + 94, header_h + 49 + (i - scroll_history) * 74), stg['color_text'])
                if stg['show_timestamps']:
                    show_text(screen, font_general, history[i][f"time_{stg['history_time']}"], (stg['bar_length'] + 104 + prg_str_len, header_h + 49 + (i - scroll_history) * 74), stg['color_text'])

        if history[i]['unread'] == 1:
            screen.blit(unreadicon, (66, header_h + 56 + (i - scroll_history) * 74))
        elif history[i]['unread'] == 2:
            screen.blit(unreadicon2, (66, header_h + 56 + (i - scroll_history) * 74))

    if len(history) > achs_to_show:
        draw_scrollbar(scroll_history, len(history) - achs_to_show, len(history) * 74 - 10)

    pygame.display.flip()

appid, achdata_source, source_extra = (None, None, None)
if len(sys.argv) > 1:
    appid = check_alias(sys.argv[1])
    if len(appid.split()) > 1:
        if len(sys.argv) > 2:
            appid = appid.split()[0]
        else:
            achdata_source = source_name(appid.split()[1])
            if achdata_source == 'codex':
                source_extra = len(appid.split()) > 2 and appid.split()[2] in ('a', 'appdata')
            elif achdata_source in ('ali213', 'sse') and len(appid.split()) > 2:
                source_extra = ' '.join(appid.split()[2:])
            elif achdata_source == 'steam' and len(appid.split()) > 2:
                source_extra = appid.split()[2]
            elif achdata_source == None:
                print('Invalid emulator name')
                sys.exit()
            appid = appid.split()[0]
    if not appid.isnumeric:
        print('Invalid AppID')
        sys.exit()
    
    if achdata_source == None and len(sys.argv) > 2:
        achdata_source = source_name(sys.argv[2])
        if achdata_source == 'codex':
            source_extra = len(sys.argv) > 3 and sys.argv[3] in ('a', 'appdata')
        elif achdata_source in ('ali213', 'sse', 'steam') and len(sys.argv) > 3:
            source_extra = sys.argv[3]
        elif achdata_source == None:
            print('Invalid emulator name')
            sys.exit()
    elif achdata_source == None:
        achdata_source = 'goldberg'
else:
    inp = input('Enter AppID: ')
    appid = check_alias(inp)
    if len(appid.split()) > 1:
        if appid == inp:
            appid = check_alias(appid.split()[0]).split()[0] + ' ' + ' '.join(appid.split()[1:])
        achdata_source = source_name(appid.split()[1])
        if achdata_source == 'codex':
            source_extra = len(appid.split()) > 2 and appid.split()[2] in ('a', 'appdata')
        elif achdata_source in ('ali213', 'sse') and len(appid.split()) > 2:
            source_extra = ' '.join(appid.split()[2:])
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

if stg['window_size_x'] < 274 or stg['window_size_y'] < 132:
    print('Window size must be at least 274x132')
    sys.exit()
elif stg['gamebar_position'] == 'under' and stg['window_size_y'] < 144:
    print('With gamebar_position=under, window size must be at least 274x144')
    sys.exit()
if stg['bar_length'] == 0:
    stg['bar_length'] = -10
if stg['gamebar_length'] == 0:
    stg['gamebar_length'] = -10

if 'LnzAch_gamename' in os.environ:
    gamename = os.environ['LnzAch_gamename']
    with open('games/games.txt', 'r+', encoding='utf-8') as gamestxt:
        txt = gamestxt.read().split('\n')
        for line in range(len(txt) + 1):
            if line >= len(txt):
                txt.append(f'{appid}={gamename}')
                txt.append('')
                gamestxt.seek(0)
                gamestxt.write('\n'.join(txt))
                gamestxt.truncate()
                break
            elif line == len(txt) - 1 and txt[line] == '':
                txt.pop(line)
            elif txt[line].split('=')[0] == appid:
                if '='.join(txt[1:]) != gamename:
                    txt.pop(line)
                else:
                    break
else:
    gamename = get_game_name(appid)
    if gamename == appid:
        l = 'english'
        if len(stg['language']) > 0:
            l = stg['language'][0]
        steam_req = send_steam_request('appdetails', f'https://store.steampowered.com/api/appdetails?appids={appid}&l={l}')
        if steam_req != None:
            gamename = steam_req[appid]['data']['name']
            with open('games/games.txt', 'a', encoding='utf-8') as gamestxt:
                gamestxt.write(f'{appid}={gamename}\n')

if achdata_source == 'steam':
    if len(stg['api_key']) == 0:
        print('An API key is required to track achievements from Steam')
        sys.exit()
    if source_extra == None or not source_extra.isnumeric():
        print('Invalid Steam user ID')
        sys.exit()

header_h = 58
if stg['gamebar_position'] in ('repname', 'hide'):
    header_h = 47
elif stg['gamebar_position'] == 'under':
    header_h = 70

save_dir = get_save_dir(appid, achdata_source, source_extra)

pygame.init()

pygame.display.set_caption(f'Achievements | {gamename}')
screen = pygame.display.set_mode((stg['window_size_x'], stg['window_size_y']))
achs_to_show = int((stg['window_size_y'] - header_h + 10) / 74)
if stg['window_size_y'] - 48 < achs_to_show * 74 + stg['frame_size'] and achs_to_show > 1:
    achs_to_show -= 1
stats_to_show = int((stg['window_size_y'] - header_h) / stg['font_line_distance_regular'])

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

achs_crc32 = {}
if achdata_source == 'sse':
    for a in achs_json:
        achs_crc32[zlib.crc32(bytes(a['name'], 'utf-8'))] = a['name']

url_random = randint(0, 10000000)
achieved_json = None
if achdata_source != 'steam':
    try:
        m = 'rt'
        if achdata_source == 'sse':
            m = 'rb'
        with open(get_player_achs_path(achdata_source, appid, source_extra), m) as player_achsfile:
            if achdata_source == 'goldberg':
                achieved_json = json.load(player_achsfile)
            elif achdata_source in ('codex', 'ali213'):
                achieved_json = player_achsfile.read()
                achieved_json = convert_achs_format(achieved_json, achdata_source)
            elif achdata_source == 'sse':
                achieved_json = player_achsfile.read()
                achieved_json = convert_achs_format(achieved_json, achdata_source, achs_crc32)
    except FileNotFoundError:
        pass
else:
    steam_req = send_steam_request('GetPlayerAchievements', f"https://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v0001/?appid={appid}&key={stg['api_key']}&steamid={source_extra}")
    if steam_req != None:
        achieved_json = steam_req['playerstats']['achievements']
        achieved_json = convert_achs_format(achieved_json, achdata_source)
    url_random += 1

stats = {}

try:
    with open(os.path.join('games', appid, 'stats.txt')) as statslist:
        statlines = statslist.read().split('\n')
        for line in statlines:
            linespl = line.split('=')
            if len(linespl) == 3:
                locinfo = {'source': achdata_source, 'appid': appid, 'name': linespl[0]}
                locinfo['source_extra'] = source_extra
                if achdata_source == 'sse':
                    locinfo['crc32'] = zlib.crc32(bytes(linespl[0], 'utf-8'))
                stats[linespl[0]] = Stat(locinfo, linespl[1], linespl[2], stg['delay_read_change'])
except FileNotFoundError:
    pass

if achdata_source == 'steam' and len(stats) > 0:
    steam_req = send_steam_request('GetUserStatsForGame', f"https://api.steampowered.com/ISteamUserStats/GetUserStatsForGame/v0002/?appid={appid}&key={stg['api_key']}&steamid={source_extra}")
    if steam_req != None:
        try:
            for s in steam_req['playerstats']['stats']:
                if s['name'] in stats.keys():
                    stats[s['name']].value = s['value']
        except KeyError:
            pass

achs = []
for ach in achs_json:
    achs.append(Achievement(ach, achieved_json, stats, stg))

achs_f, secrets_hidden = filter_achs(achs, state_filter, stg['hide_secrets'], stg['unlocks_on_top'])

ach_idxs = {}
ach_icons = {}
achs_unlocked = 0
languages_used = set()
if stg['hide_secrets'] or stg['notif_lock']:
    languages_used.add('english')
force_unlocks = {}
if stg['forced_keep'] == 'save':
    try:
        with open(f'{save_dir}/{appid}_force.json') as forcefile:
            force_unlocks = json.load(forcefile)
    except FileNotFoundError:
        pass
saved_tstamps = {}
if stg['save_timestamps']:
    try:
        with open(f'{save_dir}/{appid}_time.json') as timefile:
            saved_tstamps = json.load(timefile)
    except FileNotFoundError:
        pass

fu_change = False
ts_change = False
for i in range(len(achs)):
    ach_idxs[achs[i].name] = i
    try:
        if achs[i].icon != None and not achs[i].icon in ach_icons.keys():
            ach_icons[achs[i].icon] = pygame.image.load(os.path.join('games', appid, 'achievement_images', achs[i].icon))
    except pygame.error:
        pass
    try:
        if achs[i].icon_gray != None and not achs[i].icon_gray in ach_icons.keys():
            ach_icons[achs[i].icon_gray] = pygame.image.load(os.path.join('games', appid, 'achievement_images', achs[i].icon_gray))
    except pygame.error:
        pass
    languages_used.add(achs[i].language)
    if achs[i].name in force_unlocks.keys():
        if not achs[i].earned or achs[i].force_unlock:
            achs[i].earned = True
            achs[i].force_unlock = True
            achs[i].ts_first = None
            achs[i].ts_earliest = None
            achs[i].update_time(force_unlocks[achs[i].name])
        else:
            force_unlocks.pop(achs[i].name)
            fu_change = True
    if achs[i].force_unlock and not achs[i].name in force_unlocks:
        force_unlocks[achs[i].name] = achs[i].earned_time
        fu_change = True
    if achs[i].earned:
        achs_unlocked += 1
    if achs[i].name in saved_tstamps.keys():
        if not stg['savetime_keep_locked'] and not achs[i].earned:
            ts_change = max(ts_change, saved_tstamps[achs[i].name]['first'] != None or saved_tstamps[achs[i].name]['earliest'] != None)
            saved_tstamps[achs[i].name]['first'] = None
            saved_tstamps[achs[i].name]['earliest'] = None
        if saved_tstamps[achs[i].name]['first'] != None:
            achs[i].ts_first = saved_tstamps[achs[i].name]['first']
        elif achs[i].earned:
            saved_tstamps[achs[i].name]['first'] = achs[i].earned_time
            ts_change = True
        if saved_tstamps[achs[i].name]['earliest'] != None:
            if not achs[i].earned or saved_tstamps[achs[i].name]['earliest'] < achs[i].earned_time:
                achs[i].ts_earliest = saved_tstamps[achs[i].name]['earliest']
            elif achs[i].earned_time < saved_tstamps[achs[i].name]['earliest']:
                saved_tstamps[achs[i].name]['earliest'] = achs[i].ts_earliest
                ts_change = True
        elif achs[i].earned:
            saved_tstamps[achs[i].name]['earliest'] = achs[i].earned_time
            ts_change = True
    else:
        saved_tstamps[achs[i].name] = {}
        saved_tstamps[achs[i].name]['first'] = achs[i].ts_first
        saved_tstamps[achs[i].name]['earliest'] = achs[i].ts_earliest
        ts_change = True

if fu_change and stg['forced_keep'] == 'save':
    if not os.path.isdir(save_dir):
        os.makedirs(save_dir)
    with open(f'{save_dir}/{appid}_force.json', 'w') as forcefile:
        json.dump(force_unlocks, forcefile)
if ts_change and stg['save_timestamps']:
    if not os.path.isdir(save_dir):
        os.makedirs(save_dir)
    with open(f'{save_dir}/{appid}_time.json', 'w') as timefile:
        json.dump(saved_tstamps, timefile)
if (fu_change or ts_change) and isinstance(source_extra, str) and source_extra[:5] == 'path:':
    with open(f'{save_dir}/path.txt', 'w') as pathfile:
        pathfile.write(source_extra[5:])

for i in ach_icons.keys():
    size = (ach_icons[i].get_width(), ach_icons[i].get_height())
    if size != (64, 64):
        if stg['smooth_scale']:
            ach_icons[i] = pygame.transform.smoothscale(ach_icons[i].convert_alpha(), (64, 64))
        else:
            ach_icons[i] = pygame.transform.scale(ach_icons[i], (64, 64))

ach_icons['hidden_dummy_ach_icon'] = pygame.image.load('images/hidden.png')

font_general = pygame.font.Font(os.path.join('fonts', stg['font_general']), int(stg['font_size_general']))
font_achs_regular = {}
font_achs_small = {}
long_hidden_desc = {}
for l in languages_used:
    try:
        font_names = [None, None]
        if l in stg['font_achs'].keys():
            font_names[0] = stg['font_achs'][l]
        else:
            font_names[0] = stg['font_achs']['all']
        if l in stg['font_achs_desc'].keys():
            font_names[1] = stg['font_achs_desc'][l]
        elif 'all' in stg['font_achs_desc'].keys():
            font_names[1] = stg['font_achs_desc']['all']
        else:
            font_names[1] = font_names[0]

        font_sizes = [None, None]
        if font_names[0] in stg['font_size_regular'].keys():
            font_sizes[0] = stg['font_size_regular'][font_names[0]]
        elif 'all' in stg['font_size_regular'].keys():
            font_sizes[0] = stg['font_size_regular']['all']
        if font_names[1] in stg['font_size_small'].keys():
            font_sizes[1] = stg['font_size_small'][font_names[1]]
        elif 'all' in stg['font_size_small'].keys():
            font_sizes[1] = stg['font_size_small']['all']
        font_achs_regular[l] = pygame.font.Font(os.path.join('fonts', font_names[0]), int(font_sizes[0]))
        font_achs_small[l] = pygame.font.Font(os.path.join('fonts', font_names[1]), int(font_sizes[1]))
        long_hidden_desc[l] = multiline_text(None, 2, stg['font_line_distance_small'], stg['window_size_x'] - 94, font_achs_small[l], stg['hidden_desc'], None, (0, 0, 0), True)
    except FileNotFoundError:
        print(f'Font file not found ({l})')
        sys.exit()

for ach in achs:
    if ach.has_desc:
        ach.long_desc = multiline_text(None, 2, stg['font_line_distance_small'], stg['window_size_x'] - 94, font_achs_small[ach.language], ach.description_l, None, (0, 0, 0), True)

hover_ach = None
running = True
flip_required = True
last_update = time.time()
fchecker_achieved_locinfo = {'source': achdata_source, 'appid': appid}
fchecker_achieved_locinfo['source_extra'] = source_extra
fchecker_achieved = None
if achdata_source != 'steam':
    fchecker_achieved = FileChecker('player_achs', fchecker_achieved_locinfo, stg['delay_read_change'])
stats_delay_counter = 0
mouse_scrolling = False

draw_achs()

while running:
    notifications_sent = 0
    notifications_hidden = 0
    fu_change = False
    ts_change = False

    unread_default = 1
    if viewing == 'history':
        unread_default = 2
    if not stg['history_unread']:
        unread_default = 0

    if time.time() >= last_update + stg['delay']:
        last_update = time.time()

        if stg['delay_stats'] > 1:
            stats_delay_counter += 1

        if achdata_source != 'steam':
            changed, newdata = fchecker_achieved.check()
        elif len(achs) > 0:
            changed = False
            steam_req = send_steam_request('GetPlayerAchievements', f"https://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v0001/?appid={appid}&key={stg['api_key']}&steamid={source_extra}")
            if steam_req != None:
                changed = True
                newdata = steam_req['playerstats']['achievements']
        
        if changed:
            
            if achdata_source != 'goldberg' and newdata != None:
                newdata = convert_achs_format(newdata, achdata_source, achs_crc32)

            achs, changes = update_achs(achs, newdata, fchecker_achieved, stg)
            achs_f, secrets_hidden = filter_achs(achs, state_filter, stg['hide_secrets'], stg['unlocks_on_top'])

            lock_all_notified = False
            for change in changes:
                if change['type'] == 'unlock':
                    achs_unlocked += 1
                    if change['was_forced']:
                        force_unlocks.pop(change['ach_api'], None)
                    history.insert(0, {'type': 'unlock', 'ach': achs[ach_idxs[change['ach_api']]], 'time_real': change['time_real'], 'time_action': change['time_action'], 'unread': unread_default})
                    if stg['notif'] and not change['was_forced']:
                        if notifications_sent < stg['notif_limit'] or stg['notif_limit'] == 0:
                            send_notification('Achievement Unlocked!', change['ach'], f"games/{appid}/achievement_images/{achs[ach_idxs[change['ach_api']]].icon}")
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
                                    send_notification('Achievement Locked', change['ach'], f"games/{appid}/achievement_images/{achs[ach_idxs[change['ach_api']]].icon_gray}")
                                    notifications_sent += 1
                                else:
                                    notifications_hidden += 1
                        elif not lock_all_notified:
                            history.insert(0, {'type': 'lock_all', 'time_real': change['time_real'], 'time_action': change['time_action'], 'unread': unread_default})
                            if stg['notif']:
                                if notifications_sent < stg['notif_limit'] or stg['notif_limit'] == 0:
                                    send_notification('All achievements locked', 'Achievement data not found', 'images/lock_all.png')
                                    notifications_sent += 1
                                else:
                                    notifications_hidden += 1
                            lock_all_notified = True
                elif change['type'] == 'progress_report':
                    history.insert(0, {'type': 'progress_report', 'value': change['value'], 'ach': achs[ach_idxs[change['ach_api']]], 'time_real': change['time_real'], 'time_action': change['time_action'], 'unread': unread_default})
                    if stg['notif']:
                        if notifications_sent < stg['notif_limit'] or stg['notif_limit'] == 0:
                            send_notification('Achievement Progress', f"{change['ach']} ({change['value'][0]}/{change['value'][1]})", f"games/{appid}/achievement_images/{achs[ach_idxs[change['ach_api']]].icon_gray}")
                            notifications_sent += 1
                        else:
                            notifications_hidden += 1
                if 'ts_change' in change.keys():
                    ts_change = max(ts_change, change['ts_change'])
            if notifications_hidden > 0:
                send_notification('Too many notifications', f'{notifications_hidden} more notification(s) were hidden')
            flip_required = True

        if stg['delay_stats'] <= 1 or stats_delay_counter >= stg['delay_stats']:
            stats_delay_counter = 0
            stats_changed = False
            if achdata_source != 'steam':
                for stat in stats.values():
                    if stat.update_val():
                        stats_changed = True
            elif len(stats) > 0:
                steam_req = send_steam_request('GetUserStatsForGame', f"https://api.steampowered.com/ISteamUserStats/GetUserStatsForGame/v0002/?appid={appid}&key={stg['api_key']}&steamid={source_extra}")
                if steam_req != None:
                    try:
                        for s in steam_req['playerstats']['stats']:
                            if s['name'] in stats.keys():
                                if stats[s['name']].value != s['value']:
                                    stats_changed = True
                                    stats[s['name']].value = s['value']
                    except KeyError:
                        pass

            if stats_changed:
                flip_required = True
                for ach in achs:
                    if ach.progress != None and ach.progress.support:
                        ach.progress.calculate(stats)

                        if stg['bar_force_unlock']:
                            # actual_value = ach.progress.current_value
                            # if stg['bar_ignore_min'] or ach.progress.min_val == ach.progress.max_val:
                                # actual_value = ach.progress.real_value
                            if ach.progress.real_value >= ach.progress.max_val and not ach.earned:
                                ach.earned = True
                                ts_change = max(ts_change, ach.update_time(stats[ach.progress.value['operand1']].fchecker.last_check))
                                ach.force_unlock = True
                                force_unlocks[ach.name] = ach.earned_time
                                fu_change = True
                                achs_unlocked += 1
                                time_real = datetime.now().strftime('%d %b %Y %H:%M:%S')
                                if achdata_source != 'steam':
                                    time_action = datetime.fromtimestamp(stats[ach.progress.value['operand1']].fchecker.last_check)
                                    time_action = time_action.strftime('%d %b %Y %H:%M:%S')
                                else:
                                    time_action = time_real
                                if stg['forced_mark']:
                                    time_real += ' (F)'
                                    time_action += ' (F)'
                                history.insert(0, {'type': 'unlock', 'ach': ach, 'time_real': datetime.now().strftime('%d %b %Y %H:%M:%S (F)'), 'time_action': time_action, 'unread': unread_default})
                                if stg['notif']:
                                    if notifications_sent < stg['notif_limit'] or stg['notif_limit'] == 0:
                                        send_notification('Achievement Unlocked!', ach.display_name_l, f"games/{appid}/achievement_images/{ach.icon}")
                                        notifications_sent += 1
                                    else:
                                        notifications_hidden += 1
                            elif ach.progress.real_value < ach.progress.max_val and ach.force_unlock and stg['forced_keep'] == 'no':
                                ach.earned = False
                                ach.earned_time = 0.0
                                ach.force_unlock = False
                                force_unlocks.pop(ach.name, None)
                                fu_change = True
                                if not stg['savetime_keep_locked']:
                                    ach.ts_first = None
                                    ach.ts_earliest = None
                                    ts_change = True
                                achs_unlocked -= 1
                                if stg['notif_lock']:
                                    time_real = datetime.now().strftime('%d %b %Y %H:%M:%S')
                                    if achdata_source != 'steam':
                                        time_action = datetime.fromtimestamp(stats[ach.progress.value['operand1']].fchecker.last_check)
                                        time_action = time_action.strftime('%d %b %Y %H:%M:%S')
                                    else:
                                        time_action = time_real
                                    if stg['forced_mark']:
                                        time_real += ' (F)'
                                        time_action += ' (F)'
                                    history.insert(0, {'type': 'lock', 'ach': ach, 'time_real': datetime.now().strftime('%d %b %Y %H:%M:%S (F)'), 'time_action': time_action, 'unread': unread_default})
                                    if stg['notif']:
                                        if notifications_sent < stg['notif_limit'] or stg['notif_limit'] == 0:
                                            send_notification('Achievement Locked', ach.display_name_l, f"games/{appid}/achievement_images/{ach.icon_gray}")
                                            notifications_sent += 1
                                        else:
                                            notifications_hidden += 1

        if fu_change and stg['forced_keep'] == 'save':
            if not os.path.isdir(save_dir):
                os.makedirs(save_dir)
            with open(f'{save_dir}/{appid}_force.json', 'w') as forcefile:
                json.dump(force_unlocks, forcefile)
        if ts_change and stg['save_timestamps']:
            for a in saved_tstamps.keys():
                if a in ach_idxs.keys():
                    saved_tstamps[a]['first'] = achs[ach_idxs[a]].ts_first
                    saved_tstamps[a]['earliest'] = achs[ach_idxs[a]].ts_earliest
            if not os.path.isdir(save_dir):
                os.makedirs(save_dir)
            with open(f'{save_dir}/{appid}_time.json', 'w') as timefile:
                json.dump(saved_tstamps, timefile)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                if viewing == 'achs':
                    scroll += 1
                elif viewing == 'stats':
                    scroll_stats += 1
                elif viewing == 'history':
                    scroll_history += 1
                flip_required = True
            elif event.key == pygame.K_UP:
                if viewing == 'achs':
                    scroll -= 1
                elif viewing == 'stats':
                    scroll_stats -= 1
                if viewing == 'history':
                    scroll_history -= 1
                flip_required = True
            elif event.key == pygame.K_PAGEUP:
                if viewing == 'achs':
                    scroll -= achs_to_show
                elif viewing == 'stats':
                    scroll_stats -= stats_to_show
                if viewing == 'history':
                    scroll_history -= achs_to_show
                flip_required = True
            elif event.key == pygame.K_PAGEDOWN:
                if viewing == 'achs':
                    scroll += achs_to_show
                elif viewing == 'stats':
                    scroll_stats += stats_to_show
                if viewing == 'history':
                    scroll_history += achs_to_show
                flip_required = True

        elif event.type == pygame.MOUSEMOTION:
            if viewing == 'achs' or viewing == 'history':
                old_hover_ach = hover_ach
                hover_ach = None
                for i in range(achs_to_show):
                    if pygame.Rect(10, header_h + i * 74, stg['window_size_x'] - 20, 64).collidepoint(event.pos):
                        hover_ach = i
                        break
                if hover_ach != old_hover_ach:
                    flip_required = True

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if viewing == 'achs':
                if len(achs_f) > achs_to_show and event.pos[0] >= stg['window_size_x'] - 10 and event.pos[1] >= header_h:
                    mouse_scrolling = True
                elif pygame.Rect(stg['window_size_x'] - 164, 10, 76, 22).collidepoint(event.pos):
                    state_filter += 1
                    if state_filter > 2:
                        state_filter = 0
                    achs_f, secrets_hidden = filter_achs(achs, state_filter, stg['hide_secrets'], stg['unlocks_on_top'])
                    scroll = 0
                elif pygame.Rect(stg['window_size_x'] - 78, 10, 68, 22).collidepoint(event.pos):
                    viewing = 'stats'
                elif pygame.Rect(stg['window_size_x'] - 264, 10, 90, 22).collidepoint(event.pos) and stg['history_length'] != -1:
                    viewing = 'history'
            elif viewing == 'stats':
                if pygame.Rect(stg['window_size_x'] - 78, 10, 68, 22).collidepoint(event.pos):
                    viewing = 'achs'
                if len(stats) > stats_to_show and event.pos[0] >= stg['window_size_x'] - 10 and event.pos[1] >= header_h:
                    mouse_scrolling = True
            elif viewing == 'history':
                if len(history) > achs_to_show and event.pos[0] >= stg['window_size_x'] - 10 and event.pos[1] >= header_h:
                    mouse_scrolling = True
                elif pygame.Rect(stg['window_size_x'] - 64, 10, 54, 22).collidepoint(event.pos):
                    for entry in history:
                        entry['unread'] = 0
                    scroll_history = 0
                    viewing = 'achs'
                elif pygame.Rect(stg['window_size_x'] - 138, 10, 64, 22).collidepoint(event.pos):
                    scroll_history = 0
                    history = []
            flip_required = True

        elif event.type == pygame.MOUSEBUTTONUP:
            mouse_scrolling = False

        elif event.type == pygame.MOUSEWHEEL:
            if viewing == 'achs':
                scroll -= event.y
            elif viewing == 'stats':
                scroll_stats -= event.y
            elif viewing == 'history':
                scroll_history -= event.y
            flip_required = True

    y = pygame.mouse.get_pos()[1]
    if viewing == 'achs':
        if mouse_scrolling:
            scroll = (y - header_h) * (len(achs_f) - achs_to_show) // (stg['window_size_y'] - header_h)
            flip_required = True
        if scroll > len(achs_f) - achs_to_show:
            scroll = len(achs_f) - achs_to_show
        if scroll < 0:
            scroll = 0
    elif viewing == 'stats':
        if mouse_scrolling:
            scroll_stats = (y - header_h) * (len(stats) - stats_to_show) // (stg['window_size_y'] - header_h)
            flip_required = True
        if scroll_stats > len(stats) - stats_to_show:
            scroll_stats = len(stats) - stats_to_show
        if scroll_stats < 0:
            scroll_stats = 0
    elif viewing == 'history':
        if mouse_scrolling:
            scroll_history = (y - header_h) * (len(history) - achs_to_show) // (stg['window_size_y'] - header_h)
            flip_required = True
        if scroll_history > len(history) - achs_to_show:
            scroll_history = len(history) - achs_to_show
        if scroll_history < 0:
            scroll_history = 0

    while stg['history_length'] != 0 and len(history) > stg['history_length'] and len(history) > 0:
        history.pop(-1)

    if flip_required:
        if viewing == 'achs':
            draw_achs()
        elif viewing == 'stats':
            draw_stats()
        elif viewing == 'history':
            draw_history()
        flip_required = False

    time.sleep(stg['delay_sleep'])