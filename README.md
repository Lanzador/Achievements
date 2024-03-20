# Lanzador/Achievements
A program that lets you view your achievements and stats from Steam emulators. Most of v1.0.0 was made in around a week, although the release was delayed. Some things are unobvious, so please read this.

## Dependencies
Made with Python 3.8.10.

Packages used: `pygame (2.3.0), plyer (2.1.0), requests (2.30.0), Pillow (9.5.0)` (+ `PyGObject` for Linux)

## Usage
You need to generate the lists of achievements and stats before you can do anything. To do that, use [Goldberg's generate_emu_config.py](https://gitlab.com/Mr_Goldberg/goldberg_emulator/-/tree/master/scripts). The generated `achievements.json`, `achievement_images` and `stats.txt` should be put in `games/[AppID]`. You can also edit `games/alias.txt` to load the game's achievements using a short name instead of remembering AppIDs.

`alias.txt` follows this format:
```
AppID=alias
AppID=alias
AppID=alias
```

In addition to the AppID, it can include an emulator name, as well as any extra information needed for that emulator. Use the same format that you use when entering this info after running the program.

Once you set this up, you can open the list by running `window.py` (or `achievements.exe` if you downloaded the release version) and entering the AppID or alias of the game. You can also pass it (and the values below) as command line arguments.

You can enter an alias followed by an emulator name (and username) to load the AppID that this alias refers to, but track a different emulator/username.

By default, it's assumed that you use Goldberg. For other emulators, add their short name after the AppID.

### Codex
`[AppID] c [a]`

By default it checks the Codex folder located in Documents, but for some versions of Codex you'll want to look for achievement files in AppData instead. If that's the case, just add an `a`: `[AppID] c a`

### ALi213
`[AppID] a [Username/Path]`

It's recommended to set save type to `1` in ALi213's settings. If no username is provided, `Player` is used. (Note: The default username may get changed, since this is not what the emulator uses if the player name line is removed from the .ini file)

Save type `0` is also supported, but to load such saves you'll have to enter a full path to the user's save folder, prefixed with `path:`.

For example: `480 a path:D:/Game folder/Profile/Username`

### SmartSteamEmu
`[AppID] s [Username/Path]`

AppData is checked by default. If saves aren't separated by name in SSE's settings (`SeparateStorageByName`), provide no username. If they are, provide the username.

If saves aren't stored in AppData (`StorageOnAppdata` is disabled), enter a full path to the folder containing AppID subfolders.

For example: `480 s path:D:/Game folder/SmartSteamEmu/Username`

### Steam
`[AppID] st [User ID]`

You must enter your Steam Web API key in settings to track Steam achievements.

Remember that Steam has a daily limit of 100,000 requests per API key.

## What is supported?

### Operating systems
This was made on Windows 7, but it also supports Linux, thanks to @detiam.

### Emulators
4 emulators are supported, plus real Steam. Internal names are used when loading emulator-specific settings files. Any of the short names can be used when loading a game.

| Emulator      | Internal name | Short names                    | Support level                           |
| ------------- | ------------- | ------------------------------ | --------------------------------------- |
| Goldberg      | `goldberg`    | `g, gb, goldberg`              | Full                                    |
| Codex         | `codex`       | `c, cd, cod, cdx, codex`       | Full                                    |
| ALi213        | `ali213`      | `a, ali, ali213, 213, a213`    | Full                                    |
| SmartSteamEmu | `sse`         | `s, sse, smartsteamemu, smart` | No "Achievement Progress" notifications |
| Steam         | `steam`       | `st, steam`                    | No "Achievement Progress" notifications |

### Three ways of displaying hidden/secret achievements
By default, hidden achievements are shown in the list with their description hidden. Change the `secrets` setting to hide them completely or move them to the bottom of the list.

### Filter by state, sort and search
Achievements can be filtered to (un)locked only. They can also be sorted by rarity, unlock state or unlock time. A simple search feature is available.

### Progressbars
This is the only such tool known to me that displays progressbars under achievements. It only supports bars that are calculated by simply checking the value of one stat, but I have never seen examples of other formulas, so this should work for most (if not all) games. If an example of a different formula is found, support will likely be implemented. If the progress formula is unsupported or uses a stat type that is unsupported, a short error message will be shown instead of the progress value. This is also what happens if the bar relies on a stat that isn't present in your `stats.txt`.

### Stats
Only `int` and `float` stats are supported. I don't think Goldberg has proper `avgrate` support anyway.

### "Force unlocks"
Only Goldberg actually unlocks achievements that are based entirely on stats and aren't unlocked by the game in the normal way, so achievements with progressbars are shown as unlocked and their timestamp is saved when the target value is reached if this behavior is enabled in settings.

### "Achievement Progress" notifications
Some rare games occasionally display "Achievement Progress" notifications on Steam. Those are supported here and even have a progressbar in the "History" tab. (Not for all emulators)

### Fix for always empty progressbars
Some games' achievement pages on Steam show empty progressbars with progress numbers always being the same as target numbers. By default, this behavior is copied. Enable `bar_ignore_min` for the game in settings as a workaround. Ha, can't do that on Steam!

### Unlock rates
Achievement percentages are requested from Steam and displayed in the list. If you're offline, last known percentages will be loaded.

### Customization
Colors and fonts can be changed. Different settings can be used for specific games or emulators.

## Settings
Settings can be changed in `settings/settings.txt`. You can also create `settings/settings_[Emulator].txt`, `settings/settings_[AppID].txt` or `settings/settings_[AppID]_[Emulator]` to use different settings for an emulator (useful for `bar_force_unlock`, for example) or for a specific game (`bar_ignore_min` is a great example). All available settings are included in the default `settings.txt`, but if you remove any, their default values will be used. Below is a list of all available settings. For boolean settings, you can use `1`/`0` as well as `true`/`false`. `add_file=filename.txt` can be used to load settings from a file in the `settings` folder.

### List of settings
`window_size_x`- horizontal size of the window, in pixels. Default: `800`

`window_size_y`- vertical size of the window, in pixels. Default: `600`

`delay` - time (in seconds) that must pass before files are checked for changes. Default: `0.5`

`delay_stats` - stats will only be checked for changes on every `[value]`th check. Useful if using Goldberg for a game with a lot of stats. Default: `1` (check always)

`delay_sleep` - time (in seconds) to sleep for after every iteration of the main loop. Default: `0.1`

`delay_read_change` - time to wait for before reading a file after it was changed. Default: `0.05`

`gamebar_length` - length of the game completion bar, in pixels. Default: `375`

`gamebar_position` - decides where to show the game completion bar. `normal` - normal position (default); `repname` - hide game name and move the bar up; `under` - move the bar down, below the buttons; `hide` - hide the bar.

`frame_size` - thickness of the frames around achievement icons, in pixels. Default: `2`

`frame_color_unlock` - color to use for icon frames for unlocked achievements. Default: `255,255,255`

`frame_color_lock` - color to use for icon frames for locked achievements. Default: `128,128,128`

`frame_color_rare` - color to use for icon frames for unlocked rare achievements. Default: Empty

`frame_color_rare_lock` - color to use for icon frames for locked rare achievements. Default: Empty

`rare_below` - rarity percentage below which achievements are considered "rare" for the above settings. Default: `10.0`

`hidden_desc` - replacement description to show for locked hidden achievements. Default: `[Hidden achievement]`

`secrets` - hidden achievements. Default: `normal` - show without descriptions (default); `hide` - remove from the list, like on Steam; `bottom` - move to the bottom of the list.

`unlocks_on_top` - move unlocked achievements to the top of the list. Default: `false`

`unlocks_timesort` - sort unlocked achievements by unlock time. Only works if `unlocks_on_top` is enabled or you're viewing unlocks only. Default: `false`

`sort_by_rarity` - sort achievements by rarity instead of keeping their normal order. Default: `false`

`bar_length` - length of achievement progress bars, in pixels. Default: `300`

`bar_unlocked` - behavior of progressbars under unlocked achievements. `show` - no special rules; `full` - show a full bar even when the progress value is below the target (default); `hide` - hide the bar; `zerolen` - hide the bar, but keep `full`-like progress numbers.

`bar_hide_unsupported` - hide progressbar if its value can't be calculated. `none` - never (default); `stat` - hide if progress formula or stat type is unsupported, keep if stat not present in `stats.txt`; `all` - always.

`bar_hide_secret` - hide progressbar if the achievement is hidden and not earned. Default: `true`

`bar_ignore_min` - assume that achievement progress `min_val` is always `0`. Default: `false`

`bar_force_unlock` - display the achievement as unlocked as long as its progress has reached the target value (progressbar is full). Default: `true` (Releases include `settings_goldberg.txt` and `settings_steam.txt` that disable this setting. Re-enable it if you're using an older version of Goldberg.)

`forced_keep` - keep "force-unlocked" achievements even if the progress value drops below the achievement's target. Changing this is rather useless. `no` - don't keep; `session` - keep until the program is closed and don't save timestamps; `save` - save these unlocks in a file, together with their timestamps (default).

`forced_mark` - show `(F)` next to an achievement's timestamp if it's "force-unlocked". Default: `false`

`forced_time_load` - timestamp to set for "force-unlocks" that are detected on launch. `now` - current time (default); `filechange` - last modification time of stat file.

`show_timestamps` - show timestamps. Default: `true`

`strftime` - date/time format. Default: `%d %b %Y %H:%M:%S`

`history_length` - maximum length of history, after reaching which old entries get deleted. `0` disables the limit, `-1` disables history. Default: `0`

`history_time` - source of time to show in history. `real` - save current time when the change is recorded; `action` - save unlock times for unlock notifications and file change times for other notifications (default).

`history_unread` - mark new notifications as unread in history and show unread marks. Default: `true`

`notif` - show system notifications. Default: `true`

`notif_limit` - max amount of notifications to show during one check. Any extra notifications will be grouped into one. Default: `3`

`notif_timeout` - time (in seconds) to show the notification for. Default: `3`

`notif_lock` - show notifications (and history entries) when an achievement is locked or when the achievement progress file is deleted. Default: `false`

`notif_icons` - show achievement icons in notifications. Adds extra delay on Windows if `icon_converter` is not used in advance. Default: `true`

`notif_icons_no_ico` - behavior if achievement icons aren't converted. Ignored if `notif_icons` is disabled. Windows-only. `ignore` - do nothing; `warn` - print count of icons that need to be converted; `convert` - run `icon_converter` (default).

`language` - comma-separated (no spaces) list of languages to use for achievements. First available language is used. If nothing is available, English is used. Default: `english`

`language_requests` - language to use for Steam requests (such as game names). If empty, the first language from `language` will be used. Default: Empty

`unlockrates` - where to show achievement rarity percentages. `none` - don't load unlock rates; `load` - load unlock rates (for things like sorting), but don't display them; `name` - show unlock rates next to achievement names (default); `desc` - show them after descriptions.

`unlockrates_expire` - time after which saved unlock rates are considered expired and replaced (if possible). Avilable units: `s`, `m`, `h`, `d`. Default: `1h`

`font_general` - name of font file (inside the `fonts` folder) to use for everything except achievements. Default: `Roboto/Roboto-Regular.ttf`

`font_achs` - name of font file(s) to use for achievements. Format: `Font.ttf;language,language2:OtherFont.ttf` - the font without a language prefix is used for all languages without a language-specific font. Default: `Roboto/Roboto-Regular.ttf`

`font_achs_desc` - name of font file(s) to use for achievement descriptions, same format as `font_achs`. If not set, uses `font_achs`. Default: Empty

`font_size_general` - font size for `font_general`. Note: All font size settings are meant for small changes. Default: `15`

`font_size_regular` - font size(s) for achievement titles. Format: `15;Font.ttf:16`. Default: `15`

`font_size_small` - font size(s) for achievement descriptions. Format: `15;Font.ttf:16`. Default: `13`

`font_line_distance_regular` - distance between the beginning of each line on the stats screen. Default: `16`

`font_line_distance_small` - distance between the beginning of each line in achievement descriptions. Default: `16`

`color_background` - background color. Default: `0,0,0`

`color_text` - default text color. Default: `255,255,255`

`color_text_unlock` - text color for unlocked achievements. Default: `255,255,255`

`color_text_lock` - text color for locked achievements. Default: `128,128,128`

`color_bar_bg` - color to use for progressbar background. Default: `128,128,128`

`color_bar_fill` - color to use for progressbar fill. Default: `255,255,255` - fun fact: this was originally `0,255,0`

`color_bar_completed` - color to use instead of `color_bar_fill` for full bars. Default: Empty

`color_scrollbar` - color to use for scrollbar. Default: `128,128,128`

`color_achbg_unlock` - color to use as background for unlocked achievements. Default: Empty

`color_achbg_lock` - color to use as background for locked achievements. Default: Empty

`color_achbg_rare` - color to use as background for unlocked rare achievements. Default: Empty

`color_achbg_rare_lock` - color to use as background for locked rare achievements. Default: Empty

`color_achbg_hover` - color used to highlight achievements when they're hovered over. Default: `64,64,64`

`save_timestamps` - save first and earliest timestamps of each achievement to a file. Default: `true`

`savetime_shown` - timestamps to display. `normal` - timestamp currently saved by emulator; `first` - first timestamp that was detected (default); `earliest` - the earliest out of all detected timestamps.

`savetime_mark` - show `(S)` next to an achievement's timestamp if the displayed timestamp is different from the "normal" one. Default: `false`

`savetime_keep_locked` - don't delete saved timestamps when an achievement gets locked. Enabling this will prevent loss of timestamp data in case of an error when loading player progress, but will also require manual deletion of saved timestamps if you decide to delete your progress. Default: `false`

`smooth_scale` - use `pygame.transform.smoothscale` instead of `pygame.transform.scale` to resize achievement icons when needed. Default: `true`

`stat_display_names` - load and show display names instead of API names for stats. Requires an API key. Default: `true`

`api_key` - Steam Web API key. Required to track achievements from Steam. Default: Empty

## Unobvious features and controls

- `LnzAch_gamename` environment variable can be used to replace game name. @detiam requested this.

- Run `settings.py` to generate `settings/settings_default.txt`.

- Clicking an achievement will print some information about it: API name, languages, hidden?, progress stat, rarity (if `unlockrates=load`), unlock time (if `show_timestamps` is disabled). Hold `SHIFT` to include description, API name and progress stat even if the achievement is hidden.

- Press the `~` key to print information about which game/emulator/username is being tracked and the program's version.

- Right click the state filter button (all/unlock/lock) to access sorting/secrets settings. Right-click the secrets button in that menu to see the "reveal secret achievements" button.

- Press `Ctrl+F` to search for achievements. The orange arrows take you to the prev/next match in the main list, similar to browser `Ctrl+F`. The green button shows all matching achievements. The following keywords can be used instead of normal search requests: `#hidden` - all secret achievements, including unlocked ones; `#not_hidden` - the opposite; `#progress` - all achievements with progressbars, including those with hidden progressbars. If `secrets=hide`, locked secret achievements won't be mentioned in search results even if you use one of these keywords.

## Scripts

### icon_converter
Windows doesn't accept `.jpg` icons for notifications, so I have to convert them to `.ico`. Doing this every time a notification is shown adds some delay. (Also, temporarily converted icons are deleted in 2 seconds, so a crash is probably possible if they're not loaded in time)

To prevent that delay, achievement icons can be converted in advance. (This is done automatically since v1.3.1)

After running the converter, enter the AppID (or alias) of the game you want to convert icons for.

Multiple IDs can be entered, separated by spaces.

Use `*` to include all games that have a `games/[AppID]` folder.

The ID(s) can be passed as command line arguments.

Accepted arguments:

- `-s` - hide progress output.

- `-c` - warn if the `games/[AppID]/achievement_images/ico` folder doesn't exist, but do nothing about it. Still requires a list of AppIDs to check (or `*`).

### save_finder
Enter the AppID (or alias) to find all supported non-`path:` saves for a given game on your PC.

A list of emulators (with usernames, where applicable) will be printed. If nothing appeared, no saves were found.

### save_finder_all
Run this to find all supported non-`path:` saves on your PC.

If possible, game names will be printed next to AppIDs. Sometimes not all names are retrieved for some reason, so if too many IDs are left without a name, try running this again.

Accepted arguments:

- `-g` - group saves by game (rather than by emulator).

- `-eg` - group by emulator, but subgroup by game (rather than by username).

- `-eg2` - alternative format for `-eg`.

### ach_dumper
This script writes the achievement list for a given game to a text file which you can send to others to show your progress without screenshoting each page of the list.

Settings used: `api_key` (if loading progress from Steam), `language`, `savetime_shown`, `bar_ignore_min`, `unlockrates`, `secrets`, `stat_display_names`

Game name, unlock rates and stat display names are loaded from files created by the main program. They are not updated by the script.

Accepted arguments:

- `-u`, `-l` - (un)locked achievements only.

- `-h` - hide descriptions even for secret achievements even if they're unlocked.

- `-sn`, `-sh`, `-sb` - use a specific value for `secrets` (`normal`, `hide` or `bottom`) instead of the one from your `settings.txt`.

- `-s` - write stats instead of achievements.

- `-r`, `-uot`, `-t` - equivalents of `sort_by_rarity`, `unlocks_on_top` and `unlocks_timesort`.

## Contact me

Feel free to contact me if you have questions or if you find something weird (or if you just want to say that you found this useful). Contact info is in my profile.