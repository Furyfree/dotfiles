# Vis, Vim and Neovim comparison

Research date: 30 September 2026, on this Fedora 44 workstation. Results from
one machine do not rank the editors on other systems.

Decision: Vis is the default editor, configured to stay close to Vim's keys.
Neovim remains for Git hunk previews, persistent undo and a file tree. Servers
use stock Vim. Vis becomes `EDITOR` only where it is installed; Nimbus does not
provision it, so other machines fall back to Neovim.

**Size**

| | Vis 0.9 | Vim 9.2.1129 | Neovim 0.12.5 |
| --- | ---: | ---: | ---: |
| Installed package payload | 1.20 MiB | 43.20 MiB (`vim-enhanced` + `vim-common`) | 33.13 MiB |
| Executable | 0.36 MiB | 4.51 MiB | 5.41 MiB |
| Core C and headers (tokei code lines) | 19,926 | 467,085 | 273,791 |
| Whole checkout (tokei code lines) | 144,143 | 1,337,286 | 1,179,173 |

The core selections are Vis's root `*.c`/`*.h`, Vim's `src` without `testdir`
and `libvterm`, and Neovim's `src/nvim` without `vterm`. Vis's core is 23 times
smaller than Vim's and 14 times smaller than Neovim's: about one order of
magnitude, not two. Whole-checkout counts include tests, runtime files and
translations. Tokei classifies Vis's `.in` test fixtures as 106,003 lines of
Autoconf, so Vis's whole-checkout figure overstates its code. Vim script is
43% of Vim's and 35% of Neovim's code lines, mostly syntax, filetype and test
files rather than platform legacy.

Snapshots: Vis `254329d9f4f1` (2026-08-19), Vim `4505de43911a` (2026-09-29),
Neovim `298aea738275` (2026-09-30).

```sh
git clone --depth 1 https://github.com/martanne/vis /tmp/compare/vis   # likewise vim/vim, neovim/neovim
tokei /tmp/compare/vis/*.c /tmp/compare/vis/*.h
tokei /tmp/compare/vim/src --types C,'C Header' --exclude '**/testdir/**' --exclude '**/libvterm/**'
tokei /tmp/compare/neovim/src/nvim --types C,'C Header' --exclude '**/vterm/**'
rpm -q --qf '%{NAME}: %{SIZE} bytes\n' vis vim-enhanced vim-common neovim
```

**Speed and memory**

Every editor opens a normal file in well under 50 ms; startup does not decide
the choice. Headless startup with this repository's Neovim config took 35 ms
against 13 ms for `nvim --clean`; `config/lazy.lua` accounts for about 11.5 ms,
including a `git rev-parse` on every start. Enabling `undofile` alone raised the time to
open an 11 MiB file in `nvim --clean` from 12 ms to 46 ms.

Peak resident memory when opening and quitting a file in a pseudo-terminal:

| | Small config file | 11 MiB text file |
| --- | ---: | ---: |
| Vis, stock | 12 MiB | 16 MiB |
| Vim, defaults | 18 MiB | 29 MiB |
| Neovim, `--clean` | 12 MiB | 24 MiB |
| Neovim, this config | 15 MiB | 27 MiB |

A language server adds its own process and memory to any of these.

**Keys: where Vis differs from Vim**

Vis keeps Vim's operators, motions, text objects, registers, `:w`/`:q`/`:e` and
window splits. Its defaults differ in these places:

| Area | Vim | Vis | This config |
| --- | --- | --- | --- |
| `n` / `N` | Repeat / reverse the last search's direction | Always forward / backward | Remapped to Vim behaviour |
| `=` | Reindent | Pipes through `fmt` | Unchanged; use `:lspc-format` |
| `Ctrl-w h/l` | Left / right window | Previous / next window | Unchanged |
| Regex | Vim regex | POSIX extended regex | Unchanged |
| Substitute | `:%s/a/b/g` | Sam commands such as `:x/a/ c/b/` | Unchanged |
| Visual block | `Ctrl-v` | None; use multiple selections (`Ctrl-j`/`Ctrl-k`) | Unchanged |
| `%` | Jump to match | Sometimes needs two presses | Unchanged |

