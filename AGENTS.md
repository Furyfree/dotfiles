# Repository instructions

Before architecture or ownership changes, read:

- this repository's `README.md` and `PROFILES.md`
- the Nimbus repository's `SPEC.md` and `CLI.md`

`~/git/docs` is history, not a source of truth. It records past decisions,
superseded plans, and previous implementations such as niriland.

Keep repository metadata at the root and Chezmoi source state in `home/`.
Manage only intentional files below the current user's `$HOME`.
Keep user-facing commands in `README.md`; planning documents should link to it
instead of duplicating usage instructions.

Nimbus owns packages and system state. It supplies machine profile IDs through
`chezmoi init --promptMultichoice`; the config template consumes them with
`promptMultichoiceOnce` and derives platform profiles from `.chezmoi.os`. Do
not add imports, dependencies, aliases, or another resolver. `PROFILES.md`
owns the vocabulary and documents which IDs change managed files.

Nimbus owns the `machines/` manifests at the checkout root, outside the
Chezmoi source state. Chezmoi owns the surrounding checkout and all Git
operations and never deploys or edits those files.

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
