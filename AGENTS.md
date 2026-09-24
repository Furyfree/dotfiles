# dotfiles

Chezmoi source for user configuration; Nimbus owns workstation provisioning.
Read README.md and Nimbus's `docs/SPEC.md` before changing ownership.

## Map

- `README.md`: repository usage, profiles, apply/update and verification.
- `TASKS.md`: open work and unverified live checks only.
- `KEYBINDS.md`: Neovim, Zed/VSCodium and Zathura shortcut guide.
- `~/Projects/docs/POSTINSTALL.md`: manual desktop setup and
  troubleshooting.
- `home/`: Chezmoi source state; repository metadata stays at the root.
- `home/.chezmoi.toml.tmpl`: consume `Machine`, `ManagedByNimbus` and profile
  prompts with `prompt*Once`; preserve ordered Nimbus IDs and derive platform
  profiles. Use Nimbus vocabulary; do not add hardware roles, aliases or dependencies.
- `home/.chezmoiignore`: platform/profile gates and empty scaffolds; `.keep`
  reserves directories without deploying them.
- `home/.chezmoitemplates/configs/`: canonical content for platform wrappers.
- `home/dot_config/hypr/` and `home/dot_config/uwsm/`: compositor modules and
  session environment. Match window classes from `hyprctl clients`, not titles;
  place class tags before shared rules.
- `home/Projects/dtu-bachelor/dot_obsidian/`: per-machine vault settings; the
  vault's Git owns plugins and plugin lists. Write JSON as Obsidian does
  (2-space indent, no final newline); `modify_workspace.json` resets sidebars only.
- `home/dot_local/share/flatpak/overrides/`: Flatpak environment; Obsidian's
  reaches Mise shims and the real Git config.
- `home/run_after_*`: scoped user hooks for Mise, VSCodium extensions, Files,
  ProtonPlus preferences and the GTK icon cache. Keep their scope narrow.
- `tests/`, `ruff.toml`, `justfile`: isolated checks and Python 3.14+ lint gate.

## Boundaries

- Manage intentional user files only. Nimbus owns system packages, services,
  greeters, machine manifests, setup guidance and private diagnostic records.
  Native tools own generated services and downloaded artifacts.
- Chezmoi owns Mise/Topgrade settings; Mise installs and updates its declared
  tools. Applying dotfiles does not run Topgrade or install Mise itself.
- Chezmoi owns agent CLI permission keys and selected proxy configuration.
  ai-workflow owns agent instructions and skills; accounts and sessions stay local.
- Noctalia owns generated colors, downloads and GUI state. Nimbus may perform
  its approved lockscreen-override repair with a private backup; do not add an
  after-apply state reset. The native greeter owns sync authorization.
- Keep secrets, private keys, known hosts, VPN/GnuPG data, accounts, history,
  caches, logs, downloaded plugins and runtime databases unmanaged. Design
  1Password rendering and secret-safe checks before adding secret-backed targets.
- Do not adopt Lazygit, Poetry, JGit, Cava, Lazydocker, Fish, Octopi/CachyOS
  settings or whole app-data trees. Native theme hooks retain generated outputs.
- Use plain files first, templates for real differences, native ignore gates,
  and one-line wrappers around shared content. No profile graph, overlay system,
  custom resolver, blanket reference imports or speculative scaffolding.
- Required shell modules must fail visibly when missing; optional integrations
  may be absent. Source ble.sh at top level, not through a helper function.
- This repo is not in production. Do not add migrations or cleanup of old
  providers, compatibility layers or `.chezmoiremove` entries unless requested.
  Preserve existing user files on failure.
- Hooks must not install system packages, elevate privileges, write `/etc`,
  select a login shell, or manage services. Do not change live state during tests.
- Use the HTML skill only when the user asks for it.

## Verify

Run `just check`, `chezmoi managed`, `chezmoi status`, `chezmoi diff`,
`chezmoi verify`, and `git diff --check`; never print secret-backed output.
`JOBS=1` runs suites serially. Skips and unapplied differences are not passes.
Do not apply, commit, push, or create remote resources without explicit permission.
