# dotfiles

Cross-platform user configuration managed by Chezmoi. Linux is developed
first, with macOS and Windows target paths kept ready.

Chezmoi owns selected files below `~`. Nimbus owns system packages, services, system
files, privileged changes, and the machine profile handoff: it performs the
first `chezmoi init` with the machine ID, a managed-by-Nimbus flag, and the
selected profiles, as [PROFILES.md](PROFILES.md) documents. Machine manifests
live in the Nimbus repository, not here. Secrets and private keys never enter
Git.

The repository currently manages Bash and Zsh setup, Sheldon, Starship, Mise, Nix,
udiskie, Zathura, GitHub CLI, btop, Fastfetch, and Git configuration.
Other empty configs remain ignored until they are implemented and reviewed.

## Cargo tools

On Linux, Chezmoi manages `~/.config/mise/conf.d/cargo.toml` alongside the main
Mise configuration. It declares Caligula, Typst, Tinymist, cargo-update, Sheldon,
resvg, and VM Curator through Mise's native Cargo backend. This file is ignored
on macOS and Windows; the existing runtime selections remain in
`~/.config/mise/config.toml`.

Every full `chezmoi apply` on Linux and macOS writes configuration, then runs
`mise install` as the current user from the home directory. This works with or
without Nimbus. Nimbus installs Mise itself before its first Chezmoi apply;
standalone users must install Mise before applying. The script prefers
`~/.local/bin/mise`, then finds Mise on `PATH`, and reads the managed config in
`~/.config/mise`. For this invocation, `MISE_CEILING_PATHS` stops project-config
discovery before the home directory, excluding home-local `mise.toml`,
`.mise.toml`, version files, and parent-directory configs. The global config
and its Cargo fragment still load; normal interactive Mise discovery is unchanged.

Run Chezmoi as your normal user; the install script refuses root execution.

The [after-apply script](home/run_after_install-mise-tools.sh.tmpl) runs even
when configuration is unchanged, so another apply repairs missing tools.
Native output stays visible; a missing Mise binary, missing config, or failed
install fails the apply. Fix the reported problem and rerun the full apply to
retry. Files already written and tools already installed are retained after a
failure. Only the native Mise tool declarations request installation; an app
config elsewhere in this repository does not install that app.

The script sets `MISE_SYSTEM_DEPS=warn` and `MISE_AUTO_UPDATE=false`: system
dependencies stay outside Chezmoi, and this install step does not request
runtime upgrades or a Mise self-update. It does not install Mise itself or run
on Windows. Shell startup still only activates tools.

Mise builds these tools through Cargo and keeps their binaries under its data
directory, normally `~/.local/share/mise/installs`. `mise activate zsh` exposes
the selected versions. Use `mise upgrade` for updates; `cargo-update` is for
separate direct Cargo installations. Native `~/.cargo/config.toml` contains
Cargo build settings, not an install list, so no such file is added here.
Existing tools under `~/.cargo/bin` are left untouched.

## Bootstrap

On a new machine with access to the private repository:

```sh
chezmoi init --prompt https://github.com/Furyfree/dotfiles.git
```

From an existing source checkout:

```sh
chezmoi init --prompt
```

`--prompt` selects local options and regenerates the Chezmoi config. It does
not modify home files unless `--apply` is added.

Preview before applying:

```sh
chezmoi managed
chezmoi status
chezmoi diff
chezmoi verify
git diff --check
```

Apply only after reviewing the diff:

```sh
chezmoi apply
```

`chezmoi diff` shows the install script and `chezmoi status` reports it as a
script to run, including when the config files already match. Neither these
preview commands nor `chezmoi apply --dry-run` installs tools. A full apply is
the supported configuration-and-install flow; applying individual files need
not run the after-apply script.

## Update

Pull without applying, review, then apply:

```sh
chezmoi update --apply=false
chezmoi diff
chezmoi apply
```

## Edit

Use `chezmoi edit` for normal targets:

```sh
chezmoi edit ~/.config/zsh/.zprofile
```

Cross-platform configs have one canonical file below
`home/.chezmoitemplates/configs/`. Files in OS-specific target directories are
thin wrappers and should not contain duplicated config.

