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

Requires `steam_api.dll`, `steam_api64.dll` or `libsteam_api.so` next to `.exe`/`.py`. DLL bitness must match bitness of executable (recent public releases are 64-bit) or Python installation (if running `.py`). Use the DLL from [Steamwords SDK](https://partner.steamgames.com/downloads/list) v1.64, other versions are not guaranteed to work.

All stats are synced whenever any stat changes or an achievement is unlocked. Achievements unlocked while SteamSync is disabled are not automatically synced.

Press `A` in SteamSync menu (while it's active) to sync achievements unlocked locally before SteamSync was enabled. Also syncs stats.

Press `S` to sync stats. Unlike automatically triggered updates, the changes are immediately stored.

For automatic stat updates, `StoreStats` is only called if at least `exp_ssync_store_delay` (default: 3 minutes) have passed since last call. If it's too early, stats will be stored once the timer expires. Steam stores everything once you stop playing no matter how much time has passed since last call.

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

## Achievement display profiles

Display profiles allow applying different appearance settings to achievements based on various conditions.

To start using display profiles, enable `exp_use_display_profiles` in settings and write your configuration in `settings/profiles.txt` (game-specific configs can be created just like with `settings.txt`).

Profile files must follow the format below:

```
profile [CONDITION]
[OPTIONS]
```

For example:

```
profile title contains ending
  frame_color_unlock=0,255,0
  frame_color_lock=0,128,0

profile rarity != -1 and rarity<10
  profname yellow
  color_text_unlock=255,255,0

profile rarity != -1 and rarity<5
  color_text_unlock=0,255,255
  final

profile cmp_unlock_count<3
  applyprof yellow
  frame_size=4
```

Keywords must be lowercase. All conditions have three parts: achievement property, operator, value. `and` has priority over `or`. Parentheses can't be used, but you can use `profcond`:

```
profile conditionA or conditionB
  profname OR
profile profcond=OR and conditionC
  [options]
```

`exp_adp_ignore_stg_rare` is enabled by default, which means that options like `color_frame_rare` are ignored and regular options (like `color_frame_unlock`) are expected to be used together with rarity-related conditions.

Language, fonts and sounds can't be changed this way.

Appearance options have the same names and format used in `settings.txt`. Some special keywords are available:

- `profname NAME` - assigns a profile name for use with `applyprof` and `profcond`.

- `applyprof NAME` - apply options from the given profile. Doesn't copy `reset` or `final`.

- `final` - if this profile's condition matched, ignore all profiles below (only affects profiles from the current file).

- `final all` - same as `final`, but ignores profiles from all files.

- `reset` - if this profile's condition matched, revert all options from previous profiles before applying this profile.

- `file NAME` - load profiles from `settings/NAME` (similar to `add_file=` from `settings.txt`)

Available properties:

- `name` (string) - API name

- `title_rev` (string) - display name

- `title` (string) - display name (empty if hidden by `secrets_listhide`)

- `description_rev` (string) - description

- `description` (string) - description (empty for locked hidden achievements)

- `has_desc` (number, 0 or 1) - 1 if the achievement has a description

- `hidden` (number, 0 or 1) - 1 for hidden achievements

- `icon_gray` (string) - locked icon file name

- `icon` (string) - unlocked icon file name

- `groupid` (string) - achievement set ID (can be `None`)

- `groupdlc` - (number, 0 or 1) - 1 if the achievement's set is from a DLC

- `rarity_rel` (number) - rarity percentage relative to the most common achievement's rarity

- `rarity_position_unlock_rev` (number) - similar to `rarity_position_rev` (only unlocked achievements, -1 for locked ones)

- `rarity_position_unlock` (number) - similar to `rarity_position` (only unlocked achievements, -1 for locked ones)

- `rarity_position_lock_rev` (number) - similar to `rarity_position_rev` (only locked achievements, -1 for unlocked ones)

- `rarity_position_lock` (number) - similar to `rarity_position` (only locked achievements, -1 for unlocked ones)

- `rarity_position_rev` (number) - similar to `rarity_position` (1 = most common)

- `rarity_position` (number) - the achievement's position when achievements are sorted by rarity (1 = rarest)

- `rarity_at_pos` (special) - `rarity_at_pos = 1, 5.5` is true if the achievement with `rarity_position` equal to `1` has a rarity percentage of `5.5`.  Use negative position numbers for `rarity_position_rev`-like behavior (for example, `rarity_at_pos = -1, 100` for the most common achievement). Supports `<=`, `<`, `=`, `!=`, `>=`, `>`.

- `rarity` (number) - rarity percentage, -1 if unknown

- `min_rarity_rel` (number) - rarity percentage of the rarest achievement relative to the most common achievement's rarity

- `min_rarity` (number) - rarity percentage of the rarest achievement

- `max_rarity` (number) - rarity percentage of the most common achievement

- `prev_rarity` (number) - rarity percentage of the previous, less common achievement

- `next_rarity` (number) - rarity percentage of the next, more common achievement

- `rare` (number, 0 or 1) - 1 if the achievement is marked as rare

- `unlock_time` (number) - unlock timestamp (0 if the achievement is locked and no previous timestamp is recorded)

- `unlock` (number, 0 or 1) - 1 if the achievement is unlocked

- `force_unlock` (number, 0 or 1) - 1 if the achievement is "force-unlocked"

- `progress_exists` (number, 0 or 1) - 1 if the achievement has a progress bar

- `progress_target` (number) - progress bar target value (0 if no progress bar exists)

- `current_progress_rel` (number) - current progress bar value as a percentage (0 if no progress bar exists)

- `current_progress` (number) - current progress bar value (0 if no progress bar exists)

- `hover` (number, 0 or 1) - 1 when the achievement is hovered over

- `ach_count` (number) - total achievement count

- `grid_view` (number, 0 or 1) - 1 when grid view is active

- `cmp_unlock_count` (number) - number of comparison targets that have this achievement

- `cmp_target_count` (number) - number of comparison targets

- `cmp_targets` (list) - names of all comparison targets

- `cmp_owners` (list) - names of comparison targets that have this achievement

- `ssync_unlock` (number, 0 or 1) - 1 if SteamSync is connected and this achievement is unlocked on Steam

- `profcond` (special) - `profcond=NAME` is true when the profile with `profname NAME` has a condition that is true

- `notprofcond` (special) - `notprofcond=NAME` is true when `profcond=NAME` is false

Available operators:

- For number properties: `<=`, `<`, `=`, `!=`, `>=`, `>`

- For string properties (`case` versions are case-sensitive):

  - `=`, `!=`

  - `len<`, `len=`, `len>` (length comparison)

  - `containscase`, `contains`, `notcontainscase`, `notcontains`

  - `startswithcase`, `startswith`, `notstartswithcase`, `notstartswith`

  - `endswithcase`, `endswith`, `notendswithcase`, `notendswith`

- For list properties: `contains`, `notcontains`

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

`exp_use_display_profiles` - use achievement display profiles. Default: `false`

`exp_adp_ignore_stg_rare` - if enabled, `_rare` and `_rare_lock` settings are ignored and their values are replaced by values of corresponding `_unlock` and `_lock` settings. Only used when achievement display profiles are enabled. Default: `true`

`exp_adp_ignore_stg_hover` - if enabled, `_hover` settings are ignored and their values are considered empty. Only used when achievement display profiles are enabled. Default: `false`

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

- `n=12`, `n='adp'` - `settings/profiles.txt`

- `n=13`, `n='adpg'` - `settings/profiles_[AppID].txt` (will be created if doesn't exist)

`rmcfg()` - delete `games/[AppID]`.

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