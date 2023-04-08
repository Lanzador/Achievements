import time
from datetime import datetime
import pygame
from showtext import multiline_text
pygame.font.init()

class Achievement:
    def __init__(self, achdata, player_achs=None, stats=None, stg=None):
        self.name = achdata['name']
        self.display_name = achdata['displayName']
        self.description = achdata['description']
        self.hidden = achdata['hidden']

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
        if stg != None and stg['bar_force_unlock'] != 'no' and self.progress != None and self.progress.real_value >= self.progress.max_val and not self.earned:
            self.earned = True
            self.earned_time = time.time()
            self.force_unlock = True

        self.has_desc = isinstance(self.display_name, str) or 'english' in self.description

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

    def get_time(self, forced_mark):
        dt = datetime.fromtimestamp(self.earned_time)
        tstring = dt.strftime('%d %b %Y %H:%M:%S')
        if forced_mark and self.force_unlock:
            tstring += ' (F)'
        return tstring

class AchievementProgress:
    def __init__(self, progressdata, stats=None):
        self.value = progressdata['value']

        self.min_val = int(progressdata['min_val'])
        self.max_val = int(progressdata['max_val'])
        if self.value['operand1'] in stats:
            self.min_val = stats[self.value['operand1']].to_stat_type((progressdata['min_val']))
            self.max_val = stats[self.value['operand1']].to_stat_type((progressdata['max_val']))

        has_unknown_stats = False
        if len(self.value) == 2 and self.value['operation'] == 'statvalue':
            has_unknown_stats = not self.value['operand1'] in stats
            self.current_value = self.min_val
        self.support, self.support_error = self.check_support(stats, has_unknown_stats)
        
        if stats != None:
            self.calculate(stats)
        else:
            self.current_value = self.min_val

    def calculate(self, stats):
        if self.support:
            if len(self.value) == 2 and self.value['operation'] == 'statvalue' and self.value['operand1'] in stats:
                self.current_value = stats[self.value['operand1']].value
                if self.current_value > self.max_val:
                    self.current_value = self.max_val
                self.real_value = self.current_value
                if self.current_value < self.min_val:
                    self.current_value = self.min_val

    def get_without_min(self):
        return (self.current_value - self.min_val, self.max_val - self.min_val)

    def check_support(self, stats, has_unknown_stats):
        if not (len(self.value) == 2 and self.value['operation'] == 'statvalue'):
            return (False, 'Unsupported value formula')
        elif not stats[self.value['operand1']].type in ('int', 'float'):
            return (False, 'Unsupported stat type')
        elif has_unknown_stats:
            return (False, 'Unknown stat')
        return (True, None)

def filter_achs(achs, state, hide_secrets):
    achs_f = []
    secrets_hidden = 0
    for ach in achs:
        if hide_secrets and ach.hidden == '1' and not ach.earned:
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
    return (achs_f, secrets_hidden)

def update_achs(achs, newdata, achsfile, stg):
    changes = []
    for ach in achs:
        change = {'ach': ach.display_name_l, 'ach_api': ach.name}
        dt_real = datetime.now()
        change['time_real'] = dt_real.strftime('%d %b %Y %H:%M:%S')
        if achsfile.last_check != None:
            dt_action = datetime.fromtimestamp(achsfile.last_check)
            change['time_action'] = dt_action.strftime('%d %b %Y %H:%M:%S')

        if newdata != None and ach.name in newdata:
            if 'progress' in newdata[ach.name] and 'max_progress' in newdata[ach.name]:
                if not newdata[ach.name]['earned'] and (ach.progress_reported == None or ach.progress_reported[0] != newdata[ach.name]['progress'] or ach.progress_reported[1] != newdata[ach.name]['max_progress']):
                    ach.progress_reported = (newdata[ach.name]['progress'], newdata[ach.name]['max_progress'])
                    prg_change = {}
                    for k in change.keys():
                        prg_change[k] = change[k]
                    prg_change['type'] = 'progress_report'
                    prg_change['value'] = (ach.progress_reported)
                    changes.append(prg_change)
            else:
                ach.progress_reported = None

            if ach.earned != newdata[ach.name]['earned'] or (ach.force_unlock and newdata[ach.name]['earned']):
                if not ach.earned or ach.force_unlock:
                    ach.earned_time = newdata[ach.name]['earned_time']
                    change['type'] = 'unlock'
                    change['was_forced'] = False
                    dt_action = datetime.fromtimestamp(ach.earned_time)
                    change['time_action'] = dt_action.strftime('%d %b %Y %H:%M:%S')
                    if ach.force_unlock:
                        ach.force_unlock = False
                        change['was_forced'] = True
                elif not ach.force_unlock:
                    ach.earned_time = 0
                    change['type'] = 'lock'
                    change['lock_all'] = False
                ach.earned = newdata[ach.name]['earned']
            elif ach.earned_time != newdata[ach.name]['earned_time']:
                change['old'] = ach.earned_time
                ach.earned_time = newdata[ach.name]['earned_time']
                change['type'] = 'time'
                change['new'] = ach.earned_time
        elif not ach.force_unlock:
            if ach.earned:
                change['type'] = 'lock'
                if newdata == None:
                    change['lock_all'] = True
                    change['time_action'] = change['time_real']
                else:
                    change['lock_all'] = False
            ach.earned = False
            ach.earned_time = 0

        if 'type' in change.keys():
            changes.append(change)

    return (achs, changes)

def convert_achs_format(data, source):
    conv = {}
    if source == 'codex':
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
                if spl[0] == 'Achieved':
                    conv[reading_ach]['earned'] = bool(int(spl[1]))
                elif spl[0] == 'CurProgress' and spl[1] != '0':
                    dotspl = spl[1].split('.')
                    if len(dotspl) == 1:
                        conv[reading_ach]['progress'] = int(spl[1])
                    else:
                        conv[reading_ach]['progress'] = float(spl[1])
                elif spl[0] == 'MaxProgress' and spl[1] != '0':
                    dotspl = spl[1].split('.')
                    if len(dotspl) == 1:
                        conv[reading_ach]['max_progress'] = int(spl[1])
                    else:
                        conv[reading_ach]['max_progress'] = float(spl[1])
                if spl[0] == 'UnlockTime':
                    conv[reading_ach]['earned_time'] = int(spl[1])
    else:
        return data
    return conv