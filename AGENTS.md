# Repository instructions

Before architecture or ownership changes, read:

- this repository's `README.md` and `PROFILES.md`
- the Nimbus repository's `docs/SPEC.md` and `docs/SECURITY.md` for ownership
  and software-source policy

`~/git/docs` is history, not a source of truth. It records past decisions,
superseded plans, and previous implementations such as niriland.

Keep repository metadata at the root and Chezmoi source state in `home/`.
Manage only intentional files below the current user's `$HOME`.
Keep user-facing commands in `README.md`; planning documents should link to it
instead of duplicating usage instructions.

Nimbus owns system packages and system state. Chezmoi owns native Mise tool
configuration, including Cargo tools, and invokes `mise install` after applying
it. Mise owns tool installation and updates.
Nimbus supplies the machine ID, the managed-by-Nimbus flag, and the machine
profile IDs through the `chezmoi init`
prompt flags; the config template consumes them with the `prompt*Once`
functions, stores the profile list as sent, and derives platform profiles from
`.chezmoi.os`. Do not add imports, dependencies, aliases, or another resolver.
`PROFILES.md` owns the vocabulary and documents which IDs change managed
files. Machine manifests live in the Nimbus repository, never here.

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

Chezmoi scripts must stay exceptional and user-scoped. The after-apply script
may install tools explicitly declared in the native Mise config. The optional
VSCodium after-apply scripts may install declared editor extensions through its
native CLI; keep them ignored until explicitly enabled. Scripts must not install
system packages or Mise itself, use privilege elevation, change `/etc`, manage
services, or select a login shell.

Do not use the HTML skill unless the user explicitly asks for it.

Before handoff, run `chezmoi managed`, `chezmoi status`, `chezmoi diff`,
`chezmoi verify`, and `git diff --check`. Do not run `chezmoi apply`, commit,
push, or create remote resources without explicit permission.
