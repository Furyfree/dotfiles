# Roadmap

This file owns dotfiles order, dependencies, and design. [TASKS.md](TASKS.md)
owns actionable checklists, branch status, and validation evidence. Commands
belong in [README.md](README.md). The active Nimbus contract, including its
command contract, lives in that repository's `docs/SPEC.md`. `~/git/docs` is
history, not a source of truth.

## Current phase - Desktop preparation and platform validation

Branch integration is complete. The 1Password SSH wiring, Neovim foundation,
Niri/DMS configuration, Topgrade, and prepared webapps are present on main.
The Hyprland Lua starter is local work awaiting desktop validation. TASKS
records source implementation separately from unperformed live testing.

The next work is to test the prepared configurations on the installed desktop
and validate the captured Noctalia profile integration on the VM. The 1Password handoff,
Neovim parser setup, and native macOS/Windows checks retain their own gates.
Installation and apply still require separate permission.

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

The application PRs are merged; TASKS records their integration and remaining
live checks. Their tests and operator guidance are retained, including the
Mise installation exception and the explicitly enabled VSCodium extension hooks.

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

Voxtype and VM Curator now have Linux-only native configs. Voxtype starts with
local multilingual Whisper settings; model download, activation, shortcuts, and
hardware trials remain pending. VM Curator manages portable new-guest defaults
and a home-relative library, leaving guest data and host setup outside Chezmoi.

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

