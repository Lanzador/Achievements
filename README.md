# Lanzador/Achievements - experimental version
This version includes some changes that are for various reasons questionable or require weird changes to the code.

If the program is used without console, input will be requested in the GUI window.

`Ctrl+~` - view internal console.

`Ctrl+W` - wipe all achievement progress and stats from the emulator's save, as well as files from `save`. Disabled by default.

`Ctrl+E` - execute code. (`Ctrl+Enter` to confirm, `Ctrl+Backspace` to erase)

- `Ctrl+Shift+E` - repeat last executed code.

`Ctrl+R` - reload data such as settings without restarting the program and losing its current state.

- `Ctrl+Shift+R` - instead of loading files, just correctly apply changes made to `stg` and some other achievement-related variables through `Ctrl+E`. Doesn't work for most stat-related things.

- `Ctrl+Alt+R` - reset program state, too.

`Ctrl+G` - toggle grid view.

## Settings
There are some settings exclusive to this version.

`exp_console_max_lines` - max amount of output lines stored in the internal console. `0` disables the limit. Default: `0`

`exp_no_cmd_input` - always request input through GUI. Default: `false`

`exp_sound_console` - sound to play when new lines are printed. Same format as other `sound` options. Default: Empty

`exp_allow_wiping` - allow usage of `Ctrl+W`. Default: `false`

`exp_confirm_wiping` - if enabled, `Ctrl+W` requires confirmation. Default: `true`

`exp_history_location` - used by `save_hist()`. `*` is replaced with whatever is passed to the function. Default: `*`

`exp_history_autosave` - automatically use `save_hist()` whenever history changes. History is saved to `save`. Default: `false`

`exp_history_autosave_clear` - behavior when history is cleared while autosave is enabled. `save` - save empty history (default); `disable` - disable autosave; `ignore` - keep autosave enabled, but don't save immediately.

`exp_history_autosave_auto` - automatically enable history autosave when an achievement progress notification is sent. Default: `false`

`exp_grid_default` - switch to grid view immediately on launch. Default: `false`

`exp_grid_bar_height` - progressbar height in grid view. Default: `10`

`exp_grid_bar_hover_hide` - hide progressbar when hovering over an achievement icon in grid view. Default: `false`

`exp_grid_empty_line` - add an empty line after the last row of icons to allow hovering over icons from the last row without hiding them. Default: `true`

`exp_grid_show_extra_line` - show the partially visible row of icons at the bottom, like in normal view. Default: `false`

`exp_grid_reserve_last_line` - never use the last line for showing icons, reserve it for achievement details. Disables the two previous options. Default: `false`

## Functions
These functions can be used through `Ctrl+E`.

`find_a(ach)` - returns achievement object based on API name or index.

`unlock(a)` - show an achievement as unlocked. Doesn't change emulator save. `a` is an API name.

`unlock_all()` - show all achievements as unlocked. Doesn't change emulator save.

`edit(n)` - opens files and fodlers related to the current game.

- `n=1`, `n='a'` - achievements file

- `n=2`, `n='s'` - stats file.

- `n=3`, `n='as'`, `n='b'` - both files.

- `n=4`, `n='f'` - folder containing achievements file.

- `n=5`, `n='v'` - save dir (in `save`).

`defset()` - set default settings.

`ch_lang(l)` - change language. `l` is a string or list of strings.

`list_langs(a)` - print achievement name and description in all available languages. `a` is an achievement object, API name or index.

`ch_size(x, y)` - change window size.

`ch_game(x)` - change game. `x` follows same format as `Enter AppID:`.

`ch_emu(x)` - change emulator. Same format as `ch_game()`, but without an AppID/alias.

`ch_user(x)` - change username/ID.

`upd_hist_objs()` - replace possibly outdated achievement objects in history entries with new ones. Automatically used by `ch_lang()` and `defset()`.

`save_hist(p=None, save_ach_data=False, no_stg_loc=False)` - saves history. `p` - where to save (game save dir if not set), `save_ach_data` - save full achievement info instead of just its API name (will be used when loading), `no_stg_loc` - ignore `exp_history_location` and use the exact path given.

`load_hist(p=None, no_stg_loc=False)` - loads history.

`test_notif(t, ach=None, prog=None)` - sends a notification. `t` - type: `u` (unlock), `l` (lock), `la` (lock all - ach file removed), `p` (progress report), `sc` (schema change - achs added/removed on Steam). `ach` - ach object, API name or index for (un)lock/progress notifs. `prog` - `(current, target)` progress for progress notifs.

`Achievement.to_json(self)` - returns a dictionary with achievement data for `save_hist()` with `save_ach_data`.