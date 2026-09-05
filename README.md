# dotfiles

Cross-platform user configuration managed by Chezmoi. Linux is developed
first, with macOS and Windows target paths kept ready.

Chezmoi owns selected files below `~`. Nimbus owns packages, services, system
files, privileged changes, and the machine profile handoff: it performs the
first `chezmoi init` with the machine ID, a managed-by-Nimbus flag, and the
selected profiles, as [PROFILES.md](PROFILES.md) documents. Machine manifests
live in the Nimbus repository, not here. Secrets and private keys never enter
Git.

The repository currently manages Zsh setup, Sheldon, and Starship configuration.
Other empty configs remain ignored until they are implemented and reviewed.

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

### Environment and shell options

Interactive startup initializes Mise when installed, then loads environment
defaults and shell options. Mise manages its own tool versions, project trust,
and runtime state; this repository only adds `mise activate zsh`. Generation
errors remain visible and failed output is not evaluated. No tools are installed
by the dotfiles, and missing Mise is harmless.

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
remain unmanaged. Bash and PowerShell initialization are still deferred.

### History

Interactive Zsh shares history between terminals, keeps 20,000 entries in
memory, and saves up to 10,000 entries in `$XDG_STATE_HOME/zsh/history`
(normally `~/.local/state/zsh/history`). Duplicate commands are reduced and
commands prefixed with a space are omitted from saved history. A leading space
is a convenience, not a guarantee that sensitive input stays private.

The history directory is created with private permissions on first startup.
These settings are shared by Linux and macOS; the history itself is unmanaged.
Existing `~/.zsh_history` is left untouched and is not imported automatically.
Review a separate backup and migration before applying if you want to carry
over existing history. Back up the current startup files before applying too:
setting `ZDOTDIR` switches new shells away from the old home `.zshrc`.

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
[CONFIG_INVENTORY.md](CONFIG_INVENTORY.md) for migration scope, and
[ROADMAP.md](ROADMAP.md) for implementation order.
