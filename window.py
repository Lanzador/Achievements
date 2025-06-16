import os
import sys
import platform
import json
import time
import zlib
import threading
import shutil
from random import randint
from datetime import datetime
import pygame
import requests
import pyperclip
from PIL import Image as PILimg
from showtext import *
from achievements import *
from stats import *
from filechanges import *
from settings import *

if platform.uname().system == 'Linux':
    from gi import require_version
    require_version('Notify', '0.7')
    from gi.repository import Notify
    from atexit import register as register_exit
    os.environ['SDL_VIDEO_X11_NET_WM_BYPASS_COMPOSITOR'] = '0'
    Notify.init('Init')
    @register_exit
    def goodbye():
        Notify.uninit()
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
    p = os.path.join(icons_path, 'ico', name + '.ico')
    if not os.path.isfile(p):
        p = f"games/{appid}/{name}.ico"
        img = PILimg.open(os.path.join(icons_path, name))
        img.save(p)
        threading.Timer(2, os.remove, (p, )).start()
    return p

def send_notification(title, message, icon=None):
    kwargs = {
        'app_name': gamename,
        'title': title,
        'message': message,
        'timeout': stg['notif_timeout']
    }

    if platform.uname().system == 'Windows':
        if icon != None and ach_icons[icon] != None:
            try:
                if os.path.isdir(f'games/{appid}'):
                    kwargs['app_icon'] = convert_ico(icon)
            except Exception:
                pass
        return notification.notify(**kwargs)

    app_icon = os.path.join(icons_path, icon)

    if platform.uname().system == 'Linux':
        Notify.set_app_name(gamename)
        if icon != None and ach_icons[icon] != None:
            linux_notification = Notify.Notification.new(title,message,os.path.abspath(app_icon))
        else:
            linux_notification = Notify.Notification.new(title,message)
        # Set urgency to display notification on top of fullscreen apps
        linux_notification.set_urgency(Notify.Urgency.CRITICAL)
        if stg['notif_timeout'] > 0:
            threading.Timer(stg['notif_timeout'], linux_notification.close).start()
        return linux_notification.show()
    else:
        if icon != None and ach_icons[icon] != None:
            kwargs['app_icon'] = app_icon
        return notification.notify(**kwargs)

def send_steam_request(name, link):
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
    except Exception as ex:
        print(f'Unhandled request error: {type(ex).__name__} ({name})')
    return None