Ghostty uses one Linux/macOS config and native keybindings. The Linux
`hyprland-noctalia` profile selects Noctalia's generated theme, with its built-in
integration enabled by the desktop profile. Other setups retain the static
charcoal-blue palette. No generated themes are managed; portable settings are captured.
Linux GTK and macOS input differences stay in the template; Windows remains
ignored. The Niriland include is removed. Validation and
recovery are in [README.md](README.md#ghostty). Stop before applying; native
macOS input and visual behavior remain manual checks.

VSCodium settings/keybindings are implemented independently, matching the Zed
slice's core workflow while preserving notebook, debugger, and viewer extensions.
Noctalia template selection is profile-managed. Extension after-apply hooks and
the Microsoft Marketplace override are enabled. See [README.md](README.md#vscodium)
for extension availability, installation, validation, and migration limitations.
Stop before apply and validate native input on each operating system.

Zed is implemented independently with canonical settings/keymap inputs and
platform wrappers. It keeps the VS Code base map, adds only a terminal toggle,
and uses a Noctalia-generated theme on the Linux desktop profile with bundled
themes elsewhere. See [README.md](README.md#zed) for behavior, validation,
and recovery. Noctalia integration is selected by the profile; generated palettes stay
unmanaged. Stop before apply; native input and theme
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

Prepared SSH model (live validation waits for installation):

- `~/.ssh/config` renders the private 1Password document, followed by shared
  GitHub key selection and the Linux/macOS agent socket setting.
- One canonical `agent.toml` selects and orders the SSH keys exposed by the
  1Password agent. Linux/macOS deploy the shared wrapper; Windows stays ignored.
- Public-key selector files use field-only UUID lookups through the native
  Chezmoi secret command; private keys are not exported. Desktop integration
  handles authorization without Chezmoi requesting CLI session tokens.
- Local data key `onePasswordSsh` gates the SSH directory, config, public-key
  files, and agent config on Linux/macOS. The init prompt
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
Its minimal SSH-preference config is already merged. Explain
and test that setup rather than rewriting it. GitHub API login is separate from
SSH authentication for Git; tokens and `hosts.yml` stay unmanaged.

Exit criteria: secret-safe template and permission checks pass, disabled and
locked-vault behavior is tested, and the user verifies the intended GitHub and
homelab authentication without losing existing access. Record platform checks
separately; Linux success does not prove macOS behavior.

## Phase 5 - Neovim

Build an understandable, advanced Vim rather than adopting an editor
distribution. It remains a secondary editor, not a replacement for Zed or
VSCodium. Keep `init.lua` as a small loader, with editing defaults, search, splits,
clipboard behavior, persistent undo, and a few explained shortcuts that retain
Vim's normal modes and navigation.

The baseline uses lazy.nvim with Snacks picker/explorer, which-key, Gitsigns,
nvim-surround, and nvim-treesitter. Keep eight navigation/Git mappings plus
standard surround commands. Use terminal-palette colors, a built-in statusline,
and explicit parser installation; no Noctalia settings or extra UI modules.
The shared Linux/macOS config targets Neovim 0.12+. Plugin revisions are
tracked in a lockfile, but downloaded plugins and parsers are not source files.
Usage, prerequisites, and migration are in [README](README.md#neovim).

Add diagnostics, language servers, completion, and other IDE features only in
subsequent small slices. Keep language-tool installation with its existing
owner and downloaded plugins or runtime state out of Git. Use `lua/config/`
for options and plugin management, and `lua/plugins/` for one specification
per plugin. Keep plugin shortcuts with their settings; add further modules
only when they have deliberate content.

This can start before the new system is installed. Validate isolated headless
startup and manual editing, including missing optional tools, on Linux first.
Keep OS-specific paths and commands explicit and verify macOS separately.
Back up any existing init before an authorized apply. The first slice is done
when basic editing is comfortable and the user understands its configuration.

## Phase 6 - Linux desktop

Nimbus's first system desktop remains `hyprland-noctalia`. Nimbus owns
packages, services, portals, greeters, and system integration. Chezmoi owns normal
user settings. Profile names and gates remain governed by PROFILES.

At the owner's request, the `niri-dms` user configuration is prepared
before installing the new system. It uses explicit native modules and curated
DMS settings, replacing the layered Niriland/DMS/override keymaps. Match module
responsibilities, common shortcuts, and scrolling preferences in Hyprland's
native configuration. Usage and validation checks live in
[README](README.md#niri-and-dankmaterialshell).

Retain the old handoff branch's launcher intent when this phase is implemented:
Nimbus-managed machines may use its browser/webapp helpers. Standalone machines
need a tested native alternative. The Windows guest launcher requires both
`windows-vm` and `ManagedByNimbus` and remains deferred with Windows work.
See [README.md](README.md#future-nimbus-launchers) for the native commands; do
not add launcher files until the corresponding installed workflows are tested.

### Optional Hyprland starter

A small Hyprland 0.56+ Lua starter is prepared: Ghostty, Brave Origin, Noctalia 5
daemon startup, and basic native window/workspace controls. The entry point
loads the populated modules from `conf.d/`; unused scaffolds remain ignored.
See [starter usage and validation](README.md#hyprland-starter). Repair broken
desktop configuration from a TTY; the full keymap revamp stays deferred.

### Installed desktop revamp

Live acceptance waits for an installed, usable system. Compare the current
machine and Niriland references, define common shortcut actions for Hyprland
and Niri, then express them natively in each compositor. Preserve familiar
workflow where possible; document necessary differences rather than forcing
identical window-management semantics.

Test Hyprland before splitting its tree. Separate shared compositor settings
from Noctalia or DankMaterialShell (DMS) integration only where real differences
require it. Keep monitor and host overrides small and local; do not extend the
Nimbus handoff with hardware facts. Adopt Niri and DMS one config at a time,
leaving reserved profiles disabled until their files and gating are validated.

### Noctalia profile integration

The Fedora VM passed normal reboot and Hyprland/Noctalia login on 2026-09-08.
Portable Noctalia 5.0.1 preferences and selected app integrations are captured;
[NOCTALIA.md](NOCTALIA.md) records output paths and remaining prerequisites.
Generated colors and GUI/runtime state remain Noctalia-owned.

The published installation now passes password-login keyring unlocking without
an extra prompt. The remaining work is toolkit/app adoption: profile-gated GTK
and Qt configuration, session environment propagation, native Brave GTK
theming, and native application theme selection. Chezmoi owns toolkit
preferences; Noctalia owns generated colors and live GTK appearance updates.
Do not copy Niriland's fixed dark-mode overrides or browser/agent runtime state.

Verify light/dark changes and first-login generation across GTK, Qt, Brave and
the selected apps. Explicit extension, skin and vault prerequisites remain in
NOCTALIA.md. Existing Noctalia GUI overrides must omit the old Brave community
hook. Keyring password changes and passwordless login need separate tests.

Exit criteria: launch, focus, workspace, shell, theme, and session controls work
in each selected real session, and profile selection excludes the others.
Before apply, keep a known-good user-config backup and verify an independent
way to recover from a broken desktop. Template validation alone cannot close
these tasks.

## Phase 7 - Webapps and backgrounds

The selected initial webapps are Google Maps and FotMob. Their
desktop entries and local vendor icons are enabled on Nimbus-managed Linux.
The user reports Brave Origin detection fixed in Nimbus; VM launch validation
awaits its release and installation. Fastmail uses Nimbus's stable
Flatpak selection instead of a webapp. Background selection remains
separate. See [README](README.md#webapps) for sources and activation checks.

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

The user-scope config can be prepared now; real update testing waits until the
selected tools and desktop are installed and working. Use Mise for its declared
runtimes and tools (including its Cargo backend), plus native gh-extension,
Sheldon-plugin, and tldr-data steps. Avoid updating a tool through both Mise and
another manager. See [README](README.md#topgrade) for the exact scope.

Topgrade coordinates the update run. Managed Linux calls Nimbus first through
one pre-command; its failure stops user updates. Standalone Linux selects
native system/Flatpak steps and macOS selects Homebrew. User-tool steps retain
the explicit allowlist and Topgrade self-update remains disabled. Native fake-
updater tests must prove order, dry-run, failure propagation, and platform gates.

Upstream Topgrade 17.9 combines CLI and config `only` lists, and normal
discovery can load extra hook fragments. Use the explicit managed config when
testing the allowlist; extra local fragments and explicit CLI additions are
user customizations.

The local, unreleased `nimbus upgrade` command delegates to Topgrade. Its
`nimbus upgrade --system` callback upgrades DNF and system Flatpaks without
syncing definitions or invoking Topgrade again. Deploy the matching Nimbus
engine with this config. Configuration owns the selected steps and options.
Copilot updates use its installed COPR helper with native prompts. WoWUp waits
for its helper's standalone update command. Nimbus handles selected Snapper
protection inside its system callback; no duplicate Topgrade hooks are needed.
TTY repair replaces the separate Nimbus recovery session.

Validate parsing and previewed commands before an explicitly authorized real
update. Completion requires a real run and understood failure/retry behavior;
a dry run does not prove the downstream updates succeed. Repair tools through
their native manager or reconstruct them from declarations. Windows remains
deferred.

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
