import time
from datetime import datetime
import struct
import pygame
from showtext import long_text
pygame.font.init()

class Achievement:
    def __init__(self, achdata, player_achs=None, stats=None, ach_percentages=None, stg=None):
        self.name = achdata['name']
        self.display_name = achdata['displayName']
        self.description = achdata['description']
        self.hidden = achdata['hidden'] == '1'

        if 'icon' in achdata:
            self.icon = achdata['icon']
        else:
            self.icon = None
        if 'icon_gray' in achdata:
            self.icon_gray = achdata['icon_gray']
        elif self.icon != None:
            self.icon_gray = self.icon
        else:
            self.icon_gray = None

        self.progress = None
        if 'progress' in achdata:
            self.progress = AchievementProgress(achdata['progress'], stats)

        self.progress_reported = None
        if player_achs != None and self.name in player_achs:
            self.earned = player_achs[self.name]['earned']
            self.earned_time = float(player_achs[self.name]['earned_time'])
            if 'progress' in player_achs[self.name] and 'max_progress' in player_achs[self.name]:
                self.progress_reported = (player_achs[self.name]['progress'], player_achs[self.name]['max_progress'])
        else:
            self.earned = False
            self.earned_time = 0.0

        self.force_unlock = False
        if stg != None and stg['bar_force_unlock'] and self.progress != None and self.progress.real_value >= self.progress.max_val and not self.earned:
            self.earned = True
            if stg['forced_time_load'] == 'now':
                self.earned_time = time.time()
            else:
                self.earned_time = stats[self.progress.value['operand1']].fchecker.last_check
            self.force_unlock = True

        self.ts_first = None
        self.ts_earliest = None
        if self.earned:
            self.ts_first = self.earned_time
            self.ts_earliest = self.earned_time

        self.has_desc = isinstance(self.display_name, str) or 'english' in self.description
        self.long_desc = False
        self.long_hidden_desc = False

        self.language = 'english'
        if isinstance(self.display_name, str):
            self.display_name_l = self.display_name
            self.description_l = self.description
        else:
            if stg != None:
                for l in stg['language']:
                    if l in self.display_name and l in self.description:
                        self.language = l
                        break
            self.display_name_l = self.display_name[self.language]
            if self.has_desc:
                self.description_l = self.description[self.language]

        self.display_name_np = self.display_name_l
        if stg['unlockrates'] != 'none' and ach_percentages != None:
            for p in ach_percentages:
                if p['name'] == self.name:
                    self.rarity = round(p['percent'] * 10) / 10
                    self.rarity_text = str(self.rarity)
                    if not '.' in self.rarity_text:
                        self.rarity_text += '.0'
                    self.rarity_text = f' ({self.rarity_text}%)'

    def get_time(self, savetime_shown, forced_mark, savetime_mark):
        ts = self.earned_time
        if savetime_shown == 'first':
            ts = self.ts_first
        elif savetime_shown == 'earliest':
            ts = self.ts_earliest
        dt = datetime.fromtimestamp(ts)
        tstring = dt.strftime('%d %b %Y %H:%M:%S')
        if savetime_mark and ts != self.earned_time:
            tstring += ' (S)'
        if forced_mark and self.force_unlock:
            tstring += ' (F)'
        return tstring

    def update_time(self, t):
        save_changed = False
        self.earned_time = t
        if self.ts_first == None:
            self.ts_first = t
            save_changed = True
        if self.ts_earliest == None or t < self.ts_earliest:
            self.ts_earliest = t
            save_changed = True
        return save_changed

    def get_ts(self, savetime_shown):
        if savetime_shown == 'first':
            return self.ts_first
        elif savetime_shown == 'earliest':
            return self.ts_earliest
        else:
            return self.earned_time

