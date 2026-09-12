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
Neovim, Topgrade, Voxtype, and VM Curator configuration. Niri and DankMaterialShell
are available through the opt-in Linux `niri-dms` profile.
The Linux `hyprland-noctalia` profile also enables a minimal Hyprland starter;
portable Noctalia preferences, GTK/Qt settings and app-theme selections are
managed through Chezmoi. Noctalia generates the colors and runs its native
activation hooks. Apps without such a hook need a one-time theme choice in
their own settings; no custom config-rewriting scripts are used. Select
**Use GTK** in Brave Appearance settings. See
[NOCTALIA.md](NOCTALIA.md) for paths, prerequisites and recovery.
Other empty configs remain ignored until they are implemented and reviewed.

## License

Original configuration, scripts, and documentation are available under the
[MIT License](LICENSE), copyright 2026 Patrick Byrne.

The Google Maps and FotMob icons described under [Webapps](#webapps) are
third-party brand assets and are not covered by the MIT license.

The inactive Hyprland reference files retain their upstream terms: Omarchy's
MIT notice is in `compare/omarchy.lua`; Ryoku's excerpts in `compare/ryoku.lua`
are GPL-3.0-only.

## Mise tools

On Linux, Chezmoi manages `~/.config/mise/conf.d/linux-tools.toml` alongside
the main Mise configuration. It selects Linux CLI tools through Mise's native
backends:

| Tool | Mise backend |
|---|---|
| Tinymist | Registry `tinymist`, using Aqua |
| Sheldon | Registry `sheldon`, using Aqua |
| resvg | Registry `resvg`, using Aqua |
| AI Usage | Cargo `ai-usagebar`, compiled from crates.io |
| Caligula | GitHub `ifd3f/caligula`, native executable |
| VM Curator | GitHub `mroboff/vm-curator`, Linux x86_64 tar archive |

VM Curator's upstream release only provides Linux x86_64 binaries. Its native
Mise `os = ["linux/x64"]` restriction keeps it inactive on ARM while the other
tools remain available from the same fragment.

All selected tools use `latest` stable. `mise install` installs missing versions;
`mise upgrade` and the existing Topgrade Mise step update them without editing
version pins. The Aqua and GitHub backends download the maker's release assets
and perform native checksum and available provenance checks. There is no
separate `cargo-update` installation: Mise owns updates for its tools.
See the [Aqua backend](https://mise.jdx.dev/dev-tools/backends/aqua.html)
and [GitHub backend](https://mise.jdx.dev/dev-tools/backends/github.html).
AI Usage uses the [Cargo backend](https://mise.jdx.dev/dev-tools/backends/cargo.html)
and the managed Rust toolchain. Its `ai-usagebar` CLI supplies Noctalia's
AI Usage plugin; account authentication remains outside these dotfiles.

This Linux fragment is ignored on macOS and Windows. The existing runtime
selections remain in `~/.config/mise/config.toml`. Typst comes from Terra
through Nimbus; standalone users supply it through their package manager.

Every full `chezmoi apply` on Linux and macOS writes configuration, then runs
`mise install` as the current user from the home directory. This works with or
without Nimbus. Nimbus installs Mise itself before its first Chezmoi apply;
standalone users must install Mise before applying. The script prefers
`~/.local/bin/mise`, then finds Mise on `PATH`, and reads the managed config in
`~/.config/mise`. For this invocation, `MISE_CEILING_PATHS` stops project-config
discovery before the home directory, excluding home-local `mise.toml`,
`.mise.toml`, version files, and parent-directory configs. The global config
and its tool fragment still load; normal interactive Mise discovery is unchanged.

Run Chezmoi as your normal user; the Bash install script refuses root execution.
The [after-apply script](home/run_after_install-mise-tools.sh.tmpl) runs even
when configuration is unchanged, so another apply repairs missing tools.
Native output stays visible; missing Mise, missing config, or a failed install
fails the apply. Fix the reported problem and rerun the full apply to retry.
Files already written and tools already installed are retained after failure.
Only native Mise tool declarations request installation; other app configs do
not install those apps.

The script sets `MISE_SYSTEM_DEPS=warn` and `MISE_AUTO_UPDATE=false`: system
dependencies stay outside Chezmoi, and this install step does not request
runtime upgrades or a Mise self-update. It does not install Mise itself or run
on Windows. Shell startup still only activates tools.

For Nimbus-managed installs, the script prints applicable `Setup note: `
instructions before tool installation. Nimbus repeats them after its final
summary, even if Mise fails. They cover shell activation, 1Password sign-in and
its SSH opt-in, and Noctalia theme generation. Notes never contain credentials.
When Nimbus supplies its private installation log directory, the script also
keeps native Mise output, command timestamps, exit codes, and durations in
`mise.log`, while preserving terminal output. Log creation or write failures
fail the apply. Chezmoi template output, input, and environment variables are
not included in this tool log.

## First login and setup ownership

Installation and account authorization are separate steps:

| Owner | Setup responsibility |
|---|---|
| Nimbus | System packages and services, the default login shell, and approved native post-install actions such as Tailscale operator permission and ProtonPlus setup. |
| Chezmoi | User preferences, shortcuts, bookmarks, portable account metadata, and Mise declarations. |
| Mise | Install the declared tools after apply, including AI Usage and the agent CLIs. These are not manual package installations. |
| Each application | Account sign-in, credentials, sessions and provider connections. Keep these outside Git. |

After installation, complete the applicable account steps in the applications:

- Sign into and unlock 1Password; enable its CLI integration and, when selected,
  SSH agent. Confirm GitHub SSH access and commit signing separately.
- Authenticate GitHub CLI and confirm the local Git author identity.
- Sign into Tailscale. Its local operator permission is a separate
  `nimbus postinstall tailscale-operator` action, not an account login.
- In the Noctalia desktop session, run `nimbus postinstall noctalia-plugins`
  to inspect and repair missing enabled plugins. This requires the Nimbus
  engine containing that task; the change is not released yet. It uses the
  effective Noctalia selection, updates affected sources through Noctalia
  and waits for their missing runtime files. Noctalia refreshes the live bar. Standalone users can use Noctalia's native plugin controls.
- Add Fastmail to Noctalia using a calendar-only app password stored in the
  keyring. See [Fastmail calendars](NOCTALIA.md#fastmail-calendars).
- Sign into Claude, Grok and Codex. Connect the Codex and OpenRouter providers
  in OpenCode. Installing a CLI does not establish account authorization.
- When the Copilot application is installed, select and authorize its Codex
  backend through the application.
- Zeron works locally without sign-in. For optional multi-device sync, follow
  the [Zeron profile-switching steps](#zeron); existing local sessions stay local.
- Choose application themes where Noctalia has no native activation hook.

These are a first-login checklist, not a claim that accounts are connected.
Chezmoi and Nimbus must not infer successful authorization from the presence
of a binary, configuration file or token file. Do not capture account databases,
keyrings, passwords, API keys, browser sessions or calendar caches.

## Files

On the Linux `hyprland-noctalia` profile, Chezmoi writes GTK bookmarks for
Documents, Downloads, Projects, Pictures, `Projects/dtu-bachelor`,
`Projects/nimbus` and `Projects/dotfiles`, in that order. The native file is
`~/.config/gtk-3.0/bookmarks`, which Nautilus 50 also uses. Bookmarks do not clone projects. Chezmoi links `Projects/dotfiles` to its
working tree and, on Nimbus-managed machines, `Projects/nimbus` to the canonical
`~/.local/share/nimbus` checkout. Existing unrelated projects are preserved.

The Files hook creates all declared standard user folders, plus Projects,
Screenshots, Wallpapers and Recordings. This keeps login-time
`xdg-user-dirs-update` from resetting missing folders to the home directory.
Existing folders and their contents are retained on subsequent applies.

The [Files hook](home/run_after_configure-files.sh.tmpl) sets user GSettings
after apply: hidden files are visible, recent-file tracking is disabled, and
GTK file choosers show hidden files, put folders first and start in the current
directory. It skips unavailable schemas and runs without elevated privileges.
Other Nautilus preferences keep their native defaults, including double-click
activation and local-file thumbnails. The dconf database is not copied to Git.

Disabling recent-file tracking affects other GTK applications too. Nautilus
50.3 does not expose a supported setting to hide Starred; that sidebar item
remains. These preferences can be changed live, but the next full apply
restores the declared values. Removing the hook relinquishes management and
does not reset existing preferences.

## ProtonPlus preferences

The Linux `gaming` profile applies four native GSettings preferences: hourly
background updates, checking at boot and checking when ProtonPlus opens.
ProtonPlus owns and reconciles its generated user timer. The hook does not copy
the timer, API keys, game selections, caches or the dconf database. On a new
machine, open ProtonPlus once to initialize its application-owned scheduling.
The existing desktop timer is already active. Nimbus owns the separate initial
Proton-CachyOS Latest installation action; Steam authentication remains local.

## Launcher visibility

Linux user desktop entries under `~/.local/share/applications` hide selected
tools with `NoDisplay=true`. Their native commands, file types and desktop
actions remain available. This is a Chezmoi preference shared by launchers
that follow the desktop entry specification; no system package is removed.
`TryExec` also prevents a file handler being offered when its command is absent.

The hidden entries are:

- btop++, Neovim and Yazi File Manager.
- mpv Media Player; Celluloid is the default desktop media player.
- Icon Browser, Qt5 Settings, Qt6 Settings, NVIDIA X Server Settings,
  Goverlay, uuctl and Noctalia.
- LibrePods, pending review after the fork is installed.
- LibreOffice Base and LibreOffice Math.
- Remote Viewer and Winetricks.
- Wine's Notepad, Regedit, Wine Boot, Wine Configuration, Wine File,
  Wine Help, Wine OLE View, Wine Software Uninstaller, Wine Wordpad and
  WineMine.

Protontricks and DOSBox Staging remain visible. DOSBox emulates older DOS
software; on the reviewed Fedora desktop it arrived as Wine's recommended
weak dependency. Its visibility and installation are still awaiting a decision.

These overrides retain the installed entries' nonlocalized metadata, with
menu visibility changed. Review them if a package changes its executable,
desktop ID, file types or actions. To show an entry again, change its managed
`NoDisplay` value and apply that target. Removing a source file alone does not
delete the existing user override.

## Default applications

On the Linux `hyprland-noctalia` profile, Chezmoi manages
`~/.config/mimeapps.list`: Nautilus for folders and archives, Brave Origin for
web pages, Fastmail for email links, Loupe for images, Celluloid for media,
Zed for text/code/configuration, and the corresponding LibreOffice application
for office documents. GIMP retains its image project formats.

PDFs prefer `org.pwmt.zathura-pdf-poppler.desktop`, which Fedora's
`zathura-pdf-poppler` package supplies. Nimbus selects that package alongside
Zathura. Until the plugin is installed, the next handler is Brave; the core
Zathura package alone cannot read PDFs. No File Roller installation is needed.

Existing T3 Code, Claude, Codex and Discord URL registrations are retained.
Their applications own the handlers and authentication. Review and capture
new associations written by applications before the next apply; otherwise the
managed file restores the declared preferences. File types and links not listed
here keep their native application or distribution defaults.

Explanatory comments stay in `home/dot_config/mimeapps.list.tmpl` as Chezmoi
template comments. They do not appear in the generated file, whose compact
format matches the desktop's current output. This avoids comment-only drift
when desktop tools rewrite associations while keeping the source readable.

## Bootstrap

On a new machine with access to the repository (authentication is required
while it remains private; anonymous HTTPS is the intended published path):

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

`chezmoi diff` excludes scripts so its default output shows file changes.
`chezmoi status` still reports scripts with `R`, including when configuration
already matches. The scripts continue to run on a full apply. To review their
contents too, use:

```sh
chezmoi diff --exclude=none
```

After changing the Chezmoi config template, refresh the local configuration
without applying dotfiles or rerunning the stored prompts:

```sh
chezmoi init --apply=false
```

Neither the preview commands nor `chezmoi apply --dry-run` installs tools.
A full apply is the supported configuration-and-install flow; applying
individual files need not run the after-apply script.

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
The Hyprland startup hook runs `udiskie --no-tray --no-notify` once per
session. Automounting uses this config; Noctalia's enabled Udiskie Manager
plugin supplies drive controls and notifications. Other sessions receive the
config without a startup entry.

### Zathura

The Linux config lives directly in `home/dot_config/zathura/zathurarc.tmpl`.
It includes Noctalia's generated palette only for the desktop profile.

The palette keeps the live/Niriland charcoal background and blue highlights,
extending them to completions and the document index. A generic sans-serif
font replaces the Inter dependency. New documents open with the whole page
fitted to the window; use `s` for width fitting on long pages. Page-sized
scrolls respect page boundaries, and selected text goes to the clipboard
without a notification. Recolor stays off initially so document colors are
preserved. Bookmarks, reading positions, and databases stay unmanaged.

See [Zathura keybindings](ZATHURA_KEYBINDS.md) for everyday reading, search,
navigation, and view controls. Native bindings remain intact, with three extra
view shortcuts. [Alex Balgavy's config](https://git.alex.balgavy.eu/dotfiles/file/zathura/zathurarc.html)
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

### Voxtype

Linux manages `~/.config/voxtype/config.toml`. Nimbus supplies Voxtype and its
Wayland output tools. The config uses local Whisper with the multilingual
`small` model, detects English or Danish, and keeps speech in its original
language. This is a CPU starting point; model quality, latency, and GPU choices
still need laptop/desktop trials.

Recording uses the default microphone, pauses media, and stops after at most
60 seconds. Output tries `wtype`, then the clipboard, with automatic submission
disabled. Notifications show recording progress without the transcription.
Native recording commands replace built-in input-device hotkeys, following the
[Voxtype configuration reference](https://github.com/peteonrails/voxtype/blob/v1.0.1/docs/CONFIGURATION.md).

Download the selected model explicitly before running the daemon:

```sh
voxtype setup --download --model small
voxtype daemon
```

From another terminal, `voxtype record toggle` starts/stops recording;
`voxtype record cancel` discards it. Compositor shortcuts and automatic daemon
startup remain to be selected. Chezmoi does not download models or start the
daemon. Models, recordings, and runtime state remain outside the repository.
Edit the source config to persist choices: the native configuration TUI writes
the managed file and a later Chezmoi apply would replace those edits.

### VM Curator

Linux manages `~/.config/vm-curator/config.toml`, independently of machine
profiles. Mise supplies the executable on x86_64. The library stays at
`~/vm-space`; new guests start with 8 GiB RAM, four CPU cores, a 128 GiB disk,
GTK display, and KVM enabled. These are editable creation defaults, matching
the planned desktop VM baseline. Launch confirmation stays enabled in the TUI;
GPU passthrough retains upstream's disabled defaults.

Run `vm-curator` for the TUI or `vm-curator list` to list guests. Its native
first-run setup creates a missing library. VM images, ISOs, snapshots, metadata,
and hardware setup are not managed by Chezmoi. The Settings screen saves the
managed config; copy intended changes back to the source before applying again.
See the [upstream configuration](https://github.com/mroboff/vm-curator/tree/v1.4.0#configuration).

Both configs passed isolated native reads with Voxtype 1.0.1 and VM Curator
1.4.0. Those checks did not record audio, load models, or launch a VM.

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

The `check` GitHub workflow runs this gate in Fedora 44 with native Chezmoi,
Neovim, shell, Lua, and SSH tools. Optional application parsers skip when the
application is absent; GUI and real plugin-download checks remain opt-in.
The workflow verifies configuration without applying it to a workstation.

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
configs are excluded while the global config and tool fragment remain loaded.
Logging tests cover failure, retry, and unsafe paths. These tests never apply
this repository or download tools. None of these checks authenticates, mounts
devices, accesses the real clipboard, or writes live configuration.

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
your identity, LFS filters, credentials, and personal overrides are neither
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

No custom colors, external pager, URL rewrites, credential
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
not yet exist.

On Linux and macOS, the existing `onePasswordSsh` option also enables SSH
commit signing. Git uses the managed `~/.ssh/github.pub` selector and the
platform's 1Password signing helper. No key material or personal identity is
stored in the Git template. Windows and installations with the option disabled
keep the shared defaults without signing settings. Personal Git overrides
still take precedence.

Keep the 1Password app available and approve signing requests. Register the
public key separately as a signing key on GitHub to get verified commits;
SSH authentication alone does not register it for signing. Missing keys,
unavailable signing helpers, or denied authorization fail the commit.

Edit the source and apply only Git configuration with:

~~~sh
chezmoi edit ~/.config/git/config
chezmoi diff ~/.config/git/config
chezmoi apply --exclude=scripts ~/.config/git/config
~~~

Edit the template for future Git changes instead of re-adding the rendered
file, which would replace its platform and opt-in conditions.
Inspect one effective setting without dumping personal configuration:

```sh
git config --show-origin --get pull.ff
```

Run isolated checks with Python 3, Git 2.37+, and Chezmoi:

```sh
python3 tests/git-config.py
```

Tests use temporary homes and local fixture repositories only, including
synthetic commits and local pushes. They check automatic loading, personal
overrides, platform targets, signing opt-in and repair, ignore rules, aliases,
upstream setup, pruning, and fast-forward-only pulls without network access
or live configuration changes. Signing failures use an unavailable test
helper; no real 1Password authorization or signed commit is tested.
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
highlighting and history/completion suggestions instead of Zsh plugins.
It is discovered under `$XDG_DATA_HOME/blesh`, Linux system share directories,
or the standard Apple Silicon/Intel Homebrew prefixes. Its bell setting lives
in `bash/blerc`, also exposed through `.blerc`. Other ble.sh defaults are kept.

Following [ble.sh's startup and fzf guidance](https://github.com/akinomyoga/ble.sh#13-set-up-bashrc),
it loads before the modules and attaches last. With ble.sh, its bundled
`integration/fzf-key-bindings` handles Ctrl-T, Ctrl-R, and Alt-C; without it,
the installed `fzf --bash` integration handles them. Ctrl-T previews and
Ctrl-R's clipboard shortcut match Zsh. With both ble.sh and fzf installed,
[`integration/fzf-menu`](https://github.com/akinomyoga/blesh-contrib/blob/master/integration/fzf.md#pencil-integrationfzf-menu)
turns ordinary Tab completion into an fzf picker, including command-specific
`bash-completion` candidates. Enter accepts a candidate and Escape cancels.
Without ble.sh, Tab uses Readline completion and fzf's standard `**` trigger.
Terminal-only integrations are skipped without a usable terminal.

The Bash config does not install ble.sh. If suggestions and command coloring
are missing, check for `~/.local/share/blesh/ble.sh` or a system installation.
Installing fzf alone only provides its own shortcuts. Start a fresh Bash
session after installing ble.sh or changing the integration.

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
manages the machine. The profile enables Ghostty's built-in integration.
Noctalia generates `~/.config/ghostty/themes/noctalia`; Chezmoi manages the
selection, not that generated file.
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

Mouse scrolling uses a multiplier of 4. Linux retains the flat GTK toolbar and
explicitly copies selected text to PRIMARY for middle-click paste. Hyprland's
startup hook enables GTK's `gtk-enable-primary-paste` preference, which Ghostty
reads when opening a terminal surface. After changing that preference, open a
new tab or window. In applications that capture mouse input, hold Shift while
selecting text to use Ghostty's selection instead.
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
One-line wrappers deploy `User/settings.json`, `User/keybindings.json`, and
`product.json` beside the `User` directory:

| Platform | User directory |
|---|---|
| Linux | `~/.config/VSCodium/User/` |
| macOS | `~/Library/Application Support/VSCodium/User/` |
| Windows | `~/AppData/Roaming/VSCodium/User/` |

These are standard installation paths, not portable mode, custom user-data
directories, or named profile overrides. Review those separately if used.
The canonical `product.json` selects Microsoft Marketplace on each platform.
Snippets, credentials, chat provider settings, workspace storage, caches,
history, and extension binaries remain outside Chezmoi's managed files.

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
`noctalia.noctaliatheme`. The profile selects the `vscode` community template,
which includes VSCodium. The template currently targets extension version
0.0.5; check its target again if the extension version changes. Other setups follow system
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
Two after-apply scripts install the declared extensions:

- `home/run_after_install-vscodium-extensions.sh.tmpl` for Linux/macOS.
- `home/run_after_install-vscodium-extensions.ps1.tmpl` for Windows.

The opposite platform's template renders empty.
`run_after_` makes the appropriate script run
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

The scripts use the CLI's configured gallery, which the managed `product.json`
sets to Microsoft Marketplace. They do not force versions, install prerequisites,
or download separate VSIX files.

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
settings/shortcut semantics, preserve the extension inventory, and verify the
platform-specific gallery configuration and installer. Runtime files and
generated Noctalia colors stay unmanaged. Mock-CLI
tests cover missing tools, repeat runs, native errors, and verification without
actual installations.
They do not launch the editor, install anything,
validate every extension schema, or prove notebook/debugger/theme runtime behavior.
Installer execution tests exercise the POSIX implementation; the PowerShell
template is rendered and checked for its inventory and platform boundary;
native Windows execution testing remains pending.
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
The profile enables Zed's community template. Noctalia owns its generated
theme files; Chezmoi owns the portable selection described in
[NOCTALIA.md](NOCTALIA.md).

The named themes must be generated before Zed can use them; selecting them here
does not install the application. Restart Zed if generated colors
are not picked up. Other setups use bundled One Light/One Dark with the system
appearance.

### External agents

On Linux and macOS, the settings register Claude (`claude-acp`), Codex
(`codex-acp`) and OpenCode (`opencode`) through Zed's ACP registry. Zed downloads
their adapters or executables when launched. Grok uses a custom agent command
that runs `mise exec npm:@xai-official/grok -- grok agent stdio`, using the
Grok tool declared in the native Mise configuration. This avoids Zed's npm
registry launcher passing Grok's native executable to Node.js.

Chezmoi renders Grok's Mise command as `~/.local/bin/mise` under the current
user's home directory, matching Nimbus's official user installation. Standalone
Linux/macOS setups need Mise at that location too. The existing
[Mise install hook](#mise-tools) supplies Grok after apply; no Zed-specific
installation script is needed. Windows does not receive these registrations.
Account sign-in and agent sessions remain application-owned. The Linux Grok
command passed ACP initialization and was confirmed working in Zed; macOS
rendering is tested, but its live integration has not been checked.

### Privacy and validation

Workspace trust remains required, unsaved-buffer restoration stays enabled,
and the built-in agent defaults to Ask as in your current setup. Telemetry and
agent feedback stay disabled; private-value redaction is enabled. Additional
personal agent-server registrations, model preferences, authentication, caches, sessions,
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
a Noctalia-generated Neovim theme. The desktop profile deliberately leaves
the community Neovim hook disabled. Confirm contrast in both light and dark terminals during live testing.

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

## Zeron

On Linux, the `development` profile registers Zeron in the application launcher
and adds its native updater to Topgrade. Nimbus bootstraps a missing binary
with the [official installer][zeron-install] and installs its browser runtime
dependencies, `webkit2gtk4.1` and `json-glib`. Standalone users install Zeron
through its native installer before using these links.

The desktop entry and icon are symlinks to the bundled assets under
`~/.zeron/app/current`. Native updates switch that directory, so launcher
assets follow without copying them into Git. Chezmoi does not manage Zeron's
generated service, sessions, credentials or other application state.
An after-apply hook refreshes the user's GTK icon index when Zeron's icon and
`gtk-update-icon-cache` are available. It caches names only, leaving image data
with the native application; generated caches stay outside Git.

`zeron` opens the GUI; its user service runs the headless engine. The installer
enables and restarts this service and attempts to enable user lingering, which
allows user services to continue after logout. Nimbus discloses these effects
before installation. `zeron update` owns application updates and can restart
the engine; check its output for service restart warnings. Topgrade calls it
only when the CLI is installed, without adding elevation or login steps.

Local-only use needs no account. To switch to the optional synced profile:

~~~sh
zeron daemon stop
zeron login
zeron daemon start
~~~

Use `zeron logout` in place of `zeron login` to return to the local profile.
Signing in does not import existing local sessions. Devices signed into the
same account can access synced workspaces remotely; enabling ignored-file
visibility also makes those files available. Keep authentication manual.
`zeron daemon uninstall` removes its service, not the application or sessions;
profile removal does not delete native application data.

[zeron-install]: https://github.com/zeronsh/zeron#install-and-run-locally-linux

## Topgrade

Linux and macOS share `~/.config/topgrade.toml`, rendered from
`home/.chezmoitemplates/configs/topgrade/topgrade.toml`. Windows stays ignored.
On Nimbus-managed Linux, `nimbus upgrade` runs Topgrade with this configuration.
A pre-command runs `nimbus upgrade --system` for native DNF and system Flatpak
updates. It does not sync definitions or call Topgrade again. A failure or
cancellation stops all later updates. Use `nimbus sync` separately for system
drift, or `nimbus sync --upgrade` for both. These Nimbus command changes are
local and unreleased; deploy the matching engine before using this config.
Extra native arguments follow `--`, for example `nimbus upgrade -- --dry-run`.
Standalone Linux uses native system/Flatpak steps; macOS uses Homebrew.
Applying the configuration does not run updates beyond the existing
[Mise install hook](#mise-tools).

| Step | Updates |
|---|---|
| Mise, first | Mise itself, its plugins, and globally declared runtimes/tools, including the Cargo and npm backends |
| GitHub CLI extensions | Installed gh extensions, not gh itself or Git repositories |
| Sheldon | Downloaded shell plugins and their runtime lock, not the managed plugin selection |
| tldr | Local help-page data, not the tldr executable |
| GitHub Copilot, managed Linux | The COPR installer helper updates the app when the helper is installed |
| Zeron, Linux development | `zeron update` updates the native application when installed |

The native Mise step in the tested Topgrade 17.9.0 runs in a fresh temporary
directory, away from the caller's project and home-local Mise files. It still
loads the global config and tool fragment. `bump = false` preserves your
declared LTS/stable selectors rather than rewriting them to new major versions.
Mise's own self-update is allowed for its user-owned installation; Topgrade's
self-update is disabled because its package manager owns the executable.

No separate Cargo, Rustup, npm, Bun, or uv updater is enabled for tools already
owned by Mise. Independently installed Cargo tools under `~/.cargo/bin` are not
upgraded by this config. Editor/plugin updates retain their native workflow;
Neovim's tracked lock needs explicit review. Firmware, Nix, containers, source
checkouts, and Chezmoi updates/apply stay outside this allowlist. Topgrade does
not prime sudo, enable automatic cleanup, or bypass all confirmations. Nimbus
handles its own system approval and privilege; user-tool steps run without
elevation. The Copilot helper uses sudo and retains its native DNF confirmation.
Independent user-step failures allow later steps to run but retain a failing
final status.

The Copilot helper owns download verification and application updates; DNF
updates the helper RPM. Initial application installation remains an explicit
postinstall action. WoWUp updates wait for a standalone update command in its
COPR helper. Nimbus's system callback handles Snapper when selected; do not
add duplicate snapshot hooks here. Repair a broken session through a TTY and
use the failing manager's native commands.

Topgrade 17.9.0 combines CLI `--only` with the config's `only` list; it does not
use the CLI list as a strict restriction. The configured list defines the
managed scope; explicit CLI additions are user customizations. Do not use
`--only mise` expecting it to exclude the other configured steps. This also
means the allowlist is scope
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

## Hyprland starter

On Linux, selecting `hyprland-noctalia` manages
`~/.config/hypr/hyprland.lua` and its populated `conf.d/` modules for the
compositor. This targets Hyprland 0.56+ and Noctalia 5, matching the Lua/daemon flow in the Fedora test notes. It is a
small adaptation of the [upstream starter](https://github.com/hyprwm/Hyprland/blob/v0.55.0/example/hyprland.lua),
with `hyprland.lua` loading explicit relative module paths.
macOS, Windows, and other profiles do not receive it; Nimbus is not required
to use the user config. Nimbus owns package and greeter/session installation.

`home/dot_config/hypr/conf.d/` reserves separate Lua files for environment,
monitors, input, layout, decoration, animations, workspaces, window rules,
keybindings, and autostart. All are populated, deployed, and loaded.
Decoration loads Noctalia's optional generated palette;
window rules let Noctalia animate its own surfaces.
The grouping follows the native module layouts in
[Omarchy](https://github.com/omacom/omarchy/blob/quattro/config/hypr/hyprland.lua),
[ML4W](https://github.com/mylinuxforwork/dotfiles/blob/main/dotfiles/.config/hypr/hyprland.lua),
and [Ryoku](https://github.com/Ryoku-dev/ryoku-arch/blob/main/ryoku/hyprland/hyprland.lua).
Noctalia generates its palette separately at `~/.config/hypr/noctalia.lua`;
its upstream color template is not a ready-to-load configuration file.

`compare/omarchy.lua` and `compare/ryoku.lua` are separate reference notebooks
with commented-out excerpts from the local `~/compare` checkouts. Their headers
record exact revisions and licenses; sections explain dependencies and choices
to revisit. They are ignored by Chezmoi and are not included by `hyprland.lua`.

Ghostty, Brave Origin (`brave-origin`), and Nautilus match Nimbus's current
application selection. These are direct commands, not shell aliases or future
Nimbus launch helpers, and do not change system MIME defaults.
`conf.d/monitors.lua.tmpl` scopes output rules by machine. On
`Machine = "desktop"`, the BenQ XL2720Z (DP-4) starts at `0x0` and is the
default cursor display; the ZOWIE XL LCD (DP-3) is to its right at `1920x0`.
Both use their advertised 1920x1080 at 144 Hz mode and scale 1.
On `Machine=laptop`, the internal `eDP-1` panel uses its preferred mode and
scale 1.5: 2880x1800 becomes a 1920x1200 logical workspace. Unlisted outputs
keep automatic scaling. Window sizes remain unchanged pending visual review.

`conf.d/layout.lua` selects native scrolling with half-width columns.
Super+F toggles the focused column between half and full width, even when alone.
Focus brings columns into view without centering them, while hovering does not
scroll the view. Width presets match Niri's one-third, one-half, and two-thirds;
the layout's column focus/swap commands do not wrap at the ends.

Decoration uses inner/outer gaps of 5/10, 2-pixel borders, 12-pixel circular
corners, light blur (size 3, two passes), and small shadows. Active and inactive
windows receive no extra opacity reduction or dimming; apps retain their own
transparency. Noctalia supplies border and group colors through the generated
palette, loaded after these settings. Device-specific hardware rules remain
for the installed session.

Animations use 220 ms vertical workspace slides, subtle 95% window
scaling (150 ms open, 120 ms close), 180 ms moves/resizes, and 100 ms border
transitions. Noctalia surfaces receive blur and keep their own animations, following its
[compositor guidance](https://docs.noctalia.dev/noctalia/compositor-settings/hyprland/#blur). The profile deploys reviewed Noctalia preferences
and optional Hyprland palette loading. See [NOCTALIA.md](NOCTALIA.md) for the
application mapping, GUI override precedence, and remaining manual setup.

The `hyprland.start` hook runs `noctalia --daemon` once per session, following
[Noctalia's startup documentation](https://docs.noctalia.dev/noctalia/getting-started/running-the-shell/).
Config reload does not start another instance. Do not also enable a Noctalia
service or duplicate autostart entry. No old Quickshell startup command is used.

Bindings live in `conf.d/keybinds.lua`. Super is the Windows key:

| Shortcut | Action |
|---|---|
| Super+Shift+B | Brave Origin |
| Super+Shift+F | Nautilus |
| Super+Shift+O | OBS Studio |
| Super+Shift+P | 1Password |
| Super+Shift+A | ChatGPT |
| Super+Shift+Z | Zed |
| Super+Shift+R | Zeron |
| Super+Shift+T | T3 Code (nightly preferred when installed) |
| Super+Shift+V | VSCodium |
| Super+Shift+D | Discord through Vesktop |
| Super+Shift+G | Signal |
| Super+Shift+E | Fastmail Flatpak |
| Super+Escape | Noctalia Keybind Cheatsheet |
| Super+Ctrl+G | Git Companion |
| Super+Ctrl+D | Docker manager |
| Super+Ctrl+P | Portctl |
| Super+Ctrl+M | Screen mirroring |
| Super+Ctrl+N | Notes |
| Super+Ctrl+T | Translator |
| Super+Ctrl+S | SSH launcher |
| Super+Ctrl+C | Noctalia crash history and diagnostics |
| Super+Ctrl+L | Toggle Lid Guard (laptop only) |
| Super+Return | Ghostty |
| Super+W | Close focused window |
| Super+Q | Toggle tiled/floating |
| Super+R | Cycle column width presets |
| Super+C | Center column |
| Super+F | Toggle half/full column width |
| Super+Shift+Return | Toggle fullscreen |
| Super+L | Lock session |
| Alt+Tab | Open Noctalia window switcher |
| Super+Shift+S | Capture screen region |
| Print / Shift+Print | Capture region / current monitor |
| Volume / mute / microphone mute keys | Adjust audio through Noctalia |
| Brightness keys | Adjust display brightness through Noctalia |
| Super+Space | Noctalia launcher |
| Super+comma | Toggle Noctalia settings window |
| Super+Shift+W | Toggle Noctalia wallpaper browser |
| Super+arrows | Focus in that direction on this monitor |
| Super+Shift+arrows | Swap windows in that direction on this monitor |
| Super+Shift+Ctrl+arrows | Move window to the monitor in that direction |
| Super+1-9 / 0 | Select local workspace 1-9 / 10 on the current monitor |
| Super+Shift+1-9 / 0 | Move window to that local workspace and follow it |
| Super+Shift+L | Open Noctalia's session menu |
| Super+left/right mouse drag | Move/resize window |

OBS, 1Password, ChatGPT, Zeron, T3 Code, Vesktop, Signal, and Fastmail shortcuts focus
an existing window or launch the app when none is open. The Lua bindings select
the most recently focused matching window on its existing workspace. 1Password
uses native activation to distinguish its main window from Quick Access, which
keeps its separate Ctrl+Shift+Space shortcut. Other app shortcuts retain their
normal launch behavior.

The shared `game` tag in `conf.d/window-rules.lua` starts tagged windows in
fullscreen. Add class rules with `tag = "+game"` before that shared rule, using
the actual game class reported by `hyprctl clients`. No games are assigned yet;
Steam and other launchers retain their normal window behavior.

Directional focus and swaps stay on the same monitor through Hyprland's
[`window_direction_monitor_fallback` setting](https://wiki.hypr.land/Configuring/Basics/Variables/#binds).
Explicit monitor moves follow the window to the destination monitor's active
workspace. Workspace and monitor move shortcuts preserve a tiled scrolling
window's column width when the destination is empty. With another window there,
the moved window gets half width. Floating and fullscreen windows keep native
move behavior.
The Noctalia shortcuts use its [native IPC commands](https://docs.noctalia.dev/noctalia/compositor-settings/hyprland/#ipc-keybinds).
Volume and brightness repeat while held and work on the lock screen; mute
toggles work while locked without repeating. Noctalia's window switcher uses
Tab/Shift+Tab or arrows to select, Enter to activate, and Escape to cancel.
Its settings window floats and centers instead of joining the scrolling columns.

1Password matches the class `com.onepassword.OnePassword` and opens floating
in the center of the usable monitor area. It keeps its preferred width and
uses a height of 700 pixels, capped at 80% of the monitor height.
The reusable `centered-floating` tag in `conf.d/window-rules.lua` selects this
behavior. To include another app, add its matching rule with
`tag = "+centered-floating"` above the shared rule for that tag.

Input settings live in `conf.d/input.lua`: Danish keyboard layout, Num Lock,
fast key repeat, and focus following the pointer. The pointer moves to newly
opened foreground windows and follows workspace changes. Activation requests
can bring already-running apps forward. The touchpad uses natural
scrolling, tap to click, and finger-count clicks, and is disabled while typing.
Swipe up or down with three fingers to switch workspaces.
Swipe horizontally with three fingers to scroll through window columns.

`conf.d/workspaces.lua.tmpl` defines ten local slots per desktop monitor.
Only slots 1-5 are persistent. The number shortcuts select all ten slots,
creating 6-10 when needed; empty optional workspaces disappear after leaving.
Shift moves the focused window into the selected local slot and follows it.
Use the monitor shortcuts to cross displays.

On `Machine = "desktop"`, DP-4 and DP-3 have separate sets of unique global
IDs. The existing first-five IDs remain 1-5 and 6-10 respectively; optional
slots use 11-15 and 16-20. The shared workspace module resolves a local slot
on the currently focused monitor when the shortcut is pressed. This also
addresses slots that do not exist yet, which an open-workspace index cannot.
Default workspace names are local numbers, and Noctalia displays those names
instead of global IDs. Both bars therefore show 1-5 initially and include
their own optional workspaces as they are used. Clicks and shortcuts still
target unique IDs, so identical display names do not share a workspace.

Other machines keep five persistent workspaces and optional slots 6-10
without fixed monitor assignments. Workspaces inherit the global layout and
appearance.

Every binding has a native description for Noctalia's Hyprland Keymap.
Super+Escape opens the enabled [Keybind Cheatsheet plugin](https://noctalia.dev/plugins/community/keybind-cheatsheet)
without requiring a bar widget. The plugin reads Hyprland's live bindings;
after editing them, refresh its snapshot with
`noctalia msg plugin kenn/keybind-cheatsheet:data all refresh`.
Application bindings use `obs`, `chatgpt`, `zed`, `codium`, `vesktop`, and
`flatpak run com.fastmail.Fastmail`. Zed is not installed in the current VM;
its shortcut requires `zed` on PATH. Shell aliases are not used.
The compatible LibrePods fork starts through its headless user unit when the
command, service and Bluetooth adapter are available. Older builds are skipped.
Reloading the config does not launch another instance. Nimbus supplies the package. The
AirPods widget additionally needs a compatible LibrePods build, as
[NOCTALIA.md](NOCTALIA.md) records.

Super+Shift+L opens the menu; choose an action there. Save work before choosing
Logout. Super+V opens clipboard history; Super+Shift+N opens notifications.
Super+Ctrl+arrows focuses another monitor and moves the pointer.
Super+Shift+T prefers T3 Code Nightly and falls back to the stable command.
Noctalia locks after ten idle minutes and turns screens off after
fifteen, restoring them on activity. Idle inhibitors are respected; automatic
suspend is not configured. Extra scratchpad and wheel shortcuts are deferred. Noctalia's bar provides its
other controls. The launcher uses [Noctalia 5 IPC](https://docs.noctalia.dev/noctalia/ipc/surfaces/).

Before applying, back up any existing `hyprland.lua` and legacy `hyprland.conf`
and review explicit session `--config`/`HYPRLAND_CONFIG` overrides: those can
bypass the normal Lua file. Chezmoi does not delete an existing legacy config.
Apply only after the normal preview; Hyprland can live-reload changed files.
Log out and back in to test the startup hook. Keep a TTY or alternate session
available and restore the saved config there if necessary.

Back up existing Noctalia configuration privately before applying this profile.
Use the normal Chezmoi preview above. Noctalia watches its configuration and may
render themes immediately in an active session. Existing GUI overrides take
precedence: in Noctalia Settings, reset only the template selections you want
to return to the managed defaults. Do not remove the whole state directory.
Community templates need network access on first use. Open a new terminal after
rendering to load fzf colors. Application-specific prerequisites are listed in
[NOCTALIA.md](NOCTALIA.md).

```sh
python3 tests/noctalia.py
python3 tests/hyprland.py
just check
just check-desktop
```

The local tests check platform/profile gates, module loading, duplicate
shortcuts, descriptions, startup guards and generated-file ownership. They
do not pin gaps, rounding, animation timing, shortcut choices or session-menu
order. The Lua test double cannot validate Hyprland's complete native schema.
Run `just check-desktop` on the desktop or VM to validate both Hyprland and
Noctalia with their installed parsers; missing tools fail this gate instead
of skipping it. These parsers still cannot prove rendering, physical input,
application startup, locking or logout. Those need an interactive session.

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
until the Nimbus update flow has been tested on the installed system.

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

Two launchers are enabled on Nimbus-managed Linux machines:

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

On Linux, Chezmoi manages
`~/.local/share/flatpak/overrides/com.fastmail.Fastmail` with
`GTK_THEME=Adwaita:dark` in its `[Environment]` section. This keeps Fastmail's
native context menus dark when its startup theme detection falls back to light.
The override applies to every launch method, including mail links, without
changing permissions or other applications. It forces a dark native theme even
if the desktop switches to light mode. Fully quit and reopen Fastmail after
applying the override. No hook or launcher modification is required.

Unmodified 512x512 PNGs from the vendor sites are stored under
`home/dot_local/share/icons/hicolor/512x512/apps/`, using the unique
`nimbus-webapp-` icon prefix. Sources were checked on 2026-09-07: Maps and
FotMob publish these icons in their web manifests. These are third-party
brand assets, not original artwork
or a claim of an open-source license; their rights remain with their owners.
Icons are local, so apply and launcher display do not download them. No icon
theme, desktop settings, browser profiles, or wallpapers are changed.

The entries and icons retain their Linux and `ManagedByNimbus` gates.
The Nimbus gate applies only to these launchers and icons; unrelated `.local`
files remain available. No compositor profile is needed. Brave Origin requires
the Nimbus detection fix reported on 2026-09-10; that fix is not yet released
or installed in the VM, so live launch validation there remains pending.

After installing Nimbus with that fix, test each command on the desktop:

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

Offline checks validate native desktop syntax, the launcher command and URL
shape, referenced icons and actual platform gates in disposable homes. They
also verify that unrelated `.local` files remain available on Linux:

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

Standalone initialization asks whether to enable the integration, defaulting
to false. Nimbus supplies false during fresh initialization so there is no
extra prompt; its explicit `--onepassword-ssh` option enables the integration.
Existing stored choices survive ordinary reruns. The prompt itself requires
neither `op` nor an unlocked vault, but applying enabled targets does.
On Linux/macOS,
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
