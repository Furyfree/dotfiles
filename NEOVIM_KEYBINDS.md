# Neovim keybindings

This is a small CLI editor setup, not LazyVim or a full IDE. Most editing keys
are ordinary Neovim commands. We add file/search pickers, an explorer, Git
hunk navigation, and surround editing without replacing those fundamentals.

The keys are the same in terminal Neovim on Linux and macOS: Ctrl stays Ctrl,
not Cmd. Terminal or desktop shortcuts can intercept keys; the actual Danish
keyboard layout and macOS input still need a live check.

## Reading the keys

- **Normal mode** is for moving and editing. Press Escape to return to it.
- **Insert mode** is for typing text. Press `i` to enter it.
- **Visual mode** selects text. Press `v` for characters or `V` for whole lines.
- `Space e` means press Space, release it, then press `e`; it is not a chord.
  Space is our leader key. Pause after it to see which-key's menu.
- `Ctrl+w v` means hold Ctrl and press w, release both, then press v.
- Commands starting with `:` need Enter afterward, for example `:w`.

Unless a row says otherwise, start in Normal mode. Letters are case-sensitive.

## Everyday workflow

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

## Inside a picker or explorer

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

## Native editing worth learning

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
[README](README.md#neovim). Ordinary deletes do not overwrite the system
clipboard. Ctrl+R here means redo, not the shell's fzf history search.

## Surround editing

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

## Compared with Zed and VSCodium

The workflow is familiar, but the shortcuts intentionally teach Vim rather
than imitate a graphical editor. The other editors keep their usual bindings;
see [Zed](ZED_KEYBINDS.md) and [VSCodium](VSCODIUM_KEYBINDS.md).

| Workflow | Zed/VSCodium on Linux | This Neovim setup |
|---|---|---|
| Find a file | Ctrl+P | `Space Space` |
| Search project contents | Ctrl+Shift+F | `Space /` |
| Switch open files | Ctrl+Tab | `Space ,` |
| Browse files | Left sidebar | `Space e` |
| Search current file | Ctrl+F | `/text` then Enter |
| Save | Ctrl+S | Escape, then `:w` and Enter |
| Language-aware definition/rename | F12 / F2 | Not configured yet |

There is no completion stack, language server, automatic formatter, or agent
panel here. Compared with the previous LazyVim setup, this keeps a small set
of familiar leader-key actions without bringing along the full distro.

Setup, plugin updates, migration precautions, and validation commands live in
[README](README.md#neovim). This guide documents behavior; it does not load keys.
