# dotfiles

Cross-platform user configuration managed by Chezmoi. Linux is developed
first, with macOS and Windows target paths kept ready.

Chezmoi owns selected files below `~`. Nimbus owns packages, services, system
files, privileged changes, and the machine profile handoff. Machine manifests
live in `machines/` at the checkout root, outside the Chezmoi source state;
Chezmoi never deploys or edits them. Secrets and private keys never enter Git.

The repository is currently a safe scaffold. Empty configs remain ignored
until they are implemented and reviewed.

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
chezmoi edit ~/.config/zsh/.zshrc
```

Cross-platform configs have one canonical file below
`home/.chezmoitemplates/configs/`. Files in OS-specific target directories are
thin wrappers and should not contain duplicated config.

`home/.chezmoiignore` selects platform paths and keeps placeholder targets
unmanaged. When a config is implemented, remove its placeholder rule but keep
its platform rule.

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
