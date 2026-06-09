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

- `Ctrl+Alt+E` - execute without try-except.

- If reordering `achs`, make sure to regenerate `ach_idxs` to avoid unexpected behavior when saving timestamps and in other cases.

`Ctrl+R` - reload data such as settings without restarting the program and losing its current state.

- `Ctrl+Shift+R` - instead of loading files, just correctly apply changes made to `stg` and some other achievement-related variables through `Ctrl+E`. Doesn't work for most stat-related things.

- `Ctrl+Alt+R` - reset program state, too.

`Ctrl+G` - toggle grid view.

`Ctrl+C` - open comparison menu (see below).

`Ctrl+S` - open SteamSync menu (see below).

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

- Error code 403 indicates a problem with the target's privacy settings (or your API key).

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

## SteamSync
When this feature is enabled, new local unlocks and stat changes from a Steam emulator are copied to Steam.

This was added for re-unlocking achievements (which are already unlocked on Steam) locally while still saving first-time unlocks to Steam.

Requires `steam_api.dll` or `steam_api64.dll` next to `.exe`/`.py`. DLL bitness must match bitness of executable (recent public releases are 64-bit) or Python installation (if running `.py`). Use the DLL from [Steamwords SDK](https://partner.steamgames.com/downloads/list) v1.64, other versions are not guaranteed to work.

All stats are synced whenever any stat changes or an achievement is unlocked. Achievements unlocked while SteamSync is disabled are not automatically synced.

Press `A` in SteamSync menu (while it's active) to sync achievements unlocked locally before SteamSync was enabled. Also syncs stats.

Press `S` to sync stats. Unlike automatically triggered updates, the changes are immediately stored.

For automatic stat updates, `StoreStats` is only called if at least `exp_ssync_store_delay` (default: 3 minutes) have passed since last call. If it's too early, stats will be stored once the timer expires. Steam stores everything once you stop playig no matter how much time has passed since last call.

Since Steam sees this program as the game's process when using SteamSync, don't forget to close it to avoid extra playtime.

Run the game from Steam before enabling SteamSync (which leads to Steam replacing the PLAY button with STOP) for the overlay to attach to the game.

### SteamSync Reverse
When tracking `steam_local`, SteamSync will not write anything to Steam. Instead, it will be used to read stats without significant delays through "get stat" calls.

Tracked Steam ID must match the account actually logged into Steam, else you will see an error message.

### Stat modes
By default, stats are only synced if their local value is greater than the Steam value. Create `games/[AppID]/ssync_stats.txt` to configure this behavior.

Format example:

```
not *
inc Stat1_APIname
any Stat2_APIname
bit Stat3_APIname
```

`*` affects all stats (except those listed explicitly).

`inc` - sync if local value is greater (default).

`any` - always write local value to Steam, even if it's smaller.

`not` - never sync this stat.

`bit` - write the bitwise OR of the Steam value and the local value to Steam. Some games use stats to track which parts of an achievement's requirement were completed, using one bit per part. For example, if an achievement requires finding all chests, each bit can represent a specific chest.

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

`exp_ssync_store_delay` - minimal amount of time between automatic `StoreStats` calls. Setting this to very small values is pointless, since Steam ignores excessive calls. Default: `180s`

`exp_ssync_progress` - copy achievement progress notifications to Steam. Can be temporarily changed without affecting `settings.txt` in SteamSync menu. Default: `true`

`exp_ssync_progress_io` - only copy progress notifications if reported progress is not less than the stat value from Steam. Shouldn't be enabled if using `:r` in `force_progress.txt`. Even if this setting is disabled, Steam will not show the actual reported values if they're less than the stat's value. Default: `false`

## Functions
These functions can be used through `Ctrl+E`.

`cmp_dump(fn=None, ret=False)` - write current unlocks and stats to file `fn` which can be used to load them when adding a comparison target. If `fn` is not set, input will be requested. Keep the input empty to use ach_dumper's folder. If `ret=True`, returns the result instead of writing it to a file.

`cmp_self(name='Self')` - add comparison target with current progress.

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

- `n=11`, `n='fp'` - `force_progress.txt` (will be created if doesn't exist)

`defset()` - set default settings.

`invset(x, vals=None)` - without `vals`, inverts the value of a boolean setting named `x`. With `vals=[val1, val2]`, alternates between the given values of any type on each use. `vals=[val1]` is equivalent to `vals=[val1, known_settings[x]['default']]`.

`ch_lang(l='')` - change language. `l` is a string, same format (`language1,language2`) as in `settings.txt`.

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