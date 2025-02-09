import time
from datetime import datetime
import struct
from showtext import long_text
from experimental import *

class Achievement:
    def __init__(self, achdata, player_achs={}, stats={}, ach_percentages={}, stg=None):
        self.name = achdata['name']
        self.display_name = achdata['displayName']
        self.description = achdata['description']
        self.hidden = int(achdata['hidden']) == 1

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
        if 'progress' in achdata and isinstance(achdata['progress'], dict):
            self.progress = AchievementProgress(achdata['progress'], stats)

        self.earned = False
        self.earned_time = 0.0
        self.progress_reported = None
        if self.name in player_achs:
            self.earned = player_achs[self.name]['earned']
            self.earned_time = float(player_achs[self.name]['earned_time'])
            if 'progress' in player_achs[self.name] and 'max_progress' in player_achs[self.name]:
                self.progress_reported = (player_achs[self.name]['progress'], player_achs[self.name]['max_progress'])

        self.force_unlock = False
        if stg != None and stg['bar_force_unlock'] and self.progress != None and self.progress.real_value >= self.progress.max_val and not self.earned:
            self.earned = True
            if stg['forced_time_load'] == 'now':
                self.earned_time = time.time()
            else:
                self.earned_time = 'stat_last_change'
            self.force_unlock = True

        self.ts_first = None
        self.ts_earliest = None
        if self.earned:
            self.ts_first = self.earned_time
            self.ts_earliest = self.earned_time

        self.has_desc = isinstance(self.display_name, str) or 'english' in self.description
        self.long_desc = False

        self.language, self.display_name_l = self.pick_language(self.display_name, stg)
        if self.has_desc:
            self.language_d, self.description_l = self.pick_language(self.description, stg)
        else:
            self.language_d = self.language

        self.display_name_np = self.display_name_l
        self.rarity = -1.0
        self.rarity_text = ''
        self.rare = False
        if self.name in ach_percentages:
            self.rarity = float(ach_percentages[self.name])
            self.rarity_text = ' (' + str(self.rarity) + '%)'
            if stg != None and self.rarity != -1.0 and self.rarity < stg['rare_below']:
                self.rare = True

    def pick_language(self, data, stg):
        language = 'english'
        if isinstance(data, str):
            translation = data
        else:
            if stg != None:
                for l in stg['language']:
                    if l in data:
                        language = l
                        break
            translation = data[language]
        return (language, translation)

    def get_ts(self, savetime_shown):
        if savetime_shown == 'first':
            return self.ts_first
        elif savetime_shown == 'earliest':
            return self.ts_earliest
        else:
            return self.earned_time

    def get_time(self, stg):
        ts = self.get_ts(stg['savetime_shown'])
        dt = datetime.fromtimestamp(ts)
        tstring = dt.strftime(stg['strftime'])
        if stg['savetime_mark'] and ts != self.earned_time:
            tstring += ' (S)'
        if stg['forced_mark'] and self.force_unlock:
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

    def to_json(self):
        j = {}
        j['hidden'] = '1' if self.hidden else '0'
        j['displayName'] = self.display_name
        j['description'] = self.description
        if self.icon != None:
            j['icon'] = self.icon
        if self.icon_gray != None:
            j['icon_gray'] = self.icon_gray
        j['name'] = self.name
        if self.progress != None:
            j['progress'] = {}
            j['progress']['min_val'] = str(self.progress.min_val)
            j['progress']['max_val'] = str(self.progress.max_val)
            j['progress']['value'] = self.progress.value
        return j

class AchievementProgress:
    def __init__(self, progressdata, stats):
        self.value = progressdata['value']

        self.support, self.support_error = self.check_support(stats)

        self.min_val = float(progressdata['min_val'])
        self.max_val = float(progressdata['max_val'])
        if self.support:
            self.min_val = stats[self.value['operand1']].to_stat_type(progressdata['min_val'])
            self.max_val = stats[self.value['operand1']].to_stat_type(progressdata['max_val'])
        
        self.calculate(stats)

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

    def check_support(self, stats):
        if not (len(self.value) == 2 and self.value['operation'] == 'statvalue'):
            return (False, 'Unsupported value formula')
        if not self.value['operand1'] in stats:
            return (False, 'Unknown stat')
        if not stats[self.value['operand1']].type in ('int', 'float', 'avgrate_st'):
            return (False, 'Unsupported stat type')
        return (True, None)