class AchievementProgress:
    def __init__(self, progressdata, stats=None):
        self.value = progressdata['value']

        self.min_val = float(progressdata['min_val'])
        self.max_val = float(progressdata['max_val'])
        if self.value['operand1'] in stats:
            self.min_val = stats[self.value['operand1']].to_stat_type((progressdata['min_val']))
            self.max_val = stats[self.value['operand1']].to_stat_type((progressdata['max_val']))

        has_unknown_stats = False
        if len(self.value) == 2 and self.value['operation'] == 'statvalue':
            has_unknown_stats = not self.value['operand1'] in stats
        self.support, self.support_error = self.check_support(stats, has_unknown_stats)
        
        if stats != None:
            self.calculate(stats)
        else:
            self.current_value = self.min_val
            self.real_value = 0

    def calculate(self, stats):
        if self.support:
            self.current_value = stats[self.value['operand1']].value
            if self.current_value > self.max_val:
                self.current_value = self.max_val
            self.real_value = self.current_value
            if self.current_value < self.min_val:
                self.current_value = self.min_val
        else:
            self.current_value = self.min_val
            self.real_value = 0

    def get_without_min(self):
        return (self.current_value - self.min_val, self.max_val - self.min_val)

    def check_support(self, stats, has_unknown_stats):
        if not (len(self.value) == 2 and self.value['operation'] == 'statvalue'):
            return (False, 'Unsupported value formula')
        elif has_unknown_stats:
            return (False, 'Unknown stat')
        elif not stats[self.value['operand1']].type in ('int', 'float'):
            return (False, 'Unsupported stat type')
        return (True, None)

def filter_achs(achs, state, stg):
    achs_f = []
    secrets_hidden = 0

    achs_copy = []
    for ach in achs:
        achs_copy.append(ach)
    achs = achs_copy

    if stg['unlockrates'] != 'none' and stg['sort_by_rarity']:
        achs.sort(key=lambda a : a.rarity, reverse=True)

    for ach in achs:
        if stg['hide_secrets'] and ach.hidden and not ach.earned:
            secrets_hidden += 1
            continue
        if state == 1 and not ach.earned:
            continue
        if state == 2 and ach.earned:
            continue
        achs_f.append(ach)
    if state != 1 and secrets_hidden > 0:
        dummy_desc = f'There are {secrets_hidden} more hidden achievements'
        if secrets_hidden == 1:
            dummy_desc = 'There is 1 more hidden achievement'
        achs_f.append(Achievement({'name': None, 'displayName': {'english': 'Hidden achievements'}, 'description': {'english': dummy_desc}, 'icon': None, 'icon_gray': 'hidden_dummy_ach_icon', 'hidden': '0'}))
    if stg['unlocks_on_top']:
        u = 1
        for u in range(len(achs_f)):
            if not achs_f[u].earned:
                break
            if u == len(achs_f) - 1:
                u += 1
        for i in range(u + 1, len(achs_f)):
            if achs_f[i].earned:
                achs_f.insert(u, achs_f.pop(i))
                u += 1
        if stg['unlocks_timesort']:
            unlocked_slice = achs_f[:u]
            unlocked_slice.sort(key=lambda a : a.get_ts(stg['savetime_shown']), reverse=True)
            achs_f = unlocked_slice + achs_f[u:]
    return (achs_f, secrets_hidden)

