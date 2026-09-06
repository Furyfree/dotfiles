# Roadmap

This file owns dotfiles order, dependencies, and design. [TASKS.md](TASKS.md)
owns actionable checklists, branch status, and validation evidence. Commands
belong in [README.md](README.md). The active Nimbus contract, including its
command contract, lives in that repository's `docs/SPEC.md`. `~/git/docs` is
history, not a source of truth.

## Current phase - Reconcile the plan

Record the remaining configurations and distinguish implemented branch work
from merged code and live validation. This phase changes documentation only;
it does not enable ignored targets, install anything, or apply configurations.

Use `docs/remaining-configs`, based on `main`. Prefer merging this plan before
the pending configuration branches, then reconcile their documentation with it
as each branch lands. That order is organizational, not a runtime dependency.
Do not discard application guidance when resolving overlapping doc changes.

The phase ends when every requested area has a next action and dependency,
local links and the docs-only diff are checked, and validation limitations are
recorded in TASKS. Publishing and merging require separate permission. No live
recovery is needed because this phase does not change deployed files.

## Rules

- Keep metadata at the repository root and Chezmoi source state in `home/`.
- Keep user-facing commands in `README.md`; planning documents should link to it.
- Manage user files and install explicitly declared Mise tools after apply.
  Nimbus owns system packages and system state, including installing Mise.
  Mise owns its declared user tools and their updates, not a second package list.
- Nimbus supplies machine profile IDs through `chezmoi init
  --promptMultichoice`; the template consumes them and derives platform
  profiles from `.chezmoi.os`. Do not build a profile graph or resolver.
- Support direct Chezmoi use when Nimbus is absent.
- Rewrite one configuration at a time; never copy this machine or Niriland
  wholesale.
- Keep secrets and application state out of Git.
- Preview every slice before apply. Applying requires separate permission.

## Chezmoi style

Use the simplest source form that works:

1. Regular files for shared content.
2. Templates only for real content or path differences.
3. `.chezmoiignore` when a target exists only on some platforms or profiles.
4. Symlinks only when the target must be a symlink.
5. Scripts only for narrow user actions that file state cannot express.

Do not create profile overlay directories or merge them with custom code.
Chezmoi renders one target home.

For identical configuration at different platform paths, keep one canonical
file below `.chezmoitemplates/configs/` and use one-line target wrappers. Put
small OS conditions in the canonical template instead of duplicating config.

Linux is validated first. Chezmoi reports macOS as `darwin` and Windows as
`windows`. WSL is a separate Linux home. Platform facts may select paths or
syntax, but not roles or profiles.

## Profiles

Chezmoi has no built-in profile system. `home/.chezmoi.toml.tmpl` derives
platform profiles from `.chezmoi.os`, consumes Nimbus' machine profile
selection with `promptMultichoiceOnce` under the stable `Profiles` key, and
writes one resolved `profiles` list into the local Chezmoi config.
[PROFILES.md](PROFILES.md) owns the names and constraints.

## Shell loading

- Root entrypoints load their XDG entrypoint only when it is readable.
- When optional integrations or local overrides are added, use one namespaced
  `source_if_readable` helper per shell.
- Required tracked modules are sourced explicitly; a missing core module is a
  validation failure rather than a silent skip.
- Missing optional files are silent. Errors inside an existing file remain
  visible.
- Exception: source ble.sh at top level, not through a function, as its
  startup contract requires.

## Phase 0 - Foundation

Current state:

- `.chezmoiroot` points to `home/`.
- `.chezmoiversion` sets the minimum version.
- `home/.chezmoi.toml.tmpl` creates the local profile list.
- `home/.chezmoiignore` selects platform paths, optional features, and the
  selected machine profiles.
- Empty files reserve accepted config targets without copying live content.
- Empty config targets are listed explicitly in `.chezmoiignore`; remove only
  the matching placeholder rule when a config slice is implemented.
- `.keep` files reserve directories only and are never deployed.
- Repository rules, scope, and validation are documented.
- Zsh and its shared Sheldon and Starship configs are implemented in main;
  Phase 1 records the accepted design.

The repository foundation is implemented. Remaining work proceeds one config
at a time; merged source is not evidence of live application or testing.

## Phase 1 - Zsh

The implemented Zsh setup is the baseline for the other shell:

