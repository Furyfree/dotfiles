# Repository instructions

Before architecture or ownership changes, read:

- `~/git/docs/setup/dotfiles/README.md`
- `~/git/docs/setup/nimbus/README.md`
- `~/git/docs/setup/nimbus/home.md`
- `~/git/docs/setup/nimbus/plan.md`

Keep repository metadata at the root and Chezmoi source state in `home/`.
Manage only intentional files below the current user's `$HOME`.

Nimbus owns packages and system state. Until its profile handoff exists,
Chezmoi may use a flat local profile list. Do not add imports, dependencies,
aliases, or another resolver. `PROFILES.md` owns the local vocabulary. When
Nimbus takes over, consume its IDs unchanged.

Treat the current machine and Niriland as references. Rewrite and review one
configuration at a time; never import either wholesale.

Keep empty scaffold trees ignored until their files have deliberate, validated
content. `.keep` files reserve Git directories but must not make target
directories managed.

For one config rendered to different OS paths, keep canonical content in
`.chezmoitemplates/configs/` and make target files one-line wrappers.

Never commit secrets, private keys, sessions, history, caches, logs, or runtime
databases. Design 1Password rendering before adding secret-backed targets, and
never print their contents during validation.

Chezmoi scripts must stay exceptional and user-scoped. They must not install
packages, use privilege elevation, change `/etc`, manage services, or select a
login shell.

Do not use the HTML skill unless the user explicitly asks for it.

Before handoff, run `chezmoi managed`, `chezmoi status`, `chezmoi diff`,
`chezmoi verify`, and `git diff --check`. Do not run `chezmoi apply`, commit,
push, or create remote resources without explicit permission.