def update_achs(achs, newdata, achsfile, stg):
    changes = []
    for ach in achs:
        change = {'ach': ach.display_name_l, 'ach_api': ach.name, 'ach_obj': ach}
        dt_real = datetime.now()
        change['time_real'] = dt_real.strftime('%d %b %Y %H:%M:%S')
        if achsfile != None and achsfile.last_check != None:
            dt_action = datetime.fromtimestamp(achsfile.last_check)
            change['time_action'] = dt_action.strftime('%d %b %Y %H:%M:%S')
        elif achsfile == None:
            change['time_action'] = change['time_real']

        if newdata != None and ach.name in newdata:
            if 'progress' in newdata[ach.name] and 'max_progress' in newdata[ach.name]:
                if not newdata[ach.name]['earned'] and (ach.progress_reported != (newdata[ach.name]['progress'], newdata[ach.name]['max_progress'])):
                    ach.progress_reported = (newdata[ach.name]['progress'], newdata[ach.name]['max_progress'])
                    prg_change = {}
                    for k in change.keys():
                        prg_change[k] = change[k]
                    prg_change['type'] = 'progress_report'
                    prg_change['value'] = ach.progress_reported
                    changes.append(prg_change)
            else:
                ach.progress_reported = None

            if ach.earned != newdata[ach.name]['earned'] or (ach.force_unlock and newdata[ach.name]['earned']):
                if not ach.earned or ach.force_unlock:
                    change['ts_change'] = ach.update_time(newdata[ach.name]['earned_time'])
                    change['type'] = 'unlock'
                    change['was_forced'] = False
                    dt_action = datetime.fromtimestamp(ach.earned_time)
                    change['time_action'] = dt_action.strftime('%d %b %Y %H:%M:%S')
                    if ach.force_unlock:
                        ach.force_unlock = False
                        change['was_forced'] = True
                else:
                    ach.earned_time = 0.0
                    change['type'] = 'lock'
                    change['lock_all'] = False
                    if not stg['savetime_keep_locked']:
                        ach.ts_first = None
                        ach.ts_earliest = None
                        change['ts_change'] = True
                ach.earned = newdata[ach.name]['earned']
            elif ach.earned_time != newdata[ach.name]['earned_time']:
                change['type'] = 'time'
                change['old'] = ach.earned_time
                change['ts_change'] = ach.update_time(newdata[ach.name]['earned_time'])
                change['new'] = ach.earned_time
        elif not ach.force_unlock:
            if ach.earned:
                change['type'] = 'lock'
                if newdata == None:
                    change['lock_all'] = True
                    change['time_action'] = change['time_real']
                    ach.progress_reported = None
                else:
                    change['lock_all'] = False
            ach.earned = False
            ach.earned_time = 0.0

        change['ach_obj'] = ach

        if 'type' in change.keys():
            changes.append(change)

    return (achs, changes)

def convert_achs_format(data, source, achs_crc32=None):
    conv = {}
    if source in ('codex', 'ali213'):
        names = {'Achieved': 'Achieved', 'CurProgress': 'CurProgress',
                 'MaxProgress': 'MaxProgress', 'UnlockTime': 'UnlockTime'}
        if source == 'ali213':
            names['Achieved'] = 'HaveAchieved'
            names['CurProgress'] = 'nCurProgress'
            names['MaxProgress'] = 'nMaxProgress'
            names['UnlockTime'] = 'HaveAchievedTime'
        reading_ach = None
        for l in data.split('\n'):
            if len(l) > 0 and l[0] == '[' and l[-1] == ']':
                reading_ach = l[1:-1]
                if reading_ach != 'SteamAchievements':
                    conv[reading_ach] = {}
            elif reading_ach != None:
                spl = l.split('=')
                if len(spl) != 2 or reading_ach == 'SteamAchievements':
                    continue
                if spl[0] == names['Achieved']:
                    conv[reading_ach]['earned'] = bool(int(spl[1]))
                elif spl[0] == names['CurProgress'] and spl[1] != '0':
                    dotspl = spl[1].split('.')
                    if len(dotspl) == 1:
                        conv[reading_ach]['progress'] = int(spl[1])
                    else:
                        conv[reading_ach]['progress'] = float(spl[1])
                elif spl[0] == names['MaxProgress'] and spl[1] != '0':
                    dotspl = spl[1].split('.')
                    if len(dotspl) == 1:
                        conv[reading_ach]['max_progress'] = int(spl[1])
                    else:
                        conv[reading_ach]['max_progress'] = float(spl[1])
                if spl[0] == names['UnlockTime']:
                    conv[reading_ach]['earned_time'] = float(spl[1])
    elif source == 'sse':
        for i in range(struct.unpack('i', data[:4])[0]):
            c = struct.unpack('I', data[4 + 24 * i : 8 + 24 * i])[0]
            if c in achs_crc32:
                achname = achs_crc32[c]
                conv[achname] = {}
                conv[achname]['earned'] = bool(struct.unpack('i', data[24 + 24 * i : 28 + 24 * i])[0])
                conv[achname]['earned_time'] = float(struct.unpack('i', data[12 + 24 * i : 16 + 24 * i])[0])
    elif source == 'steam':
        for ach in data:
            achname = ach['apiname']
            conv[achname] = {}
            conv[achname]['earned'] = ach['achieved']
            conv[achname]['earned_time'] = ach['unlocktime']
    else:
        return {}
    return conv