`home/.chezmoiignore` selects platform paths and keeps placeholder targets
unmanaged. When a config is implemented, remove its placeholder rule but keep
its platform rule.

## Zsh

Run just the Zsh regression checks without changing the live configuration:

```sh
python3 tests/zsh-foundation.py
```

They execute Zsh with temporary state and fake clipboard, Yazi, and tool
integrations. They check syntax, environment defaults, quoted paths, history
permissions, startup fallbacks, and error handling. The complete suite below
also checks the Nimbus handoff with an isolated `chezmoi init --dry-run`.
`execute-template --init` simulates prompts differently and rejects unknown
multichoice values that real `init` accepts.

### Environment and shell options

Interactive startup initializes Mise when installed, then loads environment
defaults and shell options. Mise manages its own tool versions, project trust,
and runtime state; this repository only adds `mise activate zsh`. Generation
errors remain visible and failed output is not evaluated. Shell startup does
not install tools, and missing Mise is harmless during shell startup. A full
Chezmoi apply requires Mise for the install step described above.

Existing nonempty `EDITOR`, `VISUAL`, and `PAGER` choices are preserved.
Otherwise the editor defaults to the first available `nvim`, `vim`, or `vi`,
`VISUAL` follows `EDITOR`, and the pager defaults to `less -R` when available.
These defaults apply to interactive Zsh and its child processes, not all GUI
applications. `MANPAGER` is left alone; no custom bat-based man pager is added.
The same availability checks work on Linux and macOS.

`AUTOCD` lets a directory path act as a directory-change command, `NOBEEP`
disables the shell bell, and `NUMERIC_GLOB_SORT` puts numbered glob matches in
numeric order (for example, `file2` before `file10`).

### Completion

Tab completion tries exact case first, then case-insensitive matches, and
supports keyboard selection from the suggestion menu. It uses Zsh's existing
completion paths on Linux and macOS. Its initialization cache lives in
`$XDG_CACHE_HOME/zsh/zcompdump` (normally `~/.cache/zsh/zcompdump`), with a
private directory created on first startup. The cache is unmanaged and can be
removed to rebuild it on the next startup. Completion security checks remain
enabled, including when the cache already exists.

### Plugins

Sheldon loads `zsh-completions`, our completion module, `fzf-tab`, our zoxide
module, `zsh-autosuggestions`, then `zsh-syntax-highlighting`. Highlighting stays last
so it sees completion and line-editor changes. The inline `completion-init`
and `zoxide-init` entries load our modules; they are not downloaded plugins.
No path into Sheldon's downloaded repositories is hardcoded.

Autosuggestions offers the most recent matching command from history in muted
text. Press Right Arrow at the end of the line to accept it, then Enter to run
it. Syntax highlighting colors commands and arguments while typing, including
unknown command names. Both plugins use their defaults.

When `fzf` is installed, `fzf-tab` replaces the normal Tab selection menu with
a searchable list. Type to filter, use the arrow keys to select, and Enter to
accept; Escape cancels the picker. Without `fzf`, the normal completion menu
remains enabled.

The same setup is used on Linux and macOS. When Sheldon is absent or fails to
generate its script, Zsh loads standard completion and the zoxide module
directly.

Chezmoi manages `~/.config/sheldon/plugins.toml` only. Sheldon owns downloaded
plugins and its lock/cache files. Its first startup after a config change may
download missing plugins and regenerate its lock file. Download errors remain
visible, and failed output is not evaluated as shell code. Plugin updates are
explicit:

```sh
sheldon lock --update
```

Additional plugins are deferred. Applying this config replaces the existing
plugin selection with these four plugins; back up the existing config first.

### Aliases and functions

Aliases load after tool and plugin initialization. The same command-availability
checks run on Linux and macOS; no installation paths are hardcoded.

