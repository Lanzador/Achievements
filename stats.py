from filechanges import FileChecker

class Stat:
    def __init__(self, fileinfo, s_type, default, sleep_t):
        fileinfo['type'] = s_type
        self.name = fileinfo['name']
        self.type = s_type
        self.default = self.to_stat_type(default)
        self.value = self.default
        if fileinfo['source'] != 'steam':
            self.fchecker = FileChecker('stat', fileinfo, sleep_t)
            self.update_val(True)

    def update_val(self, creation = False):
        if self.type in ('int', 'float'):
            changed, newdata = self.fchecker.check(creation)
            if changed:
                if newdata != None:
                    self.value = newdata
                else:
                    self.value = self.default
                return True
        return False

    def to_stat_type(self, v):
        if self.type == 'int':
            return int(v)
        elif self.type == 'float':
            return float(v)