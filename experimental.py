import time

print_real = print
internal_console = []
def print(*args, **kwargs):
    print_real(*args, **kwargs)
    sep = ' '
    if 'sep' in kwargs:
        sep = kwargs['sep']
    text = sep.join(map(str, args))
    if 'end' in kwargs:
        text += kwargs['end']
    if text.endswith('\n'):
        text = text[:-1]
    lines = text.split('\n')
    for l in lines:
        internal_console.append({'time': time.time(), 'text': l})

screen_exists = False
console_lines_erased = 0
last_console_len = 0
new_console_line = False
last_code = ''

cmp_init_done = False
cmp_data = {}
cmp_stg = {'stat_lb': True, 'unlock_lb': True,
           'owners_count': -1, 'sort_targets': False,
           'mark_rare': -1, 'mark_rare_remove': False,
           'time': False}
cmp_global_targets = {}
cmp_save_list_shown = True
cmp_saved_targets = {}
cmp_unsaved_changes = False
cmp_unsaved_changes_global = False
cmp_reloading = False
cmp_reload_progress = 0
cmp_reload_progress_max = 0
cmp_loading_global = False
cmp_initing = False
cmp_page = 1
cmp_filter = ''
cmp_mark_rare = -1
cmp_mark_rare_remove = False
cmp_sorted = False
cmp_unlock_history = ''

ssync_dll = None
ssync_dll_found = False
ssync_dll_loaded = False
ssync_funcs = {}
ssync_dll_funcs_ok = False
ssync_conn_att = False
ssync_userstats = None
ssync_steam_unlocks = 0
ssync_resyncable_unlocks = 0
ssync_resyncable_stats = 0
ssync_connected = False
ssync_active = False
ssync_queue = []
ssync_queue_prog = []
ssync_last_store = 0.0
ssync_last_copy_stats = 0.0
ssync_stats_not_stored = False
ssync_steamid = 0
ssync_stat_modes = {}