| Alias | Action |
|---|---|
| `ls` | eza grid, directories first |
| `ll` | eza detailed listing, including hidden entries and column headers |
| `la` | eza grid including hidden entries |
| `lt` | eza directory tree |
| `n` | Neovim, when installed |
| `bat` | `bat -pp`, or `batcat -pp` when only batcat is installed |
| `hx` | Helix fallback when `helix` exists but `hx` does not |
| `code` | VSCodium fallback via `codium` or `vscodium`, only when `code` is absent |
| `zed` | Fallback to `zeditor`, only when `zed` is absent |
| `c` | Clear the screen |
| `h` | List all available shell history |
| `mkdir` | Create missing parents with `mkdir -p`; existing directories are accepted |
| `f` | Fastfetch, when installed |
| `help` | tldr examples, when installed |
| `lzd` / `lg` | Lazydocker / Lazygit, when installed |

eza icons appear only in terminal output. Without eza, native `ls` is untouched,
`ll` uses `ls -lah`, `la` uses `ls -a`, and `lt` is not added. Use `command ls`
when you specifically need native `ls`, and `command mkdir` for the original
directory-creation behavior. Existing `hx`, `code`, and `zed` commands are
preserved. Lazydocker and Lazygit shortcuts do not manage their app settings.

`bat` keeps syntax highlighting but removes decorations and paging. Native
`cat` is unchanged. Use `command bat` (or `command batcat`) to bypass the alias.

`copy file` copies a file's contents; `copy file1 file2` concatenates their
contents without adding separators. Pipe text with `some-command | copy`.
The function uses `pbcopy` on macOS. On Linux it prefers `wl-copy` when
`WAYLAND_DISPLAY` is set, then `xclip -selection clipboard` when `DISPLAY`
is set. The matching command must be installed. Selection happens when called;
missing tools/sessions and backend failures are reported, not silently ignored.

File arguments must be readable regular files and are checked before copying.
Read failures are reported, but an error after streaming begins can leave
partial clipboard content. No temporary copy of the input is stored on disk.

`clip-paste` prints clipboard contents without adding a newline. It uses
`pbpaste` on macOS, or `wl-paste --no-newline` followed by an X11 `xclip`
fallback on Linux, with the same session/tool checks as `copy`. It accepts no
arguments; use a pipe or redirection to send the contents elsewhere. Native
`paste` is unchanged.

