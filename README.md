# Lanzador/Achievements
A program that lets you view your achievements and stats from Steam emulators. Most of v1.0.0 was made in around a week, although the release was delayed. Some things are unobvious, so please read this.

## Dependencies
Made with Python 3.8.10.

Packages used: `pygame(2.3.0), plyer (2.1.0), requests (2.30.0), Pillow (9.5.0)`

## Usage
This works based on local files, so you need to generate the list of achievements before you can do anything. To do that, use [Goldberg's generate_emu_config.py](https://gitlab.com/Mr_Goldberg/goldberg_emulator/-/tree/master/scripts). The generated `achievements.json`, `achievement_images` and `stats.txt` should be put in `games/[AppID]`. You can also edit `games/alias.txt` to load the achievements using a short name instead of remembering AppIDs.

`alias.txt` follows this format:
```
AppID=alias
AppID=alias
AppID=alias
```

In addition to the AppID, it can include an emulator name, as well as any extra information needed for that emulator.

Lines not containing `=` (or containing more than one `=`) are ignored.

Once you set this up, you can open the list by running `window.py` (or `achievements.exe` if you downloaded the release version) and entering the AppID or alias of the game. You can also pass it (and the values below) as command line arguments.

By default, it's assumed that you use Goldberg. Below are instructions for other emulators.

### Codex
`[AppID] c`

By default it checks the Codex folder located in Documents, but for some versions of Codex you'll want to look for achievement files in AppData instead. If that's the case, just add an `a`: `[AppID] c a`

### ALi213
`[AppID] a [Username/Path]`

It's recommended to choose `1` as the save type in ALi213's settings. If no username is provided, `Player` is used.

Save type `0` is also supported, but in that case you'll have to enter a full path to the user's save folder, prefixed with `path:`.

For example: `480 a path:D:/Game folder/Profile/Username`

### SmartSteamEmu
`[AppID] s [Username/Path]`

AppData is checked by default. If saves aren't separated by name in SSE's settings, provide no username. If they are, provide the username.

If saves aren't stored in AppData, enter a full path to the folder containing AppID subfolders.

For example: `480 s path:D:/Game folder/SmartSteamEmu/Username`

### Steam
`[AppID] st [User ID]`

A higher delay is recommended, since there is a daily limit of 100,000 requests.

You must enter your Steam Web API key in settings to track Steam achievements.

## What is supported?

### Operating systems
This was made on Windows 7, but it also supports Linux.

### Emulators
4 emulators are supported, plus real Steam. Internal names are used when loading emulator-specific settings files. Any of the short names can be used when loading a game.

| Emulator      | Internal name | Short names                    | Support level                           |
| ------------- | ------------- | ------------------------------ | --------------------------------------- |
| Goldberg      | `goldberg`    | `g, gb, goldberg`              | Full                                    |
| Codex         | `codex`       | `c, cd, cod, cdx, codex`       | Full                                    |
| ALi213        | `ali213`      | `a, ali, ali213, 213, a213`    | Full                                    |
| SmartSteamEmu | `sse`         | `s, sse, smartsteamemu, smart` | No "Achievement Progress" notifications |
| Steam         | `steam`       | `st, steam`                    | No "Achievement Progress" notifications |

### Two ways of displaying hidden/secret achievements
By default, hidden achievements are shown in the list with their description hidden. Enable `hide_secrets` in settings to hide them from the list completely and mention their existence at the end of the list, just like Steam does.

### Filter by state
Achievements can be filtered to (un)locked only. If `unlocks_on_top` is enabled in settings, unlocked ones are moved to the top of the list.

### Progressbars
This is the only such tool known to me that displays progressbars under achievements. It only supports bars that are calculated by simply checking the value of one stat, but I never saw examples of other formulas, so this should work for most (if not all) games. If an example of a different formula is found, support will likely be implemented. If the progress formula is unsupported or uses a stat type that is unsupported, a short error message will be shown instead of the progress value. This is also what happens if the bar relies on a stat that isn't present in your `stats.txt`.

### Stats
Only `int` and `float` stats are supported. I don't think Goldberg has proper `avgrate` support anyway.

### "Force unlocks"
Only Goldberg actually unlocks achievements that are based entirely on their progress value (progressbar) and aren't unlocked by the game in the normal way, so achievements with progressbars are (optionally) shown as unlocked and their timestamp is saved when the target value is reached.

### "Achievement Progress" notifications
Some rare games occasionally display "Achievement Progress" notifications on Steam. Those are supported here and even have a progressbar in the "History" tab.

### Fix for always empty progressbars
Some games' achievement pages on Steam show empty progressbars with progress numbers always being the same as target numbers. By default, this behavior is copied. Enable `bar_ignore_min` for the game in settings as a workaround. Ha, can't do that on Steam!

### Customization
Colors and fonts can be changed. Different settings can be used for specific emulators or games.

## Settings
Settings can be changed in `settings/settings.txt`. You can also create `settings/settings_[Emulator].txt`, `settings/settings_[AppID].txt` or `settings/settings_[AppID]_[Emulator]` to use different settings for an emulator (useful for `bar_force_unlock`, for example) or for a specific game (`bar_ignore_min` is a great example, or maybe you want to set some game-specific colors). The settings files use a format similar to `games.txt` and `alias.txt`. All available settings are included in the default `settings.txt`, but if you remove any, their default values will be used. Below is a list of all available settings. For boolean settings, you can use `1`/`0` as well as `true`/`false`.

### List of settings
`window_size_x`- horizontal size of the window, in pixels. Default: `800`

`window_size_y`- vertical size of the window, in pixels. Default: `600`

`delay` - time (in seconds) that must pass before files are checked for changes. Default: `0.5`

`delay_stats` - stats will only be checked for changes on every `[value]`th check. Probably useless. Default: `1` (check always)

`delay_sleep` - time (in seconds) to sleep for after every iteration of the main loop. Default: `0.1`

`delay_read_change` - time to wait for before reading a file after it was changed. Default: `0.05`

`gamebar_length` - length of the game completion bar, in pixels. Default: `375`

`gamebar_position` - decides where to show the game completion bar. `normal` - normal position (default); `repname` - hide game name and move the bar up; `under` - move the bar down, below the buttons; `hide` - hide the bar.

`frame_size` - thickness of the frames around achievement icons, in pixels. Default: `2`

`frame_color_unlock` - color to use for icon frames for unlocked achievements. Default: `255,255,255`

`frame_color_lock` - color to use for icon frames for locked achievements. Default: `128,128,128`

`hidden_desc` - replacement description to show for locked hidden achievements. Default: `[Hidden achievement]`

`hide_secrets` - if true, hidden achievements are removed from the list and their count is shown at the bottom. Default: `false`

`unlocks_on_top` - move unlocked achievements to the top of the list. Default: `false`

`bar_length` - length of achievement progress bars, also affects achievement progress notifications in history. Default: `300`

`bar_unlocked` - behavior of progressbars under unlocked achievements. `show` - no special rules; `full` - show a full bar even when the progress value is below the target (default); `hide` - hide the bar.

`bar_hide_unsupported` - hide progressbar if it's value can't be calculated. `none` - never (default); `stat` - hide if progress formula or stat type is unsupported, keep if stat not present in `stats.txt`; `all` - always.

`bar_hide_secret` - hide progressbar if the achievement is hidden and not earned. Default: `true`

`bar_ignore_min` - assume that achievement progress `min_val` is always `0`. Default: `false`

`bar_force_unlock` - display the achievement as unlocked as long as its progress has reached the target value (progressbar is full). Default: `false`

`forced_keep` - keep "force-unlocked" achievements even if the progress value drops before the achievement's target. `no` - don't keep; `session` - keep until the program is closed and don't save timestamps; `save` - save these unlocks in a file, together with their timestamps (default).

`forced_mark` - show `(F)` next to an achievement's timestamp if it's "force-unlocked". Affects history. Default: `false`

`forced_time_load` - timestamp to set for "force-unlocks" that are detected on launch. `now` - current time (default); `filechange` - last modification time of stat file.

`show_timestamps` - show timestamps. Affects history. Default: `true`

`history_length` - maximum length of history, after reaching which old entries get deleted. `0` disables the limit, `-1` disables history. Default: `0`

`history_time` - source of time to show in history. `real` - save current time when the change is recorded; `action` - save unlock times for unlock notifications and file change times for other notifications (default).

`history_unread` - mark new notifications as unread in history and show unread marks. Default: `true`

`notif` - show system notifications. Default: `true`

`notif_limit` - max amount of notifications to show during one check. Any extra notifications will be grouped into one. Default: `3`

`notif_timeout` - time (in seconds) to show the notification for. Default: `3`

`notif_lock` - show notifications (and history entries) when an achievement is locked or when the achievement progress file is deleted.

`notif_icons` - show icons in notifications. Adds extra delay on Windows if the icon converter is not used in advance.

`language` - comma-separated (no spaces) list of languages to use for achievements. First available language is used. If nothing is available, English is used. Default: `english`

`font_general` - name of font file (inside the `fonts` folder) to use for everything except achievements. Default: `Roboto/Roboto-Regular.ttf`

`font_achs` - name of font file(s) to use for achievements. Format: `Font.ttf;language,language2:OtherFont.ttf` - the font without a language prefix is used for all languages without a language-specific font. Default: `Roboto/Roboto-Regular.ttf`

`font_achs_desc` - name of font file to use for achievement descriptions, same format as `font_achs`. If not set, uses `font_achs`. Default: Empty

`font_size_general` - font size for `font_general`. Default: `15`

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

`color_bar_completed` - color to use instead of `color_bar_fill` for full bars. Default: `255,255,255`

`color_scrollbar` - color to use for scrollbar. Default: `128,128,128`

`save_timestamps` - save first and earliest timestamps of each achievement to a file. Default: `true`

`savetime_shown` - timestamps to display. `normal` - timestamp currently saved by emulator (default); `first` - first timestamp that was detected; `earliest` - the earliest out of all detected timestamps.

`savetime_mark` - show `(S)` next to an achievement's timestamp if the displayed timestamp is different from the "normal" one. Default: `false`

`savetime_keep_locked` - don't delete saved timestamps when an achievement gets locked. Default: `false`

`smooth_scale` - use `pygame.transform.smoothscale` instead of `pygame.transform.scale` to resize achievement icons when needed. Default: `true`

`api_key` - Steam Web API key. Required to track achievements from Steam. Default: Empty

## Icon converter
Windows doesn't accept `.jpg` icons for notifications, so I have to convert them to `.ico`. Doing this every time a notification is shown adds some delay.

To prevent that delay, achievement icons can be converted in advance.

After running the converter, enter the AppID (or alias) of the game you want to convert icons for.

Multiple games can be entered, separated by spaces.

Use `*` to include all games that have a `games/[AppID]` folder.

The ID(s) can be passed as command line arguments.

Adding an `-s` argument will hide output, except errors.

## To-do
List of random ideas that *might* get added/changed someday. A lot of these are minor.

- Add code comments

- Load and show unlock rates

- Search by name/description

- Unlock history showing unlocked achievements sorted by unlock time

- Notification sound

- Save current achievement states to notify about changes on launch

- Get stat display names

- Set default emulator/game/username

- Display progressbar for (un)locks in history

- Option to always show hidden descriptions

- Try to remove freezing when requesting achievements from Steam

- A way to see emulator & AppID (+ program version) inside the program

- Some basic keyboard controls

- Replacement icons (locked and unlocked) for achievements without icons? (+ icon for "Too many notifications" notification)

- Option to show if the achievement was hidden (At least in history)

- If no stat default is set in `stats.txt`, use 0

- Rework `forced_keep`

- Load-only modes for `forced_keep`, `save_timestamps`?

- Copying achievement info or stats

- Get rid of `int&-1` setting type

- Show unlocks with unknown API names somewhere??

- Allow loading different button images with different settings files?

- Per-achievement settings???