Sources: [default mappings](https://github.com/martanne/vis/blob/254329d9f4f1df1158397080d403f3f112918aff/config.def.h),
[Differences from Vi(m)](https://github.com/martanne/vis/wiki/Differences-from-Vi(m)).

Vis defines none of `gd`, `gD`, `gi`, `gr` or `K`, so the language-server
plugin's bindings add behaviour without replacing Vis defaults. They differ
from Neovim's built-in `grn`/`grr`/`gra`/`gri` keys.

**The Vis configuration**

[visrc.lua](home/dot_config/vis/visrc.lua) keeps the earlier options and adds:

- Vim-style `n`/`N`.
- `Space Space`: fzf over `rg --files --hidden -g '!.git'`, which respects
  ignore files and keeps dotfiles, like the Snacks picker in Neovim.
- `Space /`: live `rg` search through fzf; Enter opens the file at the line.
- `Space ff` finds files too; `Space sw` searches the current word literally.
  Both text searches show a bat preview centred on the match, with
  Ctrl-u/Ctrl-d scrolling. Tab-separated fields preserve colons in paths;
  filenames containing tabs or newlines remain unsupported in text search.
- `Space e` browses directories and hidden files in a temporary fzf list.
  Choose `/..` to go up; Enter on a file opens it and closes the list.
  `Space ,` focuses an existing window without discarding its edits.
- `yy`, `yiw` and Visual `y` copy to the system clipboard, with `Copied`
  feedback after success. `p`/`P` paste globally. Named registers stay local;
  deletes do not replace the clipboard. Native yank motions and counts remain.
- A coloured status bar names Normal, Insert, Visual, Replace and pending
  operator modes. It retains the filename, modified marker and cursor position.
  An unfinished Space sequence shows `SPACE …`. Clipboard feedback stays in
  the bar for about two seconds, then clears without another keypress.
- Optional plugins through [vis-plug](https://github.com/erf/vis-plug), pinned
  to commits and installed with `:plug-install`. Startup never downloads; the
  editor works without them.

| Plugin | Purpose | Pinned commit |
| --- | --- | --- |
| [vis-lspc](https://codeberg.org/muhq/vis-lspc) | Language servers: gopls (default), ruff and taplo (configured) | `c54c24b2639c` (2026-09-22) |
| [vis-commentary](https://github.com/Nomarian/vis-commentary) | `gcc` / `gc`, as in Neovim and Vim's comment package | `223dcc6f3f70` |
| [vis-editorconfig-options](https://github.com/milhnl/vis-editorconfig-options) | Project indentation from `.editorconfig` | `2f34c4501da7` |

Our bindings use [LazyVim's keys](https://www.lazyvim.org/keymaps): `gI` implementation, `gy` type definition,
`Space cd` diagnostics, `[d`/`]d` previous/next diagnostic, `Space ss` symbols,
`Space cr` rename and `Space cf` format. `gd`, `gD`, `gr`, `K`, Ctrl-Space
completion and Ctrl-]/Ctrl-t definition/back remain. `Space e` overrides
the plugin's diagnostic shortcut with the directory browser. Full bindings
are in [KEYBINDS.md](KEYBINDS.md#vis).

Ruff provides Python diagnostics and formatting, but does not replace a
Python navigation/completion server. No additional server has been selected
or installed. Go uses gopls and TOML uses Taplo. Formatting is explicit;
there is no format-on-save hook. The EditorConfig plugin supports
`indent_style`, `indent_size`, `tab_width` and `max_line_length`.

**Tree-sitter and Telescope-style search**

Tree-sitter parses code into a syntax tree, which integrations can use for
highlighting and selecting code structures. A file tree lists directories.
A fuzzy picker filters a list and previews a selected result. These serve
different needs.

| Editor | Code highlighting and structure | Search in this setup |
| --- | --- | --- |
| Vis | Lua/LPeg highlighting; external `vis-treesitter` exists | fzf, ripgrep and bat; vis-lspc handles language-server requests |
| Vim on servers | Keyword and pattern-based syntax highlighting | Stock `/`, `?` and file commands |
| Neovim | Built-in Tree-sitter integration, with language parsers | Snacks file/text pickers and explorer |

Vis uses [LPeg grammars](https://github.com/martanne/vis#readme) for its normal
highlighting. Its [plugin wiki](https://github.com/martanne/vis/wiki/Plugins)
lists `vis-treesitter` as basic Tree-sitter support, alongside `vis-fzf-open`
and `vis-fzf-mru` for file picking and recent files. The Tree-sitter source
page could not be retrieved during this research. Its dependencies, supported
languages, text objects and compatibility with installed Vis 0.9 remain
unverified; our configuration does not load it.

[Vim's syntax engine](https://github.com/vim/vim/blob/4505de43911a/runtime/doc/syntax.txt)
matches keywords and patterns without parsing the whole file.
[Neovim integrates Tree-sitter](https://github.com/neovim/neovim/blob/298aea738275/runtime/doc/treesitter.txt)
and bundles several parsers; other languages need additional parsers. Our
Neovim configuration starts Tree-sitter when a matching parser exists and
retains ordinary highlighting otherwise. Tree-sitter does not replace a
language server for completion, rename or cross-file definitions.

If "looking glass" meant [Telescope](https://github.com/nvim-telescope/telescope.nvim),
it is a Neovim plugin for searching files, text, symbols and other lists with
previews. It depends on Neovim's APIs and cannot run as a Vis Lua plugin.
Our Neovim setup uses Snacks for that role. In Vis, `Space Space`, `Space /`
and `Space sw` cover file and text search, including match context, through
fzf/rg/bat. They do not provide Telescope's full set of language-server, help,
history and Git pickers. The intended name remains unconfirmed.

**Directory browsing and project startup**

Vis's upstream README lists an integrated file/directory browser as a
[core non-goal](https://github.com/martanne/vis#non-goals). Plugins can still
extend it. I did not identify a ready-made persistent file tree in the checked
Vis plugin list. Existing choices include:

| Choice | What exists | Limit for our workflow |
| --- | --- | --- |
| Bundled `vis-open` | `:e .` uses an external menu to traverse directories and choose a file | Temporary menu; Vis mappings do not run inside it |
| Current `Space e` | fzf directory list with hidden files and parent navigation | Closes after selection; fzf takes keyboard input |
| lf | Standalone file manager with Vim-like navigation and a file-selection mode | Needs Vis integration; owns the keyboard while open |
| Yazi | Standalone file manager with a chooser interface | Needs Vis integration; owns the keyboard while open |

The [Vis 0.9 helper](https://github.com/martanne/vis/blob/v0.9/vis-open)
uses `vis-menu`, adds a parent entry and lists directories with `ls -1`, which
omits hidden files. Daccfiles' `Space fm` calls `:open .`, then switches windows
and executes `wq!`; it does not implement a directory buffer. That forced
write-and-close behaviour should not become our browsing shortcut.

[lf's documented `-print-selection` and `-selection-path` options](https://github.com/gokcehan/lf/blob/master/doc.md)
return selected paths to a caller. Yazi's documentation demonstrates
[`--chooser-file` integration with Helix](https://yazi-rs.github.io/docs/tips/#file-tree-picker-in-helix).
Those interfaces could return a file to the existing Vis session with Lua
glue. Neither example establishes a tested Vis integration or a persistent
Vis sidebar.

For browsing with `Space Space` and `Space /` available at the same time, a
directory buffer inside Vis would keep its mappings active. External managers
would need their own bindings and a way to return a search action to Vis.
The native directory-buffer approach is a proposed configuration change,
not an existing feature of our setup. It should preserve unsaved windows and
keep project searches rooted at the project while browsing parent folders.
Vis 0.9 rejects `vis .` at startup; handling directory arguments also needs
an entry-point change. Keep LPeg and the current search tools for now;
Tree-sitter can be evaluated separately once its source and compatibility
can be checked.

**Tested on Vis 0.9**

With vis-lspc cloned into a disposable configuration directory:

| Check | Result |
| --- | --- |
| gopls, ruff and taplo start when a matching file opens | Works |
| Line diagnostic shows `6:14 UndeclaredName: undefined: undefinedVar` | Works; now bound to `Space cd` |
| `gd` jumps to the declaration under the cursor | Works |
| Hover, rename and completion | Not verified |

gopls sends an informational "Finished loading packages" notice. At the
plugin's default `message_level = 3`, it opens an unnamed window that takes
focus, and later lspc commands fail with `init.lua:1555: attempt to concatenate
a nil value (field 'path')`. The configuration sets `message_level = 2`, which
keeps warnings and errors and fixed the tested commands.

The previous configuration passed checks for `n`/`N`, file/text pickers,
ignore handling and Esc cancellation in a pseudo-terminal. The revised
configuration passes native Vis 0.9 checks for yank motions/counts, repeated
yanks, cancellation, named registers, multiple selections, linewise paste,
non-ASCII clipboard text and clipboard-helper failures, using an isolated
clipboard substitute. Navigation checks cover special filenames, unsaved
changes, directory traversal and switching windows. The real rg/fzf/bat search
shows surrounding context and opens a filename containing colons, quotes and
backslashes at its matching line. Mode labels and terminal-palette styles
also pass through Vis's status API.

The complete setup through vis-plug has not been run: executing the downloaded
plugin code in a test directory was blocked. Formatting, completion,
EditorConfig and non-ASCII language-server requests still need the live checks
below. Lua syntax and whitespace checks pass; the repository gate is blocked
by uv's read-only cache. Chezmoi's secret-skipping status and diff now report
no pending Vis configuration difference; full verify still exits nonzero.

No Lua JSON library is installed, so vis-lspc uses its bundled fallback, which
lacks UTF-8 support; non-ASCII source text may break requests. Fedora's
`lua-json` package would provide the `json` module, but system packages belong
to Nimbus.

**Setting up Vis**

1. Apply only this configuration: `chezmoi apply ~/.config/vis/visrc.lua`.
   Restart Vis to load it.
2. Install vis-plug at its pinned commit:

   ```sh
   git clone https://github.com/erf/vis-plug ~/.config/vis/plugins/vis-plug
   git -C ~/.config/vis/plugins/vis-plug checkout e963a93e563c1424fdd2b296261a5fcb593b6b44
   ```

3. Start `vis`, run `:plug-install`, then restart Vis. Plugins are cloned to
   `~/.cache/vis-plug` and checked out at the pinned commits.
4. Log in again for the session's `EDITOR` environment to change. A new shell
   may inherit the old value from its parent.

To update a plugin, run `:plug-outdated` (it fetches), change the `ref` in
`visrc.lua`, apply, restart Vis and run `:plug-install`, which checks out every
pinned ref again. Avoid `:plug-update`: it runs `git pull`, which fails on a
pinned (detached) checkout.

**Checks after setup**

In a Go file inside a module with a deliberate error:

| Keys | Expected |
| --- | --- |
| `Space cd` on the error line | The gopls diagnostic in the status area |
| `gd` on a function call | Jumps to its definition; `Ctrl-t` returns |
| `K` on an identifier | Hover documentation |
| `Ctrl-Space` in insert mode after `fmt.` | Completion menu |
| `Space cr`, type a new name, Enter | Renames every use |
| `Space cf` | Formats the file without saving it |
| `Space ss` | Opens symbols; Enter jumps to one |
| `gcc` | Toggles a `//` comment |

Also open a Python file (ruff diagnostics), a TOML file (taplo) and a
repository whose `.editorconfig` sets a different indent width.

If a check fails, test the same file with `vis` and `XDG_CONFIG_HOME` pointing
to an empty directory to separate a plugin problem from a Vis problem, and
record the result here. If non-ASCII text breaks language-server requests, add
`lua-json` through Nimbus.

**What Vis lacks compared with Neovim**

| Gap | Workaround |
| --- | --- |
| Persistent undo ([#43](https://github.com/martanne/vis/issues/43), declined) | None |
| Swap file ([#58](https://github.com/martanne/vis/issues/58)) | Save often |
| Git hunk markers and previews | `git diff` with Delta in another pane |
| Persistent file tree | `Space e` temporary directory browser |
| Diff mode, folding, tabs | Non-goals or open issues |
| Encodings other than UTF-8; CRLF files | Convert with `iconv` / `dos2unix` |
| Incremental LSP document sync | vis-lspc resends the whole file before each request |
| Autoindent during terminal paste ([#357](https://github.com/martanne/vis/issues/357)) | `:set autoindent off` while pasting |

Vis 0.9, released 2024-05-01, is the latest tag; master is about 500 commits
ahead and issue [#1374](https://github.com/martanne/vis/issues/1374) asks for a
new release. Plugins such as vis-lspc track master with 0.9 fallbacks.

**Neovim 0.12 built-ins**

Not applied to this repository's Neovim configuration. Checked in the local
`:help news` and by attaching gopls, ruff and taplo in a disposable config:

- `vim.lsp.config()` / `vim.lsp.enable()` start servers without plugins.
- Default LSP keys: `grn`, `grr`, `gra`, `gri`, `grt`, `gO`, `K`, insert-mode
  `Ctrl-S`.
- `'autocomplete'` shows completion while typing; `complete+=o` adds LSP items.
- Built in: `gc` commenting, EditorConfig, `:Undotree` after
  `packadd nvim.undotree`, treesitter selection with `an`/`in`.
- `vim.pack` is a built-in plugin manager with a committed lockfile; its help
  still calls it experimental. kickstart.nvim migrated to it in April 2026.

The current nvim-treesitter `main` branch needs `tree-sitter-cli` 0.26.1 or
newer and a C compiler for `:TSInstall`.

**Vim on servers**

Stock Vim 9.2 without a vimrc loads `defaults.vim` (incremental search, syntax,
filetype plugins, last-position restore). Creating any vimrc disables it unless
the vimrc sources it. Built-in optional packages cover common plugins:
`:packadd comment` (`gc`), `matchit`, `editorconfig`, `nohlsearch`, `hlyank`.
Vim 9.2 also has `'autocomplete'`. Fedora patches the mouse block out of
`defaults.vim`.

**Public configurations studied**

| Editor | Configuration | Why it is useful |
| --- | --- | --- |
| Vis | [neapsix](https://github.com/neapsix/.dotfiles/blob/3418a85cb906ca3de11528276acb58a90d4255b9/vis/.config/vis/visrc.lua) | 37 lines, vis-plug, format/commentary/surround, no core remaps |
| Vis | [cedogibi](https://github.com/cedogibi/.config/blob/a9b2e076748302c1041a21d96212e1e06e93d93c/vis/visrc.lua) | 27 lines, smallest with LSP |
| Vis | [jzbor](https://github.com/jzbor/nixos-config/blob/15a1e49e22e16f9f0e53029b805e9f31ea4582cb/homeModules/programs/vis/files/visrc.lua) | LSP, fzf/rg, recent files, Space-leader only |
| Vis | [Leah Neukirchen](https://leahneukirchen.org/dotfiles/.config/vis/visrc.lua) | Restores Vim `n`/`N`; quickfix |
| Vis | [milhnl](https://github.com/milhnl/dotfiles/blob/c93c3f8c817a042535bc22ea1926b0342ca6059d/XDG_CONFIG_HOME/vis/visrc.lua) | By the vis-format author; heavy remaps, useful reference |
| Neovim | [cammarb/nvim](https://github.com/cammarb/nvim) | 76 lines: `vim.pack`, `vim.lsp.enable`, `autocomplete` |
| Neovim | [gpanders](https://github.com/gpanders/dotfiles) | Maintainer config, few plugins, `nvim.undotree` |
| Neovim | [kickstart.nvim](https://github.com/nvim-lua/kickstart.nvim) | Uses `vim.pack`, but about 16 plugins and remaps LSP keys |
| Vim | [romainl/idiomatic-vimrc](https://github.com/romainl/idiomatic-vimrc) | Minimal, no remaps |
| Vim | [girishji](https://github.com/girishji/dotfiles) | Built-in packages, native fuzzy pickers |
| Vim | [habamax](https://github.com/habamax/.vim) | Maintainer config using Vim 9.2 packages |

Configurations that keep Vim's keys add Space-leader mappings rather than
changing core keys. The common extras are a fuzzy picker, a language-server
client, commenting and project indentation.
