# Roadmap

This file owns dotfiles order and design. The active Nimbus contracts live in
the Nimbus repository's `SPEC.md` and `CLI.md`. `~/git/docs` is history, not a
source of truth.

## Rules

- Keep metadata at the repository root and Chezmoi source state in `home/`.
- Keep user-facing commands in `README.md`; planning documents should link to it.
- Manage user files only. Nimbus owns packages and system state.
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
- Bash and Zsh each define one namespaced `source_if_readable` helper for
  optional integrations and local files such as work overrides.
- Required tracked modules are sourced explicitly; a missing core module is a
  validation failure rather than a silent skip.
- Missing optional files are silent. Errors inside an existing file remain
  visible.

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
- No user configuration is managed yet.

The foundation is complete. Stop before adding or applying user configuration.

## Phase 1 - Zsh

Rewrite the current Zsh setup as the first bounded slice:

- minimal `~/.zshenv`, optionally setting `ZDOTDIR`
- login setup in `.zprofile`
- interactive setup in `.zshrc` and small modules below `~/.config/zsh`
- guarded Sheldon, Starship, fzf, zoxide, and completion integration
- no dependency on `/etc/zsh/zshenv`

Test syntax, login and interactive startup, and behavior when optional tools
are missing. Do not change the login shell or apply the files.

## Phase 2 - Bash

Build a native Bash setup instead of translating Zsh:

- small standard entrypoints in `~`
- portable login and interactive modules below `~/.config/bash`
- optional `ble.sh`, completion, Starship, fzf, and zoxide
- clean behavior on servers where optional tools are absent

Compare Bash and Zsh in daily use before choosing a default. Nimbus owns any
package installation or login-shell change.

## Phase 3 - Shared applications

Adopt one family at a time from [CONFIG_INVENTORY.md](CONFIG_INVENTORY.md).
Start with low-risk files such as Git, Starship, editor settings, or terminal
configuration.

Each slice must define:

- exact target files and platform paths
- excluded state and secrets
- the smallest necessary conditions or templates
- focused validation and a reviewed `chezmoi diff`
- a stop before apply

## Phase 4 - Platform files

- Verify macOS paths on the MacBook before adding native targets.
- Verify PowerShell's `$PROFILE.CurrentUserAllHosts` on Windows.
- Give Topgrade deliberate Linux, macOS, and Windows settings.
- Keep WSL separate from the Windows host.

Do not manage Homebrew, Winget, registry settings, LaunchAgents, services, or
other system state here.

## Phase 5 - Linux desktop

Start with `hyprland-noctalia`. Nimbus owns packages, services, portals,
greeters, and other system integration.

The machine profile selection gates only Hyprland and Noctalia. Other Linux
user configuration remains available without it.

Test the real setup before structuring `~/.config/hypr/`. Identify which files
are shared Hyprland config and which settings depend on Noctalia or DMS. Prefer
a shared base plus a small shell-specific include or template. Do not duplicate
the whole Hyprland tree or invent the split before the differences are known.

Keep monitor and host differences small. Pass only explicit, non-secret values
from Nimbus. Niri and DMS profiles remain disabled until their configs are
maintained as separate slices.

## Phase 6 - 1Password and SSH

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
- `github-auth` and `homelab-user` are daily keys in 1Password.
- The same keys are available on trusted Windows, Linux, and macOS clients.
- Only public keys are installed on GitHub and homelab targets.
- A separate local, passphrase-protected `homelab-recovery` key is stored
  securely and not used daily.

Do not migrate or delete existing SSH keys during foundation work.

## Validation

Use the checks in [README.md](README.md) before every handoff. Use isolated
destinations for bootstrap or template tests. Never overwrite the active
Chezmoi configuration during development.
