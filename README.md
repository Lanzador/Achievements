# Lanzador/Achievements
A program that lets you view your achievements and stats from Steam emulators. Most of v1.0.0 was made in around a week, although the release was delayed. Some things are unobvious, so please read this.

## Dependencies
Made with Python 3.8.10. Only dependencies are pygame and plyer.

## Usage
This works based on local files, so you need to generate the list of achievements before you can do anything. To do that, use [Goldberg's generate_emu_config.py](https://gitlab.com/Mr_Goldberg/goldberg_emulator/-/tree/master/scripts). The generated `achievements.json`, `achievement_images` and `stats.txt` should be put in `games/[AppID]`. You can also edit `games/games.txt` to see a proper game name instead of the AppID and `games/alias.txt` to load the achievements using a short name instead of remembering AppIDs.

The two txts follow this format:
```
AppID=Name or alias
AppID=Name or alias
AppID=Name or alias
```
Lines not containing `=` (or containing more than one `=`) are ignored.

Once you set this up, you can open the list by running `window.py` (or `achievements.exe` if you downloaded the release version) and entering the AppID or alias of the game. You can also pass it (and the values below) as arguments.

By default, it's assumed that you use Goldberg. Below are instructions for other emulators.

### Codex
After the AppID, put a space and add a `c`: `[AppID] c`

By default it checks the Codex folder located in Documents, but for some versions of Codex you'll want to look for achievement files in AppData instead. If that's the case, just add an `a`: `[AppID] c a`

## What is supported?

### Operating systems
This was made and tested on Windows 7, but it should also support Linux.

### Emulators
As of now, only Goldberg and Codex are supported, but more may be added later.

### Two ways of displaying hidden/secret achievements
By default, hidden achievements are shown in the list with their description hidden. Enable `hide_secrets` in settings to hide them from the list completely and mention their existence at the end of the list, just like Steam does.

### Filter by state
The achievements are always shown in the same order - unlocked ones aren't moved to the top (because it's easier to implement and I prefer it like this anyway), but you can view (un)locked achievements only. Useful if you're playing a game with 637 achievements, right?

### Progressbars
This is the only such tool known to me that displays progressbars under achievements. It only supports bars that are calculated by simply checking the value of one stat, but I never saw examples of other formulas, so this should work for most (if not all) games. If an example of a different formula is found, support will likely be implemented. If the progress formula is unsupported or uses a stat type that is unsupported, a short error message will be shown instead of the progress value. This is also what happens if the bar relies on a stat that isn't present in your `stats.txt`.

### Stats
Only `int` and `float` stats are supported. I don't think Goldberg has proper `avgrate` support anyway.

### "Force unlocks"
Only Goldberg actually unlocks achievements that are based entirely on their progress value (progressbar) and aren't unlocked by the game in the normal way, so achievements with progressbars are (optionally) shown as unlocked when the target value is reached and their timestamp is saved.

### "Achievement Progress" notifications
Some rare games occasionally display "Achievement Progress" notifications on Steam. Those are supported here and even have a cool progressbar in the "History" tab.

### Fix for always empty progressbars
Some games' achievement pages on Steam show empty progressbars with progress numbers always being the same as target numbers. By default, this behavior is copied. Enable `bar_ignore_min` for the game in settings as a workaround. Ha, can't do that on Steam!

## Settings
Settings can be changed in `settings/settings.txt`. You can also create `settings/settings_[Emulator].txt` or `settings/settings_[AppID].txt` to use different settings for an emulator (useful for `bar_force_unlock`, for example) or for a specific game (`bar_ignore_min` is a great example, or maybe you want to set some game-specific colors). The settings files use a format similar to `games.txt` and `alias.txt`. All available settings are included in the default `settings.txt`, but if you remove any, their default values will be used. Below is a list of all available settings. For boolean settings, you can use `1`/`0` as well as `true`/`false`.

Allowed emulator names: `goldberg`, `codex`

### List of settings
`delay` - time (in seconds) that must pass before files are checked for changes. Default: `0.5`

`delay_stats` - stats will only be checked for changes on every [value]th check. Probably useless. Default: `1` (check always)

`delay_sleep` - time (in seconds) to sleep for after every iteration of the main loop. Default: `0.1`

`delay_read_change` - time to wait for before reading a file after it was changed. Default: `0.05`

`gamebar_length` - length of the game completion bar, in pixels. Default: `375`

`frame_size` - thickness of the frames around achievement icons, in pixels. Default: `2`

`frame_color_unlock` - color to use for icon frames for unlocked achievements. Default: `255,255,255`

`frame_color_lock` - color to use for icon frames for locked achievements. Default: `128,128,128`