def draw_image_bar(x, y, w, img):
    iw = img.get_width()
    for i in range(w // iw):
        screen.blit(img, (x + iw * i, y))
    r = w % iw
    if r > 0:
        screen.blit(img, (x + w - r, y), (0, 0, r, img.get_height()))

def draw_progressbar(x, y, w, h, p1, p2):
    if w <= 0:
        return
    if p1 > p2:
        p1 = p2
    if stg['bar_images']:
        draw_image_bar(x, y, w, barimagebg)
        if p2 != 0:
            img = barimagefill
            if p1 == p2:
                img = barimagecompleted
            draw_image_bar(x, y, p1 * w // p2, img)
    else:
        pygame.draw.rect(screen, stg['color_bar_bg'], pygame.Rect(x, y, w, h))
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
    t = gamename
    if header_extra == 'search' or search_request != '':
        t = f'Search: {search_request}'
    if (stg['gamebar_position'] != 'repname' or header_extra[:6] == 'search') and max_name_length > 0:
        ty = 10
        if stg['gamebar_position'] in ('under', 'hide') and stg['font_size_general'] <= 22:
            ty += round((22 - stg['font_size_general']) / 2)
        long_text(screen, max_name_length, font_general, t, (10, ty), stg['color_text'])
    if stg['gamebar_position'] == 'hide':
        return
    if stg['gamebar_position'] == 'repname' and header_extra[:6] == 'search':
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

    if viewing == 'achs':
        if header_extra == 'search':
            draw_game_progress(stg['window_size_x'] - 148)
            screen.blit(xbutton, (stg['window_size_x'] - 128, 10))
            screen.blit(upbutton, (stg['window_size_x'] - 96, 10))
            screen.blit(downbutton, (stg['window_size_x'] - 64, 10))
            screen.blit(listbutton, (stg['window_size_x'] - 32, 10))
        elif header_extra == 'search_results':
            draw_game_progress(btn_locs['filter_search'][state_filter].topleft[0] - 20)
            screen.blit(filter_buttons[state_filter], btn_locs['filter_search'][state_filter])
            screen.blit(xbutton, (stg['window_size_x'] - 32, 10))
        elif header_extra == 'sort':
            draw_game_progress(stg['window_size_x'] - 180)
            screen.blit(secretsbutton, (stg['window_size_x'] - 160, 10))
            screen.blit(percentsortbutton[stg['sort_by_rarity']], (stg['window_size_x'] - 128, 10))
            screen.blit(uotbutton[stg['unlocks_on_top']], (stg['window_size_x'] - 96, 10))
            screen.blit(timesortbutton[stg['unlocks_timesort']], (stg['window_size_x'] - 64, 10))
            screen.blit(xbutton, (stg['window_size_x'] - 32, 10))
        elif header_extra == 'secrets':
            draw_game_progress(stg['window_size_x'] - 180)
            screen.blit(secretsLHbutton[stg['secrets_listhide']], (stg['window_size_x'] - 160, 10))
            screen.blit(secretsNbutton[stg['secrets'] == 'normal'], (stg['window_size_x'] - 128, 10))
            screen.blit(secretsHbutton[stg['secrets'] == 'hide'], (stg['window_size_x'] - 96, 10))
            screen.blit(secretsBbutton[stg['secrets'] == 'bottom'], (stg['window_size_x'] - 64, 10))
            screen.blit(xbutton, (stg['window_size_x'] - 32, 10))
        elif header_extra == 'secrets_reveal':
            draw_game_progress(stg['window_size_x'] - 84)
            screen.blit(hidebutton[hide_all_secrets], (stg['window_size_x'] - 96, 10))
            screen.blit(revealbutton[reveal_secrets], (stg['window_size_x'] - 64, 10))
            screen.blit(xbutton, (stg['window_size_x'] - 32, 10))
        else:
            if stg['history_length'] > -1:
                draw_game_progress(btn_locs['history'][state_filter].topleft[0] - 20)
                screen.blit(historybutton, btn_locs['history'][state_filter])
                if len(history) > 0 and history[0]['unread'] == 1:
                    screen.blit(unreadicon, (btn_locs['filter'][state_filter].topleft[0] - 18, 24))
            else:
                draw_game_progress(btn_locs['filter'][state_filter].topleft[0] - 20)
            screen.blit(filter_buttons[state_filter], btn_locs['filter'][state_filter])
            screen.blit(statsbutton, btn_locs['stats'])
    if viewing == 'history_unlocks':
        # draw_game_progress(stg['window_size_x'] - 182)
        draw_game_progress(btn_locs['back'].topleft[0] - 20)
        screen.blit(backbutton, btn_locs['back'])
        # screen.blit(notifsbutton, (stg['window_size_x'] - 162, 10))

    if len(achs_f) == 0:
        show_text(screen, font_general, 'No achievements found', (10, header_h), stg['color_text'])
                
    for i in range(scroll, scroll + achs_to_show + 1):
        if i >= len(achs_f):
            break

        font_regular = font_achs_regular[achs_f[i].language]
        font_small = font_achs_small[achs_f[i].language_d]

        bar_length = stg['bar_length']

        can_show_desc = not achs_f[i].hidden or (achs_f[i].earned and not hide_all_secrets) or reveal_secrets
        long_desc = (can_show_desc and achs_f[i].long_desc) or (not can_show_desc and long_hidden_desc[achs_f[i].language_d])

        if achs_f[i].progress != None:
            bar_hidden_unlock = stg['bar_unlocked'] == 'hide' and achs_f[i].earned
            bar_hidden_unsup = stg['bar_hide_unsupported'] == 'all' and not achs_f[i].progress.support
            bar_hidden_unsup_st = stg['bar_hide_unsupported'] == 'stat' and not achs_f[i].progress.support_error in (None, "Unknown stat")
            bar_hidden_secret = stg['bar_hide_secret'] and not can_show_desc
            bar_shown = not (bar_hidden_unlock or bar_hidden_unsup or bar_hidden_unsup_st or bar_hidden_secret)
        else:
            bar_shown = False

        hovered_over = hover_ach == i - scroll
        hide_bar_and_time = hovered_over and long_desc

        reveal_icon = stg['reveal_icons_hover'] and can_show_desc and hovered_over
        reveal_icon = reveal_icon or (stg['reveal_icons_revsecr'] != 'never' and reveal_secrets and (hovered_over or stg['reveal_icons_revsecr'] == 'always'))

        desc_max_lines = 3
        if bar_shown or (achs_f[i].earned and stg['show_timestamps']):
            desc_max_lines = 2
        if hovered_over:
            desc_max_lines = 3

        achbg_color = None
        ach_text_color = None
        if achs_f[i].earned:
            if achs_f[i].rare:
                achbg_color = stg['color_achbg_rare']
                ach_text_color = stg['color_text_rare']
            else:
                achbg_color = stg['color_achbg_unlock']
                ach_text_color = stg['color_text_unlock']
        else:
            if achs_f[i].rare:
                achbg_color = stg['color_achbg_rare_lock']
                ach_text_color = stg['color_text_rare_lock']
            else:
                achbg_color = stg['color_achbg_lock']
                ach_text_color = stg['color_text_lock']
        if hovered_over:
            if stg['color_achbg_hover'] != None:
                achbg_color = stg['color_achbg_hover']
            if stg['color_text_hover'] != None:
                ach_text_color = stg['color_text_hover']

        time_color = ach_text_color
        time_font = font_regular
        if stg['color_time_general']:
            time_color = stg['color_text']
        if stg['font_time_general']:
            time_font = font_general

        if achbg_color != None:
            max_val = 100.0
            if stg['achbg_rarity_relative']:
                max_val = max_rarity
            length = stg['window_size_x'] - 84 - stg['frame_size']
            if (stg['achbg_rarity'] == 'yes' or (stg['achbg_rarity'] == 'sort' and stg['sort_by_rarity'] and viewing == 'achs')) and achs_f[i].rarity != -1.0:
                length = achs_f[i].rarity * (stg['window_size_x'] - 84 - stg['frame_size']) / max_val
            pygame.draw.rect(screen, achbg_color, pygame.Rect(74 + stg['frame_size'], header_h + (i - scroll) * 74 - stg['frame_size'], length, 64 + stg['frame_size'] * 2))

        if stg['secrets_listhide'] and not can_show_desc:
            long_text(screen, stg['window_size_x'] - 94, font_regular, stg['hidden_title'], (84, header_h + (i - scroll) * 74), ach_text_color)
        else:
            long_text(screen, stg['window_size_x'] - 94, font_regular, achs_f[i].display_name_l, (84, header_h + (i - scroll) * 74), ach_text_color)
        if not can_show_desc:
            multiline_text(screen, desc_max_lines, stg['font_line_distance_small'], stg['window_size_x'] - 94, font_small, stg['hidden_desc'], (84, header_h + 17 + (i - scroll) * 74), ach_text_color)
        elif achs_f[i].has_desc:
            multiline_text(screen, desc_max_lines, stg['font_line_distance_small'], stg['window_size_x'] - 94, font_small, achs_f[i].description_l, (84, header_h + 17 + (i - scroll) * 74), ach_text_color)

        prg_str_len = 0
        if bar_shown and not hide_bar_and_time:
            if achs_f[i].progress.support:
                if not (stg['bar_unlocked'] in ('full', 'zerolen') and achs_f[i].earned):
                    prg_val = achs_f[i].progress.current_value
                    prg_no_min = achs_f[i].progress.get_without_min()
                    if prg_no_min[1] == 0:
                        prg_no_min = (0, 1)
                    if stg['bar_ignore_min']:
                        prg_val = achs_f[i].progress.real_value
                        prg_no_min = (prg_val, achs_f[i].progress.max_val)
                else:
                    prg_val = achs_f[i].progress.max_val
                    prg_no_min = (1, 1)
                prg_str = f'{round_down(prg_val, 2)}/{achs_f[i].progress.max_val}'
                if stg['bar_percentage'] != 'no':
                    bar_percentage = round_down(prg_no_min[0] / prg_no_min[1] * 100, 1) + '%'
                    if stg['bar_percentage'] == 'show':
                        prg_str += f' ({bar_percentage})'
                    else:
                        prg_str = bar_percentage
            else:
                prg_str = achs_f[i].progress.support_error
                prg_no_min = (0, 1)
                if stg['bar_unlocked'] in ('full', 'zerolen') and achs_f[i].earned:
                    prg_no_min = (1, 1)
            prg_str_len = time_font.size(prg_str)[0]

        if achs_f[i].earned:
            if stg['bar_unlocked'] == 'zerolen':
                bar_length = -10

            if stg['frame_size'] > 0:
                frame_color = stg['frame_color_unlock']
                if achs_f[i].rare:
                    frame_color = stg['frame_color_rare']
                if hovered_over and stg['frame_color_hover'] != None:
                    frame_color = stg['frame_color_hover']
                pygame.draw.rect(screen, frame_color, pygame.Rect(10 - stg['frame_size'], header_h - stg['frame_size'] + (i - scroll) * 74, 64 + stg['frame_size'] * 2, 64 + stg['frame_size'] * 2))
            if stg['secrets_listhide'] and not can_show_desc:
                screen.blit(hiddenunlockicon, (10, header_h + (i - scroll) * 74))
            elif achs_f[i].icon != None and ach_icons[achs_f[i].icon] != None:
                screen.blit(ach_icons[achs_f[i].icon], (10, header_h + (i - scroll) * 74))
            else:
                pygame.draw.rect(screen, stg['color_background'], pygame.Rect(10, header_h + (i - scroll) * 74, 64, 64))
            if stg['show_timestamps'] and not hide_bar_and_time:
                if bar_shown:
                    show_text(screen, time_font, achs_f[i].get_time(stg), (bar_length + 104 + prg_str_len, header_h + 49 + (i - scroll) * 74), time_color)
                else:
                    show_text(screen, time_font, achs_f[i].get_time(stg), (84, header_h + 49 + (i - scroll) * 74), time_color)

            # ach_time = achs_f[i].get_time()
            # show_text(screen, font_regular, ach_time, (790 - font_regular.size(ach_time)[0] , 107 + (i - scroll) * 74))

            # ach_time = achs_f[i].get_time()
            # ach_time_len = font_regular.size(ach_time)
            # rrect = pygame.Rect(0, 0, ach_time_len[0], ach_time_len[1])
            # rrect.midright = (790, 90 + (i - scroll) * 74)
            # show_text(screen, font_regular, ach_time, rrect)

        else:
            if stg['frame_size'] > 0:
                frame_color = stg['frame_color_lock']
                if achs_f[i].rare:
                    frame_color = stg['frame_color_rare_lock']
                if hovered_over and stg['frame_color_hover'] != None:
                    frame_color = stg['frame_color_hover']
                pygame.draw.rect(screen, frame_color, pygame.Rect(10 - stg['frame_size'], header_h - stg['frame_size'] + (i - scroll) * 74, 64 + stg['frame_size'] * 2, 64 + stg['frame_size'] * 2))
            if stg['secrets_listhide'] and not can_show_desc:
                screen.blit(hiddenlockicon, (10, header_h + (i - scroll) * 74))
            elif reveal_icon and achs_f[i].icon != None and ach_icons[achs_f[i].icon] != None:
                screen.blit(ach_icons[achs_f[i].icon], (10, header_h + (i - scroll) * 74))
            elif achs_f[i].icon_gray != None and ach_icons[achs_f[i].icon_gray] != None:
                screen.blit(ach_icons[achs_f[i].icon_gray], (10, header_h + (i - scroll) * 74))
            else:
                pygame.draw.rect(screen, stg['color_background'], pygame.Rect(10, header_h + (i - scroll) * 74, 64, 64))
            if stg['show_timestamps'] and stg['savetime_show_locked'] and stg['savetime_shown'] != 'normal' and achs_f[i].get_ts(stg['savetime_shown']) != None and not hide_bar_and_time:
                if bar_shown:
                    show_text(screen, time_font, achs_f[i].get_time(stg), (bar_length + 104 + prg_str_len, header_h + 49 + (i - scroll) * 74), time_color)
                else:
                    show_text(screen, time_font, achs_f[i].get_time(stg), (84, header_h + 49 + (i - scroll) * 74), time_color)

        if achs_f[i].progress != None and not hide_bar_and_time and bar_shown:
            draw_progressbar(84, header_h + 51 + (i - scroll) * 74, bar_length, 13, prg_no_min[0], prg_no_min[1])
            show_text(screen, time_font, prg_str, (bar_length + 94, header_h + 49 + (i - scroll) * 74), time_color)

    if len(achs_f) > achs_to_show:
        draw_scrollbar(scroll, len(achs_f) - achs_to_show, len(achs_f) * 74 - 10)

    pygame.display.flip()

def draw_stats():
    screen.fill(stg['color_background'])

    draw_game_progress(btn_locs['achs'].topleft[0] - 20)
    screen.blit(achsbutton, btn_locs['achs'])

    if len(stats) == 0:
        show_text(screen, font_general, 'No stats found', (10, header_h), stg['color_text'])

    already_shown = 0 - scroll_stats
    for stat in stats.values():
        if already_shown >= 0:
            value = str(stat.value)
            if stat.inc_only and stat.value != stat.real_value:
                value += ' (*)'
            if stat.type in ('avgrate', 'avgrate_st'):
                value += ' (A)'
            short_name = long_text(screen, stg['window_size_x'] - 20 - font_general.size(f' = {value}')[0], font_general, stat.dname, None, None, True)
            show_text(screen, font_general, f'{short_name} = {value}', (10, header_h + already_shown * stg['font_line_distance_regular']), stg['color_text'])
        already_shown += 1
        if already_shown == stats_to_show + 1:
            break

    if len(stats) > stats_to_show:
        draw_scrollbar(scroll_stats, len(stats) - stats_to_show, len(stats) * stg['font_line_distance_regular'])

    pygame.display.flip()

def draw_history():
    screen.fill(stg['color_background'])

    draw_game_progress(btn_locs['history_unlocks'].topleft[0] - 20)
    screen.blit(backbutton, btn_locs['back'])
    screen.blit(clearbutton, btn_locs['clear'])
    screen.blit(unlocksbutton, btn_locs['history_unlocks'])

    if len(history) == 0:
        show_text(screen, font_general, 'History is empty', (10, header_h), stg['color_text'])

    for i in range(scroll_history, min(scroll_history + achs_to_show + 1, len(history))):

        if 'ach' in history[i]:
            font_regular = font_achs_regular[history[i]['ach'].language]
            font_small = font_achs_small[history[i]['ach'].language_d]
        else:
            font_regular = font_achs_regular['english']
            font_small = font_achs_small['english']

        hovered_over = hover_ach == i - scroll_history
        if 'ach' in history[i]:
            can_show_desc = not history[i]['ach'].hidden or (history[i]['type'] == 'unlock' and not hide_all_secrets) or reveal_secrets
            long_desc = (can_show_desc and history[i]['ach'].long_desc) or (not can_show_desc and long_hidden_desc[history[i]['ach'].language_d])
            hide_bar_and_time = hovered_over and long_desc

        desc_max_lines = 2
        if hovered_over or (not stg['show_timestamps'] and history[i]['type'] != 'progress_report'):
            desc_max_lines = 3

        unlock_colors = history[i]['type'] == 'unlock' or (history[i]['type'] == 'progress_report' and stg['color_progress_report'] == 'unlock')
        achbg_color = None
        ach_text_color = None
        frame_color = None
        if unlock_colors:
            if history[i]['ach'].rare:
                achbg_color = stg['color_achbg_rare']
                ach_text_color = stg['color_text_rare']
                frame_color = stg['frame_color_rare']
            else:
                frame_color = stg['frame_color_unlock']
                achbg_color = stg['color_achbg_unlock']
                ach_text_color = stg['color_text_unlock']
        else:
            if 'ach' in history[i] and history[i]['ach'].rare:
                achbg_color = stg['color_achbg_rare_lock']
                ach_text_color = stg['color_text_rare_lock']
                frame_color = stg['frame_color_rare_lock']
            else:
                achbg_color = stg['color_achbg_lock']
                ach_text_color = stg['color_text_lock']
                frame_color = stg['frame_color_lock']
        if hovered_over:
            if stg['color_achbg_hover'] != None:
                achbg_color = stg['color_achbg_hover']
            if stg['color_text_hover'] != None:
                ach_text_color = stg['color_text_hover']
            if stg['frame_color_hover'] != None:
                frame_color = stg['frame_color_hover']

        time_color = ach_text_color
        time_font = font_regular
        if stg['color_time_general']:
            time_color = stg['color_text']
        if stg['font_time_general']:
            time_font = font_general

        if history[i]['type'] != 'schema_change' and achbg_color != None:
            max_val = 100.0
            if stg['achbg_rarity_relative']:
                max_val = max_rarity
            length = stg['window_size_x'] - 84 - stg['frame_size']
            if stg['achbg_rarity'] == 'yes' and 'ach' in history[i] and history[i]['ach'].rarity != -1.0:
                length = history[i]['ach'].rarity * (stg['window_size_x'] - 84 - stg['frame_size']) / max_val
            pygame.draw.rect(screen, achbg_color, pygame.Rect(74 + stg['frame_size'], header_h + (i - scroll_history) * 74 - stg['frame_size'], length, 64 + stg['frame_size'] * 2))
        if stg['frame_size'] > 0:
            pygame.draw.rect(screen, frame_color, pygame.Rect(10 - stg['frame_size'], header_h - stg['frame_size'] + (i - scroll_history) * 74, 64 + stg['frame_size'] * 2, 64 + stg['frame_size'] * 2))
        
        if history[i]['type'] in ('unlock', 'lock'):
            if history[i]['type'] == 'unlock':
                icon = history[i]['ach'].icon
                t = 'Unlocked: '
            else:
                icon = history[i]['ach'].icon_gray
                t = 'Locked: '
            if icon != None and ach_icons[icon] != None:
                screen.blit(ach_icons[icon], (10, header_h + (i - scroll_history) * 74))
            else:
                pygame.draw.rect(screen, stg['color_background'], pygame.Rect(10, header_h + (i - scroll) * 74, 64, 64))
            long_text(screen, stg['window_size_x'] - 94, font_regular, t + history[i]['ach'].display_name_l, (84, header_h + (i - scroll_history) * 74), ach_text_color)
            if not can_show_desc:
                multiline_text(screen, desc_max_lines, stg['font_line_distance_small'], stg['window_size_x'] - 94, font_small, stg['hidden_desc'], (84, header_h + 17 + (i - scroll_history) * 74), ach_text_color)
            elif history[i]['ach'].has_desc:
                multiline_text(screen, desc_max_lines, stg['font_line_distance_small'], stg['window_size_x'] - 94, font_small, history[i]['ach'].description_l,
                              (84, header_h + 17 + (i - scroll_history) * 74), ach_text_color)
            if stg['show_timestamps'] and not hide_bar_and_time:
                show_text(screen, time_font, history[i]['time_' + stg['history_time']], (84, header_h + 49 + (i - scroll_history) * 74), time_color)
        elif history[i]['type'] == 'lock_all':
            screen.blit(lockallicon, (10, header_h + (i - scroll_history) * 74))
            long_text(screen, stg['window_size_x'] - 94, font_regular, 'All achievements locked', (84, header_h + (i - scroll_history) * 74), ach_text_color)
            multiline_text(screen, 3 - stg['show_timestamps'], stg['font_line_distance_small'], stg['window_size_x'] - 94, font_small, 'File containing achievement data was deleted',
                          (84, header_h + 17 + (i - scroll_history) * 74), ach_text_color)
            if stg['show_timestamps']:
                show_text(screen, time_font, history[i]['time_' + stg['history_time']], (84, header_h + 49 + (i - scroll_history) * 74), time_color)
        elif history[i]['type'] == 'progress_report':
            if history[i]['ach'].icon != None and ach_icons[history[i]['ach'].icon] != None:
                screen.blit(ach_icons[history[i]['ach'].icon_gray], (10, header_h + (i - scroll_history) * 74))
            else:
                pygame.draw.rect(screen, stg['color_background'], pygame.Rect(10, header_h + (i - scroll) * 74, 64, 64))

            color1 = stg['color_text_unlock']
            color2 = stg['color_text_lock']
            if history[i]['ach'].rare:
                if stg['color_text_rare'] != None:
                    color1 = stg['color_text_rare']
                if stg['color_text_rare_lock'] != None:
                    color2 = stg['color_text_rare_lock']
            if hovered_over and stg['color_text_hover'] != None:
                color1 = stg['color_text_hover']
                color2 = stg['color_text_hover']
            elif stg['color_progress_report'] == 'unlock':
                color2 = color1
            elif stg['color_progress_report'] == 'lock':
                color1 = color2

            progress_str = f"{history[i]['value'][0]}/{history[i]['value'][1]}"
            prg_str_len = time_font.size(progress_str)[0]
            title_str = long_text(screen, stg['window_size_x'] - 94 - font_regular.size(f' ({progress_str})')[0], font_regular, 'Progress: ' + history[i]['ach'].display_name_np, None, (255, 255, 255), True)
            show_text(screen, font_regular, f'{title_str} ({progress_str})', (84, header_h + (i - scroll_history) * 74), color1)

            if not can_show_desc:
                multiline_text(screen, desc_max_lines, stg['font_line_distance_small'], stg['window_size_x'] - 94, font_small, stg['hidden_desc'], (84, header_h + 17 + (i - scroll_history) * 74), color2)
            elif history[i]['ach'].has_desc:
                multiline_text(screen, desc_max_lines, stg['font_line_distance_small'], stg['window_size_x'] - 94, font_small, history[i]['ach'].description_l,
                              (84, header_h + 17 + (i - scroll_history) * 74), color2)

            if not stg['color_time_general']:
                time_color = color1

            if not hide_bar_and_time:
                draw_progressbar(84, header_h + 51 + (i - scroll_history) * 74, stg['bar_length'], 13, history[i]['value'][0], history[i]['value'][1])
                show_text(screen, time_font, progress_str, (stg['bar_length'] + 94, header_h + 49 + (i - scroll_history) * 74), time_color)
                if stg['show_timestamps']:
                    show_text(screen, time_font, history[i]['time_' + stg['history_time']], (stg['bar_length'] + 104 + prg_str_len, header_h + 49 + (i - scroll_history) * 74), time_color)
        elif history[i]['type'] == 'schema_change':
            screen.blit(schemachangeicon, (10, header_h + (i - scroll_history) * 74))
            long_text(screen, stg['window_size_x'] - 94, font_regular, 'Achievement list has changed', (84, header_h + (i - scroll_history) * 74), stg['color_text'])
            multiline_text(screen, 3 - stg['show_timestamps'], stg['font_line_distance_small'], stg['window_size_x'] - 94, font_small, 'Some achievements were added or removed on Steam',
                          (84, header_h + 17 + (i - scroll_history) * 74), stg['color_text'])
            if stg['show_timestamps']:
                show_text(screen, font_general, history[i]['time_' + stg['history_time']], (84, header_h + 49 + (i - scroll_history) * 74), stg['color_text'])

        if history[i]['unread'] == 1:
            screen.blit(unreadicon, (66, header_h + 56 + (i - scroll_history) * 74))
        elif history[i]['unread'] == 2:
            screen.blit(unreadicon2, (66, header_h + 56 + (i - scroll_history) * 74))

    if len(history) > achs_to_show:
        draw_scrollbar(scroll_history, len(history) - achs_to_show, len(history) * 74 - 10)

    pygame.display.flip()

def ach_dumper():
    dump_time = datetime.now()

    text = appid
    if gamename != appid:
        text += ' - ' + gamename
    text += ' | ' + dump_time.strftime(stg_ad['strftime'])
    text += f'\nUnlocked: {achs_unlocked}/{len(achs)}'
    if viewing == 'history':
        text += ' (History)'
    elif viewing == 'history_unlocks' or state_filter == 1:
        text += ' (Unlocked only)'
    elif state_filter == 2:
        text += ' (Locked only)'
    if viewing == 'history_unlocks':
        text += ' [T↓]'
    else:
        if stg['sort_by_rarity']:
            text += ' [%↓]'
        if stg['unlocks_on_top']:
            text += ' [U↑]'
        if stg['unlocks_timesort']:
            text += ' [T↓]'
        if header_extra == 'search_results':
            text += '\nSearch: ' + search_request

    if viewing in ('achs', 'history_unlocks'):
        for a in achs_f:
            if a.icon_gray == 'hidden_dummy_ach_icon':
                text += '\n\n' + a.description_l
                continue

            can_show_desc = not a.hidden or (a.earned and not hide_all_secrets) or reveal_secrets

            if stg['secrets_listhide'] and not can_show_desc:
                text += '\n\n' + stg_ad['hidden_title']
            else:
                text += '\n\n' + a.display_name_np
                if stg_ad['unlockrates'] == 'name':
                    text += a.rarity_text

            if can_show_desc:
                if a.has_desc:
                    d = a.description_l
                    if stg['unlockrates'] == 'desc' and a.rarity != -1.0:
                        d = d[: -len(a.rarity_text)]
                    if stg_ad['unlockrates'] == 'desc' and a.rarity != 1.0:
                        d += a.rarity_text
                    text += '\n' + d
            elif len(stg_ad['hidden_desc']) > 0:
                text += '\n' + stg_ad['hidden_desc']

            if a.earned:
                text += '\n' + f"[Unlocked - {datetime.fromtimestamp(a.get_ts(stg_ad['savetime_shown'])).strftime(stg_ad['strftime'])}]"
            else:
                text += '\n[Locked]'

            if a.progress != None and (can_show_desc or not stg_ad['bar_hide_secret']):
                val = a.progress.current_value
                if stg_ad['bar_ignore_min']:
                    val = a.progress.real_value
                if a.earned:
                    val = a.progress.max_val
                text += f' ({val}/{a.progress.max_val})'
    elif viewing == 'history':
        prefixes = {'unlock': 'Unlocked: ', 'lock': 'Locked: ', 'progress_report': 'Progress: '}
        for h in history:
            if h['type'] == 'lock_all':
                text += '\n\nAll achievements locked'
                text += '\nFile containing achievement data was deleted'
            elif h['type'] == 'schema_change':
                text += '\n\nAchievement list has changed'
                text += '\nSome achievements were added or removed on Steam'
            else:
                if h['type'] == 'progress_report':
                    text += '\n\n' + prefixes[h['type']] + h['ach'].display_name_np
                    text += f" ({h['value'][0]}/{h['value'][1]})"
                else:
                    text += '\n\n' + prefixes[h['type']] + h['ach'].display_name_l
                if not h['ach'].hidden or (h['type'] == 'unlock' and not hide_all_secrets) or reveal_secrets:
                    text += '\n' + h['ach'].description_l
                elif len(stg_ad['hidden_desc']) > 0:
                    text += '\n' + stg_ad['hidden_desc']
            text += '\n[' + h['time_' + stg['history_time']] + ']'
    elif viewing == 'stats' and len(stats) > 0:
        text += '\n'
        for s in stats:
            text += '\n' + stats[s].dname + ' = ' + str(stats[s].value)

    filename = f"ach_dumper/{dump_time.strftime('%Y%m%d_%H%M%S')}_{achdata_source}_{appid}"
    if viewing == 'stats':
        filename += '_stats'
    elif viewing == 'history':
        filename += '_history'
    elif state_filter == 1 or viewing == 'history_unlocks':
        filename += '_unlock'
    elif state_filter == 2:
        filename += '_lock'
    filename += '.txt'

    if not os.path.isdir('ach_dumper'):
        os.makedirs('ach_dumper')
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(text)

if len(sys.argv) > 1:
    appid, achdata_source, source_extra = load_game(sys.argv[1:4], True)
else:
    appid, achdata_source, source_extra = load_game(input('Enter AppID: '))

if not os.path.isdir('games'):
    os.makedirs('games')

stg = load_settings(appid, achdata_source)
stg_ad = load_settings(appid, achdata_source, True)

# min_size_x = 274
min_size_x = 170
min_size_y = 132
# if stg['history_length'] < 0:
    # min_size_x = 174
if stg['gamebar_position'] == 'under':
    min_size_y = 144

if stg['window_size_x'] < min_size_x or stg['window_size_y'] < min_size_y:
    print(f'Window size must be at least {min_size_x}x{min_size_y} with current settings')
    sys.exit()
if stg['bar_length'] == 0:
    stg['bar_length'] = -10
if stg['gamebar_length'] == 0:
    stg['gamebar_length'] = -10
if stg['frame_size'] > 5:
    stg['frame_size'] = 5
if stg['frame_color_rare'] == None:
    stg['frame_color_rare'] = stg['frame_color_unlock']
if stg['frame_color_rare_lock'] == None:
    stg['frame_color_rare_lock'] = stg['frame_color_lock']
if stg['color_achbg_rare'] == None:
    stg['color_achbg_rare'] = stg['color_achbg_unlock']
if stg['color_achbg_rare_lock'] == None:
    stg['color_achbg_rare_lock'] = stg['color_achbg_lock']
if stg['color_text_rare'] == None:
    stg['color_text_rare'] = stg['color_text_unlock']
if stg['color_text_rare_lock'] == None:
    stg['color_text_rare_lock'] = stg['color_text_lock']
if stg['color_bar_completed'] == None:
    stg['color_bar_completed'] = stg['color_bar_fill']
if len(stg['language']) == 0:
    stg['language'].append('english')
if stg['language_requests'] == None:
    stg['language_requests'] = stg['language'][0]

header_h = 58
if stg['gamebar_position'] in ('repname', 'hide'):
    header_h = 47
elif stg['gamebar_position'] == 'under':
    header_h = 70

if achdata_source == 'steam':
    if len(stg['api_key']) == 0:
        print('An API key is required to track achievements from Steam')
        sys.exit()
    # source_extra = check_alias(source_extra)
    # if source_extra == None or not source_extra.isnumeric():
        # print('Invalid Steam user ID')
        # sys.exit()

url_random = randint(0, 10000000)

def generator_cleanup():
    if os.path.isdir(f'{appid}_output'):
        shutil.rmtree(f'{appid}_output')
    elif os.path.isdir(f'output/{appid}'):
        shutil.rmtree(f'output/{appid}')
        if len(os.listdir('output')) == 0:
            shutil.rmtree('output')
    if os.path.isdir(f'backup/{appid}'):
        shutil.rmtree(f'backup/{appid}')
        if len(os.listdir('backup')) == 0:
            shutil.rmtree('backup')
    if os.path.isdir('login_temp'):
        shutil.rmtree('login_temp')

if len(stg['generator_path']) > 0 and not os.path.isdir(f'games/{appid}'):
    interrupted_gen = False
    if os.path.isdir(f'{appid}_output'):
        interrupted_gen = True
        cfg_format = 0
        cfg_path = f'{appid}_output/steam_settings'
    elif os.path.isdir(f'output/{appid}'):
        interrupted_gen = True
        cfg_format = 1
        cfg_path = f'output/{appid}/steam_settings'
    if interrupted_gen:
        print(f'Found possibly incomplete auto-generated config: {cfg_path}')
        cfg_achs = []
        a_count = 0
        s_count = 0
        if os.path.isfile(f'{cfg_path}/achievements.json'):
            with open(f'{cfg_path}/achievements.json') as f:
                cfg_achs = json.load(f)
                a_count = len(cfg_achs)
        if os.path.isfile(f'{cfg_path}/stats.txt'):
            with open(f'{cfg_path}/stats.txt') as f:
                for l in f.readlines():
                    s_count += l.count('=') >= 2
        elif os.path.isfile(f'{cfg_path}/stats.json'):
            with open(f'{cfg_path}/stats.json') as f:
                s_count = len(json.load(f))
        i_set = set()
        for a in cfg_achs:
            if 'icon' in a:
                i_set.add(a['icon'])
            if 'icon_gray' in a:
                i_set.add(a['icon_gray'])
        i_expected_count = len(i_set)
        i_count = 0
        i_missing = set()
        for i in i_set:
            if os.path.isfile(f'{cfg_path}/achievement_images/{i}') or os.path.isfile(f'{cfg_path}/{i}'):
                i_count += 1
            else:
                i_missing.add(i)
        print(f' - Achievements: {a_count}')
        print(f' - Stats: {s_count}')
        print(f' - Achievement icons: {i_count}/{i_expected_count}')
        print('Press ENTER to use this config or write anything to discard it')
        if i_count != i_expected_count:
            print(f'({i_expected_count - i_count} icons will be downloaded)')
        if input() == '':
            if i_count != i_expected_count:
                import urllib.request
                base_urls =  ['https://cdn.akamai.steamstatic.com/steamcommunity/public/images/apps/',
                              'https://cdn.cloudflare.steamstatic.com/steamcommunity/public/images/apps/']
                i_path = f'{cfg_path}/achievement_images'
                if cfg_format == 1:
                    i_path = f'{cfg_path}/img'
                if not os.path.isdir(i_path):
                    os.makedirs(i_path)
                done = 0
                total = i_expected_count - i_count
                for i in i_missing:
                    if cfg_format == 1:
                        i = i[4:]
                    done += 1
                    print(f'[{done}/{total}] {i}')
                    success = False
                    for u in range(len(base_urls)):
                        url = base_urls[u] + appid + '/' + i
                        try:
                            urllib.request.urlretrieve(url, i_path + '/' + i)
                            success = True
                            break
                        except Exception as ex:
                            pass
                    if not success:
                        print('Failed to download icon. Restart to retry')
                        input()
                        sys.exit()
            shutil.move(cfg_path, f'games/{appid}')
        generator_cleanup()

    if not os.path.isdir(f'games/{appid}'):
        command = '"' + os.path.abspath(stg['generator_path']) + '" ' + appid
        if stg['generator_path'].endswith('.py'):
            command = 'python ' + command
        print('Generating game config...')
        print('------------------------------')
        exit_code = os.system(command)
        print('------------------------------')
        if exit_code == 0:
            if os.path.isdir(f'{appid}_output/steam_settings'):
                cfg_path = f'{appid}_output/steam_settings'
            elif os.path.isdir(f'output/{appid}/steam_settings'):
                cfg_path = f'output/{appid}/steam_settings'
            shutil.move(cfg_path, f'games/{appid}')
        else:
            print('An error occurred. Press ENTER and restart to check if this config can be used or write anything to remove it')
            if input() == '':
                sys.exit()
        generator_cleanup()

    if not os.path.isdir(f'games/{appid}'):
        print('Failed to generate config!')
    elif os.path.isfile('games/alias.txt'):
        try:
            alias = input('Alias: ')
        except RuntimeError:
            alias = ''
        if alias != '':
            emu_info = appid + ' ' + input(f'Alias target: {appid} ')
            emu_info = emu_info.rstrip()
            with open('games/alias.txt') as f:
                a = f.read().split('\n')
            a.append(emu_info + '=' + alias)
            with open('games/alias.txt', 'w') as f:
                f.write('\n'.join(a))

if 'LnzAch_gamename' in os.environ:
    gamename = os.environ['LnzAch_gamename']
else:
    gamenames = {}
    if os.path.isfile('games/games.json'):
        with open('games/games.json') as f:
            gamenames = json.load(f)
    if appid in gamenames and stg['language_requests'] in gamenames[appid]:
        gamename = gamenames[appid][stg['language_requests']]
    else:
        gamename = get_game_name(appid)
    if gamename == appid:
        steam_req = send_steam_request('appdetails', f"https://store.steampowered.com/api/appdetails?appids={appid}&l={stg['language_requests']}")
        if steam_req != None:
            gamename = steam_req[appid]['data']['name']
            if not appid in gamenames:
                gamenames[appid] = {}
            gamenames[appid][stg['language_requests']] = gamename
            with open('games/games.json', 'w') as f:
                json.dump(gamenames, f, indent=4)

ach_percentages = {}
if stg['unlockrates'] != 'none' and os.path.isdir(f'games/{appid}'):
    try:
        with open(f'games/{appid}/unlockrates.json') as percentfile:
            percentdata = json.load(percentfile)
    except FileNotFoundError:
        percentdata = None
    if percentdata == None or time.time() >= percentdata['time'] + stg['unlockrates_expire']:
        steam_req = send_steam_request('GetGlobalAchievementPercentagesForApp', f'https://api.steampowered.com/ISteamUserStats/GetGlobalAchievementPercentagesForApp/v0002/?gameid={appid}')
        if steam_req != None:
            try:
                for p in steam_req['achievementpercentages']['achievements']:
                    ach_percentages[p['name']] = p['percent']
                with open(f'games/{appid}/unlockrates.json', 'w') as percentfile:
                    json.dump({'time': time.time(), 'achievements': ach_percentages}, percentfile, indent=4)
            except KeyError:
                steam_req = None
        if steam_req == None and percentdata != None:
            ach_percentages = percentdata['achievements']
        elif steam_req == None:
            stg['unlockrates'] = 'none'
    else:
        ach_percentages = percentdata['achievements']

stat_dnames = {}
if stg['stat_display_names'] and os.path.isdir(f'games/{appid}'):
    if not os.path.isfile(f'games/{appid}/statdisplay.json'):
        steam_req = None
        if len(stg['api_key']) > 0:
            steam_req = send_steam_request('GetSchemaForGame', f"https://api.steampowered.com/ISteamUserStats/GetSchemaForGame/v2/?appid={appid}&key={stg['api_key']}&l={stg['language_requests']}")
        if steam_req != None:
            with open(f'games/{appid}/statdisplay.json', 'w') as dname_file:
                try:
                    for n in steam_req['game']['availableGameStats']['stats']:
                        stat_dnames[n['name']] = n['displayName']
                    json.dump(stat_dnames, dname_file, indent=4)
                except KeyError:
                    dname_file.write('{}')
    else:
        with open(f'games/{appid}/statdisplay.json') as dname_file:
            stat_dnames = json.load(dname_file)

save_dir = get_save_dir(appid, achdata_source, source_extra)

pygame.init()

pygame.display.set_caption(f'Achievements | {gamename}')
pygame.display.set_allow_screensaver(True)
screen = pygame.display.set_mode((stg['window_size_x'], stg['window_size_y']))
achs_to_show = (stg['window_size_y'] - header_h + 10) // 74
if stg['window_size_y'] - header_h + 10 < achs_to_show * 74 + stg['frame_size'] and achs_to_show > 1:
    achs_to_show -= 1
stats_to_show = (stg['window_size_y'] - header_h) // stg['font_line_distance_regular']

viewing = 'achs'
scroll = 0
scroll_stats = 0
scroll_history = 0
state_filter = 0
history = []
header_extra = ''
search_request = ''
reveal_secrets = False
hide_all_secrets = False

def load_image(name):
    for i in stg['images']:
        p = os.path.join('images', i, name)
        if os.path.isfile(p):
            return pygame.image.load(p)
    return pygame.image.load('images/' + name)

def button_location(img, next_btn=None):
    if next_btn != None:
        x = next_btn.topleft[0]
    else:
        x = stg['window_size_x']
    x -= 10
    x -= img.get_width()
    return pygame.Rect(x, 10, img.get_width(), 22)

statsbutton = load_image('stats.png')
achsbutton = load_image('achs.png')
filter_buttons = [load_image('filter_all.png'), load_image('filter_unlock.png'), load_image('filter_lock.png')]
historybutton = load_image('history.png')
backbutton = load_image('back.png')
clearbutton = load_image('clear.png')
unlocksbutton = load_image('unlocks.png')
# notifsbutton = load_image('notifs.png')
unreadicon = load_image('unread.png')
unreadicon2 = load_image('unread2.png')
lockallicon = load_image('lock_all.png')
upbutton = load_image('up.png')
downbutton = load_image('down.png')
xbutton = load_image('x.png')
listbutton = load_image('list.png')
secretsbutton = load_image('sort_secrets.png')
percentsortbutton = {False: load_image('sort_percent0.png'), True: load_image('sort_percent1.png')}
uotbutton = {False: load_image('sort_uot0.png'), True: load_image('sort_uot1.png')}
timesortbutton = {False: load_image('sort_time0.png'), True: load_image('sort_time1.png')}
secretsNbutton = {False: load_image('sort_secrets_n0.png'), True: load_image('sort_secrets_n1.png')}
secretsHbutton = {False: load_image('sort_secrets_h0.png'), True: load_image('sort_secrets_h1.png')}
secretsBbutton = {False: load_image('sort_secrets_b0.png'), True: load_image('sort_secrets_b1.png')}
secretsLHbutton = {False: load_image('sort_secrets_lh0.png'), True: load_image('sort_secrets_lh1.png')}
revealbutton = {False: load_image('sort_secrets_reveal0.png'), True: load_image('sort_secrets_reveal1.png')}
hidebutton = {False: load_image('sort_secrets_hideall0.png'), True: load_image('sort_secrets_hideall1.png')}
schemachangeicon = load_image('schema_change.png')
hiddenlockicon = load_image('hidden_lock.png')
hiddenunlockicon = load_image('hidden_unlock.png')
barimagebg = load_image('bar_bg.png')
barimagefill = load_image('bar_fill.png')
barimagecompleted = load_image('bar_completed.png')

btn_locs = {}
btn_locs['stats'] = button_location(statsbutton)
btn_locs['filter'] = [button_location(i, btn_locs['stats']) for i in filter_buttons]
btn_locs['history'] = [button_location(historybutton, i) for i in btn_locs['filter']]
btn_locs['achs'] = button_location(achsbutton)
btn_locs['back'] = button_location(backbutton)
btn_locs['clear'] = button_location(clearbutton, btn_locs['back'])
btn_locs['history_unlocks'] = button_location(unlocksbutton, btn_locs['clear'])
search_results_x_rect = pygame.Rect(stg['window_size_x'] - 32, 10, 22, 22)
btn_locs['filter_search'] = [button_location(i, search_results_x_rect) for i in filter_buttons]

def load_sound(name):
    vol = 1.0
    name = name.rsplit(':', 1)
    if len(name) > 1 and name[1].count('.') < 2 and name[1].replace('.', '').isnumeric():
        vol = float(name[1])
    name = name[0]
        
    if name == '':
        return None
    p = os.path.join('sounds', name)
    if os.path.isfile(p):
        s = pygame.mixer.Sound(p)
        s.set_volume(vol)
        return s
    else:
        print(f'Sound file not found ({name})')
 
sounds = {}
if stg['sound']:
    sounds[1] = load_sound(stg['sound_progress'])
    sounds[2] = load_sound(stg['sound_unlock'])
    sounds[3] = load_sound(stg['sound_rare'])
    sounds[4] = load_sound(stg['sound_multi'])
    sounds[5] = load_sound(stg['sound_complete'])

try:
    with open(f'games/{appid}/achievements.json') as achsfile:
        achs_json = json.load(achsfile)
except FileNotFoundError:
    achs_json = {}

achs_crc32 = {}
if achdata_source == 'sse':
    for a in achs_json:
        achs_crc32[zlib.crc32(bytes(a['name'], 'utf-8'))] = a['name']

achieved_json = {}
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
    except Exception as ex:
        print(f'Failed to read file (player achs) - {type(ex).__name__}')
else:
    steam_req = send_steam_request('GetPlayerAchievements', f"https://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v0001/?appid={appid}&key={stg['api_key']}&steamid={source_extra}")
    if steam_req != None:
        achieved_json = steam_req['playerstats']['achievements']
        achieved_json = convert_achs_format(achieved_json, achdata_source)

stats = {}
stats_crc32 = {}
increment_only_names = []
increment_only = {}
io_change = False

if achdata_source != 'steam' and os.path.isfile(f'games/{appid}/increment_only.txt'):
    with open(f'games/{appid}/increment_only.txt') as iofile:
        increment_only_names = iofile.read().split('\n')
    if os.path.isfile(f'{save_dir}/{appid}_inc_only.json'):
        with open(f'{save_dir}/{appid}_inc_only.json') as iofile:
            increment_only = json.load(iofile)

stat_info = []
stat_file_exists = False
if os.path.isfile(f'games/{appid}/stats.txt'):
    stat_file_exists = True
    with open(f'games/{appid}/stats.txt') as f:
        statlines = f.read().split('\n')
    for line in statlines:
        stat_info.append(line.rsplit('=', 2))
elif os.path.isfile(f'games/{appid}/stats.json'):
    stat_file_exists = True
    with open(f'games/{appid}/stats.json') as f:
        statjson = json.load(f)
    for s in statjson:
        stat_info.append([s['name'], s['type'], s['default']])
if stat_file_exists:
    for linespl in stat_info:
        if len(linespl) == 3:
            locinfo = {'source': achdata_source, 'appid': appid, 'name': linespl[0]}
            locinfo['source_extra'] = source_extra
            if achdata_source == 'sse':
                c = zlib.crc32(bytes(linespl[0], 'utf-8'))
                stats_crc32[c] = linespl[0]
            stats[linespl[0]] = Stat(locinfo, linespl[1], linespl[2], stg['delay_read_change'], stat_dnames, increment_only_names)

            if stats[linespl[0]].inc_only:
                if not linespl[0] in increment_only or (achdata_source == 'goldberg' and stats[linespl[0]].value > increment_only[linespl[0]]):
                    increment_only[linespl[0]] = stats[linespl[0]].value
                    io_change = True
                elif stats[linespl[0]].value < increment_only[linespl[0]]:
                    stats[linespl[0]].value = increment_only[linespl[0]]

def load_stats():
    global stats_last_change, io_change
    m = 'rt'
    if achdata_source == 'sse':
        m = 'rb'
    statsdata = {}
    try:
        stamp = os.stat(stats_path).st_mtime
        if stamp == stats_last_change:
            return False
        stats_last_change = stamp
        with open(stats_path, m) as statsfile:
            statsdata = statsfile.read()
        statsdata = convert_stats_format(stats, statsdata, achdata_source, stats_crc32)
    except FileNotFoundError:
        stats_last_change = None
    except Exception as ex:
        stats_last_change = 'Retry'
        print(f'Failed to load stats - {type(ex).__name__}')
    stats_changed = False
    for stat in stats:
        if stat in statsdata:
            new = statsdata[stat]
        else:
            new = stats[stat].default
        showing_older_io_val = stats[stat].value != stats[stat].real_value
        if stats[stat].set_val(new):
            stats_changed = True
            if stats[stat].inc_only:
                increment_only[stat] = stats[stat].value
                io_change = True
        if showing_older_io_val != (stats[stat].value != stats[stat].real_value):
            global flip_required
            flip_required = True

    return stats_changed

def get_stat_last_change(name):
    if achdata_source == 'goldberg':
        return stats[name].fchecker.last_check
    elif achdata_source == 'steam':
        return time.time()
    else:
        return stats_last_change

if achdata_source == 'steam' and len(stats) > 0:
    steam_req = send_steam_request('GetUserStatsForGame', f"https://api.steampowered.com/ISteamUserStats/GetUserStatsForGame/v0002/?appid={appid}&key={stg['api_key']}&steamid={source_extra}")
    if steam_req != None and 'stats' in steam_req['playerstats']:
        for s in steam_req['playerstats']['stats']:
            if s['name'] in stats:
                stats[s['name']].value = stats[s['name']].to_stat_type(s['value'])
elif achdata_source != 'goldberg' and len(stats) > 0:
    stats_path = get_stats_path(achdata_source, appid, source_extra)
    stats_last_change = -1.0
    load_stats()

if stg['rare_below_relative'] or stg['rare_guaranteed']:
    sorted_urates = list(map(float, ach_percentages.values()))
    sorted_urates.sort()
    if stg['rare_below_relative'] and len(sorted_urates) > 0:
        stg['rare_below'] *= sorted_urates[-1] * 0.01
    if stg['rare_guaranteed'] > 0 and len(sorted_urates) > stg['rare_guaranteed']:
        stg['rare_below'] = max(stg['rare_below'], round((sorted_urates[stg['rare_guaranteed'] - 1] + 0.1) * 10) / 10)

achs = []
for ach in achs_json:
    achs.append(Achievement(ach, achieved_json, stats, ach_percentages, stg))

ach_idxs = {}
ach_icons = {}
achs_unlocked = 0
languages_used = set(['english'])
max_rarity = -1.0

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

config_from_fork = os.path.isdir(f'games/{appid}/img')
icons_path = f'games/{appid}/achievement_images'
if config_from_fork:
    icons_path = f'games/{appid}/img'

fu_change = False
ts_change = False
ts_lost = False
for i in range(len(achs)):
    ach_idxs[achs[i].name] = i

    if config_from_fork:
        if achs[i].icon != None and achs[i].icon[:4] =='img/':
            achs[i].icon = achs[i].icon[4:]
        if achs[i].icon_gray != None and achs[i].icon_gray[:4] =='img/':
            achs[i].icon_gray = achs[i].icon_gray[4:]
    if achs[i].icon != None and not achs[i].icon in ach_icons:
        try:
            ach_icons[achs[i].icon] = pygame.image.load(os.path.join(icons_path, achs[i].icon))
        except pygame.error:
            ach_icons[achs[i].icon] = None
    if achs[i].icon_gray != None and not achs[i].icon_gray in ach_icons:
        try:
            ach_icons[achs[i].icon_gray] = pygame.image.load(os.path.join(icons_path, achs[i].icon_gray))
        except pygame.error:
            ach_icons[achs[i].icon_gray] = None

    languages_used.add(achs[i].language)
    languages_used.add(achs[i].language_d)

    if achs[i].earned_time == 'stat_last_change':
        achs[i].earned_time, achs[i].ts_first, achs[i].ts_earliest = [get_stat_last_change(achs[i].progress.value['operand1'])] * 3

    if achs[i].name in force_unlocks:
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

    if achs[i].name in saved_tstamps:
        if not stg['savetime_keep_locked'] and not achs[i].earned:
            if saved_tstamps[achs[i].name]['first'] != None or saved_tstamps[achs[i].name]['earliest'] != None:
                ts_change = True
                ts_lost = True
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
        if achs[i].ts_first != None:
            ts_change = True

    if achs[i].rarity > 0:
        max_rarity = max(achs[i].rarity, max_rarity)

if fu_change and stg['forced_keep'] == 'save':
    if not os.path.isdir(save_dir):
        os.makedirs(save_dir)
    with open(f'{save_dir}/{appid}_force.json', 'w') as forcefile:
        json.dump(force_unlocks, forcefile, indent=4)
if ts_change and stg['save_timestamps']:
    if not os.path.isdir(save_dir):
        os.makedirs(save_dir)
    if ts_lost and os.path.isfile(f'{save_dir}/{appid}_time.json'):
        n = f"save/time_backup/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{achdata_source}_{appid}.json"
        if not os.path.isdir('save/time_backup'):
            os.makedirs('save/time_backup')
        shutil.copy(f'{save_dir}/{appid}_time.json', n)
    with open(f'{save_dir}/{appid}_time.json', 'w') as timefile:
        json.dump(saved_tstamps, timefile, indent=4)
if io_change:
    if not os.path.isdir(save_dir):
        os.makedirs(save_dir)
    with open(f'{save_dir}/{appid}_inc_only.json', 'w') as iofile:
        json.dump(increment_only, iofile, indent=4)
if os.path.isdir(save_dir) and isinstance(source_extra, str) and source_extra[:5] == 'path:':
    with open(f'{save_dir}/path.txt', 'w') as pathfile:
        pathfile.write(source_extra[5:])

for i in ach_icons:
    if ach_icons[i] == None: continue
    size = (ach_icons[i].get_width(), ach_icons[i].get_height())
    if size != (64, 64):
        if stg['smooth_scale']:
            ach_icons[i] = pygame.transform.smoothscale(ach_icons[i].convert_alpha(), (64, 64))
        else:
            ach_icons[i] = pygame.transform.scale(ach_icons[i], (64, 64))

if platform.uname().system == 'Windows' and stg['notif_icons'] and stg['notif_icons_no_ico'] != 'ignore':
    icons_not_conv = 0
    for i in ach_icons:
        if ach_icons[i] == None: continue
        if not os.path.isfile(os.path.join(icons_path, 'ico', i + '.ico')):
            icons_not_conv += 1
    if icons_not_conv > 0:
        print('Icons not converted:', icons_not_conv)
        if stg['notif_icons_no_ico'] == 'convert':
            print('------------------------------')
            if os.path.isfile('icon_converter.py'):
                os.system(f'python icon_converter.py {appid} -s')
            elif os.path.isfile('icon_converter.exe'):
                os.system(f'icon_converter.exe {appid} -s')
            else:
                print('Icon converter not found')
            print('------------------------------')

ach_icons['hidden_dummy_ach_icon'] = load_image('hidden.png')

if not os.path.isfile(os.path.join('fonts', stg['font_general'])):
    print('Font file not found (general)')
    sys.exit()
font_general = pygame.font.Font(os.path.join('fonts', stg['font_general']), stg['font_size_general'])
font_achs_regular = {}
font_achs_small = {}
long_hidden_desc = {}
for l in languages_used:
    try:
        font_names = [None, None]
        if l in stg['font_achs']:
            font_names[0] = stg['font_achs'][l]
        else:
            font_names[0] = stg['font_achs']['all']
        if l in stg['font_achs_desc']:
            font_names[1] = stg['font_achs_desc'][l]
        elif 'all' in stg['font_achs_desc']:
            font_names[1] = stg['font_achs_desc']['all']
        else:
            font_names[1] = font_names[0]

        font_sizes = [None, None]
        if font_names[0] in stg['font_size_regular']:
            font_sizes[0] = stg['font_size_regular'][font_names[0]]
        elif 'all' in stg['font_size_regular']:
            font_sizes[0] = stg['font_size_regular']['all']
        if font_names[1] in stg['font_size_small']:
            font_sizes[1] = stg['font_size_small'][font_names[1]]
        elif 'all' in stg['font_size_small']:
            font_sizes[1] = stg['font_size_small']['all']
        font_achs_regular[l] = pygame.font.Font(os.path.join('fonts', font_names[0]), int(font_sizes[0]))
        font_achs_small[l] = pygame.font.Font(os.path.join('fonts', font_names[1]), int(font_sizes[1]))
        long_hidden_desc[l] = multiline_text(None, 2, stg['font_line_distance_small'], stg['window_size_x'] - 94, font_achs_small[l], stg['hidden_desc'], None, (0, 0, 0), True)
    except FileNotFoundError:
        print(f'Font file not found ({l})')
        sys.exit()

for ach in achs:
    if ach.has_desc:
        ach.long_desc = multiline_text(None, 2, stg['font_line_distance_small'], stg['window_size_x'] - 94, font_achs_small[ach.language_d], ach.description_l, None, (0, 0, 0), True)
    if ach.rarity == -1.0:
        continue
    if stg['unlockrates'] == 'name':
        ach.display_name_l = long_text(None, stg['window_size_x'] - 94 - font_achs_regular[ach.language].size(ach.rarity_text)[0], font_achs_regular[ach.language], ach.display_name_l, None, (0, 0, 0), True)
        ach.display_name_l += ach.rarity_text
    elif stg['unlockrates'] == 'desc' and ach.has_desc:
        ach.description_l += ach.rarity_text

    force_progress = {}
    if os.path.isfile(f'games/{appid}/force_progress.txt'):
        with open(f'games/{appid}/force_progress.txt') as f:
            force_progress_text = f.read().split('\n')
        def_step = 0.0
        def_round = False
        def_removal = False
        for x in force_progress_text:
            x = x.rsplit(':', 1)
            x[0] = x[0].strip()
            s, r, rem = def_step, def_round, def_removal
            if len(x) == 2:
                x[1] = x[1].strip()
                if x[1] == '-':
                    rem = True
                    x[1] = ''
                elif x[0] == '':
                    rem = False
                last = x[1][-1:].lower()
                if last == 'r' or last == 'x':
                    r = last == 'r'
                    x[1] = x[1][:-1]
                if x[1] != '':
                    if not (x[1].count('.') < 2 and x[1].replace('.', '').isnumeric()):
                        continue
                    s = float(x[1])
                if x[0] == '':
                    def_step, def_round, def_removal = s, r, rem
                    continue
            n = x[0]
            if n == '*':
                for a in achs:
                    if a.progress != None and a.progress.support:
                        st = a.progress.value['operand1']
                        if not st in force_progress:
                            force_progress[st] = []
                        force_progress[st].append({'ach': a.name, 'max': a.progress.max_val, 'step': s, 'round': r})
                continue
            if n not in ach_idxs:
                continue
            a = achs[ach_idxs[n]]
            if a.progress == None or not a.progress.support:
                continue
            st = a.progress.value['operand1']
            if st in force_progress:
                for i in range(len(force_progress[st])):
                    if force_progress[st][i]['ach'] == n:
                        force_progress[st].pop(i)
                        break
            elif not rem:
                force_progress[st] = []
            if rem:
                continue
            force_progress[st].append({'ach': n, 'max': a.progress.max_val, 'step': s, 'round': r})
        for st in force_progress:
            force_progress[st].sort(key=lambda x : x['max'])

achs_f = filter_achs(achs, state_filter, stg)

hover_ach = None
running = True
flip_required = True
filter_needed = False
last_update = time.time()
fchecker_achieved_locinfo = {'source': achdata_source, 'appid': appid}
fchecker_achieved_locinfo['source_extra'] = source_extra
fchecker_achieved = None
if achdata_source != 'steam':
    fchecker_achieved = FileChecker('player_achs', fchecker_achieved_locinfo, stg['delay_read_change'])
stats_delay_counter = 0
mouse_scrolling = False
steam_requests_data = {'achievements': None, 'stats': None}
steam_requests_state = {'achievements': -1, 'stats': -1}
steam_requests_time = {'achievements': time.time(), 'stats': time.time()}

def steam_update(reqtype):
    global steam_requests_state
    global steam_requests_data
    steam_requests_state[reqtype] = 0
    steam_requests_time[reqtype] = time.time()
    if reqtype == 'achievements':
        steam_req = send_steam_request('GetPlayerAchievements', f"https://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v0001/?appid={appid}&key={stg['api_key']}&steamid={source_extra}")
    if reqtype == 'stats':
        steam_req = send_steam_request('GetUserStatsForGame', f"https://api.steampowered.com/ISteamUserStats/GetUserStatsForGame/v0002/?appid={appid}&key={stg['api_key']}&steamid={source_extra}")
    if steam_req != None:
        if steam_req != steam_requests_data[reqtype]:
            steam_requests_data[reqtype] = steam_req
            steam_requests_state[reqtype] = 1
        else:
            steam_requests_state[reqtype] = 2
    else:
        steam_requests_state[reqtype] = -1

def check_search_match(ach, rq):
    if ach.icon_gray == 'hidden_dummy_ach_icon':
        return stg['secrets'] == 'bottom'
    if rq == '#hidden':
        return ach.hidden
    elif rq == '#not_hidden':
        return not ach.hidden
    elif rq == '#progress':
        return ach.progress != None
    can_show_desc = not ach.hidden or (ach.earned and not hide_all_secrets) or reveal_secrets
    if stg['secrets_listhide'] and not can_show_desc:
        return False
    rq = rq.lower()
    if rq in ach.display_name_np.lower():
        return True
    if ach.has_desc and can_show_desc:
        d = ach.description_l
        if stg['unlockrates'] == 'desc' and ach.rarity != -1.0:
            d = d[: -len(ach.rarity_text)]
        if rq in d.lower():
            return True
    return False

notif_names = {'unlock': 'Achievement Unlocked!', 'lock': 'Achievement Locked',
               'lock_all': 'All achievements locked', 'progress_report': 'Achievement Progress',
               'schema_change': 'Achievements'}

def pick_sound(x):
    global sound_to_play
    if sound_to_play == 5 or x == 5:
        sound_to_play = 5
    elif stg['sound_rare_over_multi'] and (sound_to_play == 3 or x == 3):
        sound_to_play = 3
    elif sounds[4] != None and sound_to_play != 0:
        sound_to_play = 4
    else:
        sound_to_play = max(x, sound_to_play)

def create_notification(t, change):
    u = 1
    if viewing == 'history':
        u = 2
    if not stg['history_unread']:
        u = 0

    h = {'type': t, 'unread': u, 'time_real': change['time_real'], 'time_action': change['time_action']}
    if 'ach_obj' in change and t != 'lock_all':
        ach = change['ach_obj']
        h['ach'] = ach
    if t == 'progress_report':
        h['value'] = change['value']
    if stg['history_length'] > -1:
        history.insert(0, h)

    if stg['sound']:
        if t == 'unlock':
            if achs_unlocked == len(achs) and sounds[5] != None:
                pick_sound(5)
            elif ach.rare and sounds[3] != None:
                pick_sound(3)
            elif sounds[2] != None:
                pick_sound(2)
        elif t == 'progress_report' and sounds[1] != None:
            pick_sound(1)

    if stg['notif']:
        if t != 'schema_change':
            global notifications_sent, notifications_hidden
            if stg['notif_limit'] == 0 or notifications_sent < stg['notif_limit']:
                notifications_sent += 1
            else:
                notifications_hidden += 1
                return
        
        title = notif_names[t]
        if 'ach' in h:
            message = ach.display_name_np
        elif t == 'lock_all':
            message = 'Achievement data not found'
        elif t == 'schema_change':
            message = 'Achievement list has changed'
        if t == 'progress_report':
            message += f" ({change['value'][0]}/{change['value'][1]})"

        if 'ach' in h and stg['notif_desc'] and t != 'lock' and ach.has_desc and (not ach.hidden or (ach.earned and not hide_all_secrets) or reveal_secrets):
            title = message
            message = ach.description_l
            if stg['unlockrates'] == 'desc' and ach.rarity != -1.0:
                message = message[: -len(ach.rarity_text)]

        if t == 'unlock' and stg['notif_unlock_count']:
            title = f'[{achs_unlocked}/{len(achs)}] ' + title

        if len(title) > 64:
            title = title[:61]
        if len(message) > 256:
            message = message[:253] + '...'

        icon = None
        if stg['notif_icons'] and 'ach' in h:
            if t == 'unlock':
                icon = ach.icon
            else:
                icon = ach.icon_gray

        send_notification(title, message, icon)

if len(ach_percentages) > 0 and len(ach_idxs) > 0 and set(ach_percentages) != set(ach_idxs):
    t = datetime.now().strftime(stg['strftime'])
    ch = {'time_real': t, 'time_action': t}
    create_notification('schema_change', ch)

while running:

    update_time = time.time() >= last_update + stg['delay']
    if update_time or 1 in steam_requests_state.values():

        notifications_sent = 0
        notifications_hidden = 0
        sound_to_play = 0
        fu_change = False
        ts_change = set()
        ts_lost = False
        io_change = False

        if update_time:
            last_update = time.time()

        if achdata_source != 'steam':
            changed, newdata = fchecker_achieved.check()
            stats_delay_counter += 1
        else:
            changed = steam_requests_state['achievements'] == 1
            if changed:
                newdata = steam_requests_data['achievements']['playerstats']['achievements']
                steam_requests_state['achievements'] = 2
            stats_changed = False
            if steam_requests_state['stats'] == 1:
                if 'stats' in steam_requests_data['stats']['playerstats']:
                    stats_changed = 'stats' in steam_requests_data['stats']['playerstats']
                    stat_response = steam_requests_data['stats']
                steam_requests_state['stats'] = 2

            for t in steam_requests_state:
                if steam_requests_state[t] == 0 and time.time() >= steam_requests_time[t] + 30:
                    steam_requests_state[t] = -1
                    print(f'Steam request ({t}) timed out')

            if not 0 in steam_requests_state.values() and update_time:
                stats_delay_counter += 1
                if len(achs) > 0:
                    threading.Thread(target=steam_update, args=('achievements', ), daemon=True).start()
                if len(stats) > 0 and stats_delay_counter >= stg['delay_stats']:
                    threading.Thread(target=steam_update, args=('stats', ), daemon=True).start()
                    stats_delay_counter = 0

        if changed:

            if achdata_source != 'goldberg' and newdata != None:
                newdata = convert_achs_format(newdata, achdata_source, achs_crc32)

            achs, changes = update_achs(achs, newdata, fchecker_achieved, stg)

            if len(changes) > 0:
                filter_needed = True
                flip_required = True

            lock_all_notified = False
            for change in changes:
                if 'ts_change' in change and change['ts_change']:
                    ts_change.add(change['ach_api'])
                if 'ts_lost' in change and change['ts_lost']:
                    ts_lost = True

                if change['type'] == 'unlock':
                    if change['was_forced']:
                        force_unlocks.pop(change['ach_api'], None)
                        fu_change = True
                        continue
                    achs_unlocked += 1
                    create_notification('unlock', change)
                elif change['type'] == 'lock':
                    achs_unlocked -= 1
                    if change['lock_all']:
                        achs_unlocked = 0
                    if stg['notif_lock']:
                        if not change['lock_all']:
                            create_notification('lock', change)
                        elif not lock_all_notified:
                            create_notification('lock_all', change)
                            lock_all_notified = True
                elif change['type'] == 'progress_report' and change['value'][0] > 0:
                    create_notification('progress_report', change)

        if achdata_source == 'steam' or stats_delay_counter >= stg['delay_stats']:
            if achdata_source != 'steam':
                stats_delay_counter = 0
                stats_changed = False
                if achdata_source == 'goldberg':
                    for stat in stats.values():
                        showing_older_io_val = stat.value != stat.real_value
                        if stat.update_val():
                            stats_changed = True
                            if stat.inc_only:
                                increment_only[stat.name] = stat.value
                                io_change = True
                        if showing_older_io_val != (stat.value != stat.real_value):
                            flip_required = True
                elif len(stats) > 0:
                    stats_changed = load_stats()
            elif stats_changed:
                for s in stat_response['playerstats']['stats']:
                    if s['name'] in stats:
                        if stats[s['name']].value != s['value']:
                            stats_changed = True
                            stats[s['name']].value = stats[s['name']].to_stat_type(s['value'])

            if stats_changed:
                flip_required = True
                for ach in achs:
                    if ach.progress != None and ach.progress.support:
                        old = ach.progress.current_value
                        ach.progress.calculate(stats)

                        if ach.progress.value['operand1'] in force_progress and ach.progress.current_value > old and not ach.earned:
                            for achf in force_progress[ach.progress.value['operand1']]:
                                if ach.progress.current_value >= achf['max']:
                                    if old < achf['max']:
                                        break
                                    continue
                                if achf['ach'] != ach.name:
                                    break
                                if achf['step'] == 0 or (ach.progress.current_value // achf['step'] > old // achf['step']):
                                    v = ach.progress.current_value
                                    if achf['round']:
                                        whole = isinstance(v, int)
                                        v = v // achf['step'] * achf['step']
                                        if whole and v % 1 == 0:
                                            v = int(v)
                                    time_real = datetime.now().strftime(stg['strftime']) + ' (F)'
                                    time_action = datetime.fromtimestamp(get_stat_last_change(ach.progress.value['operand1']))
                                    time_action = time_action.strftime(stg['strftime']) + ' (F)'
                                    ch = {'ach_obj': ach, 'time_real': time_real, 'time_action': time_action, 'value': (v, achf['max'])}
                                    create_notification('progress_report', ch)
                                    break

                        if stg['bar_force_unlock']:
                            if ach.progress.real_value >= ach.progress.max_val and not ach.earned:
                                ach.earned = True
                                if stg['savetime_overwrite_locked']:
                                    ach.ts_first = None
                                    ach.ts_earliest = None
                                if ach.update_time(get_stat_last_change(ach.progress.value['operand1'])):
                                    ts_change.add(ach.name)
                                ach.force_unlock = True
                                force_unlocks[ach.name] = ach.earned_time
                                fu_change = True
                                filter_needed = True
                                achs_unlocked += 1
                                time_real = datetime.now().strftime(stg['strftime'])
                                time_action = datetime.fromtimestamp(get_stat_last_change(ach.progress.value['operand1']))
                                time_action = time_action.strftime(stg['strftime'])
                                if stg['forced_mark']:
                                    time_real += ' (F)'
                                    time_action += ' (F)'
                                ch = {'ach_obj': ach, 'time_real': time_real, 'time_action': time_action}
                                create_notification('unlock', ch)
                            elif ach.progress.real_value < ach.progress.max_val and ach.force_unlock and stg['forced_keep'] == 'no':
                                ach.earned = False
                                ach.earned_time = 0.0
                                ach.force_unlock = False
                                force_unlocks.pop(ach.name, None)
                                fu_change = True
                                filter_needed = True
                                if not stg['savetime_keep_locked']:
                                    ach.ts_first = None
                                    ach.ts_earliest = None
                                    ts_change.add(ach.name)
                                achs_unlocked -= 1
                                if stg['notif_lock']:
                                    time_real = datetime.now().strftime(stg['strftime'])
                                    time_action = datetime.fromtimestamp(get_stat_last_change(ach.progress.value['operand1']))
                                    time_action = time_action.strftime(stg['strftime'])
                                    if stg['forced_mark']:
                                        time_real += ' (F)'
                                        time_action += ' (F)'
                                    ch = {'ach_obj': ach, 'time_real': time_real, 'time_action': time_action}
                                    create_notification('lock', ch)

        if notifications_hidden > 0:
            send_notification('Too many notifications', f'{notifications_hidden} more notification(s) were hidden')
        if sound_to_play != 0:
            pygame.mixer.Sound.play(sounds[sound_to_play])

        if fu_change and stg['forced_keep'] == 'save':
            if not os.path.isdir(save_dir):
                os.makedirs(save_dir)
                if isinstance(source_extra, str) and source_extra[:5] == 'path:':
                    with open(f'{save_dir}/path.txt', 'w') as pathfile:
                        pathfile.write(source_extra[5:])
            with open(f'{save_dir}/{appid}_force.json', 'w') as forcefile:
                json.dump(force_unlocks, forcefile, indent=4)
        if ts_change and stg['save_timestamps']:
            for a in ts_change:
                saved_tstamps[a]['first'] = achs[ach_idxs[a]].ts_first
                saved_tstamps[a]['earliest'] = achs[ach_idxs[a]].ts_earliest
            if not os.path.isdir(save_dir):
                os.makedirs(save_dir)
                if isinstance(source_extra, str) and source_extra[:5] == 'path:':
                    with open(f'{save_dir}/path.txt', 'w') as pathfile:
                        pathfile.write(source_extra[5:])
            if ts_lost and os.path.isfile(f'{save_dir}/{appid}_time.json'):
                n = f"save/time_backup/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{achdata_source}_{appid}.json"
                if not os.path.isdir('save/time_backup'):
                    os.makedirs('save/time_backup')
                shutil.copy(f'{save_dir}/{appid}_time.json', n)
            with open(f'{save_dir}/{appid}_time.json', 'w') as timefile:
                json.dump(saved_tstamps, timefile, indent=4)
        if io_change:
            if not os.path.isdir(save_dir):
                os.makedirs(save_dir)
                if isinstance(source_extra, str) and source_extra[:5] == 'path:':
                    with open(f'{save_dir}/path.txt', 'w') as pathfile:
                        pathfile.write(source_extra[5:])
            with open(f'{save_dir}/{appid}_inc_only.json', 'w') as iofile:
                json.dump(increment_only, iofile, indent=4)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if header_extra == 'search':
                keys = pygame.key.get_pressed()
                if event.key == pygame.K_RETURN:
                    scroll_achs_copy = scroll
                    state_filter_copy = state_filter
                    scroll = 0
                    state_filter = 0
                    header_extra = 'search_results'
                    filter_needed = True
                elif event.key == pygame.K_BACKSPACE:
                    search_request = search_request[:-1]
                elif event.key == pygame.K_v and 1 in (keys[pygame.K_LCTRL], keys[pygame.K_RCTRL]):
                    if 1 in (keys[pygame.K_LCTRL], keys[pygame.K_RCTRL]):
                        search_request += pyperclip.paste()
                else:
                    search_request += event.unicode
                flip_required = True
            if event.key == pygame.K_DOWN:
                if viewing in ('achs', 'history_unlocks'):
                    scroll += 1
                elif viewing == 'stats':
                    scroll_stats += 1
                elif viewing == 'history':
                    scroll_history += 1
                flip_required = True
            elif event.key == pygame.K_UP:
                if viewing in ('achs', 'history_unlocks'):
                    scroll -= 1
                elif viewing == 'stats':
                    scroll_stats -= 1
                elif viewing == 'history':
                    scroll_history -= 1
                flip_required = True
            elif event.key == pygame.K_PAGEUP or (event.key == pygame.K_KP9 and not event.mod & pygame.KMOD_NUM):
                if viewing in ('achs', 'history_unlocks'):
                    scroll -= achs_to_show
                elif viewing == 'stats':
                    scroll_stats -= stats_to_show
                elif viewing == 'history':
                    scroll_history -= achs_to_show
                flip_required = True
            elif event.key == pygame.K_PAGEDOWN or (event.key == pygame.K_KP3 and not event.mod & pygame.KMOD_NUM):
                if viewing in ('achs', 'history_unlocks'):
                    scroll += achs_to_show
                elif viewing == 'stats':
                    scroll_stats += stats_to_show
                elif viewing == 'history':
                    scroll_history += achs_to_show
                flip_required = True
            elif event.key == pygame.K_HOME or (event.key == pygame.K_KP7 and not event.mod & pygame.KMOD_NUM):
                if viewing in ('achs', 'history_unlocks'):
                    scroll = 0
                elif viewing == 'stats':
                    scroll_stats = 0
                elif viewing == 'history':
                    scroll_history = 0
                flip_required = True
            elif event.key == pygame.K_END or (event.key == pygame.K_KP1 and not event.mod & pygame.KMOD_NUM):
                if viewing in ('achs', 'history_unlocks'):
                    scroll = len(achs_f) - achs_to_show
                elif viewing == 'stats':
                    scroll_stats = len(stats) - stats_to_show
                elif viewing == 'history':
                    scroll_history = len(history) - achs_to_show
                flip_required = True
            elif event.key == pygame.K_f and viewing == 'achs' and header_extra[:6] != 'search' and search_request == '':
                keys = pygame.key.get_pressed()
                if 1 in (keys[pygame.K_LCTRL], keys[pygame.K_RCTRL]):
                    header_extra = 'search'
                    flip_required = True
            elif event.key == pygame.K_d:
                keys = pygame.key.get_pressed()
                if not 1 in (keys[pygame.K_LCTRL], keys[pygame.K_RCTRL]):
                    continue
                if not 1 in (keys[pygame.K_LSHIFT], keys[pygame.K_RSHIFT]):
                    print('Using internal ach_dumper')
                    if keys[pygame.K_TAB] == 1:
                        stg_ad = load_settings(appid, achdata_source, True)
                    ach_dumper()
                elif viewing in ('achs', 'stats', 'history_unlocks'):
                    if os.path.isfile('ach_dumper.py'):
                        command = f'python ach_dumper.py'
                        print('Using ach_dumper.py')
                    elif os.path.isfile('ach_dumper.exe'):
                        command = f'ach_dumper.exe'
                        print('Using ach_dumper.exe')
                    else:
                        print('Ach dumper not found')
                        continue
                    command += ' ' + appid + ' ' + achdata_source
                    if achdata_source == 'codex':
                        command += ' a' * source_extra
                    elif source_extra != None:
                        command += f' "{source_extra}"'
                    else:
                        command += ' /'
                    if viewing == 'history_unlocks':
                        command += ' -u -t'
                    else:
                        command += ' -u' * (state_filter == 1)
                        command += ' -l' * (state_filter == 2)
                        command += ' -r' * stg['sort_by_rarity']
                        command += ' -uot' * stg['unlocks_on_top']
                        command += ' -t' * stg['unlocks_timesort']
                    command += ' -s' + stg['secrets'][0]
                    command += ' -h' * hide_all_secrets
                    command += ' -lh' * stg['secrets_listhide']
                    command += ' -s' * (viewing == 'stats')
                    os.system(command)
            elif event.key == pygame.K_BACKQUOTE and header_extra != 'search':
                xnote = ''
                if achdata_source == 'goldberg' and source_extra == 'f':
                    xnote = ' ("GSE Saves" fork)'
                elif achdata_source == 'codex':
                    xnote = {False: ' (Documents)', True: ' (AppData)'}
                    xnote = xnote[source_extra]
                elif (isinstance(source_extra, str) and source_extra[:5] == 'path:'):
                    xnote = ' (' + save_dir.split('_')[-1] + ')'
                print(f'\n - Tracking: {appid} / {achdata_source} / {source_extra}{xnote}')
                print(' - Version: v1.5.1')

        elif event.type == pygame.MOUSEMOTION:
            if viewing in ('achs', 'history', 'history_unlocks'):
                old_hover_ach = hover_ach
                hover_ach = None
                for i in range(achs_to_show + 1):
                    if pygame.Rect(10 - stg['frame_size'], header_h + i * 74 - stg['frame_size'], stg['window_size_x'] - 20 + stg['frame_size'], 64 + stg['frame_size'] * 2).collidepoint(event.pos):
                        hover_ach = i
                        break
                if hover_ach != old_hover_ach:
                    flip_required = True

        elif event.type == pygame.MOUSEBUTTONDOWN:
            flip_required = True

            if event.button == 3:
                if viewing == 'achs':
                    if ((header_extra == '' and btn_locs['filter'][state_filter].collidepoint(event.pos)) or \
                       (header_extra == 'search_results' and btn_locs['filter_search'][state_filter].collidepoint(event.pos))):
                        header_extra = 'sort'
                    elif header_extra == 'sort' and pygame.Rect(stg['window_size_x'] - 160, 10, 22, 22).collidepoint(event.pos):
                        header_extra = 'secrets_reveal'
                elif viewing == 'history':
                    if hover_ach != None and scroll_history + hover_ach < len(history) and 'ach' in history[scroll_history + hover_ach]:
                        ach = history[scroll_history + hover_ach]['ach']
                        if not (stg['secrets'] == 'hide' and ach.hidden) or ach.earned:
                            if state_filter != 0:
                                state_filter = 0
                                achs_f = filter_achs(achs, state_filter, stg)
                            scroll_history = 0
                            viewing = 'achs'
                            for entry in history:
                                if entry['unread'] == 0:
                                    break
                                entry['unread'] = 0
                            for i in range(len(achs_f)):
                                if achs_f[i].name == ach.name:
                                    scroll = i
                                    break
            if event.button != 1:
                continue

            if viewing == 'achs':
                if header_extra == 'search':
                    if pygame.Rect(stg['window_size_x'] - 128, 10, 22, 22).collidepoint(event.pos):
                        search_request = ''
                        header_extra = ''
                    elif search_request == '':
                        pass
                    elif pygame.Rect(stg['window_size_x'] - 96, 10, 22, 22).collidepoint(event.pos):
                        for i in range(scroll - 1, -1, -1):
                            if check_search_match(achs_f[i], search_request):
                                scroll = i
                                break
                    elif pygame.Rect(stg['window_size_x'] - 64, 10, 22, 22).collidepoint(event.pos):
                        for i in range(scroll + 1, len(achs_f)):
                            if check_search_match(achs_f[i], search_request):
                                scroll = i
                                break
                    elif pygame.Rect(stg['window_size_x'] - 32, 10, 22, 22).collidepoint(event.pos):
                        scroll_achs_copy = scroll
                        state_filter_copy = state_filter
                        scroll = 0
                        state_filter = 0
                        header_extra = 'search_results'
                        filter_needed = True
                elif header_extra == 'search_results':
                    if btn_locs['filter_search'][state_filter].collidepoint(event.pos):
                        state_filter += 1
                        if state_filter > 2:
                            state_filter = 0
                        filter_needed = True
                        scroll = 0
                    elif pygame.Rect(stg['window_size_x'] - 32, 10, 22, 22).collidepoint(event.pos):
                        search_request = ''
                        header_extra = ''
                        filter_needed = True
                        state_filter = state_filter_copy
                        scroll = scroll_achs_copy
                elif header_extra == 'sort':
                    if pygame.Rect(stg['window_size_x'] - 160, 10, 22, 22).collidepoint(event.pos):
                        header_extra = 'secrets'
                    elif pygame.Rect(stg['window_size_x'] - 128, 10, 22, 22).collidepoint(event.pos):
                        stg['sort_by_rarity'] = not stg['sort_by_rarity']
                        filter_needed = True
                    elif pygame.Rect(stg['window_size_x'] - 96, 10, 22, 22).collidepoint(event.pos):
                        stg['unlocks_on_top'] = not stg['unlocks_on_top']
                        filter_needed = True
                    elif pygame.Rect(stg['window_size_x'] - 64, 10, 22, 22).collidepoint(event.pos):
                        stg['unlocks_timesort'] = not stg['unlocks_timesort']
                        filter_needed = True
                    elif pygame.Rect(stg['window_size_x'] - 32, 10, 22, 22).collidepoint(event.pos):
                        if search_request == '':
                            header_extra = ''
                        else:
                            header_extra = 'search_results'
                elif header_extra == 'secrets':
                    if pygame.Rect(stg['window_size_x'] - 160, 10, 22, 22).collidepoint(event.pos):
                        stg['secrets_listhide'] = not stg['secrets_listhide']
                        filter_needed = True
                    elif pygame.Rect(stg['window_size_x'] - 128, 10, 22, 22).collidepoint(event.pos):
                        stg['secrets'] = 'normal'
                        filter_needed = True
                    elif pygame.Rect(stg['window_size_x'] - 96, 10, 22, 22).collidepoint(event.pos):
                        stg['secrets'] = 'hide'
                        filter_needed = True
                    elif pygame.Rect(stg['window_size_x'] - 64, 10, 22, 22).collidepoint(event.pos):
                        stg['secrets'] = 'bottom'
                        filter_needed = True
                    elif pygame.Rect(stg['window_size_x'] - 32, 10, 22, 22).collidepoint(event.pos):
                        header_extra = 'sort'
                elif header_extra == 'secrets_reveal':
                    if pygame.Rect(stg['window_size_x'] - 96, 10, 22, 22).collidepoint(event.pos):
                        hide_all_secrets = not hide_all_secrets
                        reveal_secrets = False
                        filter_needed = True
                    elif pygame.Rect(stg['window_size_x'] - 64, 10, 22, 22).collidepoint(event.pos):
                        reveal_secrets = not reveal_secrets
                        hide_all_secrets = False
                        filter_needed = True
                    elif pygame.Rect(stg['window_size_x'] - 32, 10, 22, 22).collidepoint(event.pos):
                        header_extra = 'sort'
                else:
                    if btn_locs['filter'][state_filter].collidepoint(event.pos):
                        state_filter += 1
                        if state_filter > 2:
                            state_filter = 0
                        filter_needed = True
                        scroll = 0
                    elif btn_locs['stats'].collidepoint(event.pos):
                        viewing = 'stats'
                    elif btn_locs['history'][state_filter].collidepoint(event.pos) and stg['history_length'] > -1:
                        viewing = 'history'
                if len(achs_f) > achs_to_show and event.pos[0] >= stg['window_size_x'] - 10 and event.pos[1] >= header_h:
                    mouse_scrolling = True
            elif viewing == 'stats':
                if btn_locs['achs'].collidepoint(event.pos):
                    viewing = 'achs'
                if len(stats) > stats_to_show and event.pos[0] >= stg['window_size_x'] - 10 and event.pos[1] >= header_h:
                    mouse_scrolling = True
                pos = pygame.mouse.get_pos()
                if 10 <= pos[0] < stg['window_size_x'] - 10 and header_h <= pos[1] < header_h + (len(stats) - scroll_stats) * stg['font_line_distance_regular']:
                    s = (pos[1] - header_h) // stg['font_line_distance_regular'] + scroll_stats
                    s = list(stats.keys())[s]
                    s = stats[s]
                    print()
                    try:
                        print(s.dname)
                    except Exception as ex:
                        print(f'Error when printing stat name: {type(ex).__name__}')
                    if len(stat_dnames) > 0:
                        print(f' - API name: {s.name}')
                    if s.default != 0:
                        print(f' - Default: {s.default}')
                    if achdata_source == 'goldberg':
                        t = get_stat_last_change(s.name)
                        if t != None and t != 'Retry':
                            print(f" - Last change: {datetime.fromtimestamp(t).strftime(stg['strftime'])}")
                    if s.inc_only:
                        print(' - Increment-only')
                        if s.value != s.real_value:
                            print(f' - Real value: {s.real_value}')
            elif viewing == 'history':
                if len(history) > achs_to_show and event.pos[0] >= stg['window_size_x'] - 10 and event.pos[1] >= header_h:
                    mouse_scrolling = True
                elif btn_locs['back'].collidepoint(event.pos):
                    for entry in history:
                        if entry['unread'] == 0:
                            break
                        entry['unread'] = 0
                    scroll_history = 0
                    viewing = 'achs'
                elif btn_locs['clear'].collidepoint(event.pos):
                    if stg['history_clearable']:
                        scroll_history = 0
                        history.clear()
                    else:
                        print('Clear history button was disabled in settings')
                elif btn_locs['history_unlocks'].collidepoint(event.pos):
                    for entry in history:
                        if entry['unread'] == 0:
                            break
                        entry['unread'] = 0
                    scroll_achs_copy = scroll
                    scroll = 0
                    scroll_history = 0
                    filter_needed = True
                    viewing = 'history_unlocks'
            elif viewing == 'history_unlocks':
                if len(achs_f) > achs_to_show and event.pos[0] >= stg['window_size_x'] - 10 and event.pos[1] >= header_h:
                    mouse_scrolling = True
                elif btn_locs['back'].collidepoint(event.pos):
                    scroll = scroll_achs_copy
                    filter_needed = True
                    # viewing = 'achs'
                    viewing = 'history'
                # elif pygame.Rect(stg['window_size_x'] - 162, 10, 88, 22).collidepoint(event.pos):
                    # scroll = scroll_achs_copy
                    # achs_f, secrets_hidden = filter_achs(achs, state_filter, stg)
                    # viewing = 'history'
            if viewing in ('achs', 'history', 'history_unlocks') and hover_ach != None:
                if viewing == 'history' and scroll_history + hover_ach < len(history) and 'ach' in history[scroll_history + hover_ach]:
                    a = history[scroll_history + hover_ach]['ach']
                elif viewing != 'history' and scroll + hover_ach < len(achs_f):
                    a = achs_f[scroll + hover_ach]
                else:
                    continue
                if a.icon_gray == 'hidden_dummy_ach_icon':
                    continue

                keys = pygame.key.get_pressed()
                show_hidden_info = not a.hidden or (a.earned and not hide_all_secrets) or reveal_secrets or 1 in (keys[pygame.K_LSHIFT], keys[pygame.K_RSHIFT])
                if stg['secrets_listhide'] and not show_hidden_info:
                    if a.rarity != -1.0:
                        print()
                        print(stg['hidden_title'])
                        print(f' - Rarity: {a.rarity}%')
                    continue

                print()
                try:
                    print(a.display_name_np)
                    if show_hidden_info and a.has_desc:
                        d = a.description_l
                        if stg['unlockrates'] == 'desc' and a.rarity != -1.0:
                            d = d[: -len(a.rarity_text)]
                        print(d)
                except Exception as ex:
                    print(f'Error when printing name/description: {type(ex).__name__}')

                try:
                    if show_hidden_info:
                        print(f' - API name: {a.name}')
                    if isinstance(a.display_name, dict):
                        print(f" - Languages: {', '.join(a.display_name)}")
                        if a.has_desc and isinstance(a.description, dict) and set(a.display_name) != set(a.description):
                            print(f" - Languages (desc): {', '.join(a.description)}")
                    print(f' - Hidden: {a.hidden}')
                    if a.progress != None and 'operand1' in a.progress.value and show_hidden_info:
                        s = a.progress.value['operand1']
                        if s in stats:
                            s = stats[s].dname
                        print(f' - Progress stat: {s}')
                        if a.progress.min_val != 0:
                            print(f' - Progress min val: {a.progress.min_val}')
                        if a.progress.value['operand1'] in force_progress:
                            for f in force_progress[a.progress.value['operand1']]:
                                if f['ach'] == a.name:
                                    step = f['step'] if f['step'] % 1 != 0 else int(f['step'])
                                    print(f" - Forced progress notifications enabled ({step}{'r' * f['round']})")
                                    break
                    if (stg['unlockrates'] == 'load' or (stg['unlockrates'] == 'desc' and (not show_hidden_info or not a.has_desc))) and a.rarity != -1.0:
                        print(f' - Rarity: {a.rarity}%')
                    if not stg['show_timestamps'] and a.earned:
                        print(f' - Unlocked: {a.get_time(stg)}')
                except Exception as ex:
                    print(f'Error when printing achievement info: {type(ex).__name__}')

                if stg['ctrl_click'] and isinstance(a.display_name, dict) and 1 in (keys[pygame.K_LCTRL], keys[pygame.K_RCTRL]):
                    try:
                        l = input('Choose a language: ')
                    except RuntimeError:
                        l = None
                    if l in a.display_name:
                        try:
                            print(f' - {a.display_name[l]}')
                            if a.has_desc and show_hidden_info:
                                d = a.description[l]
                                if stg['unlockrates'] == 'desc' and a.rarity != -1.0:
                                    d = d[: -len(a.rarity_text)]
                                print(f' - {d}')
                        except Exception as ex:
                            print(f'Error when printing name/description: {type(ex).__name__}')


        elif event.type == pygame.MOUSEBUTTONUP:
            mouse_scrolling = False

        elif event.type == pygame.MOUSEWHEEL:
            if viewing in ('achs', 'history_unlocks'):
                scroll -= event.y
            elif viewing == 'stats':
                scroll_stats -= event.y
            elif viewing == 'history':
                scroll_history -= event.y
            flip_required = True
 
        elif event.type == pygame.ACTIVEEVENT:
            if event.gain != 1 and hover_ach != None:
                hover_ach = None
                flip_required = True

    if filter_needed:
        if viewing != 'history_unlocks':
            achs_f = filter_achs(achs, state_filter, stg)
            if search_request != '' and header_extra != 'search':
                results = []
                dummy_place = -1
                for i in range(len(achs_f)):
                    a = achs_f[i]
                    if check_search_match(a, search_request):
                        results.append(a)
                        if a.icon_gray == 'hidden_dummy_ach_icon':
                            dummy_place = len(results) - 1

                if dummy_place != -1:
                    hidden_results = len(results) - 1 - dummy_place
                    dummy_desc = f'There are {hidden_results} more hidden achievements'
                    if hidden_results == 1:
                        dummy_desc = 'There is 1 more hidden achievement'
                    if hidden_results > 0:
                        results[dummy_place].description_l = dummy_desc
                    else:
                        results.pop(dummy_place)
                achs_f = results
        else:
            fake_stg = {'unlockrates': 'none', 'secrets': 'normal',
                'unlocks_on_top': False, 'unlocks_timesort': True,
                'savetime_shown': stg['savetime_shown']}
            achs_f = filter_achs(achs, 1, fake_stg)
        filter_needed = False

    y = pygame.mouse.get_pos()[1]
    if viewing in ('achs', 'history_unlocks'):
        if mouse_scrolling:
            oldscr = scroll
            scroll = (y - header_h) * (len(achs_f) - achs_to_show) // (stg['window_size_y'] - header_h - 1)
            if scroll != oldscr:
                flip_required = True
        if scroll > len(achs_f) - achs_to_show:
            scroll = len(achs_f) - achs_to_show
        if scroll < 0:
            scroll = 0
    elif viewing == 'stats':
        if mouse_scrolling:
            oldscr = scroll_stats
            scroll_stats = (y - header_h) * (len(stats) - stats_to_show) // (stg['window_size_y'] - header_h - 1)
            if scroll_stats != oldscr:
                flip_required = True
        if scroll_stats > len(stats) - stats_to_show:
            scroll_stats = len(stats) - stats_to_show
        if scroll_stats < 0:
            scroll_stats = 0
    elif viewing == 'history':
        if mouse_scrolling:
            oldscr = scroll_history
            scroll_history = (y - header_h) * (len(history) - achs_to_show) // (stg['window_size_y'] - header_h - 1)
            if scroll_history != oldscr:
                flip_required = True
        if scroll_history > len(history) - achs_to_show:
            scroll_history = len(history) - achs_to_show
        if scroll_history < 0:
            scroll_history = 0

    while stg['history_length'] != 0 and len(history) > 0 and len(history) > stg['history_length']:
        history.pop(-1)

    if flip_required:
        if viewing in ('achs', 'history_unlocks'):
            draw_achs()
        elif viewing == 'stats':
            draw_stats()
        elif viewing == 'history':
            draw_history()
        flip_required = False

    time.sleep(stg['delay_sleep'])