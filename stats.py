import struct
from filechanges import FileChecker

class Stat:
    def __init__(self, fileinfo, s_type, default, sleep_t, stat_dnames, inc_only):
        fileinfo['type'] = s_type
        self.name = fileinfo['name']
        self.type = s_type
        self.default = self.to_stat_type(default)
        self.value = self.default
        self.real_value = self.value

        self.inc_only = '*' in inc_only or self.name in inc_only

        if fileinfo['source'] == 'goldberg':
            self.fchecker = FileChecker('stat', fileinfo, sleep_t)
            self.update_val(True)
        elif fileinfo['source'] in ('steam', 'steam_local') and s_type == 'avgrate':
            self.type = 'avgrate_st'

        self.dname = self.name
        if self.name in stat_dnames and stat_dnames[self.name] != '':
            self.dname = stat_dnames[self.name]

    def set_val(self, new):
        self.real_value = new
        if self.inc_only:
            if new > self.value:
                self.value = new
                return True
        elif self.value != new:
            self.value = new
            return True
        return False

    def update_val(self, creation=False):
        if self.type in ('int', 'float'):
            changed, newdata = self.fchecker.check(creation)
            if changed:
                if newdata != None:
                    return self.set_val(newdata)
                else:
                    return self.set_val(self.default)
        return False

    def to_stat_type(self, v):
        if self.type == 'int':
            return int(v)
        else:
            return float(v)

def convert_stats_format(stats, data, source, source_stat_ids=None):
    try:
        conv = {}
        if source == 'codex':
            for l in data.split('\n'):
                spl = l.rsplit('=', 1)
                if len(spl) > 1:
                    stat = spl[0]
                    if stat in stats:
                        stat = stats[stat]
                        conv[stat.name] = stat.to_stat_type(spl[1])
        elif source == 'ali213':
            stat = None
            for l in data.split('\n'):
                if len(l) > 0 and l[0] == '[' and l[-1] == ']':
                    stat = l[1:-1]
                    if stat in stats:
                        stat = stats[stat]
                    else:
                        stat = None
                elif stat != None:
                    spl = l.split('=')
                    if len(spl) != 2:
                        continue
                    conv[stat.name] = stat.to_stat_type(spl[1])
        elif source == 'sse':
            for i in range(struct.unpack('i', data[:4])[0]):
                e = data[4 + 24 * i : 28 + 24 * i]
                c = struct.unpack('I', e[0:4])[0]
                if c in source_stat_ids:
                    stat = stats[source_stat_ids[c]]
                    if stat.type == 'int':
                        conv[stat.name] = struct.unpack('i', e[20:24])[0]
                    else:
                        conv[stat.name] = struct.unpack('f', e[20:24])[0]
        elif source == 'steam_local':
            data = data['cache']
            for stat_id in source_stat_ids:
                if not stat_id in data: continue
                name = source_stat_ids[stat_id]
                if name in stats:
                    stat = stats[name]
                    if stat.type == 'int':
                        conv[name] = data[stat_id]['data']
                    else:
                        conv[name] = struct.unpack('>f', struct.pack('>i', data[stat_id]['data']))[0]
        return conv
    except Exception as ex:
        print(f'Failed to convert stats - {type(ex).__name__}')
        return {}