`hidden_desc` - replacement description to show for locked hidden achievements. Default: `[Hidden achievement]`

`hide_secrets` - if true, hidden achievements are removed from the list and their count is shown at the bottom. Default: `false`

`bar_length` - length of achievement progress bars, also affects achievement progress notifications in history. Default: `300`

`bar_unlocked` - behavior of progressbars under unlocked achievements. `show` - no special rules; `full` - show a full bar even when the progress value is below the target (default); `hide` - hide the bar.

`bar_hide_unsupported` - hide progressbar if it's value can't be calculated. `none` - never (default); `stat` - hide if progress formula or stat type is unsupported, keep if stat not present in `stats.txt`; `all` - always.

`bar_hide_secret` - hide progressbar if the achievement is hidden and not earned. Default: `true`

`bar_ignore_min` - assume that achievement progress `min_val` is always `0`.

`bar_force_unlock` - display the achievement as unlocked as long as its progress has reached the target value (progressbar is full). Default: `false`

`forced_keep` - keep "force-unlocked" achievements even if the progress value drops before the achievement's target. `no` - don't keep; `session` - keep until the program is closed and don't save timestamps; `save` - save these unlocks in a file, together with their timestamps (default).

`forced_mark` - show `(F)` next to an achievement's timestamp if it's "force-unlocked". Affects history. Default: `false`

`show_timestamps` - show timestamps. Affects history. Default: `true`

`history_length` - maximum length of history, after reaching which old entries get deleted. `0` disables the limit, `-1` disables history. Default: `0`

`history_time` - source of time to show in history. `real` - save current time when the change is recorded; `action` - save unlock times for unlock notifications and file change times for other notifications (default).

`history_unread` - mark new notifications as unread in history and show unread marks. Default: `true`

`notif` - show system notifications. Default: `true`

`notif_limit` - max amount of notifications to show during one check. Any extra notifications will be grouped into one. Default: `3`

`notif_timeout` - time (in seconds) to show the notification for. Default: `3`

`notif_lock` - show notifications (and history entries) when an achievement is locked or when the achievement progress file is deleted.

`language` - comma-separated (no spaces) list of languages to use for achievements. First available language is used. If nothing is available, English is used. Default: `english`

`font_general` - name of font file (inside the `fonts` folder) to use for everything except achievements. Default: `Roboto/Roboto-Regular.ttf`

`font_achs` - name of font file(s) to use for achievements. Format: `Font.ttf;language,language2:OtherFont.ttf` - the font without a language prefix is used for all languages without a language-specific font. If there's no default font and a language without its own font is chosen, the program will not run. Default: `Roboto/Roboto-Regular.ttf`

`font_size_regular` - regular font size. Default: `15`

`font_size_small` - small font size (used for descriptions). Default: `13`

`font_line_distance_regular` - distance between the beginning of each line. Default: `16`

`font_line_distance_small` - distance between the beginning of each line (small font). Default: `16`

`color_background` - background color. Default: `0,0,0`

`color_text` - default text color. Default: `255,255,255`

`color_text_unlock` - text color for unlocked achievements. Default: `255,255,255`

`color_text_lock` - text color for locked achievements. Default: `128,128,128`

`color_bar_bg` - color to use for progressbar background. Default: `128,128,128`

`color_bar_fill` - color to use for progressbar fill. Default: `255,255,255` - fun fact: this was originally `0,255,0`

`color_scrollbar` - color to use for scrollbar. Default: `128,128,128`

## To-do
List of random ideas that *might* get added/changed someday. A lot of these are minor.

- **Support for ALi213 and/or SmartSteamEmu**

- **Save timestamps.** Necessary for proper timestamps on SSE. Also prevents the timestamp from changing if an achievement transitions from a "force unlock" to a normal unlock.

- Add code comments

- Scroll using mouse wheel (mine's broken, so can't test if I add this)

- Set default emu/game

- Notification sound

- Options to save history and/or disallow duplicates in history???? (Unlikely)

- Show another notification after a "forced-to-normal" unlock transition

- Stat/progress rounding accuracy option?

- Search by name/description

- Option to always show hidden descriptions?

- Display progressbar for (un)locks in history??

- A way to see the emulator used inside the program?

- Replacement icons (locked and unlocked) for achievements without icons

- Option to show if the achievement was hidden? (At least in history)

- Improve alias system

- Run "force unlock" checks when an achievement gets locked

- If no stat default is set in `stats.txt`, use 0?

- Rework `forced_keep`?

- Some basic keyboard controls

- A time-based `notif_limit`?

- Different color for full bars

- Get rid of `int&-1` setting type

- Show version somewhere inside the program?
