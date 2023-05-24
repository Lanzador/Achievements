## v1.2.0
- Achievement unlock rates. Can be added after achievement name or after its description. They're saved in a file for offline access. Achievements can be sorted by rarity in settings. Different colors can be set for rare achievements.
- No longer freezes during achievements/stats requests when tracking achievements from Steam.
- "History unlocks" screen where unlocks are sorted by time. This can also be enabled for the main list.
- Changed default for `savetime_shown` to `first`. It makes sense because there are likely cases where an achievement gets re-unlocked normally after a "force-unlock". In general, you usually don't want timestamps to change. Note that if you disable `save_timestamps`, they'll still be saved within the current session.
- Added `bar_unlocke=zerolen`, which hides the bar, but keeps the numbers (their behavior is similar to `full`).
- Highlight achievements when they're hovered over. Highlight color can be changed in settings.
- Click an achievement to print some info about it. Hold `SHIFT` to include description if the achievement is hidden. I also made an option to hold `CTRL` to choose a language for name/description, but commented it out since `input()` freezes everything and kills `pyw`.
- Other minor things.

## v1.1.2
- Fix SSE achievements not updating.

## v1.1.1
- If bar length is set to 0, remove the empty space between the bar and the x/y text. (This was supposed to be in v1.1.0, but I forgot to finish it. And I also forgot to name the commit just now.)

## v1.1.0
- Can now use an alias only for its AppID. If an emulator name is specified after the alias, it's used instead of the one from `alias.txt`.
- Unlock timestamps can now be saved to display the correct time even if the emulator overwrites it. Related options were added.
- Added support for ALi213, SmartSteamEmu and even normal Steam.
- Now using `pygame.transform.smoothscale` instead of `pygame.transform.scale` by default. This is a better way to resize icons if needed. Old behavior can be restored by disabling `smooth_scale` in settings.
- Saves are now separated by username/ID. This affects different storage locations for Codex, too.
- `forced_time_load` setting to choose timestamp for force-unlocks achieved while the program wasn't running.
- `unlocks_on_top` setting to optionally show unlocked achievements at the top of the list.
- Font sizes can now be chosen for each font with a syntax similar to `font_achs`. Added `font_size_general`.
- Added `font_achs_desc` to allow choosing a separate font for descriptions.
- If no default font is chosen in one of the options, Roboto is used.
- Game names are now automatically retrieved from Steam. Game name can also be changed through `LnzAch_gamename` environment variable. `=` can be used in names.
- Added window size options.
- Added multiple options for the game progress bar's position to not break things with a small window size.
- Notifications have icons now. This causes extra delay on Windows, but `icon_converter.py` can solve that. Can be disabled in settings (`notif_icons`).
- Full bars now use `color_bar_completed` instead of `color_bar_fill`. By default, it's white, just like `color_bar_fill`.
- `settings_[AppID]_[Emulator].txt` is now loaded.
- On Linux, use `unotify` to display notifications on top of full screen games.
- Can scroll using mouse wheel and Page Up / Page Down.
- Bugfixes and minor changes.
