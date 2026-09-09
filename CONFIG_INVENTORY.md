# Configuration inventory

Reviewed scope from the Linux laptop on 2026-08-31. This is migration input,
not permission to copy live files. Every selected config must be rewritten and
reviewed before Chezmoi manages it. Current implementation status and branch
evidence live in [TASKS.md](TASKS.md); this inventory describes scope only.

## Linux, macOS, and Windows

| Config | Plan |
|---|---|
| Git | Managed shared XDG config and OS-metadata ignores on all platforms. Personal `~/.gitconfig`, identity, credentials, and signing remain unmanaged. |
| SSH client | Render private `~/.ssh/config` from 1Password. Key design is in [ROADMAP.md](ROADMAP.md). |
| 1Password SSH agent | Track selected-key filters only. Nimbus owns installation; enable the agent in 1Password. |
| Neovim | Small advanced-Vim Lua setup first; incremental IDE features, not a distribution. Isolate platform commands in Lua. |
| Zed | Managed shared settings and one additive terminal keybind, with platform paths/modifiers. Noctalia theme on its Linux profile; bundled themes elsewhere. Generated themes, backups, and personal agent settings stay unmanaged. |
| VSCodium | Managed settings/keybindings match the Zed workflow, with native platform paths. Extension inventory and disabled after-apply installers are tracked; gallery overrides, snippets, and runtime state stay unmanaged. |
| Starship | Shared basic prompt config is managed; Bash and Zsh initialization are implemented, PowerShell initialization is deferred. |
| Fastfetch | Managed shared config: native OS logo, compact hardware/software groups, inherited terminal foreground; no commands or custom artwork. |
| Topgrade | Curated Linux/macOS user-scope updates; Mise owns its Cargo tools. System updates and pre/post recovery belong to Nimbus. Live update testing and Windows remain deferred. |
| GitHub CLI | Managed canonical config: SSH, editor prompts, and `co` alias; platform wrappers. Verify authentication separately. Never track `hosts.yml`. |

VSCodium uses Open VSX by default. Check required extensions there first. If
it is insufficient, VSCodium's `product.json` can point `extensionsGallery` at
Microsoft Marketplace. Check compatibility and Marketplace terms before using
that fallback. VSIX files remain another option.

## Linux and macOS

| Config | Plan |
|---|---|
| Zsh | Core startup, environment, options, tool integrations, and selected helpers are managed. Do not depend on `/etc/zsh/zshenv`; optional personal integrations remain deferred. |
| Bash | Implemented: standard entrypoints and explicit `~/.config/bash` modules mirror Zsh behavior with native Bash integrations and optional `ble.sh`. |
| Ghostty | Managed Linux/macOS config; Noctalia theme on the Linux desktop profile, charcoal-blue elsewhere; native keybindings. Enable Noctalia integration in its GUI. |
| Sheldon | Manages `zsh-completions`, `fzf-tab`, `zsh-autosuggestions`, and `zsh-syntax-highlighting`; review additional plugins individually. |
| Mise | Managed runtime/CLI selections and minimal settings; LTS where available. The after-apply script installs declared tools through Mise; installed artifacts, credentials, and trust state remain unmanaged. |
| Nix | Managed user feature flags only; installation and daemon state stay outside Chezmoi. |
| btop | Managed minimal terminal-palette config; no generated defaults, hardware paths, or persistent UI rewrites. |
| Environment | Review each variable. Share only portable values. |

fzf and zoxide have no standalone config. Shell initialization may use them
when installed; never track zoxide's database. Cava and Lazydocker configs are
out of scope. Zsh launcher aliases for Lazygit and Lazydocker are allowed;
their settings and runtime state remain unmanaged.

## Linux desktop

| Config | Plan |
|---|---|
| Hyprland | Minimal Lua starter on `hyprland-noctalia`: Ghostty, Brave Origin, Noctalia daemon startup. Test before splitting files or aligning the Niri keymap. Nimbus owns system integration. |
| Noctalia | Profile-managed portable preferences, 17 enabled plugin selections, native Brave GTK integration and Noctalia's session menu. Generated themes, runtime state, caches and downloaded plugins remain unmanaged. See NOCTALIA.md. |
| Noctalia Greeter | Nimbus owns it and its files below `/var/lib`. |
| Niri | Modular native config on `niri-dms`, with one keybind source and no Nirius; mirror module responsibilities in future Hyprland work. |
| DankMaterialShell | Curated portable settings on `niri-dms`; generated palettes, monitor state, caches, and plugins stay unmanaged. |
| udiskie | Managed Linux-only user config: automount, notifications, smart tray, default file manager. No profile gate or autostart. |
| Zathura | Managed Linux-only reading defaults, dark UI, and shortcuts. No profile gate or document state. |
| VM Curator | Manage after removing machine-specific paths. |
| Launchers and icons | Remove stale and duplicate web apps before adopting selected files. |
| Wallpapers | Manage selected user assets for the Linux desktop. |

GTK/Qt preferences are profile-managed. Noctalia owns its native theme hooks;
OBS, Prism, Vesktop, Heroic and Herdr retain their native configuration and
one-time theme selection. Test these and XDG portals after a fresh login. MIME defaults and further autostart
remain to review. Chezmoi owns user preferences; Nimbus owns packages, services
and greeter selection. UWSM adoption is deferred.

Niri and DankMaterialShell use the opt-in `niri-dms` profile in
[PROFILES.md](PROFILES.md). Their packages, greeters, and system session
integration still need Nimbus support. No generated service links are tracked.

## macOS and Windows

No native macOS-only file is selected yet. Inspect the MacBook before managing
paths below `~/Library` or macOS-specific Zsh setup.

Windows will get a PowerShell 7 profile. Verify
`$PROFILE.CurrentUserAllHosts` on Windows before choosing its target path.
Registry settings, Winget, Windows services, and WSL setup are outside this
inventory. WSL has its own Linux home and Chezmoi instance.

## Not selected

Do not adopt config for:

- Lazygit, Poetry, JGit, OpenCode, or other 1Password app settings
- Cava, Lazydocker, or Fish
- Octopi or CachyOS tools
- browser profiles, Signal, Obsidian vaults, ChatGPT, and other app-data trees
- OBS, Prism, Vesktop, Heroic and Herdr runtime settings

An installed application is not a reason to track its state.

## Never import

- private keys, `known_hosts`, GnuPG data, VPN config, or credentials
- histories, sessions, cookies, databases, caches, logs, or crash data
- generated enablement links, first-run files, backups, or downloaded plugins
- package caches, installed binaries, telemetry, or language registries
- whole `~/.config` or `~/.local/share` directories

The planned 1Password SSH keys are stored in 1Password, never in Git.

## References

- Current laptop and `~/git/niriland/`, inspected as references only
- [Topgrade](https://github.com/topgrade-rs/topgrade)
- [VSCodium extensions](https://github.com/VSCodium/vscodium/blob/master/docs/extensions.md)
- [1Password SSH agent](https://www.1password.dev/ssh/agent)
- [Chezmoi and 1Password](https://www.chezmoi.io/user-guide/password-managers/1password/)
- [Noctalia configuration](https://docs.noctalia.dev/noctalia/configuration/)
- [Noctalia Greeter](https://github.com/noctalia-dev/noctalia-greeter)
