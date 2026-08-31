# dotfiles

Personal user configuration managed by Chezmoi. Linux comes first; macOS and
Windows remain supported targets.

## Ownership

- Chezmoi owns selected files below the user's home directory.
- Nimbus owns packages, services, system files, privileged work, and profile
  resolution.
- Chezmoi starts with a flat local profile list. Nimbus may later supply the
  resolved list on Linux; direct use remains supported everywhere.
- Secrets stay out of Git and may later be rendered from 1Password.

Chezmoi does not manage `/etc`, root's home, packages, services, or the login
shell.

## Layout

`.chezmoiroot` points to `home/`:

```text
.
|-- AGENTS.md
|-- CONFIG_INVENTORY.md
|-- PROFILES.md
|-- README.md
|-- ROADMAP.md
`-- home/               # Chezmoi source state
    |-- .chezmoi.toml.tmpl
    |-- .chezmoiignore.tmpl
    |-- .chezmoitemplates/ # canonical cross-platform config content
    |-- dot_*            # shared home entrypoints
    |-- dot_config/      # shared and Linux/Unix application config
    |-- dot_local/       # selected user assets
    |-- Library/         # macOS target paths
    |-- AppData/         # Windows application target paths
    `-- Documents/       # Windows PowerShell target path
```

Existing home files and Niriland are references only. Adopt one reviewed
configuration at a time. Empty scaffold targets stay in
`.chezmoiignore.tmpl` until their content is implemented and reviewed.

When one config has different target paths across operating systems, edit its
single canonical file below `.chezmoitemplates/configs/`. Target files are
thin wrappers only.

## Checks

```sh
chezmoi managed
chezmoi status
chezmoi diff
chezmoi verify
git diff --check
```

Do not run `chezmoi apply`, commit, or push without explicit permission.

See [ROADMAP.md](ROADMAP.md) for order, [PROFILES.md](PROFILES.md) for profiles,
and [CONFIG_INVENTORY.md](CONFIG_INVENTORY.md) for scope.
