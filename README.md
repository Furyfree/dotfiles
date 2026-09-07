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
udiskie, Zathura, GitHub CLI, btop, Fastfetch, Git, Ghostty, VSCodium, Zed,
Neovim, and Topgrade configuration. Niri and DankMaterialShell are available
through the opt-in Linux `niri-dms` profile.
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

For the complete local gate, including the separate Bash suite and whitespace
checks, use `just check`. `just preview` runs the four read-only Chezmoi commands
against this checkout and your current home; it returns a failure when
`chezmoi verify` detects unapplied differences. Neither recipe applies configs.
The direct commands above and in [Bash](#bash) remain available without Just.

`just lint-docs` is an optional Markdown style report, not part of the regression
gate. It requires markdownlint and currently reports existing formatting debt.

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
check is not validation of that app. Empty scaffolds are not covered. Bash has
its own suite, which `just check` runs after the Python suites.
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
Login startup adds `~/.local/bin` to PATH when missing before loading the
existing `.profile`, which may itself load `.bashrc`. A per-shell guard prevents
duplicate interactive hooks.
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

## Ghostty

Linux and macOS share `~/.config/ghostty/config`.
The config keeps your 9pt JetBrainsMono Nerd Font Mono, 14px padding, 95%
opacity, and steady block cursor. Ghostty falls back to its bundled font if
the requested font is unavailable; font installation stays outside this config.
Blur depends on the compositor/platform and is not guaranteed on Linux.

Linux with `hyprland-noctalia` selects `theme = noctalia`, whether or not Nimbus
manages the machine. Enable Ghostty's built-in app-theme integration in Noctalia's
GUI after installation. Noctalia generates `~/.config/ghostty/themes/noctalia`;
Chezmoi does not manage that file or any Noctalia settings or template selections.
Let Noctalia generate the theme before opening Ghostty on a fresh setup,
otherwise Ghostty reports a missing theme. Keep that integration enabled while
using this profile. Avoid fixed background, foreground, or palette overrides
in Ghostty, since they take precedence over the generated colors.

Other Linux setups and macOS use the managed `charcoal-blue` palette, preserving
your previous colors without requiring Noctalia or Niriland/DankMaterialShell.
The old `themes/dankcolors` file remains unmanaged and untouched.

No custom keybindings are added. Native tab/split/search shortcuts remain,
and Alt-C/D/F reach the shell again; plain PageUp/PageDown reach terminal
applications. The old Ctrl-Space leader and duplicate Alt bindings are not
loaded. Shell integration keeps the block cursor, enables SSH TERM compatibility,
and does not install terminfo on remote hosts. Default close confirmation and
paste protection remain enabled. No login shell is forced.

Linux retains the flat GTK toolbar and native selection-clipboard behavior.
On macOS, left Option acts as Alt for shell shortcuts, while right Option
remains available for special characters on layouts such as Danish. Selecting
text does not replace the macOS clipboard; use the normal copy shortcut.

Inspect the native shortcuts for your installed version:

```sh
ghostty +list-keybinds --default
```

Run isolated rendering, platform-selection, safety, and native parser/keymap
checks with Python 3.11+, Chezmoi, and optionally Ghostty:

```sh
python3 tests/ghostty.py
```

Tests cover profile selection with and without Nimbus, generated-file ownership,
and changed theme colors using an isolated stand-in for Noctalia's output.
They do not run Noctalia's renderer or reload a running terminal.
Missing Ghostty skips only its native checks. No window is opened or live
configuration changed. Native macOS input, fonts, transparency, and real
shortcut behavior still require manual verification after an approved apply.

Before applying, back up the existing config and review the normal Chezmoi
preview. We retain the supported `config` filename to replace the old Niriland
include rather than leaving it active beside a new `config.ghostty`. Check for
another `config.ghostty` or macOS `Library/Application Support/com.mitchellh.ghostty`
config: Ghostty can load multiple files, and later settings can override this
one. Restore the backed-up config to recover the previous setup.

See the [Ghostty configuration guide](https://ghostty.org/docs/config) and
[option reference](https://ghostty.org/docs/config/reference), plus
[Noctalia app theming](https://docs.noctalia.dev/noctalia/theming/app-theming/).

## VSCodium

Canonical settings and shortcuts are in `home/.chezmoitemplates/configs/vscodium/`.
One-line wrappers deploy only `User/settings.json` and `User/keybindings.json`:

| Platform | User directory |
|---|---|
| Linux | `~/.config/VSCodium/User/` |
| macOS | `~/Library/Application Support/VSCodium/User/` |
| Windows | `~/AppData/Roaming/VSCodium/User/` |

These are standard installation paths, not portable mode, custom user-data
directories, or named profile overrides. Review those separately if used.
Product/gallery overrides, snippets, credentials, chat provider settings,
workspace storage, caches, history, and extension binaries remain unmanaged.
The canonical `product.json` contains the Microsoft Marketplace configuration
as ordinary JSON. Its platform targets remain ignored by `.chezmoiignore`, so
it is not deployed and nothing switches galleries automatically. Review the
Marketplace terms and extension compatibility before enabling deployment.

### Matching Zed

The shared behavior matches the Zed slice on `config/zed`: 15px JetBrainsMono
Nerd Font, no ligatures, block cursor, absolute line numbers, bracket colors,
selected whitespace, no inlay hints or minimap, persistent tabs, left sidebar,
bottom terminal, and manual save/formatting. Prettier remains installed but is
disabled globally to match Zed's Prettier policy; choose a language formatter
or opt in per project. Go/Zig format-on-save, Go import organization on save,
and Pylance format-on-type defaults are explicitly overridden to keep editing
manual. Error Lens supplies inline diagnostics without line
background fills. Go's extension supplies Chezmoi template highlighting;
Tinymist exports PDFs beside the source on save. Fonts and runtimes must
already be installed; Python environment activation remains off as in your
current setup, leaving the shell's Mise environment alone.

New empty windows start with an untitled file. Previous windows are not reopened
automatically, but hot-exit backups preserve unsaved work for native recovery.
Reopening a workspace may restore its tabs; this is not identical to Zed's
startup/session model. The terminal starts at the workspace root and uses the
platform's default shell, with no Linux paths or forced Zsh profile on Windows.

See [VSCodium keybindings](VSCODIUM_KEYBINDS.md) for the shared workflow,
previous-keymap comparison, and notebook/debugger extras. VSCodium cannot
natively reproduce Zed's Inter 16px UI font; no CSS injector or global zoom
workaround is added. Editor-specific diagnostics, syntax colors, panels, and
agent providers are not identical. Native trust prompts stay enabled and global
chat tool auto-approval stays off; this does not configure extension-specific
agent permissions. Editor telemetry and the existing Red Hat/GitLens telemetry
settings are off, without claiming every extension is telemetry-free.

### Themes and extensions

Linux with `hyprland-noctalia` selects `NoctaliaTheme`, the name contributed by
`noctalia.noctaliatheme`. Enable its app-theme integration yourself in Noctalia's
GUI after installation. No Noctalia config, template, hook, or palette is managed
here. The community template currently targets extension version 0.0.5; check
its target again if the extension version changes. Other setups follow system
appearance with Atom One Light/Dark, close counterparts to Zed's One themes.
Theme extensions must be installed before these selections can take effect.

`VSCODIUM_EXTENSIONS.json` preserves all 57 IDs from the current installation:
49 available on Open VSX plus eight listed under `manual`. Three theme extensions
are added, making 52 entries in `install`. The old DMS theme is retained as an
available extension but not selected. Notebook/Jupyter, Excel/Office,
Excalidraw, Git Graph/GitLens, language, and debugger selections are preserved.
The manifest lives at the repository root because it is installation metadata,
not a VSCodium user config. VSCodium does not load it; Chezmoi embeds its
`install` entries into the scripts below when rendering them. Keeping it outside
`home/` prevents accidental deployment and avoids a runtime JSON-parser dependency.

Unlike Zed, VSCodium has no equivalent global `auto_install_extensions` setting.
Two after-apply scripts are prepared but disabled:

- `home/run_after_install-vscodium-extensions.sh.tmpl` for Linux/macOS.
- `home/run_after_install-vscodium-extensions.ps1.tmpl` for Windows.

Both target names (`install-vscodium-extensions.sh` and
`install-vscodium-extensions.ps1`) remain in `home/.chezmoiignore`. No extension
installation runs during setup or apply while those rules remain. The opposite
platform's template also renders empty.

When explicitly enabled later, `run_after_` makes the appropriate script run
after files on every full apply, including the first `chezmoi init --apply`.
Plain `chezmoi init` without apply does not install extensions. This is not a
`run_once_` or `run_onchange_` hook: rerunning apply restores missing selections
even if the manifest has not changed.

The scripts require an existing `codium` or `vscodium` CLI on PATH. They list
installed extensions, compare IDs case-insensitively, request only missing
`install` entries, and verify all those entries through a final native listing.
Existing extensions are not forcibly updated or uninstalled; native auto-update
settings own updates. The `manual` list is reported but never installed.

Missing CLI, listing errors, failed installs, or failed verification stop the
script with an error. Completed installs remain; fix the cause and rerun apply.
There is no privilege elevation or installation of VSCodium itself. Windows uses
PowerShell; Linux/macOS use POSIX shell, without Python or jq at runtime.

Before enabling, review the manifest and remove only these two script ignore
rules, then run the standard Chezmoi preview commands above. Leave the three
`product.json` ignore rules intact unless separately enabling that configuration.
The scripts use the CLI's configured gallery:
Open VSX is VSCodium's default, but an existing unmanaged `product.json` may
override it. No gallery switch, forced version, prerequisite installation, or
download of unreviewed VSIX files is performed by this repository.

The eight manual entries are Copilot Chat, C#, Pylance, Microsoft's three SSH/
remote extensions, and two IntelliCode extensions. They returned no Open VSX
entry when checked on 2026-09-06. Existing installations are untouched. Evaluate
publisher-supported distribution, licensing, and VSCodium compatibility before
reinstalling; a gallery switch does not solve runtime restrictions. BasedPyright
and Open Remote SSH are possible alternatives, not silently installed replacements.
Registry presence also does not prove runtime compatibility: VSCodium documents
limitations for Python and LaTeX Workshop despite available Open VSX packages.

### Validation and migration

Back up the existing settings/keybindings before an approved apply: Chezmoi
replaces whole files, including omitted personal model settings and old keybinds.
Use Preferences: Open Default Keyboard Shortcuts (JSON) and Developer: Toggle
Keyboard Shortcuts Troubleshooting from the command palette to check live input.
Existing workbench layout state and per-project settings can override defaults.

```sh
python3 tests/vscodium.py
```

The tests render all three platforms with/without the desktop profile, check
settings/shortcut semantics, preserve the extension inventory, and ensure runtime
files, disabled scripts, and Noctalia stay unmanaged. Mock-CLI tests cover missing
tools, repeat runs, native errors, and verification without actual installations.
They do not launch the editor, install anything,
validate every extension schema, or prove notebook/debugger/theme runtime behavior.
Installer execution tests exercise the POSIX implementation; the PowerShell
template is rendered and checked for its inventory/ignore boundary, but still
needs native Windows execution testing before enabling it there.
Run the standard Chezmoi preview commands above before applying.

References: [VSCodium extensions and gallery](https://github.com/VSCodium/vscodium/blob/master/docs/extensions.md),
[compatibility](https://github.com/VSCodium/vscodium/blob/master/docs/extensions-compatibility.md),
[native CLI](https://code.visualstudio.com/docs/configure/command-line), and
[Noctalia's VS Code template](https://github.com/noctalia-dev/community-templates/blob/main/vscode/template.toml).

## Zed

Canonical settings and keybindings live in
`home/.chezmoitemplates/configs/zed/`. One-line wrappers deploy them to
`~/.config/zed/` on Linux/macOS and `~/AppData/Roaming/Zed/` on Windows.
Linux custom XDG paths and relocated Windows AppData require matching target
paths; the managed files use the standard locations.

The settings retain your VS Code base keymap, Inter 16px UI, JetBrainsMono
Nerd Font 15px editor/terminal, disabled ligatures, block cursor, persistent
tabs, inline diagnostics, and manual save/formatting. Bracket colors follow
the active theme. Language servers, outline, folding, Git indicators, and
other features use Zed's defaults instead of copying hundreds of settings.
The terminal uses the system shell and project directory; it never forces Zsh
onto Windows or replaces the machine's chosen shell.

Your Chezmoi file associations and Tinymist PDF-on-save settings are kept.
The extension list retains all 33 enabled selections from your live settings,
plus 12 other installed extensions, including Just, Typst, and your alternative
themes. Docker Compose stays explicitly disabled. Your existing per-extension
update preferences are retained. Installing alternative themes does not change
the Noctalia/system theme selection. Zed owns extension downloads and updates;
fonts and separate tool installations are outside this slice.

See [Zed keybindings](ZED_KEYBINDS.md) for the everyday workflow and comparison
with your previous overrides. The keymap file only adds overrides to the VS Code
base; it does not replace the inherited shortcuts.

The sole added shortcut toggles the terminal panel without needing backtick:

| Linux / Windows | macOS | Action |
|---|---|---|
| Ctrl+Alt+Shift+J | Cmd+Option+Shift+J | Toggle terminal panel |

The old Ctrl+Shift+T terminal override, Ctrl+Shift+O recent-project override,
panel-key swaps, and duplicate agent shortcuts are omitted. Reopen-tab,
symbol search, outline/right-dock toggles, and other native shortcuts remain
available. Use the command palette's `zed: open default keymap` and
`zed: open keymap` to inspect bindings for the installed version. Native
bindings were checked against Zed 1.18.1; verify the added shortcut on the
actual Danish keyboard and compositor before daily use.

### Noctalia colors

On Linux with `hyprland-noctalia`, Zed follows the system appearance using
`Noctalia Light` and `Noctalia Dark`. These are the selectable names exported by
[Noctalia's Zed template](https://github.com/noctalia-dev/community-templates/blob/02a566a27ccd299958c2c6a34e0e0727bab46b93/zed/zed.json);
`Noctalia` is only the theme family name.
Enable and configure Zed's app-theme integration yourself through Noctalia's
GUI after installation. This repository does not configure Noctalia, select
its templates, or supply a custom theme template. Its entire config directory
and Zed's generated theme files remain unmanaged.

The named themes must be generated before Zed can use them; selecting them here
does not install or enable the integration. Restart Zed if generated colors
are not picked up. Other setups use bundled One Light/One Dark with the system
appearance.

### Privacy and validation

Workspace trust remains required, unsaved-buffer restoration stays enabled,
and the built-in agent defaults to Ask as in your current setup. Telemetry and
agent feedback stay disabled; private-value redaction is enabled. Personal
agent-server registrations, model preferences, authentication, caches, sessions,
downloaded extensions, and theme output are not imported.

This replaces settings/keymap files, not just selected keys. Back up the live
files and review any personal agent/model settings you want to retain before
an approved apply. Restoring that backup restores the previous setup.

Run isolated structural/rendering tests with Python 3.11+ and Chezmoi:

```sh
python3 tests/zed.py
```

Tests cover platform/profile selection, extension inventory and update preferences,
security preferences, keymap scope, and the unmanaged Noctalia boundary.
They do not perform full Zed schema validation. The installed Zed CLI has
no config-validation command; settings autocomplete, live theme rendering,
reload behavior, fonts, and macOS/Windows input still require manual checks.
No GUI, downloads, or live config writes are performed by the tests.

References: [Zed settings](https://zed.dev/docs/reference/all-settings),
[keybindings](https://zed.dev/docs/key-bindings), and
[local themes](https://zed.dev/docs/themes#local-themes).

## Neovim

A small CLI editor, not LazyVim or a replacement for Zed/VSCodium. Linux and
macOS share the files below `~/.config/nvim/`, rendered from
`home/.chezmoitemplates/configs/nvim/`. Neovim loads `init.lua` automatically;
no shell loader is needed. Windows remains ignored. Custom `XDG_CONFIG_HOME`
or `NVIM_APPNAME` values require the files under the matching config directory.

```text
nvim/
|-- init.lua                  # Loads options, then the plugin manager
|-- lazy-lock.json            # Pinned plugin revisions
`-- lua/
    |-- config/
    |   |-- options.lua       # Editing defaults, undo, terminal colors
    |   `-- lazy.lua          # Bootstrap and explicit plugin list
    `-- plugins/
        |-- snacks.lua       # File/search pickers and explorer, including keys
        |-- which-key.lua    # Shortcut help and group labels
        |-- gitsigns.lua     # Git change indicators and buffer-local keys
        |-- surround.lua     # Quote/bracket editing
        `-- treesitter.lua   # Syntax highlighting with installed parsers
```

Neovim finds Lua modules under `lua/`: `require("config.options")` loads
`lua/config/options.lua`. The plugin manager explicitly loads the five plugin
modules; each returns its plugin specification. Adding a file alone does not
enable another plugin. Plugin-specific shortcuts stay beside their settings;
there is no empty general keymap or autocmd file. This is a LazyVim-style
layout, not an import of the LazyVim distribution or its defaults.

### Plugins and prerequisites

The five feature plugins are Snacks (picker/explorer only), which-key,
Gitsigns, nvim-surround, and nvim-treesitter. lazy.nvim is the plugin manager,
not the LazyVim distribution. The lockfile records all six revisions. On first
launch, Git downloads the manager at its locked revision and lazy.nvim installs
missing plugins below Neovim's data directory. This needs Git and access to
GitHub. Every startup also verifies the installed manager's commit against
the lock before loading it; a mismatched or unverifiable checkout is left
untouched and plugins stay disabled. Apply itself does not download editor
plugins. Startup update checks,
LuaRocks, and automatic project `.lazy.lua` loading are disabled.

Use Neovim 0.12+ with this Tree-sitter generation. Git and ripgrep are needed
for Git integration and text search; fd is recommended for finding files.
Nimbus already declares those packages. Native clipboard detection uses
pbcopy/pbpaste on macOS and an available session provider such as
wl-copy/wl-paste or xclip on Linux. It does not install a clipboard provider.
Without Git on first launch or after a failed bootstrap, basic editing remains
usable and a message explains why plugins could not load.

Parser installation additionally requires `tree-sitter` CLI 0.26.1+, a C
compiler, tar, and curl. The CLI is a remaining system prerequisite, not added
to Mise or installed by this config. Supply it through Nimbus/system packages
on Linux or your package manager on macOS, not npm. Once available, start with:

```vim
:TSInstall bash json lua markdown markdown_inline query toml vim vimdoc yaml
```

Wait for installation to finish, then reopen the files. Parsers are installed
explicitly, not downloaded on every launch. Installed parsers enable syntax
highlighting; missing ones leave ordinary highlighting available. There is no
Tree-sitter folding, indentation override, or text-object extension.

### Everyday keys

See [Neovim keybindings](NEOVIM_KEYBINDS.md) for modes, the everyday workflow,
native editing commands, picker/explorer controls, and surround examples.
It also compares the workflow with Zed and VSCodium. Space is the leader;
pause after it in Normal mode to see which-key's menu.

### Defaults, colors, and state

Use absolute line numbers, smart-case search, right/below splits, two-space
indentation as a fallback, and manual saves. Filetype plugins and EditorConfig
can override indentation. The simple built-in statusline shows the filename,
modified/read-only markers, filetype, and cursor location. No dashboard, tab
bar, session restorer, language servers, completion stack, or formatter is added.

The bundled `vim` colorscheme uses the terminal's ANSI palette with RGB output
disabled. In Noctalia-themed Ghostty it therefore uses that terminal's colors;
elsewhere it follows the current terminal. This is terminal inheritance, not
a Noctalia-generated Neovim theme. No Noctalia settings are changed. Confirm
contrast in both light and dark terminals during live testing.

The system clipboard is explicit: `"+y` copies a selection and `"+p` pastes.
Ordinary deletes do not overwrite it. Persistent undo lives in
`stdpath('state')/undo`, normally `~/.local/state/nvim/undo`, with directory mode
0700. Failure to create/secure that directory disables persistent undo rather
than preventing editing. Undo files contain previous file contents, so never
commit them. Plugins, parsers, caches, ShaDa history, and other runtime files
remain unmanaged. No existing LazyVim data is imported or deleted.

### Updates, migration, and validation

Use `:Lazy` to inspect plugins and `:Lazy update` for an intentional upgrade.
After updating nvim-treesitter, run `:TSUpdate` so its parsers match its queries.
The manager updates the deployed lockfile. After testing those versions, copy
it back to the canonical source before the next apply, then review the diff:

```sh
cp ~/.config/nvim/lazy-lock.json home/.chezmoitemplates/configs/nvim/lazy-lock.json
```

Run that from this checkout with the standard config path. Do not `chezmoi add`
the entire Neovim directory: it would import unrelated files. To restore the
tracked revisions, restore the deployed lockfile through a reviewed Chezmoi
apply and run `:Lazy restore`, followed by `:TSUpdate` and a restart. If the
manager revision differs, use the recovery below first: `:Lazy` is unavailable
while the manager is blocked. Applying a lockfile alone does not switch
already installed plugin checkouts.

Before an approved migration, privately back up and move aside the old config
directory, not just its init: old `plugin/` or `after/` files could still load.
Chezmoi does not delete unmanaged leftovers. Preserve the old data/state too
if you need a complete LazyVim rollback, and do not run `:Lazy clean` against
that old plugin store. To recover, restore the saved config and, if changed,
its data/state. For a failed manager bootstrap, inspect its exact data path
and move the incomplete `lazy.nvim.bootstrap` directory (or a broken
`lazy.nvim` installation) aside before retrying. No partial bootstrap is loaded.

If startup reports that it cannot verify the manager, ensure Git is available.
Then inspect the manager directory under Neovim's actual data path, normally
`~/.local/share/nvim/lazy/lazy.nvim`. Back up and move that exact directory
aside, then restart to bootstrap the locked revision. Do not remove the whole
data directory or edit the lock just to accept an unknown checkout. This also
handles an older LazyVim manager without changing its files. Other existing
plugins still share the data store; use a separate `NVIM_APPNAME` with a copy
of this config for an isolated trial, and preserve the old store for rollback.

Run the offline suite, or explicitly include actual plugin downloads into a
disposable home. Both keep the live editor and credentials untouched:

```sh
python3 tests/neovim.py
DOTFILES_NVIM_INTEGRATION=1 python3 tests/neovim.py
just check
```

Tests cover rendering, plugin scope, shortcuts, missing tools/parsers, failed
downloads, existing-manager verification, undo permissions, and undo across
restarts. The opt-in test adds
real pinned-plugin startup and basic surround/picker/highlighting behavior;
it does not compile additional parsers. Missing Neovim skips native checks.
Interactive input, clipboard, theme contrast, parser installation, and native
macOS operation still need live checks. Keep the current LazyVim until the
replacement is comfortable; isolated tests are not a migration.

References: [lazy.nvim](https://lazy.folke.io/),
[Snacks picker](https://github.com/folke/snacks.nvim/blob/main/docs/picker.md),
[Tree-sitter prerequisites](https://github.com/nvim-treesitter/nvim-treesitter),
and [isolated Neovim application names](https://neovim.io/doc/user/starting/#%24NVIM_APPNAME).

## Topgrade

Linux and macOS share `~/.config/topgrade.toml`, rendered from
`home/.chezmoitemplates/configs/topgrade/topgrade.toml`. Windows stays ignored.
This is the user-tool part of updating, not a replacement for Nimbus's system
update workflow. Applying the file does not run Topgrade or update anything
beyond the existing [Mise install hook](#cargo-tools).

| Step | Updates |
|---|---|
| Mise, first | Mise itself, its plugins, and globally declared runtimes/tools, including the Cargo and npm backends |
| GitHub CLI extensions | Installed gh extensions, not gh itself or Git repositories |
| Sheldon | Downloaded shell plugins and their runtime lock, not the managed plugin selection |
| tldr | Local help-page data, not the tldr executable |

The native Mise step in the tested Topgrade 17.9.0 runs in a fresh temporary
directory, away from the caller's project and home-local Mise files. It still
loads the global config and Cargo fragment. `bump = false` preserves your
declared LTS/stable selectors rather than rewriting them to new major versions.
Mise's own self-update is allowed for its user-owned installation; Topgrade's
self-update is disabled because its package manager owns the executable.

No separate Cargo, Rustup, npm, Bun, or uv updater is enabled for tools already
owned by Mise. Independently installed Cargo tools under `~/.cargo/bin` are not
upgraded by this config. Editor/plugin updates retain their native workflow;
Neovim's tracked lock needs explicit review. System packages, Flatpaks, firmware,
Nix, containers, source checkouts, and Chezmoi updates/apply are excluded. There
are no custom commands, pre/post hooks, sudo priming, automatic cleanup, or
blanket confirmation bypass. Failures remain visible with the native retry
prompt; completed steps are not rolled back.

The intended full Nimbus flow is: pre recovery point, system changes and
RPM/Flatpak upgrades, verified post recovery point, then a separate Topgrade
user-tool phase. Nimbus's recovery and Topgrade handoff are still pending;
this branch does not implement them or claim current system updates have
snapshots. Snapshots cover system subvolumes, not home-directory tools. The old
Topgrade Snapper hooks, Limine sync, DMS update callback, Arch-specific settings,
and privileged system npm command are deliberately not carried over.

Topgrade 17.9.0 combines CLI `--only` with the config's `only` list; it does not
use the CLI list as a strict restriction. Nimbus must account for that when
implementing its allowlist contract. Do not use `--only mise` expecting it to
exclude the other configured steps. This also means the allowlist is scope
configuration, not a sandbox against a malicious manager or extra config.

Before migration, back up the live Topgrade file and inspect any `topgrade.d`
fragments. A normal invocation automatically merges that directory, which can
add hooks outside the allowlist. On the tested version, the explicit `--config`
form below bypasses that directory. Review the selected main file too: dry-run
is not a general sandbox for arbitrary hooks, and native read-only probes may
still run. Stop if Topgrade reports configuration errors: it can fall back to
defaults rather than fail closed. After an approved apply, preview using:

```sh
topgrade --config "$HOME/.config/topgrade.toml" --dry-run --no-self-update
```

Only when ready to update, run the same command without `--dry-run` as your
normal user. Review the summary and use the failing tool's native repair/retry
workflow. Rerun the isolated tests when upgrading Topgrade; native behavior was
tested on Linux, not macOS. No real update has been performed in this branch.

```sh
python3 tests/topgrade.py
```

These tests use a disposable home and fake updater executables, including for
native Topgrade execution, and a read-only isolated Mise config-discovery probe.
See the [Topgrade reference config](https://github.com/topgrade-rs/topgrade/blob/v17.9.0/config.example.toml)
and [native Mise step](https://github.com/topgrade-rs/topgrade/blob/v17.9.0/src/steps/generic.rs).

## Niri and DankMaterialShell

Select `niri-dms` through the existing Linux profile prompt when you are ready
to use these files. Profile selection alone does not apply them or install the
session. On other profiles, macOS, and Windows they remain ignored. Nimbus
still needs the corresponding system profile; packages, portals, polkit, the
greeter, and system session integration are not added by this dotfiles branch.
No Hyprland or Noctalia settings are changed.

The Niri layout deliberately uses the same responsibilities we can use for
Hyprland later, expressed in each compositor's native syntax:

| Niri file | Responsibility to mirror in future Hyprland config |
|---|---|
| `config.kdl` | Small loader with explicit includes |
| `input.kdl` | Keyboard and pointing-device preferences |
| `outputs.kdl` | Deliberate monitor settings after hardware testing |
| `layout.kdl` | Gaps, borders, corners, sizing, and visual defaults |
| `rules.kdl` | Application-specific window rules |
| `autostart.kdl` | User-session startup, with one owner per process |
| `shell.kdl` | Shell-specific surface integration and generated colors |
| `keybinds.kdl` | One authoritative shortcut list |

Niri's files all live in `~/.config/niri/`. There is no shared generator or
cross-compositor language, no Niriland dependency, and no layered override
keymaps. [Niri keybindings](NIRI_KEYBINDS.md) explains the workflow, preserved
shortcuts, removed duplicates, and the future Hyprland mapping. Niri scrolling
columns and vertical workspaces should remain native rather than being forced
to behave exactly like Hyprland.

Use Niri 26.04+ and DMS 1.6.0+ for this baseline. The configuration retains
touchpad tapping/natural scrolling and mouse-follow focus, but hovering no
longer scrolls to partly hidden windows. Keyboard layout comes from the
system. Monitor modes and scales use automatic detection until reviewed on
each machine; old connector names and hardware-specific overrides are not
imported. Native animation defaults replace the old tuning blocks.
Install DMS's Quickshell dependencies and Matugen for dynamic color generation
through the session's package owner; without Matugen, Niri's fallback remains
usable but does not prove DMS's wallpaper-derived theming works.

Niri starts `dms run` once. Do not also enable a DMS service or a second
autostart entry. Portals and polkit belong to the installed session;
1Password's GUI owns its own autostart. The old `niriusd`, hardcoded polkit
binary, and delayed duplicate 1Password launch are removed from this config.
Terminal launch needs `xdg-terminal-exec`; browser launch uses `xdg-settings`
and `gtk-launch`, and file browsing uses `xdg-open`. Configure your preferred
native desktop defaults separately; no unimplemented Nimbus helper is needed.

DMS generates `~/.config/niri/dms/colors.kdl`; Chezmoi does not own it. Niri
loads that palette optionally, with neutral defaults for first startup. A
missing file produces a warning, not a failed config; an invalid existing
file still needs repair. Old DMS layout, output, keybind, cursor, and window-rule
files are not included. Keep compositor/keybind changes in the source modules,
not DMS's compositor editors, and do not rerun DMS setup over this layout.
Generated app themes and DMS runtime state must not be added to Chezmoi.

Existing Ghostty/Zed/VSCodium theme selection is unchanged: the Noctalia profile
selects its themes, and other profiles use their existing fallback palettes.
Selecting both desktop profiles does not switch app themes with the current
session. DMS application-theme writers are disabled so they do not replace
Chezmoi-owned editor configs. App-theme integration can be a separate slice.

DMS settings target the current 1.6 schema instead of importing the old full
settings dump. They preserve your dynamic vibrant palette, transparent top bar,
workspace switcher, music/clock, tray and controls, Inter/JetBrainsMono fonts,
list launcher, and no dock. Clipboard selection does not automatically paste,
and notification history stays disabled. Weather and automatic location stay
off until you choose a location locally. The system-update widget is omitted
until the intended Nimbus update/recovery flow is available.

On AC, the older reference's five-minute lock and ten-minute screen-off replace
the live config's disabled timers; suspend remains three hours. Battery timings
remain three minutes to lock, five to screen-off, and one hour to suspend.
Lock-before-suspend stays enabled. Verify lock/PAM and resume on the actual
machine; configuration alone cannot guarantee a working lock screen.

DMS owns its GUI's runtime writes. After experimenting in the GUI, review and
copy only intentional preference changes back to the curated source JSON;
do not add the whole DMS directory or expanded settings dump. The next apply
will replace changes you have not captured. Wallpaper paths, monitor settings,
device selections, downloaded plugins, cache and session state remain local.

Before an approved migration, privately back up both live configuration trees.
Review the diff, install the session prerequisites through their proper owner,
and keep a working TTY or alternate session for recovery. Niri live-reloads
config changes, so even a file-only apply can immediately change an active
session's shortcuts. Stop DMS before replacing its settings to avoid racing
its GUI writes. Chezmoi replaces managed files; it does not merge preferences
or delete old Niriland files. Restore the saved files from the TTY to recover.

```sh
python3 tests/niri.py
python3 tests/dms.py
just check
```

The tests render into disposable homes and validate Niri without starting a
compositor. They cannot prove real monitor scaling, key delivery, generated
palette contrast, DMS panels, lock/idle/resume, or session startup. Test those
on the installed system before relying on the new setup. Disabling the profile
stops management but does not remove deployed files or stop an active session.

See [Niri includes](https://niri-wm.github.io/niri/Configuration%3A-Include.html)
and [keybindings](https://niri-wm.github.io/niri/Configuration%3A-Key-Bindings.html),
plus [DMS settings](https://github.com/AvengeMedia/DankMaterialShell/blob/v1.6.0/quickshell/Common/settings/SettingsSpec.js)
and [settings migrations](https://github.com/AvengeMedia/DankMaterialShell/blob/v1.6.0/quickshell/Common/settings/SettingsStore.js).

## Webapps

Two Linux launchers are prepared, but remain ignored by Chezmoi until
Nimbus implements and tests its webapp helper:

| Launcher | Website | Icon source |
|---|---|---|
| Google Maps | [Maps](https://www.google.com/maps) | [Google's Maps icon](https://www.gstatic.com/images/branding/productlogos/maps_2025_round/v1/web-512dp/logo_maps_2025_round_color_1x_web_512dp.png) |
| FotMob | [FotMob](https://www.fotmob.com/) | [FotMob's app icon](https://www.fotmob.com/img/icon-512x512.png) |

The entries live in `home/dot_local/share/applications/`. Each calls
`nimbus launch webapp URL` directly, without shell evaluation or a separate
browser-selection script. Nimbus owns browser selection and application-mode
launching. `TryExec=nimbus` lets launchers hide entries when Nimbus is absent;
it cannot detect whether an installed Nimbus supports the webapp subcommand.
No URL includes an account, private destination, tracking query, or credentials.
Site sign-in and preferences remain in the browser, not these files.

Fastmail instead uses the stable `com.fastmail.Fastmail` Flatpak, selected by
Nimbus's desktop profile. Nimbus owns installation and updates through its
existing system Flathub remote; the package supplies its launcher and icons.
Chezmoi does not install it, track its account/offline-mail state, or set it as
the default mail app automatically. Sign-in, notifications, and email-link
handling need a live test after installation. See [Fastmail's official downloads](https://www.fastmail.com/download/).

Unmodified 512x512 PNGs from the vendor sites are stored under
`home/dot_local/share/icons/hicolor/512x512/apps/`, using the unique
`nimbus-webapp-` icon prefix. Sources were checked on 2026-09-07: Maps and
FotMob publish these icons in their web manifests. These are third-party
brand assets, not original artwork
or a claim of an open-source license; their rights remain with their owners.
Icons are local, so apply and launcher display do not download them. No icon
theme, desktop settings, browser profiles, or wallpapers are changed.

The temporary five-rule block in `home/.chezmoiignore` keeps both entries
and their icons inactive. Once the helper works, remove only that block's five
rules, retaining the separate Linux and `ManagedByNimbus` gates. macOS,
Windows, and standalone Linux remain omitted. No compositor profile is needed.

Before enabling, test each command on the installed Nimbus desktop:

```sh
nimbus launch webapp https://www.google.com/maps
nimbus launch webapp https://www.fotmob.com/
```

Then preview and apply only with approval. Confirm names, icons, app-window
behavior, and window grouping in the real launcher. The Maps desktop filename
matches the inspected Niriland entry so it replaces that entry instead of
creating a duplicate. Back it up before migration. The old Niriland Fastmail
webapp, if present, remains untouched and may duplicate the Flatpak's launcher;
remove it only after verifying the desktop app and approving that cleanup.
Browser-installed PWAs with other filenames may also need separate cleanup.
Existing icons and unrelated launchers are not removed. Disabling management
later does not delete already deployed files; their removal is a separate step.

Offline checks validate desktop syntax, exact launch arguments, local icons,
inactive targets, and the future platform/Nimbus gates in disposable homes:

```sh
python3 tests/webapps.py
just check
```

The native syntax check uses `desktop-file-validate` when installed. Tests do
not open websites, launch Nimbus, download assets, or prove live app behavior.
The entry and icon layout follow the [Desktop Entry Specification](https://specifications.freedesktop.org/desktop-entry/latest/recognized-keys.html)
and [Icon Theme Specification](https://specifications.freedesktop.org/icon-theme-spec/latest/).

## Future Nimbus launchers

The desktop phase may use `nimbus launch browser [URL] [--private]` and
`nimbus launch webapp URL` on Nimbus-managed machines. Standalone setups need
a tested native alternative; do not call Nimbus when `ManagedByNimbus` is false.
The deferred Windows guest launcher may call `nimbus windows connect` only when
both `windows-vm` and `ManagedByNimbus` are selected. These are planning notes,
not installed launchers; they do not enable Windows integration.

## 1Password SSH

The Linux/macOS wiring is ready for installation; real 1Password retrieval,
agent authorization, and destination authentication remain untested. Windows
SSH targets stay ignored, including when the feature is selected.

Bootstrap asks whether to enable the integration, defaulting to false. The
prompt requires neither `op` nor an unlocked vault. On Linux/macOS,
`onePasswordSsh = true` manages:

- `~/.ssh/` with mode `0700`, without removing unrelated files
- `~/.ssh/config` with mode `0600`, rendered from the SSH Document item
- `~/.ssh/github.pub` and `~/.ssh/homelab.pub` with mode `0600`
- `~/.config/1Password/ssh/agent.toml`, selecting the two existing key IDs

The template appends the GitHub key selection and the platform's 1Password
agent socket after the document. The socket is `~/.1password/agent.sock` on
Linux and `~/Library/Group Containers/2BUA8C4S2C.com.1password/t/agent.sock`
on macOS. This makes 1Password the default SSH agent for all hosts, not a
forwarded agent on remote machines. No agent forwarding is enabled here.

The document holds your homelab host blocks, using
`IdentityFile ~/.ssh/homelab.pub` and `IdentitiesOnly yes` to select the Homelab
key. GitHub uses `~/.ssh/github.pub` and user `git`. Keep those shared GitHub
settings out of the document: multiple `IdentityFile` entries accumulate.
The document is plain SSH config, not another Chezmoi template. Edit it in
1Password rather than editing or re-adding the rendered file to Git.

Only the public-key fields are requested from the SSH Key items; private keys
are never exported. Chezmoi's native `secret` function runs `op item get`
with a public-field selector, allowing UUID-only lookups and `--skip-secrets`.
The generated Chezmoi config sets `secret.command = "op"` and
`onepassword.prompt = false`: authorization stays with the desktop app instead
of Chezmoi requesting CLI session tokens. `op` uses its selected account;
ensure it is the account containing all three items.

When disabled, those targets are ignored but existing files are not deleted.
Run `chezmoi init --prompt` to change the choice; this still does not apply.
Existing checkouts must also rerun init to pick up the new secret-command
settings before enabling this feature.

A missing `op`, denied authorization, or inaccessible item fails rendering
instead of silently dropping a target. An empty document or public-key text
that fails the basic format check also fails. This does not validate arbitrary
SSH directives in the private document; review its content before applying.
Chezmoi is not transactional
across files: an apply failure may leave earlier files updated. Fix the cause
and preview again before retrying.

If 1Password is only temporarily locked, inspect the remaining files without
requesting secrets:

```sh
chezmoi --skip-secrets status
chezmoi --skip-secrets diff
chezmoi --skip-secrets verify
```

After enabling or unlocking 1Password, run the normal preview before applying.

### Manual setup on the new machine

These steps are for the future installation. The current computer does not
need to be activated or used for live authentication tests while preparing
the dotfiles. Chezmoi does not enable the desktop app's integrations for you.

1. Have the 1Password desktop app, `op` CLI, and OpenSSH client installed through
   Nimbus or your standalone package setup. On Linux, use the native 1Password
   package: its SSH agent does not support Flatpak or Snap installations.
2. Sign in to the desktop app with access to the SSH Document and both existing
   SSH Key items. Reuse these keys; do not generate replacements during setup.
3. In Settings > Developer, complete **Set up the SSH Agent** or enable
   **Use the SSH Agent**, depending on the app version. Keep 1Password running
   in the background using its General settings.
4. Separately enable **Integrate with 1Password CLI** so Chezmoi can retrieve
   the document. CLI integration alone does not enable the SSH agent. SDK and
   MCP integrations are not required for this workflow.
5. Confirm the document contains your real host configuration, not placeholder
   text. Back up any existing SSH config, public-key selector files, and agent
   config privately outside the repository. Enable the Chezmoi option and
   follow the [bootstrap preview and apply steps](#bootstrap).
   Review secret-backed diffs locally; do not paste them into logs or reviews.
6. Confirm the destination already authorizes the intended public key for the
   configured user. For the proposed homelab alias, connect with `ssh ms-a2`
   and approve the Homelab key request in 1Password. Verify a new server's host
   fingerprint through a trusted channel before accepting it.

After applying, `ssh -G ms-a2` inspects the effective host configuration without
connecting; review it locally because it includes private host details. Test
`ssh ms-a2` only once the server authorizes the Homelab public key for root.
Test GitHub separately with `ssh -T git@github.com` after adding the GitHub
public key to your account. GitHub's successful authentication message comes
with exit status 1 because it does not provide an interactive shell.
Never disable host-key verification to make these tests pass.

To recover, turn off the Chezmoi option first, then restore the privately saved
files if needed. Disabling management does not delete deployed files, stop the
agent, or undo earlier overwrites. Agent enablement is a separate GUI setting.
Keep any existing working access until the new setup has been verified; a
separate recovery key remains a future user-controlled task.

### Offline validation

```sh
python3 tests/onepassword-ssh.py
just check
```

The SSH tests use disposable homes, fake documents, synthetic public keys, and
a strict fake `op` with no real credentials or agent access. They check Linux
and macOS rendering, disabled and deferred Windows targets, field-only key
requests, file permissions, retrieval failures, and secret-skipping previews.
Native `ssh -G` parses only the fake config without connecting. Temporary
applies exclude scripts. These tests do not prove native macOS operation,
real vault retrieval, or server authentication; those checks wait for installation.

References: [1Password SSH setup](https://www.1password.dev/ssh/get-started)
and [CLI integration](https://www.1password.dev/cli/app-integration),
[key selection](https://www.1password.dev/ssh/agent/advanced), and
[Chezmoi secret functions](https://www.chezmoi.io/reference/templates/secret-functions/secret/).

See [PROFILES.md](PROFILES.md) for the profile vocabulary,
[CONFIG_INVENTORY.md](CONFIG_INVENTORY.md) for migration scope,
[ROADMAP.md](ROADMAP.md) for implementation order, and
[TASKS.md](TASKS.md) for current status and dependencies.
