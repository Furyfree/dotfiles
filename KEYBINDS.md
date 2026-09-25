# Keybindings

[Neovim](#neovim) · [Zed and VSCodium](#zed-and-vscodium) · [Obsidian](#obsidian) · [Zathura](#zathura) · [Ghostty](#ghostty)

For desktop shortcuts, press **Super+Escape** in Hyprland or Niri to open the
session's shortcut guide. Super is the Windows key.

## Neovim

Use the same keys on Linux and macOS; Ctrl remains Ctrl. Setup and plugin
prerequisites are in [post-installation steps](https://github.com/Furyfree/docs/blob/main/POSTINSTALL.md#neovim).
Language-server navigation,
completion and automatic formatting are not configured.

### Reading the keys

- **Normal mode** is for moving and editing. Press Escape to return to it.
- **Insert mode** is for typing text. Press `i` to enter it.
- **Visual mode** selects text. Press `v` for characters or `V` for whole lines.
- `Space e` means press Space, release it, then press `e`; it is not a chord.
  Space is our leader key. Pause after it to see which-key's menu.
- `Ctrl+w v` means hold Ctrl and press w, release both, then press v.
- Commands starting with `:` need Enter afterward, for example `:w`.

Unless a row says otherwise, start in Normal mode. Letters are case-sensitive.

### Everyday workflow

Start Neovim from the project directory; there is no automatic project-root
switcher. Find a file with `Space Space`, press Enter to open it, then `i` to
type. Press Escape and `:w` to save. Use `Space /` to search across files and
`Space ,` to return to another open buffer. A buffer is an open file in memory;
it does not need its own visible split or tab.

These are our added mappings, defined in `lua/plugins/snacks.lua` and
`lua/plugins/gitsigns.lua` under the managed Neovim config:

| Keys | Action |
|---|---|
| `Space Space` | Find a filename below the current working directory |
| `Space /` | Search file contents below the current working directory |
| `Space ,` | Switch between open buffers |
| `Space e` | Toggle the file explorer |
| `Space s h` | Search Neovim help |
| `]h` / `[h` | Next/previous Git hunk |
| `Space g h p` | Preview the Git hunk under the cursor |

A hunk is a group of consecutive changed lines. Git keys are available in
buffers attached to Gitsigns, not every scratch buffer. There are no custom
staging or reset keys. Use the shell's existing `lg` shortcut for full Lazygit.

### Inside a picker or explorer

File searches include hidden dotfiles, respect Git ignores, and exclude `.git`.
These controls belong to Snacks, not the ordinary text-editing buffer:

| Context | Keys | Action |
|---|---|---|
| Picker input | Type text | Filter/search results |
| Picker input | `Ctrl+n` / `Ctrl+p` or arrows | Next/previous result |
| Picker input | Enter | Open the selected result |
| Picker input | Escape | Close the picker, including while typing |
| Explorer list | `j` / `k` | Move down/up |
| Explorer list | `l` or Enter | Open a file or expand a directory |
| Explorer list | `h` | Close a directory |
| Explorer list | Backspace | Go to the parent directory |
| Explorer list | `a` / `r` / `d` | Add, rename, or delete a file/directory |

Explorer file operations affect files on disk. These are plugin defaults, not
global remaps: `d` in a text buffer remains Vim's delete operator.

### Native editing worth learning

These come from Neovim itself, not our plugins:

| Keys | Action |
|---|---|
| `h` / `j` / `k` / `l` | Move left/down/up/right |
| `w` / `b` | Move forward/backward by word |
| `gg` / `G` | Go to the first/last line |
| `:w` / `:q` / `:wq` | Save / quit the current window / save and quit |
| `u` / `Ctrl+r` | Undo/redo |
| `/text` then Enter | Search this file |
| `n` / `N` | Next/previous search match |
| `ciw` | Replace the current word, entering Insert mode |
| `ci"` | Replace text inside double quotes, keeping the quotes |
| `.` | Repeat the last text change |
| `gcc` | Toggle a line comment |
| `gc` in Visual mode | Toggle comments on selected lines |
| `y` in Visual mode / `p` in Normal mode | Copy selected text / paste from Neovim's register |
| `"+y` in Visual mode / `"+p` in Normal mode | Copy to / paste from the system clipboard |
| `Ctrl+w v` / `Ctrl+w s` | Split vertically / horizontally |
| `Ctrl+w h/j/k/l` | Move to the left/down/up/right split |

Clipboard access needs a working platform provider; see the prerequisites in
[post-installation steps](https://github.com/Furyfree/docs/blob/main/POSTINSTALL.md#neovim).
Ordinary deletes do not overwrite the system
clipboard. Ctrl+R here means redo, not the shell's fzf history search.

### Surround editing

These are nvim-surround's standard commands, not built-in Neovim commands.
Press them sequentially in Normal mode with the cursor inside the text:

| Keys | Example |
|---|---|
| `ysiw"` | Add quotes: `hello` becomes `"hello"` |
| `cs"'` | Change quotes: `"hello"` becomes `'hello'` |
| `ds"` | Delete quotes: `"hello"` becomes `hello` |

Think of `ys` as adding a surround, `cs` as changing it, and `ds` as deleting
it. In the first example, `iw` means "inner word", the same text object used
by the native `ciw` command.

## Zed and VSCodium

Both use a VS Code-style base keymap with the managed overrides. The table
covers Linux and macOS with normal editor focus, without Vim mode. Windows
uses the same custom terminal shortcut as Linux; verify native input there.

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
| Toggle agent sidebar (left) | Ctrl+B | Cmd+B |
| Focus outline | Ctrl+Shift+B | Cmd+Shift+B |
| Toggle file explorer (right) | Ctrl+Alt+B | Cmd+Option+B |
| Toggle bottom panel | Ctrl+J | Cmd+J |
| Toggle terminal specifically | Ctrl+Alt+Shift+J | Cmd+Option+Shift+J |
| Source control | Ctrl+Shift+G | Ctrl+Shift+G |
| Focus agent / open chat (see differences below) | Ctrl+Alt+I | Ctrl+Cmd+I |

Open a project, find a file, jump to a function, follow definitions, then format
and save manually. Ctrl+J is the convenient bottom-panel toggle; it restores
whichever panel was last selected, not necessarily the terminal. Use the custom
four-key shortcut to target the terminal directly. Inside the terminal, Ctrl+R
remains shell history search.

VSCodium needs explicit aliases for formatting, outline, left/right sidebars, source
control, chat, and macOS recent projects to match Zed. On Linux/Windows,
Ctrl+Shift+A toggles block comments like Zed's VS Code base map.
Ctrl+Shift+B therefore no longer runs a build task in VSCodium; use the command
palette's Tasks: Run Build Task. No build capability is disabled.

### Editor differences

In VSCodium, Shift+Enter runs a notebook cell;
F5 starts/continues debugging, F10 steps over, and F11 steps into code. Their
availability depends on the active editor, installed extensions, and project
configuration. Notebook cells deliberately retain their own navigation context.

In VSCodium, Ctrl+Alt+G (Cmd+Option+G on macOS) opens the Git Graph extension.
Extensions remain available on Ctrl+Shift+X / Cmd+Shift+X. Neither requires a
matching Zed feature or a new keymap extension.

Chat is not interchangeable: the shared shortcut opens VSCodium's built-in chat
in Ask mode only when chat is available. It does not target the separate Codex
or Claude extension panels, install Copilot, or configure credentials/providers.
Zed toggles focus to its own agent, whose default profile is Ask.

OS shortcuts and extensions can intercept keys. Check the actual keyboard
using the [VSCodium troubleshooting commands](https://github.com/Furyfree/docs/blob/main/POSTINSTALL.md#vscodium)
or Zed's `zed: open default keymap` and `zed: open keymap` commands.
Native Ctrl+backtick also toggles Zed's terminal when your keyboard can send it.

References: [VS Code keybindings](https://code.visualstudio.com/docs/configure/keybindings),
[default shortcuts](https://code.visualstudio.com/docs/reference/default-keybindings),
and [Zed keybinding inheritance](https://zed.dev/docs/key-bindings).

## Obsidian

The dtu-bachelor vault follows the Zed and VSCodium layout: the Agent Client
chat sits in the left sidebar; files, search, outline and source control in
the right. Each `chezmoi apply` resets both sidebars. Close Obsidian first; while
it runs, chezmoi warns and leaves the layout alone. Mod is Ctrl on Linux and
Cmd on macOS.

| Action | Keys |
|---|---|
| Open file by name | Mod+P |
| Command palette | Mod+Shift+P |
| Switch vault | Mod+R |
| Search all notes (Omnisearch) | Mod+Shift+F |
| Toggle AI sidebar (left) | Mod+Shift+A |
| Focus outline | Mod+Shift+B |
| Toggle file explorer (right) | Mod+Alt+B |
| Focus file explorer | Mod+Shift+E |
| Split editor right | Mod+\\ |
| Source control | Mod+Shift+G |
| Focus agent chat | Mod+Alt+I |
| Toggle Typst preview | Mod+Shift+V |
| New Typst file (next to the open file) | Mod+Alt+N |
| Export Typst PDF (replaces the old one) | Mod+Alt+E |

Mod+B stays bold, so the AI sidebar uses Mod+Shift+A instead of Zed's Mod+B.

## Zathura

Everyday shortcuts for the managed Linux setup, checked against Zathura
2026.07.18. The [config](home/dot_config/zathura/zathurarc.tmpl) keeps native
bindings and adds three view shortcuts. Setup is in
[post-installation steps](https://github.com/Furyfree/docs/blob/main/POSTINSTALL.md#zathura-and-webapps).

Letters are case-sensitive: `j` scrolls, while `J` changes page. Type sequences
such as `18G` and `125=` directly in normal reading mode, without `:` or Enter.
Press Escape to cancel a prompt or leave the document index.

### Reading

| Keys | Action |
|---|---|
| `a` / `s` | Fit the whole page / fit page width |
| `P` | Align the current page in the view |
| `j` / `k` | Scroll down / up |
| `h` / `l` | Scroll left / right when zoomed in |
| `Page Down` or `J` | Next page |
| `Page Up` or `K` | Previous page |
| `Home` or `gg` | First page (start of the document) |
| `End` or `G` | Last page (end of the document) |
| `18G` | Go to physical PDF page 18 (with the default zero page offset) |
| `+` / `-` | Zoom in / out |
| `125=` / `=` | Set 125% zoom / reset zoom |

New documents start fitted to the whole page. For slides, press `a`, then `P`
to fit and align the current slide. For long pages, use `s` and scroll.
Previously opened documents restore their saved zoom, so press `a` once if an
old document still opens too large.

### Slide labels and PDF pages

In `[25 (35/71)]`, `25` is the slide/page label and `35` is the physical PDF
page. Several physical pages can share a label when a slide reveals content
in stages. `35G` goes directly to physical page 35; Page Up/Down move through
individual physical pages. Zathura displays embedded labels but has no native
shortcut to jump to a label or skip to the next distinct label. If the PDF
provides an index, use Tab to navigate its entries.

### Find and return

| Keys | Action |
|---|---|
| `/text` then Enter | Search the document |
| `n` / `N` | Next / previous search result |
| `Tab` | Open or close the document index |
| `f` | Follow a document link |
| `Ctrl-O` / `Ctrl-I` | Backward / forward through jump history |

After jumping through the index or following an internal link, `Ctrl-O`
returns to the previous reading position. Inside the index, use `j`/`k` to
choose an entry and Enter to open it.

### View controls

| Keys | Action |
|---|---|
| `Ctrl-R` or `F4` | Toggle recoloring |
| `d` or `F6` | Toggle one/two-page layout |
| `b` or `Ctrl-N` | Toggle the status bar |
| `r` | Rotate the page |
| `R` | Reload the document |
| `F5` / `F11` | Toggle presentation mode / fullscreen |
| `q` | Quit |

Recoloring starts off so diagrams and images keep their original colors.

References: [native Zathura shortcuts](https://pwmt.org/projects/zathura/documentation/)
and [default bindings for 2026.07.18](https://github.com/pwmt/zathura/blob/2026.07.18/zathura/config.c#L273-L290).

## Ghostty

The [config](home/dot_config/ghostty/config.tmpl) keeps Ghostty's native
shortcuts and adds split resizing on Linux, where the desktop takes the
default. Linux keys come from `ghostty +list-keybinds` on Ghostty 1.3.1;
macOS keys come from Ghostty 1.3.1's
[default bindings](https://github.com/ghostty-org/ghostty/blob/v1.3.1/src/config/Config.zig).

| Action | Linux | macOS |
|---|---|---|
| Copy / paste | Ctrl+Shift+C / Ctrl+Shift+V | Cmd+C / Cmd+V |
| Search scrollback | Ctrl+Shift+F, Escape to close | Cmd+F, Escape to close |
| Command palette | Ctrl+Shift+P | Cmd+Shift+P |
| New tab / close tab | Ctrl+Shift+T / Ctrl+Shift+W | Cmd+T / Cmd+Option+W |
| Next / previous tab | Ctrl+Tab / Ctrl+Shift+Tab | Ctrl+Tab / Ctrl+Shift+Tab |
| Go to tab 1-8 / last tab | Alt+1-8 / Alt+9 | Cmd+1-8 / Cmd+9 |
| Split right / split down | Ctrl+Shift+O / Ctrl+Shift+E | Cmd+D / Cmd+Shift+D |
| Move between splits | Ctrl+Alt+arrows | Cmd+Option+arrows |
| Resize the current split | Ctrl+Alt+Shift+arrows | Cmd+Ctrl+arrows |
| Zoom the current split | Ctrl+Shift+Enter | Cmd+Shift+Enter |
| Close the current split | Ctrl+D or `exit` | Cmd+W, Ctrl+D or `exit` |
| Previous / next prompt | Ctrl+Shift+Page Up / Page Down | Cmd+Up / Cmd+Down |
| Scroll a page / to top or bottom | Shift+Page Up/Down / Shift+Home/End | Cmd+Page Up/Down / Cmd+Home/End |
| Font size bigger / smaller / reset | Ctrl+= / Ctrl+- / Ctrl+0 | Cmd+= / Cmd+- / Cmd+0 |
| New window | Ctrl+Shift+N | Cmd+N |
| Reload config | Ctrl+Shift+, | Cmd+Shift+, |

On Linux, selecting text copies it to the primary selection; middle-click
pastes it. Ctrl+Shift+V still pastes the regular clipboard.