- minimal `~/.zshenv` setting the XDG defaults and `ZDOTDIR` (implemented)
- login PATH setup in `.zprofile` (implemented)
- `.zshrc` loads Mise, environment defaults, shell options, history,
  keybindings, functions, fzf, the prompt, the plugin loader, then aliases;
  Sheldon orders completion definitions, completion initialization, fzf-tab, zoxide,
  autosuggestions, and highlighting (implemented). The loader supplies standard
  completion and zoxide if Sheldon is absent or fails to generate its script.
- shared XDG history with 20,000 in-memory and 10,000 saved entries (implemented)
- one completion initialization with an XDG cache, security checks, menu
  selection, and case-insensitive fallback matching (implemented)
- Emacs-style editing with terminal-aware Home/End/Delete, word navigation,
  and word deletion before fzf and plugins; Backspace is preserved (implemented)
- guarded Sheldon integration with `zsh-completions` loaded before `compinit`
  and default `zsh-autosuggestions` and `zsh-syntax-highlighting` settings
  (implemented); other plugins remain deferred
- `fzf-tab` loads after `compinit` when `fzf` exists; otherwise the normal
  completion menu remains enabled (implemented)
- guarded fzf Ctrl-R history search, Ctrl-T path insertion, and Alt-C directory
  switching before line-editor plugins, shared by Linux and macOS
  with optional bat/batcat Ctrl-T previews and Ctrl-Y clipboard copying inside
  history search (implemented)
- guarded listing, editor, and utility aliases after initialization, plus
  clipboard copy/paste functions using macOS, Wayland, or X11 tools (implemented);
  Yazi directory switching, Git-root navigation, and path copying (implemented)
- guarded Mise activation in its own module (implemented)
- environment defaults preserving existing editor/pager choices and shared
  AUTOCD, NOBEEP, and NUMERIC_GLOB_SORT preferences (implemented)
- guarded zoxide integration with default `z` and `zi` commands; ordinary `cd`
  is unchanged and the directory database remains unmanaged (implemented)
- guarded Starship initialization before line-editor plugins and a shared
  basic prompt config with matching success/error arrows (implemented)
- no dependency on `/etc/zsh/zshenv`

