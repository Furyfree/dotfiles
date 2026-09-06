# VSCodium and Zed workflow

This matches the Zed setup from commit `467b4a2` on `config/zed`. The branches
are independent: VSCodium does not load Zed's files. Both retain their native
VS Code-style base bindings and add only the overrides needed for this workflow.

## Shared shortcuts

These are editor/workspace shortcuts, not notebook cell or terminal editing
commands. Language actions require the corresponding language support.

| Action | Linux | macOS |
|---|---|---|
| Recent projects | Ctrl+R | Cmd+Option+O |
| Open file by name | Ctrl+P | Cmd+P |
| Command palette | Ctrl+Shift+P | Cmd+Shift+P |
| Search current file | Ctrl+F | Cmd+F |
| Search project | Ctrl+Shift+F | Cmd+Shift+F |
| Current-file symbols | Ctrl+Shift+O | Cmd+Shift+O |
| Switch open tabs | Ctrl+Tab | Ctrl+Tab |
| Go to definition | F12 | F12 |
| Rename symbol | F2 | F2 |
| Code actions | Ctrl+. | Cmd+. |
| Format document | Alt+Shift+F | Option+Shift+F |
| Save | Ctrl+S | Cmd+S |
| Reopen closed tab | Ctrl+Shift+T | Cmd+Shift+T |
| Toggle left sidebar | Ctrl+B | Cmd+B |
| Focus outline | Ctrl+Shift+B | Cmd+Shift+B |
| Toggle right sidebar | Ctrl+Alt+B | Cmd+Option+B |
| Toggle bottom panel | Ctrl+J | Cmd+J |
| Toggle terminal specifically | Ctrl+Alt+Shift+J | Cmd+Option+Shift+J |
| Source control | Ctrl+Shift+G | Ctrl+Shift+G |
| Open built-in chat in Ask mode | Ctrl+Alt+I | Ctrl+Cmd+I |

Open a project, find a file, jump to a function, follow definitions, then format
and save manually. Ctrl+J is the convenient bottom-panel toggle; it restores
whichever panel was last selected, not necessarily the terminal. Use the custom
four-key shortcut to target the terminal directly. Inside the terminal, Ctrl+R
remains shell history search.

VSCodium needs explicit aliases for formatting, outline, right sidebar, source
control, chat, and macOS recent projects to match Zed. On Linux/Windows,
Ctrl+Shift+A toggles block comments like Zed's VS Code base map.
Ctrl+Shift+B therefore no longer runs a build task in VSCodium; use the command
palette's Tasks: Run Build Task. No build capability is disabled.

## VSCodium-only features

Keep native notebook and debugger bindings: Shift+Enter runs a notebook cell;
F5 starts/continues debugging, F10 steps over, and F11 steps into code. Their
availability depends on the active editor, installed extensions, and project
configuration. Notebook cells deliberately retain their own navigation context.

Ctrl+Alt+G (Cmd+Option+G on macOS) opens the installed Git Graph extension.
Extensions remain available on Ctrl+Shift+X / Cmd+Shift+X. Neither requires a
matching Zed feature or a new keymap extension.

Chat is not interchangeable: the shared shortcut opens VSCodium's built-in chat
in Ask mode only when chat is available. It does not target the separate Codex
or Claude extension panels, install Copilot, or configure credentials/providers.
Zed toggles focus to its own agent, whose default profile is Ask.

## Changes from the previous VSCodium keymap

| Previous Linux binding | Managed behavior |
|---|---|
| Ctrl+Shift+T: terminal | Reopen closed tab; terminal moves to Ctrl+Alt+Shift+J |
| Ctrl+Shift+O: recent projects | File symbols; recent projects use Ctrl+R |
| Ctrl+Shift+J: file symbols | Old override removed; use Ctrl+Shift+O |
| Ctrl+Shift+F: new Search Editor | Standard project-search view |
| Ctrl+Shift+B: primary sidebar | Outline; primary sidebar uses Ctrl+B |
| Ctrl+Shift+A: secondary sidebar | Block comment; secondary sidebar uses Ctrl+Alt+B |
| Ctrl+Shift+Y: workspace symbols | Old override removed; native Ctrl+T finds workspace symbols |
| Ctrl+K Ctrl+K: keyboard settings | Native Ctrl+K Ctrl+S opens keyboard settings |
| Ctrl+Alt+G: Git Graph | Kept |

Settings, extensions, and source-control shortcuts that already match native
behavior are not duplicated unnecessarily. Installed extensions can contribute
other bindings; use the troubleshooting commands in [README](README.md#vscodium)
to inspect conflicts on the actual Danish keyboard and operating system.

References: [VS Code keybindings](https://code.visualstudio.com/docs/configure/keybindings)
and [default shortcuts](https://code.visualstudio.com/docs/reference/default-keybindings).