def filter_achs(achs, state, stg):
    achs_f = []
    secrets_hidden = 0
    first_lock = 0

    achs = achs.copy()

    if stg['unlockrates'] != 'none' and stg['sort_by_rarity']:
        achs.sort(key=lambda a : a.rarity, reverse=True)

    for ach in achs:
        if state == 1 and not ach.earned:
            continue
        if state == 2 and ach.earned:
            continue

        if stg['secrets'] != 'normal' and ach.hidden and not ach.earned:
            secrets_hidden += 1
            if stg['secrets'] == 'hide':
                continue
            elif stg['secrets'] == 'bottom':
                achs_f.append(ach)
                continue
 
        if stg['unlocks_on_top'] and ach.earned:
            achs_f.insert(first_lock, ach)
            first_lock += 1
            continue
        
        insert_at = len(achs_f)
        if stg['secrets'] == 'bottom':
            insert_at -= secrets_hidden
        achs_f.insert(insert_at, ach)

    if state != 1 and secrets_hidden > 0 and not (stg['secrets'] == 'bottom' and not stg['secrets_bottom_count']):
        insert_at = len(achs_f)
        if stg['secrets'] == 'bottom':
            insert_at = -secrets_hidden

        dummy_desc = f'There are {secrets_hidden} more hidden achievements'
        if secrets_hidden == 1:
            dummy_desc = 'There is 1 more hidden achievement'
        achs_f.insert(insert_at, Achievement({'name': None, 'displayName': {'english': 'Hidden achievements'}, 'description': {'english': dummy_desc},
                                              'icon': None, 'icon_gray': 'hidden_dummy_ach_icon', 'hidden': '0'}))

    if stg['unlocks_timesort'] and (stg['unlocks_on_top'] or state == 1) and state != 2:
        if state == 1:
            first_lock = len(achs_f)
        unlocked_slice = achs_f[:first_lock]
        unlocked_slice.reverse()
        unlocked_slice.sort(key=lambda a : a.get_ts(stg['savetime_shown']), reverse=True)
        achs_f = unlocked_slice + achs_f[first_lock:]

    return achs_f

def update_achs(achs, newdata, achsfile, stg):
    changes = []
    for ach in achs:
        change = {'ach': ach.display_name_l, 'ach_api': ach.name, 'ach_obj': ach}
        dt_real = datetime.now()
        change['time_real'] = dt_real.strftime(stg['strftime'])
        if achsfile != None and achsfile.last_check != None:
            dt_action = datetime.fromtimestamp(achsfile.last_check)
            change['time_action'] = dt_action.strftime(stg['strftime'])
        else:
            change['time_action'] = change['time_real']

        if newdata != None and ach.name in newdata:
            if not 'earned' in newdata[ach.name]:
                newdata[ach.name]['earned'] = False
            if not 'earned_time' in newdata[ach.name]:
                newdata[ach.name]['earned_time'] = 0.0

            if 'progress' in newdata[ach.name] and 'max_progress' in newdata[ach.name]:
                if ach.progress_reported != (newdata[ach.name]['progress'], newdata[ach.name]['max_progress']):
                    ach.progress_reported = (newdata[ach.name]['progress'], newdata[ach.name]['max_progress'])
                    if not newdata[ach.name]['earned'] and not ach.force_unlock:
                        prg_change = change.copy()
                        prg_change['type'] = 'progress_report'
                        prg_change['value'] = ach.progress_reported
                        changes.append(prg_change)
            else:
                ach.progress_reported = None

            if (not ach.force_unlock and ach.earned != newdata[ach.name]['earned']) or (ach.force_unlock and newdata[ach.name]['earned']):
                if not ach.earned or ach.force_unlock:
                    change['ts_change'] = ach.update_time(newdata[ach.name]['earned_time'])
                    change['type'] = 'unlock'
                    change['was_forced'] = False
                    dt_action = datetime.fromtimestamp(ach.earned_time)
                    change['time_action'] = dt_action.strftime(stg['strftime'])
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
                        change['ts_lost'] = True
                ach.earned = newdata[ach.name]['earned']
            elif ach.earned_time != newdata[ach.name]['earned_time'] and ach.earned and not ach.force_unlock:
                change['type'] = 'time'
                change['old'] = ach.earned_time
                change['ts_change'] = ach.update_time(newdata[ach.name]['earned_time'])
                change['new'] = ach.earned_time
        elif not ach.force_unlock:
            if ach.earned:
                change['type'] = 'lock'
                change['lock_all'] = False
                if newdata == None:
                    change['lock_all'] = True
                    change['time_action'] = change['time_real']
                if not stg['savetime_keep_locked']:
                    ach.ts_first = None
                    ach.ts_earliest = None
                    change['ts_change'] = True
                    change['ts_lost'] = True
            ach.earned = False
            ach.earned_time = 0.0
            ach.progress_reported = None

        change['ach_obj'] = ach

        if 'type' in change:
            changes.append(change)

    return (achs, changes)

def convert_achs_format(data, source, achs_crc32=None):
    try:
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
                        conv[reading_ach]['earned'] = False
                        conv[reading_ach]['earned_time'] = 0.0
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
                    elif spl[0] == names['UnlockTime']:
                        conv[reading_ach]['earned_time'] = float(spl[1])
        elif source == 'sse':
            for i in range(struct.unpack('i', data[:4])[0]):
                e = data[4 + 24 * i : 28 + 24 * i]
                c = struct.unpack('I', e[0:4])[0]
                if c in achs_crc32:
                    achname = achs_crc32[c]
                    conv[achname] = {}
                    conv[achname]['earned'] = bool(struct.unpack('i', e[20:24])[0])
                    conv[achname]['earned_time'] = float(struct.unpack('i', e[8:12])[0])
        elif source == 'steam':
            for ach in data:
                achname = ach['apiname']
                conv[achname] = {}
                conv[achname]['earned'] = bool(ach['achieved'])
                conv[achname]['earned_time'] = float(ach['unlocktime'])
        return conv
    except Exception as ex:
        print(f'Failed to convert achievements - {type(ex).__name__}')
        return {}