History uses shared Linux/macOS settings. Existing history is not migrated;
see the backup and migration boundary in [README.md](README.md#history).

Test syntax, login and interactive startup, and behavior when optional tools
are missing. Do not change the login shell or apply the files.

## Phase 2 - Bash

Implemented with native Bash mechanisms preserving Zsh's user-facing workflow:

- small standard entrypoints in `~`
- portable login and interactive modules below `~/.config/bash`
- optional `ble.sh`, completion, Starship, fzf, and zoxide
- clean behavior on servers where optional tools are absent

Compare Bash and Zsh in daily use before choosing a default. Nimbus owns any
package installation or login-shell change.
See [README.md](README.md#bash) for differences and validation. Native macOS
and installed ble.sh interactive validation remain pending.

The implementation already exists on the branch tracked in TASKS. Integrate
and validate it rather than creating another Bash implementation.

## Phase 3 - Shared applications

Adopt one family at a time from [CONFIG_INVENTORY.md](CONFIG_INVENTORY.md).
Start with low-risk files such as Git, Starship, editor settings, or terminal
configuration.

Several slices are already implemented on separate branches; TASKS records
their heads and outstanding integration. Merge and test those deliberately,
including their tests and operator guidance. Reconcile the Mise installation
exception and the disabled VSCodium extension hooks with the repository rules
when their branches land; do not activate optional hooks as a merge side effect.

Each slice must define:

- exact target files and platform paths
- excluded state and secrets
- the smallest necessary conditions or templates
- focused validation and a reviewed `chezmoi diff`
- a stop before apply

Mise, Nix, udiskie, Zathura, GitHub CLI, and btop are implemented as one
application-config slice, independent of the Bash branch. User-supplied Mise
tools are retained with current LTS runtime selections and reviewed settings;
Nix remains a minimal user config. Linux desktop apps use Linux-only gates,
not a new machine profile. GitHub CLI shares canonical content across its
platform paths. btop uses terminal colors without saving runtime UI changes.

See [README.md](README.md#tooling-and-applications) for settings, sources,
validation, and recovery. Stop before installation, apply, commit, or PR.
Native macOS/Windows and real desktop key behavior remain manual checks.

The user-tool handoff now belongs to Chezmoi: one native after-apply script
invokes Mise after configuration on every full Linux/macOS apply, including
standalone use. It restores missing tools on repeat applies and propagates
installation failures for retry. Preview and dry-run do not install; system
packages, privilege, and installing Mise itself remain outside this script.
The isolated lifecycle checks use a synthetic source, temporary home, and fake
Mise, covering order, repair, failure/retry, prerequisite errors, and platform
rendering. Native downloads and macOS/Windows execution remain untested.

Fastfetch is implemented independently as one shared config with native OS
logo/detection, compact hardware/software groups, and no command or network
modules. The old Arch artwork remains unmanaged. See
[README.md](README.md#fastfetch) for preview, validation, and recovery. Stop
before apply; native macOS/Windows detection remains a manual check.

Git is implemented independently through its native XDG config and ignore
paths, with personal `~/.gitconfig` left unmanaged. Shared defaults keep native
colors and add fast-forward-only pulls, remote-tracking pruning, upstream
setup, conflict context, and two read-only aliases. See
[README.md](README.md#git) for loading, validation, and recovery. Stop before apply.

Ghostty is implemented independently: one Linux/macOS config, a static palette
based on the existing terminal colors, and native keybindings. Linux GTK and
macOS input differences stay in the template; Windows remains ignored. The
Niriland include and generated theme dependency are removed. Validation and
recovery are in [README.md](README.md#ghostty). Stop before applying; native
macOS input and visual behavior remain manual checks.

VSCodium settings/keybindings are implemented independently, matching the Zed
slice's core workflow while preserving notebook, debugger, and viewer extensions.
Noctalia integration is configured manually. Extension after-apply hooks are
prepared but ignored until explicitly enabled. See [README.md](README.md#vscodium)
for extension availability, installation, validation, and migration limitations.
Stop before apply and validate native input on each operating system.

Zed is implemented independently with canonical settings/keymap inputs and
platform wrappers. It keeps the VS Code base map, adds only a terminal toggle,
and uses a Noctalia-generated theme on the Linux desktop profile with bundled
themes elsewhere. See [README.md](README.md#zed) for behavior, validation,
and recovery. Noctalia integration is enabled manually in its GUI; no Noctalia
settings or templates are managed. Stop before apply; native input and theme
reload remain manual checks.

## Phase 4 - 1Password, SSH, and GitHub CLI

This is the next configuration slice after the documentation phase and relevant
branch integration. The user already has two SSH keys in 1Password; explain
the flow and map those existing items to their intended roles before adding
anything. The agent authenticates SSH requests without exporting private keys.
Enable it in the installed, signed-in desktop app, then connect the SSH client
to the platform-specific agent socket. Real authentication needs the app and
an authorized destination; templates can be prepared before the new system.

Design one secret-backed target before adding any:

- authentication and locked-vault behavior
- target permissions
- diff and checks that never print secrets
- removal and recovery

Planned SSH model:

- `~/.ssh/config` is a private 1Password document rendered by Chezmoi.
- One canonical `agent.toml` selects and orders the SSH keys exposed by the
  1Password agent. Thin wrappers target Linux, macOS, and Windows paths.
- Local data key `onePasswordSsh` gates both SSH targets. The init prompt
  records intent without requiring `op`; temporary vault locks do not change
  the managed set.
- Nimbus owns 1Password installation. Agent enablement stays in the app.
- `github-auth` and `homelab-user` are the planned daily roles; confirm the
  existing items instead of creating duplicate keys to match these names.
- The same keys are intended for trusted Linux and macOS clients; Windows
  implementation and live testing remain deferred.
- Only public keys are installed on GitHub and homelab targets.
- A separate local, passphrase-protected `homelab-recovery` key is stored
  securely and not used daily.

Keep the separate recovery-key plan, but do not generate, migrate, or delete
keys as an incidental setup step. Preserve working access until the replacement
has been tested. Disabling the feature stops management; it does not restore
an overwritten SSH config, so a private backup is required before apply.

GitHub CLI (`gh`) complements Git with pull requests, issues, and CI operations.
Its minimal SSH-preference config already exists on the tooling branch. Explain
and test that setup rather than rewriting it. GitHub API login is separate from
SSH authentication for Git; tokens and `hosts.yml` stay unmanaged.

Exit criteria: secret-safe template and permission checks pass, disabled and
locked-vault behavior is tested, and the user verifies the intended GitHub and
homelab authentication without losing existing access. Record platform checks
separately; Linux success does not prove macOS behavior.

## Phase 5 - Neovim

Build an understandable, advanced Vim rather than adopting an editor
distribution. It remains a secondary editor, not a replacement for Zed or
VSCodium. Begin with a small `init.lua`: editing defaults, search, splits,
clipboard behavior, persistent undo, and a few explained shortcuts that retain
Vim's normal modes and navigation.

Add diagnostics, language servers, completion, and other IDE features only in
subsequent small slices. Keep language-tool installation with its existing
owner and downloaded plugins or runtime state out of Git. Split Lua modules
when the content warrants it, not to imitate a distribution's directory tree.

This can start before the new system is installed. Validate isolated headless
startup and manual editing, including missing optional tools, on Linux first.
Keep OS-specific paths and commands explicit and verify macOS separately.
Back up any existing init before an authorized apply. The first slice is done
when basic editing is comfortable and the user understands its configuration.

## Phase 6 - Linux desktop

Start with `hyprland-noctalia`. Nimbus owns packages, services, portals,
greeters, and system and recovery-session integration. Chezmoi owns normal
user settings. Profile names and gates remain governed by PROFILES.

### Optional Hyprland starter

A small starter may precede full installation: terminal launch, close window,
focus, workspace movement, and session controls. Check the actual Hyprland
version and its native format before replacing the old scaffold; `hyprland.lua`
is a candidate, not an assumption about the installed version. Keep it one
readable file initially. It is not a substitute for Nimbus's recovery session.

### Installed desktop revamp

The full revamp waits for an installed, usable system. Compare the current
machine and Niriland references, define common shortcut actions for Hyprland
and Niri, then express them natively in each compositor. Preserve familiar
workflow where possible; document necessary differences rather than forcing
identical window-management semantics.

Test Hyprland before splitting its tree. Separate shared compositor settings
from Noctalia or DankMaterialShell (DMS) integration only where real differences
require it. Keep monitor and host overrides small and local; do not extend the
Nimbus handoff with hardware facts. Adopt Niri and DMS one config at a time,
leaving reserved profiles disabled until their files and gating are validated.

### Noctalia GUI first

Install Noctalia and choose settings in its GUI before adopting its files.
Then inspect the installed version's actual paths and capture only intentional,
portable preferences. Do not guess a schema now or import the entire state
directory. Generated application themes, caches, sessions, and downloaded
plugins stay unmanaged; theme integration must respect Noctalia's ownership.

Exit criteria: launch, focus, workspace, shell, theme, and session controls work
in each selected real session, and profile selection excludes the others.
Before apply, keep a known-good user-config backup and verify an independent
way to recover from a broken desktop. Template validation alone cannot close
these tasks.

## Phase 7 - Webapps and backgrounds

Selection is the dependency, not necessarily system installation. Review the
existing webapps, icons, and wallpapers with the user; choose a small everyday
launcher set and deliberate backgrounds before importing assets. Keep personal
URLs and unwanted duplicates out. Test final launcher visibility and wallpaper
selection after desktop installation.

Nimbus-dependent entries must be gated on its presence; standalone setups need
a supported native launch path or omission. Do not invent another launcher
framework. Validate desktop entries, referenced icons, paths, and asset sources.
Only selected user files become managed; removing an entry from management
does not delete its previously deployed copy without a separate decision.

## Phase 8 - Topgrade

Wait until the selected tools and desktop are installed and working. Inventory
their real update owners before choosing an explicit set of user-scope steps.
Avoid updating a tool through both Mise and another manager.

Align Nimbus use with its `docs/SPEC.md` allowlist contract: its Topgrade phase
excludes system, Flatpak, firmware, Nix, Chezmoi, Git-repository, and self-update
steps. Direct standalone use needs a separately reviewed safe configuration;
do not assume Nimbus's invocation flags protect it. No privilege escalation or
automatic repository pulls/apply should arise from these dotfiles.

Validate parsing and previewed commands before an explicitly authorized real
update. Completion requires a real run and understood failure/retry behavior;
a dry run does not prove the downstream updates succeed. User tools are outside
Nimbus's system recovery snapshots and must be repaired through their native
manager or reconstructed from declarations. Windows remains deferred.

## Phase 9 - Platform validation and Windows

Verify shared macOS paths and behavior on the MacBook as each slice is adopted;
native macOS-only additions wait for inspection. All new Windows work and live
validation are explicitly deferred, including PowerShell, SSH, Topgrade, and
Windows guest launcher integration. Preserve existing wrappers without treating
them as tested support. Verify PowerShell's native profile path when resumed.

Keep WSL separate from the Windows host. Do not manage Homebrew, Winget,
registry settings, LaunchAgents, services, or other system state here.

## Validation

Use the checks in [README.md](README.md) before every handoff. Use isolated
destinations for bootstrap or template tests. Never overwrite the active
Chezmoi configuration during development.
