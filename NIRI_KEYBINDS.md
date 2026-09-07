# Niri keybindings

`Mod` is Super in a normal Niri session (Alt in a nested test window).
The source of truth is `home/dot_config/niri/keybinds.kdl`. These are native
Niri actions plus DMS shell controls, not a Nirius wrapper. Setup, dependencies
and validation are in [README.md](README.md#niri-and-dankmaterialshell).

## Everyday workflow

| Keys | Action |
|---|---|
| Mod+Return | Open the default terminal |
| Mod+Space | Application launcher; find other apps here |
| Mod+Shift+B | Open the default browser through its desktop entry |
| Mod+Shift+F | Open home in the default file manager |
| Ctrl+Shift+Space | 1Password Quick Access |
| Mod+O | Overview |
| Mod+Escape | Niri's keyboard-shortcut overlay |
| Alt+Tab / Alt+Shift+Tab | Next / previous recent window on this output |
| Mod+W | Close the focused window |
| Mod+F | Toggle maximized column width |
| Mod+Shift+Return | Toggle fullscreen |
| Mod+Q | Toggle floating |
| Mod+Shift+Q | Switch focus between floating and tiled windows |
| Mod+Ctrl+T | Toggle tabs for the current column |

The terminal/browser/file-manager keys launch through desktop defaults. They
do not promise focus-or-spawn: whether an existing window is reused belongs
to the application. Alt+Tab or the overview finds existing windows.

## Navigation and layout

| Keys | Action |
|---|---|
| Mod+Left / Right | Focus adjacent column |
| Mod+Up / Down | Focus a window within a stacked column |
| Add Shift to those arrows | Move the column horizontally / window vertically |
| Mod+Ctrl+arrows | Focus the monitor in that direction |
| Mod+Ctrl+Shift+arrows | Move the column to that monitor |
| Mod+PageUp / PageDown | Previous / next workspace |
| Mod+Shift+PageUp / PageDown | Move the column to the previous / next workspace |
| Mod+1-9 | Focus workspace 1-9 |
| Mod+Shift+1-9 | Move the column to workspace 1-9 |
| Mod+[ / ] | Combine with a neighboring column, or split toward that side |
| Mod+R | Cycle column widths: one third, half, two thirds |
| Mod+Shift+R | Cycle window heights |
| Mod+Ctrl+R | Reset window height |
| Mod+C | Center the current column |
| Mod+- / = | Narrow / widen column by 10% |
| Mod+Shift+- / = | Reduce / increase window height by 10% |

Shift consistently means "move" in the navigation families. Niri columns
can hold several windows; moving a column moves that whole group. Numbered
workspaces remain dynamic, not nine permanently named workspaces.

## Shell and hardware

| Keys | Action |
|---|---|
| Mod+V | Clipboard history |
| Mod+M | Task manager |
| Mod+N | Notifications |
| Mod+, | DMS settings |
| Mod+L | Lock screen |
| Mod+Shift+L | Power menu |
| Mod+Shift+Alt+Escape | Quit Niri, with confirmation |
| Print | Select a screenshot area |
| Ctrl+Print | Screenshot the focused screen |
| Alt+Print | Screenshot the focused window |
| Volume keys | Change volume by 3%, or toggle mute |
| Microphone mute key | Toggle microphone mute |
| Play / Pause / Previous / Next | Control media playback |
| Brightness keys | Change brightness by 5% |

Only hardware media and brightness shortcuts work while locked. The Pause
key pauses; Play toggles play/pause. The screenshot UI can cancel with Escape.
Screenshots use Niri's native clipboard/save behavior and the existing
`~/Pictures/Screenshots/` location. Keyboard layouts differ: especially check
brackets, minus/equal and Print on the installed machine.

## Differences from the reference setup

Most daily keys are unchanged. These are the deliberate simplifications:

- Arrow navigation remains; the U/I and wheel workspace aliases are removed.
- Mod+Shift+PageUp/PageDown now moves the column, not the workspace itself.
  Workspace reordering has no dedicated shortcut for now.
- Print/Ctrl+Print/Alt+Print replace the overlapping Mod+Shift+S and
  XF86Launch1 screenshot families. On a keyboard without Print, replace this
  family in the source rather than adding a second parallel family.
- Mod+M remains the task manager; the duplicate Ctrl+Alt+Delete is removed.
- Per-app and per-webapp shortcuts, their focus/new pairs, wallpaper and
  notepad shortcuts are removed. Use the launcher and DMS settings instead.
- Mod+Shift+B remains the browser key; Mod+Alt+B is removed with Nirius.
- Mod+Home/End, extra centering/expel actions, and workspace-reorder shortcuts
  are left unbound. Native actions remain available if they become useful.

The module names (input, outputs, layout, rules, autostart, shell, keybinds)
are intended to match the responsibilities of the future Hyprland config.
The files stay separate because the compositors have different syntax and
layout models. No Hyprland bindings are changed by this branch.

References: [Niri keybindings](https://niri-wm.github.io/niri/Configuration:-Key-Bindings.html),
[recent-window switching](https://niri-wm.github.io/niri/Configuration:-Recent-Windows.html),
and [DMS IPC](https://danklinux.com/docs/dankmaterialshell/keybinds-ipc).