`y` opens Yazi and changes the shell to its last directory when exiting with
`q`; `Q` leaves the shell directory unchanged. The wrapper follows
[Yazi's shell integration](https://yazi-rs.github.io/docs/quick-start/#shell-wrapper)
with missing-tool/error handling and temporary-file cleanup. Yazi must already
be installed; its config and state are not managed here.

`croot` jumps to the current Git working tree's root. Outside a working tree,
it reports Git's error and leaves the directory unchanged. `copypath` copies
the current directory's absolute path; `copypath file` copies an existing file
or directory's absolute path, resolving symlinks. It reuses `copy` and does not
add a newline. Neither helper replaces `cd` or another native command.

### Keybindings

The shell explicitly uses Emacs-style editing, matching the earlier setup.
Keybindings load before fzf and the plugins so their shortcuts stay intact.

| Key | Action |
|---|---|
| Home / End | Move to the beginning / end of the line |
| Delete | Delete the character under the cursor |
| Ctrl-Left / Ctrl-Right | Move backward / forward by a word |
| Ctrl-Delete | Delete the next word |
| Ctrl-W / Alt-Backspace | Delete the previous word |

Home, End, and Delete use terminal-provided sequences, with common fallback
sequences. This is shared by Linux and macOS: the terminal determines which
bytes a key sends. Modifier shortcuts work only if the terminal forwards the
expected sequence; macOS may require Option configured as Alt/Meta, and OS
shortcuts may intercept Ctrl-arrow keys.

Plain Backspace is unchanged. Ctrl-H is not remapped to word deletion because
some terminals also send it for Backspace; use Ctrl-W instead of relying on
Ctrl-Backspace. PageUp/PageDown are left alone. Configure scrollback in the
terminal; unbinding these keys in Zsh does not make them scroll the terminal.

### fzf shortcuts

Ctrl-R opens a searchable list of shell history. Type to filter, then Enter
to put the selected command on the command line for editing; press Enter
again to run it. Escape cancels the search.

When a clipboard backend is available at startup, Ctrl-Y inside the Ctrl-R
picker copies the focused command (without its history number) and closes the
picker without inserting or executing it. It uses `pbcopy` on macOS, prefers
`wl-copy` on Wayland, and falls back to `xclip -selection clipboard` on X11.
The shortcut copies only the focused entry, not a multi-selection.

Ctrl-T searches files and directories below the current directory and inserts
the selected paths on the command line. Alt-C searches directories and changes
into the selected one immediately. These replace Zsh's transpose-characters
and capitalize-word shortcuts. Escape cancels either picker.

With `bat` (or `batcat`) installed, Ctrl-T previews the first 300 lines of files
with syntax highlighting and line numbers, and lists directory entries.
Ctrl-/ toggles the preview when the terminal forwards that key. These options
only affect Ctrl-T, not history, Tab, or directory-jumping pickers.

The fzf module loads before the plugins so highlighting stays last. It uses
the installed binary's `fzf --zsh` integration on Linux and macOS, without
Homebrew or distribution-specific paths. Tab stays with our completion setup.

The module runs only in a terminal with Zsh's line editor enabled. If fzf
is absent, Zsh keeps its standard key bindings. The installed fzf must
support `--zsh`; if generating its script fails, the error remains
visible and the script is not evaluated. No additional Sheldon plugin or
separate history file is needed.

### Directory jumping

When zoxide is installed, it learns directories as you visit them. Use
`z name` to jump to a matching remembered directory, or `zi name` to choose
one interactively with fzf. Ordinary `cd` is unchanged. Unlike Alt-C, `zi`
searches remembered directories rather than directories below the current one.

The same module runs on Linux and macOS after completion initialization and
before autosuggestions and highlighting. Without zoxide it does nothing;
without fzf, `z` still works but `zi` needs fzf. Initialization errors remain
visible and failed generated scripts are not evaluated. Zoxide owns its local
directory database; Chezmoi neither manages nor migrates it.

### Prompt

When Starship is installed, `prompt.zsh` initializes it using `starship init
zsh` on both Linux and macOS. It loads before the plugin loader so syntax
highlighting still sees all line-editor changes. Without Starship, the normal
Zsh prompt remains. Initialization errors stay visible, and failed generated
scripts are not evaluated.

Chezmoi manages one shared `~/.config/starship.toml`. It keeps Starship's
default layout and blank line, uses a green arrow for success and the same
arrow in red for errors, and hides package versions. Other modules use their
defaults; no OS-specific settings or custom commands are needed.

Zsh sets `STARSHIP_CONFIG` to `$XDG_CONFIG_HOME/starship.toml`, overriding any
inherited old config path. With our XDG defaults, this is the managed file.
If you override `XDG_CONFIG_HOME`, the config must be available there too;
Chezmoi still deploys to `~/.config`. The old nested
`~/.config/starship/starship.toml` is left untouched. Starship's cache and logs
remain unmanaged. Bash uses the same prompt config; PowerShell initialization is deferred.

### History

Interactive Zsh shares history between terminals, keeps 20,000 entries in
memory, and saves up to 10,000 entries in `$XDG_STATE_HOME/zsh/history`
(normally `~/.local/state/zsh/history`). Duplicate commands are reduced and
commands prefixed with a space are omitted from saved history. A leading space
is a convenience, not a guarantee that sensitive input stays private.

The history directory is created or tightened to private permissions on startup.
History saving is disabled if creating or securing the directory fails.
These settings are shared by Linux and macOS; the history itself is unmanaged.
Existing `~/.zsh_history` is left untouched and is not imported automatically.
Review a separate backup and migration before applying if you want to carry
over existing history. Back up the current startup files before applying too:
setting `ZDOTDIR` switches new shells away from the old home `.zshrc`.

## Tooling and applications

These configs are independent of the Bash branch. Mise, Nix, and btop deploy
on Linux and macOS. udiskie and Zathura deploy on Linux without a desktop
profile gate. GitHub CLI uses one canonical template with Linux/macOS and
Windows wrappers. Only the deliberate config files are managed, never whole
application state directories.

### Mise

The global config retains your selected runtimes, agent CLIs, LiteParse,
markdownlint, and gopls. It fixes the quoted Grok package key. Runtime policy
was checked on 2026-09-05:

| Runtime | Selection | Policy |
|---|---|---|
| .NET | `10` | Latest patch in the current LTS family |
| Java | `corretto-25` | Latest patch in Corretto's current LTS family |
| Node | `lts` | Follow the latest LTS family, currently 24 |
| Go | `latest` | Latest stable release; no separate LTS channel |
| Rust | `stable` | Stable release channel |

The [Node release schedule](https://nodejs.org/en/about/previous-releases),
[.NET support policy](https://dotnet.microsoft.com/en-us/platform/support/policy),
and [Corretto support calendar](https://aws.amazon.com/corretto/faqs/) own
release status. .NET and Java major families need a deliberate edit when a
new LTS arrives. Selectors do not automatically upgrade already installed
runtimes; project configs can override these global defaults.

`auto_update = true` follows Nimbus's contract and enables Mise's own update
mechanism, not runtime upgrades. `system_deps = "warn"` reports missing system
dependencies without offering to install them. Python's uv integration uses
`"source"`: activate an existing project `.venv`, but do not create one simply
by entering a directory. The old boolean `true` is deprecated. Forced Python
and Ruby compilation was removed; neither runtime is declared globally here.
See [Mise settings](https://mise.jdx.dev/configuration/settings.html).

Your CLI selections remain on `latest`. Keep Claude's package-specific build
allowlist; no blanket npm build permission or trusted-directory list is added.
Antigravity, OpenCode, and Herdr use Mise's registry. Their login, agent
configuration, hooks, and session data are not managed. This requires a recent
Mise; the config and registry names were checked with 2026.9.0. Chezmoi's
after-apply script invokes the native installation lifecycle without requesting
upgrades or blanket trust. Mise's own configuration and trust checks still
apply.

### Nix

The user config keeps only `extra-experimental-features = nix-command flakes`.
The `extra-` form adds to system features instead of replacing them. No caches,
access tokens, trusted users, automatic flake trust, daemon options, or store
maintenance are introduced. Installation and system policy remain outside
Chezmoi. See [Nix configuration](https://nix.dev/manual/nix/stable/command-ref/conf-file.html).

### udiskie

Use automount, notifications, a flat menu, and the smart tray. Settings live
under `program_options`; the smart-tray value is `auto`, not `smart`.
`xdg-open` follows the default file manager instead of requiring Nautilus.
These correct the live/Niriland reference structure using the
[upstream configuration example](https://github.com/coldfix/udiskie/blob/master/doc/udiskie.8.txt).
No device rules, key files, password caching, startup entries, or service
changes are added. This config takes effect when udiskie is started; it does
not start the daemon itself.

### Zathura

The palette keeps the live/Niriland charcoal background and blue highlights,
extending them to completions and the document index. A generic sans-serif
font replaces the Inter dependency. Documents open fitted to width, page-sized
scrolls respect page boundaries, and selected text goes to the clipboard
without a notification. Recolor stays off initially so document colors are
preserved. Bookmarks, reading positions, and databases stay unmanaged.

Keep the [native Zathura shortcuts](https://pwmt.org/projects/zathura/documentation/)
instead of overriding useful navigation:

| Keys | Action |
|---|---|
| `h/j/k/l`, `J/K`, `gg/G` | Scroll, next/previous page, first/last page |
| `a` / `s` | Fit page / fit width |
| `/`, `n/N` | Search, next/previous match |
| `Tab`, `f`, `r` | Document index, follow links, rotate |
| `Ctrl-O` / `Ctrl-I` | Back/forward through jump history |
| `Ctrl-R` or `F4` | Toggle recolor |
| `R` | Reload document |
| `d` or `F6` | Toggle one/two-page layout |
| `b` | Toggle status bar |
| `F5` / `F11` | Presentation / fullscreen |

This deliberately replaces the old Ctrl-R reload / Ctrl-I recolor mappings.
Only the three additional shortcuts are configured; the rest are application
defaults. [Alex Balgavy's config](https://git.alex.balgavy.eu/dotfiles/file/zathura/zathurarc.html)
also demonstrates the small status-bar toggle. No editor-specific SyncTeX
command or default PDF-handler change is made.

### GitHub CLI

Prefer SSH for Git operations, your editor for longer interactive input, and
keep `gh co` for `gh pr checkout`. Editor, pager, and browser choices otherwise
follow the environment and application defaults. SSH keys and authentication
must already work; this does not configure them or rewrite existing remotes.
Host-specific preferences in the unmanaged `hosts.yml` can override the global
Git protocol. See [gh configuration](https://cli.github.com/manual/gh_config).
The directory and config use Chezmoi's private attributes so applying does not
loosen the existing GitHub config directory's permissions on Unix.

The Windows wrapper targets `%AppData%/GitHub CLI/config.yml`; Linux/macOS
use `~/.config/gh/config.yml`. Custom `GH_CONFIG_DIR` or Windows XDG overrides
need the config in that location instead. Credentials, `hosts.yml`, extensions,
and caches are excluded.

### btop

Use the built-in `TTY` color theme for the terminal's ANSI palette and disable
the theme background. This is not forced TTY mode: normal rounded borders and
high-resolution graphs remain available. CPU, memory/disks, and processes are
shown; the network panel starts hidden. A single CPU graph, plain process-list
colors, and no clock reduce visual noise. Defaults retain the two-second
refresh and stable CPU sorting. No theme file or hardware-specific paths are
needed. The behavior is defined in [btop's theme code](https://github.com/aristocratos/btop/blob/main/src/btop_theme.cpp).

`j/k` navigate processes; `H` opens help and `K` opens the kill dialog in Vim
key mode. `1/2/3/4` toggle CPU/memory/network/process panels. Settings changed
in the menus last only for that session: `save_config_on_exit = false` prevents
btop from expanding or overwriting the curated file. Persist preferences by
editing the source config. Checked with btop 1.4.7.

### Validation and recovery

Run all checks with Python 3.11+ and PyYAML:

```sh
python3 tests/check.py
```

The runner collects the standalone Python test files in `tests/`. Python
organizes the checks; Zsh executes the shell behavior tests. No extra test
framework is needed. Tests protect validity and safety, not exact versions,
colors, or other personal preferences.

Coverage includes TOML/YAML syntax, native Mise/Nix/gh/udiskie/Starship parsing,
Sheldon inline shell syntax, btop's supported keys and types, Zathura's
documented settings, and the Zsh checks above. Chezmoi checks Linux/macOS/Windows
target selection, canonical templates, private gh permissions, empty scaffold
exclusion, and the native host's real Nimbus initialization path.

Native checks are explicitly skipped when their tools are absent; a skipped
check is not validation of that app. Empty scaffolds and the separate, unmerged
Bash implementation are not covered. Add relevant tests as those configs land.
Native macOS/Windows behavior, visual appearance, and real desktop shortcuts
still need manual checking on those systems.

Optionally include Zathura startup on an isolated GTK Broadway display:

```sh
DOTFILES_GUI_TESTS=1 python3 tests/check.py
```

This requires Linux Zathura and its matching Broadway server. It uses a private
Unix socket, not the live desktop or a TCP listener.

The install suite runs Chezmoi against a tiny synthetic source and temporary
home with a fake Mise binary. It checks config-before-install ordering,
repeated apply and repair, failure/retry, missing prerequisites, platform
rendering, and previews that never invoke the installer. When Mise is installed,
a read-only native discovery probe also checks that home-local and parent
configs are excluded while the global config and Cargo fragment remain loaded.
It never applies this repository or downloads tools. None of these checks
authenticates, mounts devices, accesses the real clipboard, or writes live
configuration.

Use the repository preview commands before applying. Back up the six existing
config files first (if present); applying replaces files rather than merging
their settings. To undo an applied preference, restore that file from backup
and reopen the application. Removing an ignore exception stops future
management but does not restore or delete an already deployed file.

## Fastfetch

One shared `~/.config/fastfetch/config.jsonc` keeps hardware and software in
compact groups with plain labels and the terminal's default foreground. The small
built-in logo follows the detected OS; no Arch artwork or Nerd Font is required.
Fastfetch uses this path on Linux, macOS, and Windows (below the user profile).
Custom XDG paths or portable Windows installations may need an explicit config
path; inspect the installed binary's search paths if it does not find the file.

Logo and keys inherit the terminal's foreground instead of imposing cyan or
RGB colors. In Noctalia-themed Ghostty they follow Noctalia; elsewhere they
follow that terminal's theme. This is terminal inheritance, not a separate
Noctalia accent template. Do not enable Noctalia's community Fastfetch template:
its hook rewrites the same config Chezmoi manages. No generated color files or
extra hooks are needed for this setup.

CPU, GPU, memory, disks, displays, and battery precede OS, kernel, window manager,
shell, terminal, packages, and uptime. Native detection handles platform and
hardware differences; unavailable modules are normally hidden. There are no
network requests or shell-command modules, and the old root-filesystem "age"
estimate is omitted. The old `arch.txt` remains unmanaged and untouched.

Use `fastfetch`, or the existing `f` alias in the managed Zsh config. It does not
run automatically at startup. Preview the source without applying it:

```sh
fastfetch --config home/dot_config/fastfetch/config.jsonc
```

Run the focused checks with Python 3.11+, Chezmoi, and optionally Fastfetch:

```sh
python3 tests/fastfetch.py
```

They check syntax, safe module selection, identical platform targets, native
parsing, headless output, and foreground inheritance in built-in logos using
isolated application state. Missing optional tools are reported as skips. Native
macOS/Windows detection and visual appearance remain manual checks. Review the
normal Chezmoi previews and back up the live config before applying; restoring
that backup restores the previous layout.

See the [Fastfetch configuration guide](https://github.com/fastfetch-cli/fastfetch/wiki/Configuration).

## Git

Chezmoi manages `~/.config/git/config` and `~/.config/git/ignore` on Linux,
macOS, and Windows. Git reads this config automatically, then `~/.gitconfig`,
then repository-local settings. The existing `~/.gitconfig` stays unmanaged:
your identity, LFS filters, credentials, and signing configuration are neither
copied nor replaced. Existing personal settings can override these defaults.
With a custom `XDG_CONFIG_HOME`, make the files available under that directory;
on Windows, the managed home must match Git's `HOME`.

The shared defaults are:

- New repositories start on `main`; existing branches are not renamed.
- Fetch removes stale remote-tracking branches, not local branches or tags.
- Pull only fast-forwards. Divergence stops for an explicit merge/rebase choice.
- The first plain push can set the upstream automatically with Git's default
  `simple` push mode. This does not push anything until you run `git push`.
- `zdiff3` conflict markers include the common ancestor with less repeated text.
- Git requires an explicit identity rather than guessing one from the machine.
- `git st` shows compact status; `git lg` shows a one-line graph of all branches.

No custom colors, external pager, URL rewrites, signing defaults, credential
helper, or global line-ending conversions are added. Git uses the terminal's
palette, including Noctalia's palette in a themed terminal. Prefer SSH clone
URLs when desired; existing remotes and HTTPS dependencies stay unchanged.
Projects should declare line-ending policy in their own `.gitattributes`.

The global ignore file uses Git's default discovery path and ignores only
`.DS_Store`, `Thumbs.db`, and desktop metadata. It does not hide `.env`, editor
directories, source files, or build outputs globally. Repositories own those
rules; ignore patterns are not a security boundary. An existing
`core.excludesFile` override still wins. The old `~/.gitignore` stays untouched.

On a new machine, put personal identity in the unmanaged file explicitly:

```sh
git config --file ~/.gitconfig user.name "Your Name"
git config --file ~/.gitconfig user.email "your-address@example.com"
```

Using `--file` avoids changing the managed XDG config when `~/.gitconfig` does
not yet exist. Configure signing and authentication separately when needed.
Inspect one effective setting without dumping personal configuration:

```sh
git config --show-origin --get pull.ff
```

Run isolated checks with Python 3, Git 2.37+, and optionally Chezmoi:

```sh
python3 tests/git-config.py
```

Tests use temporary homes and local fixture repositories only, including
synthetic commits and local pushes. They check automatic loading, personal
overrides, platform targets, ignore rules, aliases, upstream setup, pruning,
and fast-forward-only pulls without network access or live configuration changes.
Windows/macOS native discovery remains a manual check. Review the normal
Chezmoi previews and back up any existing XDG Git files before applying;
restore those backups to recover the previous shared configuration.

See Git's [configuration loading rules](https://git-scm.com/docs/git-config#FILES)
and [ignore documentation](https://git-scm.com/docs/gitignore).

## Bash

Bash mirrors the Zsh aliases, helpers, editor/pager defaults, history limits,
Emacs-style keys, Mise, fzf, zoxide, and shared Starship prompt. Root
`.bash_profile` and `.bashrc` load the explicit modules in `~/.config/bash`.
Login startup preserves the existing `.profile` and adds `~/.local/bin` to
PATH when missing. A per-shell guard prevents duplicate interactive hooks.
To reload all modules after editing, start a new shell.

Linux and macOS use the same modules, with platform checks for clipboard tools
and optional plugin paths. Missing tools are harmless; nothing is installed.
The core files use Bash 3.2-compatible syntax. `autocd` requires Bash 4 or
newer; Bash has no direct equivalent of Zsh's numeric glob sorting.

History lives separately in `$XDG_STATE_HOME/bash/history`, with 20,000 entries
in memory and a 10,000-line file limit. The private directory and failure
handling match Zsh. Bash appends and imports new history at each prompt while
preserving existing prompt hooks and command exit status. Duplicate reduction
is best-effort across terminals, not Zsh's exact shared-history semantics.
Multiline commands use Bash's `cmdhist` format. `h` lists all history, and
space-prefixed commands are omitted. This is not a secrets protection mechanism.
Existing `.bash_history` is neither migrated nor managed.

Installed `bash-completion` supplies command completions. Ordinary Readline
completion is case-insensitive and shows ambiguous matches; unlike Zsh, it
does not try an exact-case-only pass first. Optional `ble.sh` supplies syntax
highlighting, suggestions, and its native Tab menu instead of Zsh plugins.
It is discovered under `$XDG_DATA_HOME/blesh`, Linux system share directories,
or the standard Apple Silicon/Intel Homebrew prefixes. Its bell setting lives
in `bash/blerc`, also exposed through `.blerc`. Other ble.sh defaults are kept.

Following [ble.sh's startup and fzf guidance](https://github.com/akinomyoga/ble.sh#13-set-up-bashrc),
it loads before the modules and attaches last. With ble.sh, its bundled
`integration/fzf-key-bindings` handles Ctrl-T, Ctrl-R, and Alt-C; without it,
the installed `fzf --bash` integration handles them. Ctrl-T previews and
Ctrl-R's clipboard shortcut match Zsh. Bash does not use `fzf-tab`: Tab stays
with native/ble.sh completion (plain fzf also offers its standard `**` trigger).
Terminal-only integrations are skipped without a usable terminal.

The empty `.profile`, `.bash_logout`, and `bash/logout` scaffold remains
unmanaged. Back up existing startup files and inspect the diff before applying.
No login-shell change is made.

Run the isolated Bash regression checks:

```sh
bash tests/bash-foundation.bash
```

They require ShellCheck and test syntax, environment preservation, private
history setup and failure handling, prompt-hook preservation, aliases,
clipboard platform selection, helpers, failed tool initialization, and startup.
Clipboard commands and optional tools are test doubles; live history and
clipboard contents are not used. Native macOS and installed ble.sh need a
separate interactive check on a machine with those available.

## 1Password SSH

Bootstrap asks whether to enable the 1Password SSH integration. The prompt
records intent only and does not require the `op` CLI to be present. The local
`onePasswordSsh` value controls:

- private `~/.ssh/config` rendered from 1Password
- `agent.toml` at the Linux/macOS or Windows target path

When disabled, those targets are ignored but existing files are not deleted.
Run `chezmoi init --prompt` to change the choice; this still does not apply.

If 1Password is only temporarily locked, inspect the remaining files without
requesting secrets:

```sh
chezmoi --skip-secrets status
chezmoi --skip-secrets diff
chezmoi --skip-secrets verify
```

After enabling or unlocking 1Password, run the normal preview before applying.

See [PROFILES.md](PROFILES.md) for the profile vocabulary,
[CONFIG_INVENTORY.md](CONFIG_INVENTORY.md) for migration scope,
[ROADMAP.md](ROADMAP.md) for implementation order, and
[TASKS.md](TASKS.md) for current status and dependencies.
