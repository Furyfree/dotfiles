# Configuration inventory

Reviewed scope from the Linux laptop on 2026-08-31. This is migration input,
not permission to copy live files. Every selected config must be rewritten and
reviewed before Chezmoi manages it.

## Linux, macOS, and Windows

| Config | Plan |
| --- | --- |
| Git | Shared config with small platform or identity differences. |
| SSH client | Private `~/.ssh/config` from 1Password; see [ROADMAP.md](ROADMAP.md). |
| 1Password SSH agent | Selected-key filters only. Nimbus installs the app. |
| Neovim | Shared Lua config; isolate platform commands in Lua. |
| Zed | Settings and keymap only; no themes or backups. Check macOS keys. |
| VSCodium | Settings and keybindings only; no snippets or runtime state. |
| Starship | One prompt config for Zsh, Bash, and PowerShell. |
| Fastfetch | Shared config with OS-specific output or artwork where needed. |
| Topgrade | Review each OS config. Share only matching settings. |
| GitHub CLI | Add a config later. Never track `hosts.yml`. |

VSCodium uses Open VSX by default. Check required extensions there first. If
it is insufficient, VSCodium's `product.json` can point `extensionsGallery` at
Microsoft Marketplace. Check compatibility and Marketplace terms before using
that fallback. VSIX files remain another option.

## Linux and macOS

| Config | Plan |
| --- | --- |
| Zsh | Small home entrypoint and XDG modules; no `/etc/zsh/zshenv`. |
| Bash | Standard entrypoints load `~/.config/bash`; `ble.sh` optional. |
| Ghostty | Shared config with small platform differences. |
| Sheldon | Review as the Zsh plugin manager. |
| Mise | Review versions and machine-specific paths. |
| Nix | User config only. Nimbus installs Fedora's `nix` and its daemon. |
| btop | Deliberate config from chosen settings, not generated defaults. |
| Environment | Review each variable. Share only portable values. |

fzf and zoxide have no standalone config. Shell initialization may use them
when installed; never track zoxide's database. Cava and Lazydocker are out of
scope.

## Linux desktop

| Config | Plan |
| --- | --- |
| Hyprland | Split shared and shell-specific files only after testing. |
| Noctalia | Curated v5 `config.toml` only; no GUI state, caches, plugins. |
| Noctalia Greeter | Nimbus owns it and its system configuration. |
| udiskie | Manage its user config on the relevant workstation profile. |
| Zathura | Manage its user config on the relevant workstation profile. |
| VM Curator | On the `virtualization` profile, without machine paths. |
| Launchers and icons | Remove stale and duplicate web apps first. |
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
