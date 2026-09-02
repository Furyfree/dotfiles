# Repository instructions

Before architecture or ownership changes, read:

- this repository's `README.md` and `PROFILES.md`
- the Nimbus repository's `docs/SPEC.md` for the handoff and ownership, and
  its `docs/SECURITY.md` for which tools Nimbus installs and which the user
  installs below `~/.local`

`~/git/docs` is history, not a source of truth. It records past decisions,
superseded plans, and previous implementations such as niriland.

Keep repository metadata at the root and Chezmoi source state in `home/`.
Manage only intentional files below the current user's `$HOME`.
Keep user-facing commands in `README.md`; planning documents should link to it
instead of duplicating usage instructions.

Nimbus owns packages and system state on Linux. It supplies `machine`,
`managed_by_nimbus`, and the machine profile IDs through `chezmoi init`
prompt flags; the config template consumes them with the `prompt*Once`
functions and derives platform profiles from `.chezmoi.os`. Do not add
imports, dependencies, aliases, another resolver, or a machine manifest.
`PROFILES.md` owns the vocabulary and documents which IDs change managed files.

This repository must work without Nimbus on Linux, macOS, and Windows. Gate a
target on `managed_by_nimbus` only when it calls Nimbus; Hyprland and Noctalia
are selected by profile, not by Nimbus.

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
system packages, use privilege elevation, change `/etc`, manage services, or
select a login shell. User-scope runtime installation through Mise is the one
accepted exception.

Do not use the HTML skill unless the user explicitly asks for it.

Before handoff, run `just check` and `just preview`. Do not run
`chezmoi apply`, commit, push, or create remote resources without explicit
permission.
