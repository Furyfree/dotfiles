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
| Zed | Manage settings and keymap only. Exclude themes and backups. Verify macOS modifiers. |
| VSCodium | Managed settings/keybindings match the Zed workflow, with native platform paths. Extension inventory and disabled after-apply installers are tracked; gallery overrides, snippets, and runtime state stay unmanaged. |
| Starship | Shared basic prompt config is managed; Bash and Zsh initialization are implemented, PowerShell initialization is deferred. |
| Fastfetch | Managed shared config: native OS logo, compact hardware/software groups, inherited terminal foreground; no commands or custom artwork. |
| Topgrade | Wait for the installed setup; review user-scope update ownership and each OS config. Windows remains deferred. |
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
| Ghostty | Managed Linux/macOS config and static charcoal-blue palette; native keybindings, small platform-specific input/UI settings. |
| Sheldon | Manages `zsh-completions`, `fzf-tab`, `zsh-autosuggestions`, and `zsh-syntax-highlighting`; review additional plugins individually. |
| Mise | Managed runtime/CLI selections and minimal settings; LTS where available. No installs, credentials, or trust state. |
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
| Hyprland | Test with Noctalia before splitting shared and shell-specific files below `~/.config/hypr/`. Nimbus owns system integration. |
| Noctalia | Configure through the GUI after installation, then capture reviewed portable preferences from the actual version's files. Exclude generated themes, runtime state, caches, and downloaded plugins. |
| Noctalia Greeter | Nimbus owns it and its files below `/var/lib`. |
| udiskie | Managed Linux-only user config: automount, notifications, smart tray, default file manager. No profile gate or autostart. |
| Zathura | Managed Linux-only reading defaults, dark UI, and shortcuts. No profile gate or document state. |
| VM Curator | Manage after removing machine-specific paths. |
| Launchers and icons | Remove stale and duplicate web apps before adopting selected files. |
| Wallpapers | Manage selected user assets for the Linux desktop. |

Review GTK, Qt, XDG portals, MIME defaults, autostart, and user systemd units
after Hyprland and Noctalia are tested. User preferences may belong to
Chezmoi; packages, services, enablement, and system defaults belong to Nimbus.

Niri and DankMaterialShell configs remain deferred migration references. Their
profile names are reserved but disabled in [PROFILES.md](PROFILES.md). Do not
track their files, greeters, or generated service links yet.

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
- browsers, Signal, Obsidian, ChatGPT, Vesktop, and other app-data trees

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
