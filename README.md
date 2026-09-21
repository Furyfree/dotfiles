# dotfiles

Personal user configuration managed with Chezmoi. Linux is the primary target;
macOS and Windows support varies by application. Nimbus installs system packages
and sessions; this repository manages selected files in your home directory.

## Initialize

Install Chezmoi and Git first. On Linux/macOS, install Mise before a full apply;
Nimbus supplies it on managed machines. Install applications through Nimbus or
your platform's package manager. Run Chezmoi as your normal user.

**Nimbus:** let Nimbus initialize the source and supply machine/profile choices.
Use its printed refresh command after changing the machine manifest.

**Standalone:** initialize without applying:

```sh
chezmoi init --prompt https://github.com/Furyfree/dotfiles.git
```

On an existing checkout, use `chezmoi init --prompt` to change saved choices.
Init does not apply files unless you add `--apply`.

## Profiles and machine choices

Chezmoi detects the operating system and adds `common`, plus `unix` and the
platform profile where applicable. Choose machine profiles on Linux:

| Profile | User configuration selected |
| --- | --- |
| `hyprland-noctalia` | Hyprland/UWSM, Noctalia, themes and preferences |
| `niri-dms` | Niri and DankMaterialShell |
| `development` | Zeron launcher and updater |
| `gaming` | ProtonPlus update preferences |

`common` supplies the baseline. The other offered Nimbus labels
(`virtualization`, `laptop-gaming`, `windows-vm`) add no profile-specific files
here yet. Profiles do not install desktop sessions or system packages.

For a standalone Hyprland desktop, choose `common`, `development` and
`hyprland-noctalia`; leave `ManagedByNimbus` false. On Nimbus machines, keep the
selection equal to the machine manifest. Nimbus's Niri system profile remains
pending; standalone `niri-dms` selection is available.

`Machine` defaults to the hostname. `desktop` and `laptop` select the owner's
monitor/hardware preferences; use another name unless those settings fit.
`work-laptop` changes the optional SSH identity selection; read the
[work-laptop setup][work-laptop] before enabling it. `ManagedByNimbus` enables
configuration that calls Nimbus and should be true only on a managed machine.

The 1Password SSH option defaults off. Complete [1Password setup][ssh] before
applying enabled targets. Selecting both desktop profiles keeps both sets of
files; it does not switch application themes when changing sessions.

## Preview and apply

Back up existing files before the first apply. Chezmoi replaces managed files;
only templates that preserve selected local values merge those values.

```sh
chezmoi managed
chezmoi status
chezmoi diff
chezmoi verify
```

Review secret-backed output locally; do not paste it into logs or reviews.
If 1Password is locked, use `chezmoi --skip-secrets diff` to inspect other files.
Verify exits nonzero for unapplied differences. Status marks always-run scripts
with `R`; inspect them with `chezmoi diff --exclude=none` before applying.

```sh
chezmoi apply
```

A full apply also runs scoped user hooks:

- Linux/macOS: install declared Mise tools. Missing Mise or a failed install
  stops apply; fix the error and rerun. Already written files remain.
- VSCodium: install missing declared extensions. Interactive prompts offer
  removal of extras; without a terminal, extras remain. Linux/macOS failures
  warn and can leave extensions missing; Windows install failures stop apply.
- Applicable Linux profiles: set selected Files/ProtonPlus preferences and
  refresh the user's application-icon cache.

Rerunning full apply repairs missing tools/extensions. Preview and dry-run do
not install them; applying individual files need not run the hooks. Apply does
not run Topgrade or install system packages. A failure can leave earlier files
updated, so review the next diff before retrying.

Finish account authorization and manual application setup using
[POSTINSTALLV2.md][postinstall]. For desktop changes, keep a working TTY or
alternate session and a private backup for recovery.

## Edit configuration

Edit a managed target through Chezmoi:

```sh
chezmoi edit ~/.config/zsh/.zprofile
chezmoi diff
chezmoi apply
```

Source files live under `home/`. Shared application templates are in
`home/.chezmoitemplates/configs/`; platform target files often include them.
Edit the canonical template for shared changes. `home/.chezmoiignore` controls
platform/profile selection. Avoid adding whole application-state directories.

Edit `VSCODIUM_EXTENSIONS.json` to select extensions: `install` requests
installation; `manual` retains an extension without installing it.
Mise tool declarations live in `home/dot_config/mise/`.

After changing the init template, refresh local configuration without applying
or reasking stored choices:

```sh
chezmoi init --apply=false
```

Use `chezmoi init --prompt` when you intend to change choices. On Nimbus machines,
use its refresh command so machine, profiles and the SSH choice stay aligned.
Removing a profile or ignoring a file stops management; it does not delete the
deployed file or restore its previous contents. Restore your backup to undo an
unwanted overwrite.

## Update

Pull changes without applying, then review and apply:

```sh
chezmoi update --apply=false
chezmoi diff
chezmoi apply
```

## Check changes

From the source checkout, run:

```sh
just check
```

This requires Python 3.14+, PyYAML, Ruff, Just and the native tools listed in
[the CI workflow](.github/workflows/check.yml). Use `JOBS=1 just check` for serial
execution. The isolated checks do not apply this repository to your live home.
Skipped tools and untested desktop behavior still need verification.

`just preview` runs the read-only Chezmoi commands above. On a Hyprland/Noctalia
machine, `just check-desktop` requires both native parsers. `just lint-docs`
runs the optional Markdown style check. Recipes are in [justfile](justfile).

## References

- [Post-installation and recovery][postinstall]
- [Keybindings](KEYBINDS.md); Super+Escape shows desktop shortcuts in Hyprland/Niri
- [Open tasks](TASKS.md)
- [Agent repository map](AGENTS.md)
- [MIT license](LICENSE)

[postinstall]: https://github.com/Furyfree/docs/blob/main/POSTINSTALLV2.md
[ssh]: https://github.com/Furyfree/docs/blob/main/POSTINSTALLV2.md#1password-ssh-and-github
[work-laptop]: https://github.com/Furyfree/docs/blob/main/POSTINSTALLV2.md#work-laptop
