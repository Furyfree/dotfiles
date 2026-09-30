# Vis, Vim and Neovim comparison

Research date: 30 September 2026. Local measurements refer to this Fedora 44
workstation. Package versions and repository snapshots matter; results from one
machine do not establish a speed ranking for other systems.

For your setup, Vis makes sense as a small terminal editor and for coding with
shell tools. Neovim remains the stronger main editor if you want your existing
file explorer, Git previews, persistent undo and native Windows support. Vim
offers a broad set of built-in editing tools and a Vimscript/Vim9script
configuration path. The choice depends more on those features and editing habits
than on a few milliseconds of startup time.

**Design and built-in features**

| Area | Vis | Vim | Neovim |
| --- | --- | --- | --- |
| Editing model | Vi-style operators and motions, multiple selections, Sam commands | Vim operators, motions, text objects and Ex commands | Vim editing model with additional APIs and defaults |
| Main implementation | C core, Lua configuration and extensions | C core, Vimscript and Vim9script | C core, Lua/LuaJIT and Vimscript |
| Highlighting | Lua/LPeg lexers | Traditional syntax engine | Traditional syntax engine and Tree-sitter integration |
| Language-server support | Community client plugin | Client plugins | Built-in LSP client; servers require separate installation/configuration |
| Search/build result lists | Community quickfix plugin | Built-in quickfix and location lists | Built-in quickfix and location lists |
| Persistent undo | In-memory history; no built-in undo-file persistence found | Built-in undo files | Built-in undo files |
| Diff editing | External tools | Built-in diff mode | Built-in diff mode |
| File navigation | Bundled external chooser; fzf integration possible | File commands and bundled netrw | File commands, netrw and many picker/explorer plugins |
| Integrated terminal | External shell/multiplexer workflow | Built-in terminal buffers | Built-in terminal buffers |
| Plugin compatibility | Vis-specific Lua API | Vim plugins, subject to version/build requirements | Many Vim plugins plus Neovim-specific Lua plugins |

