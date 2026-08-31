# Roadmap

This file owns dotfiles order and design. Nimbus architecture remains in:

- `~/git/docs/setup/dotfiles/README.md`
- `~/git/docs/setup/nimbus/README.md`
- `~/git/docs/setup/nimbus/home.md`
- `~/git/docs/setup/nimbus/plan.md`

## Rules

- Keep metadata at the repository root and Chezmoi source state in `home/`.
- Manage user files only. Nimbus owns packages and system state.
- Use a flat local profile list until Nimbus can supply one. Do not build a
  profile graph or resolver.
- Support direct Chezmoi use when Nimbus is absent.
- Rewrite one configuration at a time; never copy this machine or Niriland
  wholesale.
- Keep secrets and application state out of Git.
- Preview every slice before apply. Applying requires separate permission.

## Chezmoi style

Use the simplest source form that works:

1. Regular files for shared content.
2. Templates only for real content or path differences.
3. `.chezmoiignore.tmpl` when a target exists only on some profiles.
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

Chezmoi has no built-in profile system. Until Nimbus exists,
`home/.chezmoi.toml.tmpl` will create a flat `profiles` list in the local
Chezmoi config. [PROFILES.md](PROFILES.md) owns the names and constraints.
Nimbus can later replace the producer after both repositories reconcile them.

## Phase 0 - Foundation

Current state:

- `.chezmoiroot` points to `home/`.
- `.chezmoiversion` sets the minimum version.
- `home/.chezmoi.toml.tmpl` creates the local profile list.
- `home/.chezmoiignore.tmpl` selects the chosen desktop stack.
- Empty files reserve accepted config targets without copying live content.
- Empty config trees are ignored until their first slice is implemented; the
  broad rule is then narrowed around the files that remain empty.
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

- portable login environment
- interactive `.bashrc`
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
- `github-auth` and `homelab-user` are daily keys in 1Password.
- The same keys are available on trusted Windows, Linux, and macOS clients.
- Only public keys are installed on GitHub and homelab targets.
- A separate local, passphrase-protected `homelab-recovery` key is stored
  securely and not used daily.

Do not migrate or delete existing SSH keys during foundation work.

## Validation

Before every handoff:

```sh
chezmoi managed
chezmoi status
chezmoi diff
chezmoi verify
git diff --check
```

Use isolated destinations for bootstrap or template tests. Never overwrite the
active Chezmoi configuration during development.
