# Lanzador/Achievements - experimental version
This version includes some changes that are for various reasons questionable or require weird changes to the code.

If the program is used without console, input will be requested in the GUI window.

`Ctrl+~` - view internal console.

- Click a line to view its full text (if it's too long) and the time when it was printed.

- `Ctrl+C` to copy the selected line's text. 

- `Ctrl+D` to write all lines to `ach_dumper/..._console.txt`.

`Ctrl+W` - wipe all achievement progress and stats from the emulator's save, as well as files from `save`. Disabled by default.

`Ctrl+E` - execute code. (`Ctrl+Enter` to confirm, `Ctrl+Backspace` to erase)

- `Ctrl+Shift+E` - repeat last executed code.

`Ctrl+R` - reload data such as settings without restarting the program and losing its current state.

- `Ctrl+Shift+R` - instead of loading files, just correctly apply changes made to `stg` and some other achievement-related variables through `Ctrl+E`. Doesn't work for most stat-related things.

- `Ctrl+Alt+R` - reset program state, too.

`Ctrl+G` - toggle grid view.

`Ctrl+C` - open comparison menu (see below).

## Comparison
You can use the comparison menu to load your friends' progress from Steam (or from a file) for comparison purposes.

- You will see who has a specific achievement next to its timestamp.

- Your position relative to others' results and the closest target will be shown next to the unlock count and stat values.

- Clicking an achievement or stat will print more information (unlock times and stat values).

- Achievements can be filtered or sorted based on friends' unlocks.

### Adding a comparison target
Once you initialize the comparison features, you will be prompted to add the comparison targets you need. (`Shift+ENTER` to initialize without adding targets)

When adding a target, you need to enter two values.

- The target name is used for display purposes and to select the target for various operations later.

- The second value is either the target's Steam ID or path to a file generated with `cmp_dump()`. Can be empty if the target's name is present in global targets or `alias.txt`.

Enter an empty target name to stop batch-adding targets.

If a target wasn't actually added, check the console to see the error.

- Error code 403 indicates a problem with the target's privacy settings.

- Error code 400 is returned if the target doesn't own the game.

Use `Shift+A` to batch-add targets later.

### Save targets
The `S - save targets` option leads to another menu. In addition to saving game-specific targets, it has options to manage global targets.

Unless `exp_cmp_autoload_global` is disabled, the program will try to load every global target's progress when you load a game for the first time. The result will be saved automatically. Manually selecting `R - reset targets to global list` does the same, but without autosave.

Global display options are loaded if targets and options for the given game were never saved.

All saved game-specific targets' progress is autosaved when reloaded.

### Filter achievements
The following filter conditions are valid:

- `<2` - 2 or less targets have the achievement.

- `>2` - 2 or more targets have the achievement.

- `TargetName` - `TargetName` has the achievement.

- `!TargetName` - `TargetName` does't have the achievement.

Conditions can be joined using `|` (OR, highest priority), `&` (AND), `+` (OR, lowest priority).

Example: `<2|!Targ1&Targ2+>10`

## Settings
There are some settings exclusive to this version.

`exp_console_max_lines` - max amount of output lines stored in the internal console. `0` disables the limit. Default: `0`

`exp_no_cmd_input` - always request input through GUI. Default: `false`

`exp_no_cmd_input_auto` - enable `exp_no_cmd_input` once the window is opened. Default: `true`

`exp_sound_console` - sound to play when new lines are printed. Same format as other `sound` options. Default: Empty

`exp_allow_wiping` - allow usage of `Ctrl+W`. Default: `false`

`exp_confirm_wiping` - if enabled, `Ctrl+W` requires confirmation. Default: `true`

`exp_history_location` - used by `save_hist()`. `*` is replaced with whatever is passed to the function. Default: `*`

`exp_history_autosave` - automatically use `save_hist()` whenever history changes. History is saved to `save`. Default: `false`

`exp_history_autosave_clear` - behavior when history is cleared while autosave is enabled. `save` - save empty history (default); `disable` - disable autosave; `ignore` - keep autosave enabled, but don't save immediately.

`exp_history_autosave_auto` - automatically enable history autosave when an achievement progress notification is sent or if saved history already exists. Default: `false`

`exp_grid_default` - switch to grid view immediately on launch. Default: `false`

`exp_grid_bar_height` - progressbar height in grid view. Default: `10`

`exp_grid_bar_hover_hide` - hide progressbar when hovering over an achievement icon in grid view. Default: `false`

`exp_grid_empty_line` - add an empty line after the last row of icons to allow hovering over icons from the last row without hiding them. Default: `true`

`exp_grid_show_extra_line` - show the partially visible row of icons at the bottom, like in normal view. Default: `false`

`exp_grid_reserve_last_line` - never use the last line for showing icons, reserve it for achievement details. Disables the two previous options. Default: `false`

`exp_cmp_expire` - similar to `unlockrates_expire`, but for comparison targets' progress data. Default: `1h`

`exp_cmp_autoload_global` - attempt to load all global comparison targets and save the result when loading a new game. Default: `true`

`exp_cmp_color_bar_next` - color used to show closest comparison target's progress on the game completion progress bar. Default: `192,192,192`

`exp_cmp_color_bar_best` - color used to show the highest comparison target's progress on the game completion progress bar. Default: `160,160,160`

## Functions
These functions can be used through `Ctrl+E`.

`cmp_dump(fn=None)` - write current unlocks and stats to file `fn` which can be used to load them when adding a comparison target. If `fn` is not set, input will be requested. Keep the input empty to use ach_dumper's folder.

`find_a(ach)` - returns achievement object based on API name or index (internal order, not sorted order).

`get_hover(api_name=False)` - returns achievement object or API name for achievement currently hovered over. If not hovering over an achievement, returns the first achievement. Does not work correctly for notification history screen.

`unlock(a)` - show an achievement as unlocked. Doesn't change emulator save. `a` is an achievement object, API name or index.

`f_unlock(a)` - force-unlock an achievement. It will be kept unlocked between sessions. `a` is an achievement object, API name or index.

`unlock_all()` - show all achievements as unlocked. Doesn't change emulator save.

`edit(n)` - opens files and folders related to the current game.

- `n=1`, `n='a'` - achievements file

- `n=2`, `n='s'` - stats file

- `n=3`, `n='as'`, `n='b'` - both files

- `n=4`, `n='f'` - folder containing achievements file

- `n=5`, `n='sv'`, `n='v'` - save dir (in `save`)

- `n=6`, `n='c'` - config dir

- `n=7`, `n='g'` - `settings.txt`

- `n=8`, `n='al'` - `alias.txt`

- `n=9`, `n='gg'` - `settings_[AppID].txt` (will be created if doesn't exist)

- `n=10`, `n='st'` - `Steam/appcache/stats`

`defset()` - set default settings.

`invset(x, vals=None)` - without `vals`, inverts the value of a boolean setting named `x`. With `vals=[val1, val2]`, alternates between the given values of any type on each use. `vals=[val1]` is equivalent to `vals=[val1, known_settings[x]['default']]`.

`ch_lang(l)` - change language. `l` is a string or list of strings.

`list_langs(a=None)` - print achievement name and description in all available languages. `a` is an achievement object, API name or index. If `a` is `None`, it is set to `get_hover()`.

`ch_size(x, y)` - change window size.

`ch_game(x)` - change game. `x` follows same format as `Enter AppID:`.

`ch_emu(x)` - change emulator. Same format as `ch_game()`, but without an AppID/alias.

`ch_user(x)` - change username/ID.

`upd_hist_objs()` - replace possibly outdated achievement objects in history entries with new ones. Automatically used by `ch_lang()` and `defset()`.

`save_hist(p=None, save_ach_data=False, no_stg_loc=False)` - saves history. `p` - where to save (game save dir if not set), `save_ach_data` - save full achievement info instead of just its API name (will be used when loading), `no_stg_loc` - ignore `exp_history_location` and use the exact path given.

`load_hist(p=None, no_stg_loc=False)` - loads history.

`test_notif(t, ach=None, prog=None)` - sends a notification. `t` - type: `u` (unlock), `l` (lock), `la` (lock all - ach file removed), `p` (progress report), `sc` (schema change - achs added/removed on Steam). `ach` - ach object, API name or index for (un)lock/progress notifs. `prog` - `(current, target)` progress for progress notifs.

`generate_inc_only()` - generates `games/[AppID]/increment_only.txt` based on UserGameStatsSchema from `games/[AppID]` or Steam's `appcache`.

`Achievement.to_json(self)` - returns a dictionary with achievement data for `save_hist()` with `save_ach_data`.