Vis's authors focus on text editing and external utilities. They list integrated
directory browsing, tab workspaces, GUI support, Vimscript and diff mode among
their non-goals. The bundled file chooser still lets you select files from a
directory; it is separate from a sidebar explorer. [Vis project](https://github.com/martanne/vis).

Neovim's built-in LSP client supports language-aware operations such as
definitions, references, renaming and diagnostics after you configure a server.
Its Tree-sitter interface provides parsing and highlighting; language parsers
remain a separate requirement. Vim also supports coding workflows through
plugins such as the Vim9 LSP client. [Neovim LSP](https://neovim.io/doc/user/lsp/),
[Neovim Tree-sitter](https://neovim.io/doc/user/treesitter/),
[Vim9 LSP plugin](https://github.com/yegappan/lsp),
[Vim quickfix](https://vimhelp.org/quickfix.txt.html).

**Codebase size**

Your original `tokei` results match the local checkouts checked again on the
research date:

| Whole checkout | Files | Total lines | Code | Comments | Blank lines |
| --- | ---: | ---: | ---: | ---: | ---: |
| Vis | 477 | 159,710 | 144,143 | 9,179 | 6,388 |
| Vim | 3,658 | 1,993,533 | 1,337,286 | 407,336 | 248,911 |
| Neovim | 3,778 | 1,717,550 | 1,178,776 | 359,069 | 179,705 |

The largest contributions to the code column are:

| Language/category | Vis | Vim | Neovim |
| --- | ---: | ---: | ---: |
| C | 23,002 | 443,357 | 275,230 |
| C headers | 1,969 | 33,612 | 16,691 |
| Lua | 11,311 | 10 | 351,051 |
| Vimscript | 0 | 579,403 | 412,733 |
| Translation files (`.po`) | 0 | 234,971 | 112,559 |
| Reported Autoconf | 106,003 | 5,314 | 50 |
| Other code, including embedded snippets | 1,858 | 40,619 | 10,462 |

These totals include tests, runtime scripts, syntax definitions, translations
and auxiliary tools. They do not measure the amount of code involved in a
keypress. Tokei counts strings in translation files as code. Its classification
of Vis's `.in` test fixtures accounts for the large Autoconf number; Vis does
not contain 106,000 lines of build-system implementation.

Neovim still ships substantial Vimscript runtime content. Its large Lua count
includes tests and runtime code, so describing it as a 351,000-line Lua editor
core would be misleading. Vim's additional platform and feature code also
contributes to its C count.

A narrower count gives a more useful view of the implementations:

| Selected source paths | C code | Header code | Combined |
| --- | ---: | ---: | ---: |
| Vis root `*.c` and `*.h` | 18,135 | 1,791 | 19,926 |
| Vim `src`, excluding `testdir` and `libvterm` | 435,891 | 31,194 | 467,085 |
| Neovim `src/nvim`, excluding `vterm` | 258,784 | 14,904 | 273,688 |

The selected Vim and Neovim C/header paths contain about 23 and 14 times as much
code as the selected Vis paths. These scopes differ: the Vis selection includes
small helper executables, and the other selections include their own support
code. Lua, external dependencies and generated build output fall outside this
comparison. A smaller implementation is easier to explore; line counts alone
do not establish correctness, maintainability or feature quality.

Repository snapshots used for the counts:

| Project | Commit | Commit date |
| --- | --- | --- |
| Vis | `254329d9f4f1df1158397080d403f3f112918aff` | 2026-08-19 |
| Vim | `4505de43911a0220e58ee3cb7208dcd7bfeaadef` | 2026-09-29 |
| Neovim | `cc4e0c8d60ede60d2a48efe322a9bd1f71198b8a` | 2026-09-30 |

You can reproduce the selected counts with the existing local clones:

```sh
tokei /tmp/compare/vis
tokei /tmp/compare/vim
tokei /tmp/compare/neovim
tokei /tmp/compare/vis/*.c /tmp/compare/vis/*.h
tokei /tmp/compare/vim/src --types C,'C Header' --exclude '**/testdir/**' --exclude '**/libvterm/**'
tokei /tmp/compare/neovim/src/nvim --types C,'C Header' --exclude '**/vterm/**'
```

**Text storage and extension architecture**

Sam is a Plan 9 text editor whose command language lets you select structured
regions with regular expressions. Vis combines that language with interactive
multiple selections. For example, `:0,$x/TODO/` selects matching regions across
the file for a subsequent editing operation. This is a reason to try Vis beyond
its size: you can work with several selected regions without installing a
multi-cursor plugin. [Vis structural editing](https://github.com/martanne/vis/wiki/FAQ#what-are-structural-regular-expressions).

Vis keeps text in a piece chain: pieces refer to spans of original or inserted
data, and edits change those references. Its revision history retains the
information needed for undo. Vim and Neovim use the memline/memfile structure,
with text lines in data blocks beneath a tree of pointer blocks. Those designs
affect editing and recovery, but they do not predict performance without a
specific workload. [Vis text implementation](https://github.com/martanne/vis/blob/254329d9f4f1df1158397080d403f3f112918aff/text.c),
[Vim memline](https://github.com/vim/vim/blob/4505de43911a0220e58ee3cb7208dcd7bfeaadef/src/memline.c),
[Neovim memline](https://github.com/neovim/neovim/blob/cc4e0c8d60ede60d2a48efe322a9bd1f71198b8a/src/nvim/memline.c).

Vis uses Lua event handlers for configuration and plugins. Version 0.9 added
the asynchronous communication API used by its LSP client and the options API
used by newer plugins. Interactive fullscreen pipes still wait for the external
tool. Plugins for Neovim depend on its own API and cannot be loaded in Vis merely
because both use Lua. [Vis Lua API](https://martanne.github.io/vis/doc/),
[Vis releases](https://github.com/martanne/vis/releases).

**Installed size**

Local Fedora package metadata and executable file sizes:

| Editor/version | Executable | Installed package payload |
| --- | ---: | ---: |
| Vis 0.9-4.fc44 | 0.36 MiB | 1.20 MiB (`vis`) |
| Vim 9.2.1129-1.fc44 | 4.51 MiB | 43.20 MiB (`vim-enhanced` + `vim-common`) |
| Neovim 0.12.5-1.fc44 | 5.41 MiB | 33.13 MiB (`neovim`) |

One MiB is 1,048,576 bytes. The local Vis build reports
`+curses +lua +tre +acl +selinux`; the Vim build is a huge terminal build, and
Neovim uses LuaJIT. The size comparison covers those builds, not stripped custom
builds or Vim's smaller package variants.

Package payload excludes separately packaged shared libraries, downloaded
plugins, Tree-sitter parsers and language servers. It also differs from download
size, allocated disk space and memory use. For example, Arch packages Vis lexers
separately, so its editor package size alone does not match Fedora's scope.
[Arch package details](https://archlinux.org/packages/extra/x86_64/vis/).

The local package figures can be checked with:

```sh
rpm -q --qf '%{NAME}: %{SIZE} bytes\n' vis vim-enhanced vim-common neovim
stat -c '%n %s' /usr/bin/vis /usr/bin/vim /usr/bin/nvim
```

**Speed**

The earlier local smoke measurements recorded these warm-cache medians for
stock editor startup, loading and exit:

| Workload | Vis | Vim | Neovim |
| --- | ---: | ---: | ---: |
| Empty editor, then exit | 4.84 ms | 5.34 ms | 7.27 ms |
| Open an 8 MiB file, then exit | 13.27 ms | 16.52 ms | 17.89 ms |

The retained results put Vis ahead for those two workloads on this machine. The
benchmark harness and individual samples are not retained with this document,
so treat the values as earlier observations, not a reproducible performance
study. The package sizes above were checked again while writing this comparison;
these timings were not rerun.

These measurements do not cover interactive rendering, typing latency, search,
formatting, repeated edits, long single-line files or your configured Neovim.
They also do not establish peak memory use. An LSP setup includes server
processes, while a file picker includes the search tool and fzf. Measure that
complete workflow before assuming the small editor executable means a small
coding session. The startup differences alone are too small to justify giving
up features you use.

**Platform and distribution availability**

| Platform | Vis | Vim | Neovim |
| --- | --- | --- | --- |
| Linux | Packaged by several distributions | Distribution packages | Distribution packages and upstream binaries |
| macOS | Homebrew and MacPorts; Homebrew invokes the editor as `vise` | macOS includes Vim; newer builds available | Homebrew, MacPorts and upstream binaries |
| Native Windows | Upstream does not support native Windows binaries | Upstream Windows builds | Upstream Windows builds and package-manager options |
| Windows with a Unix environment | Upstream describes Cygwin; Linux packages offer a WSL route | Available through the relevant environment | Available through the relevant environment |

Homebrew names the command `vise` to avoid macOS's existing `/usr/bin/vis`
utility. Cygwin provides a POSIX environment on Windows; WSL provides a Linux
environment. Neither makes Vis a native Windows editor. The Cygwin route comes
from upstream documentation; it was not tested here. [Homebrew Vis](https://formulae.brew.sh/formula/vis),
[MacPorts Vis](https://ports.macports.org/port/vis/),
[Vis Windows FAQ](https://github.com/martanne/vis/wiki/FAQ#what-about-windows),
[Vim downloads](https://www.vim.org/download.php),
[Neovim installation](https://github.com/neovim/neovim/blob/master/INSTALL.md).

Vis package availability checked during the research:

| Distribution/environment | Finding | Source |
| --- | --- | --- |
| Fedora 44 | Official `vis` package, 0.9-4.fc44; installed on this machine | [Fedora](https://packages.fedoraproject.org/pkgs/vis/vis/) |
| Fedora 43 / Rawhide | Official packages; listed as 0.9-3.fc43 / 0.9-7.fc45 | [Fedora](https://packages.fedoraproject.org/pkgs/vis/vis/) |
| Debian 13, trixie | `vis` 0.9-1, with architecture-specific rebuilds | [Debian](https://packages.debian.org/trixie/vis) |
| Ubuntu 24.04 LTS, noble | Universe package, 0.8-1 | [Ubuntu noble](https://packages.ubuntu.com/noble/vis) |
| Ubuntu 26.04 LTS, resolute | Universe package, 0.9-1build1 in the checked listing | [Ubuntu resolute](https://packages.ubuntu.com/resolute/armhf/vis) |
| Arch Linux | Extra repository; current listing uses a post-0.9 Git snapshot | [Arch](https://archlinux.org/packages/extra/x86_64/vis/) |
| Alpine Linux | Community package; checked v3.23 listing has 0.9-r0 | [Alpine](https://pkgs.alpinelinux.org/package/v3.23/community/riscv64/vis) |
| Gentoo | `app-editors/vis`, including 0.9-r2 and a live source version | [Gentoo](https://packages.gentoo.org/packages/app-editors/vis) |
| Void Linux | Official package recipe, 0.9 revision 1 | [Void recipe](https://github.com/void-linux/void-packages/blob/master/srcpkgs/vis/template) |
| NixOS / Nix | Upstream lists a package; exact channel/version not confirmed | [Upstream package list](https://github.com/martanne/vis/wiki/Distribution-Packages) |
| openSUSE | Upstream links the OBS `editors/vis` project; target release/default-repository availability not confirmed | [Upstream package list](https://github.com/martanne/vis/wiki/Distribution-Packages) |

The Nix package source and openSUSE package pages could not be fetched during
this check. Their upstream listings support package existence, but do not prove
availability in a particular release's default repositories. Upstream also
lists BSD, Guix and Termux packages. [Distribution list](https://github.com/martanne/vis/wiki/Distribution-Packages).

Version differences affect configuration portability. Ubuntu 24.04's Vis 0.8
lacks the 0.9 options API expected by `vis-editorconfig-options` and the supported
main-branch API expected by `vis-lspc`. Check `vis -v` before copying a setup from
Fedora or Arch. The native core, lexer packaging and clipboard helpers can also
differ between distributions. [EditorConfig requirements](https://github.com/milhnl/vis-editorconfig-options),
[LSP client requirements](https://github.com/fischerling/vis-lspc).

Vis's documented text workflow assumes UTF-8 and LF line breaks. Its FAQ directs
users to external conversion for legacy encodings and CRLF files. That is a
practical difference for Windows-oriented projects even if you run Vis under
WSL. [Vis encoding and line-ending FAQ](https://github.com/martanne/vis/wiki/FAQ#how-should-i-edit-files-in-legacy-encodings).

**Keybindings and Vim familiarity**

Vis preserves much of the operator/motion/text-object grammar. Basic movement,
search, `diw`, `ci"`, registers and save/quit commands feel familiar. Its Sam
command language and selection model introduce differences; upstream does not
promise Vim compatibility. [Differences from Vim](https://github.com/martanne/vis/wiki/Differences-from-Vi%28m%29).

| Operation | Vim / Neovim | Vis |
| --- | --- | --- |
| Movement | `h j k l`, word motions, `gg`, `G` | Familiar equivalents |
| Search current file | `/`, `?`, `n`, `N` | Familiar keys, with Vis regex/search semantics |
| Save / quit | `:w`, `:q`, `:wq` | Supported |
| Open a file | `:e path` | Supported |
| Split a window | `:split`, `:vsplit`, `Ctrl-w s/v` | Supported |
| Switch windows | `Ctrl-w h/j/k/l` moves by direction | Familiar keys; Vis aliases them to previous/next window traversal |
| Word completion in insert mode | `Ctrl-n` / `Ctrl-p` | Bundled `Ctrl-n` current-file word chooser |
| Filename completion in insert mode | `Ctrl-x Ctrl-f` | Bundled equivalent |
| Reindent | `=` operator | `=` runs external `fmt`; different behaviour |
| Change indentation | `<` / `>` operators | Supported |
| Search/build results | `:grep`, `:make`, `:cnext`, `:cprev` | Requires a suitable plugin |
| Toggle comments | Current Neovim has `gcc` / `gc`; classic Vim setups use plugins | Commentary plugin |
| Surround a word with quotes | Plugin mapping `ysiw"` | vis-surround uses `ys"iw` |
| Change/remove a surround | Plugin mappings such as `cs"'`, `ds"` | vis-surround provides these forms |

The Vis keys above come from its default mappings and bundled completion code.
The `=` difference corrects the earlier suggestion to preserve that key for
indentation: doing so in Vis would require changing its native behaviour.
[Vis default mappings](https://github.com/martanne/vis/blob/254329d9f4f1df1158397080d403f3f112918aff/config.def.h),
[Bundled completion plugins](https://github.com/martanne/vis/blob/254329d9f4f1df1158397080d403f3f112918aff/lua/vis-std.lua),
[Neovim commenting](https://neovim.io/doc/user/various/#commenting),
[Vis surround](https://repo.or.cz/vis-surround.git).

Your Neovim `Space Space`, `Space /`, `Space ,` and `Space e` mappings are personal
plugin bindings. They are useful for consistency between your editors, but they
are not native Vim or Neovim defaults. Surround mappings also come from a plugin.
Current Neovim's `gcc` is a built-in exception.

Your preference for native Vim/Neovim-style keys suggests preserving Vis's shared
defaults and using familiar command names for additions. Quickfix becomes more
relevant if you want `:grep` and `:make`. A formatter should have a separate
command unless you choose to replace Vis's `=` behaviour. This document records
that direction; no new mapping or plugin configuration has been implemented.

**Opening a project directory**

The reported error is expected for a directory passed as a startup file:

```text
vis .
Can not load '.': Is a directory
```

Start `vis`, then use `:e .` to invoke the bundled `vis-open` chooser, or use the
existing `Space Space` fzf mapping. File-taking commands invoke `vis-open` for
directories or patterns. That chooser does not provide a persistent project
sidebar. [Vis file commands](https://martanne.github.io/vis/man/vis.1.html).

Launch from the project root if you want the current fzf mapping to search that
project: its source is `find .`, so the editor's working directory controls the
search scope.

**Your current Neovim configuration**

The [canonical Neovim configuration](home/.chezmoitemplates/configs/nvim/) uses
lazy.nvim and five plugins:

| Plugin | Configured purpose | Vis replacement or gap |
| --- | --- | --- |
| Snacks | File/content/buffer/help pickers and a right-side explorer | fzf/rg can cover file and text search; the sidebar and buffer picker need separate work |
| Gitsigns | Git gutter marks, next/previous hunk and inline preview | No equivalent established by this research; a Git statusline is a narrower feature |
| nvim-surround | Surround editing with default mappings | vis-surround, with the add-surround key order difference |
| which-key | Delayed help for mappings | Vis `:help` lists bindings; no equivalent delayed menu established |
| nvim-treesitter | Highlighting when an explicitly installed parser exists | Native LPeg highlighting covers the baseline; parser-based behaviour differs |

Your options include line numbers, case-aware search, two-space defaults,
explicit clipboard registers, a terminal-palette theme and private persistent
undo. You have no configured LSP servers, completion plugin or formatter
integration in this Neovim setup. Adding those to Vis would expand your workflow,
not replace something this configuration already supplies.
[Neovim options](home/.chezmoitemplates/configs/nvim/lua/config/options.lua),
[Neovim plugins](home/.chezmoitemplates/configs/nvim/lua/plugins/).

Persistent undo is a material gap. Vim and Neovim can restore editing history
after a restart. The inspected Vis implementation frees its revision history
when it releases the text; no undo-file serializer or corresponding setting was
found. Cursor-restoration and backup plugins do not supply persistent undo.
[Vim undo files](https://vimhelp.org/undo.txt.html#undo-persistence),
[Vis history implementation](https://github.com/martanne/vis/blob/254329d9f4f1df1158397080d403f3f112918aff/text.c).

**Your current Vis configuration**

[visrc.lua](home/dot_config/vis/visrc.lua) contains the standard Vis Lua support,
the default theme, autoindent, line numbers, two-space indentation and the
`Space Space` fzf file picker. It declares no third-party plugins. Windows
deployment is excluded by the existing Chezmoi ignore gate.

The existing picker skips `.git` directories but includes other ignored paths,
such as `node_modules`, virtual environments and build output. A proposed source
for the same zero-terminated fzf pipeline is:

```sh
rg --files --hidden -g '!.git' -0
```

Ripgrep respects ignore files, while `--hidden` keeps hidden project files
eligible. This would bring the picker closer to your current Snacks behaviour.
The command is a recommendation, not a change made to `visrc.lua`.
[Ripgrep guide](https://github.com/BurntSushi/ripgrep/blob/master/GUIDE.md),
[fzf ignore-aware sources](https://github.com/junegunn/fzf#respecting-gitignore).

The standard Vis support already loads basic word completion, filename
completion, filetype detection and other helpers. Its clipboard utility
supports platform tools including Wayland, X11 and macOS helpers, subject to
their presence. These features do not require a new completion or clipboard
plugin. [Standard support](https://github.com/martanne/vis/blob/254329d9f4f1df1158397080d403f3f112918aff/lua/vis-std.lua),
[Clipboard helper](https://github.com/martanne/vis/blob/254329d9f4f1df1158397080d403f3f112918aff/vis-clipboard).

Your shell configuration still prefers an installed `nvim`, then `vim`, then
`vi` when choosing a default editor. A Vis trial does not require changing that
choice. [Shell editor selection](home/dot_config/zsh/conf.d/env.zsh).

**Vis ecosystem**

The [plugin catalogue you shared](https://erf.github.io/vis-plugins/) and the
[upstream plugin wiki](https://github.com/martanne/vis/wiki/Plugins) cover editing,
formatting, linting, navigation, LSP and other extensions. The wiki warns that
plugin quality varies. There is enough coverage for a practical coding setup,
but fewer interchangeable implementations and fewer established integrations
than in the Vim/Neovim ecosystem.

Plugin hosting spans GitHub, GitLab, Codeberg, SourceHut and repo.or.cz. Some
examples still use older forks or APIs. In particular, `vis-lspc` moved to
Codeberg; its abandoned GitHub mirror does not establish that the plugin itself
is abandoned. Check the target repository and supported Vis version before
copying a `require` statement.

Vis 0.9 remains the packaged stable release in several checked distributions.
The local upstream checkout includes an August 2026 commit, and Arch packages a
post-0.9 snapshot. A slow tagged-release cadence and ongoing source development
can coexist. The available information does not justify describing Vis as dead
or promising a particular maintenance schedule.

**Public setups worth studying**

| Reference | Approach | Useful ideas | Reason to adapt it |
| --- | --- | --- | --- |
| [HACKTIVISME](https://hacktivis.me/git/dotfiles/file/.config/vis/visrc.lua.html) | About 25 lines of display/theme/indentation settings | Small event-based structure and filetype overrides | Personal theme and indentation choices |
| [Anders Damsgaard](https://src.adamsgaard.dk/dotfiles/file/.config/vis/visrc.lua.html) | fzf, recent files, commenting, snippets, tags and tmux language commands | External tools and project navigation | Personal scripts, paths and language assumptions |
| [Łukasz Pankowski](https://gitea.lupan.pl/lupan/dotfiles/blame/commit/9582b162198bb8ad7ada595b54bf0ba79119ccff/vis/.config/vis/visrc.lua) | LSP, quickfix, build tools, fzf, bookmarks and editing plugins | A fuller coding workflow and searchable diagnostics | More configuration; the linked commit is a snapshot, not a checked current head |
| [Matěj Cepl](https://gitlab.com/-/snippets/2520668) | EditorConfig, LSP, Git status, snippets, formatting and packaging helpers | Broad examples of tool integration | A 2023 setup with version-specific APIs and personal paths |
| [jeebak](https://gist.github.com/jeebak/8f9281c7d91855ffba348edca26097d8) | Custom plugin bootstrap, fzf previews, recent files and cursor restoration | Picker previews and reopening files | Extra bootstrap logic and preview-tool dependencies |

Damsgaard's setup provides the closest reference for a small shell-oriented
workflow. Pankowski's setup shows a more ambitious coding environment. Its
snapshot even notes that asynchronous Go formatting may require another save
after formatting finishes. That is a reason to verify save/format sequencing
before enabling automation, not a claim that all Vis formatting has that issue.

The repeated useful pattern is a small editor configuration, a file/search
picker, external language tools and a few editing plugins. Copy the parts that
match your work. Public configs are examples rather than tested distributions
with a shared support contract.

**Plugin candidates and tradeoffs**

| Component | Purpose | Fit for your setup | Requirement or limitation |
| --- | --- | --- | --- |
| [vis-editorconfig-options](https://github.com/milhnl/vis-editorconfig-options) | Project indentation/column settings | First coding addition to consider | Vis 0.9 options API; supports `indent_style`, `indent_size`, `tab_width`, `max_line_length`; other properties ignored |
| [vis-surround](https://repo.or.cz/vis-surround.git) | Add/change/delete delimiters | Replaces a feature you use | Different add-surround key order; vis-pairs is optional |
| [vis-commentary, Nomarian fork](https://github.com/Nomarian/vis-commentary) | Comment/uncomment operations | Familiar `gcc` and `gc` workflow | This fork documents calling the function returned by `require`; older examples differ |
| [vis-format](https://github.com/milhnl/vis-format) | Run external formatters | Matches several declared Mise tools | Whole-file formatting is the simplest starting point; Prettier range formatting is unsupported |
| [vis-lint](https://github.com/rnpnr/vis-lint) | Lint/fix commands and output | Optional diagnostics without LSP | A configured pre-save fixer failure can stop saving; configure commands for your tools |
| [vis-quickfix](https://repo.or.cz/vis-quickfix.git) | Search/build error lists | Strong fit for familiar `:grep` / `:make` commands | Needs command and output-format configuration; supports next/previous result navigation |
| [vis-fzf-mru](https://github.com/peaceant/vis-fzf-mru) | Recent-file picker | Useful if reopening files is frequent | Recent files do not equal the set of open files; history stays local |
| [vis-cursors](https://github.com/erf/vis-cursors) | Remember cursor positions | Small optional convenience | Position storage does not preserve undo history |
| [vis-lspc](https://codeberg.org/muhq/vis-lspc) | Language-server client | Later experiment if you want language-aware features | Current upstream could not be inspected; limitations below come from its previous mirror |
| [vis-plug](https://github.com/erf/vis-plug) | Download/update plugin repositories | Useful once several plugins are selected | Supports commit/branch/tag references and explicit install/update commands |

The EditorConfig plugin uses a Lua parser without an external parsing library.
Its narrower property support fits the immediate indentation problem. Formatter
configuration still belongs to the formatter or project; an editor's tab width
does not replace `pyproject.toml`, `.editorconfig` or tool-specific files.

Your [Mise configuration](home/dot_config/mise/config.toml) declares Go, Ruff,
StyLua, shfmt, ShellCheck, gopls, Staticcheck, golangci-lint, Taplo, actionlint and
Delta. `vis-format` documents Go/gofmt, Python/Ruff, Lua/StyLua and Bash/shfmt
integrations. These declarations identify tools you intend to have; they do not
prove each executable is available in every Vis process's environment.
[Formatter integrations](https://github.com/milhnl/vis-format).

Manual whole-file formatting is a sensible first step. The formatter plugin
offers a pre-save hook, but enabling multiple formatting routes, such as that
hook, a lint fixer and LSP formatting, makes ownership and ordering harder to
understand. Select one route after checking its behaviour on your projects.

`vis-quickfix` can populate navigable results from `:make`, `:grep` and external
commands, including streamed results while a command runs. Its familiar commands
reduce the need for custom leader mappings. Configure the search/build command
and parser for Go, Ruff or other output you use; do not assume a default Make or
Git-grep setup fits every project. [Quickfix documentation](https://repo.or.cz/vis-quickfix.git).

For plugin management, pin exact commits once a combination works and update
through an explicit command. Keep downloaded plugin code and history outside
Chezmoi's managed source. Avoid a custom startup downloader when a maintained
manager already provides the required operations. [vis-plug](https://github.com/erf/vis-plug).

**LSP as a coding option**

LSP means Language Server Protocol: the editor asks an external language server
for code information. The previous `vis-lspc` mirror documents completion,
definitions, declarations, references, hover, renaming, formatting and
diagnostics, using Vis 0.9's communication API.

That mirror also documents whole-file synchronization before requests, stdio
communication, and a bundled JSON fallback without UTF-8 support. A separate
JSON implementation can avoid the documented fallback limitation. The active
Codeberg upstream blocked the research tool, so these are documented historical
constraints rather than confirmed limitations of its current head.
[Previous client documentation](https://github.com/fischerling/vis-lspc).

Go with gopls is a sensible first trial because your Mise configuration already
declares it. Verify project roots, unsaved edits, non-ASCII text, completion,
diagnostics and rename behaviour before relying on the integration. No Vis LSP
session or combined third-party plugin setup was tested during this research.

Neovim offers a built-in client and a broader integration ecosystem, which makes
it the stronger recommendation if language-aware editing becomes central to
your work. Installing a language server does not itself activate it in your
current Neovim configuration. [Neovim LSP setup](https://neovim.io/doc/user/lsp/).

**Fit for your terminal and coding work**

| Use | Recommendation | Reason |
| --- | --- | --- |
| Config files, Git messages, SSH sessions and short edits | Vis is a good trial | Small installed footprint, familiar editing grammar and few configured extras |
| Coding with shell builds, tests and formatters | Vis can make sense | Native filters plus navigation, project indentation and optional quickfix cover much of this workflow |
| Your current Neovim workflow with file tree and Git previews | Keep Neovim available | The researched Vis setup does not reproduce those features or persistent undo |
| Frequent language-aware refactoring/completion | Prefer Neovim; trial Vis separately | Built-in client support and more established integrations |
| One native editor configuration across Linux, macOS and Windows | Vim or Neovim | Vis's Windows route requires a Unix environment |
| Exploring or changing an editor's C implementation | Vis is attractive | The selected implementation is much smaller and its editing model is explicit |

A practical Vis setup for you would retain native movement, file and window
commands, use ignore-aware project navigation, follow project indentation, and
add surround/commenting only where you want those operations. Quickfix is the
most relevant next addition for your preference for Vim-style command names.
External formatting can follow; LSP remains a separate experiment.

The current Vis config is still the minimal setup described above. The research
recommendations, plugin installations, new bindings and default-editor changes
have not been applied. Runtime size, earlier startup observations, source
inspection and plugin documentation answer different questions; the full coding
workflow still needs a real usage trial.
