# Tasks

[ROADMAP.md](ROADMAP.md) owns order and design; this file owns actionable status
and evidence. Commands live in [README.md](README.md).

## Current phase - Documentation

Plan: [reconcile the plan](ROADMAP.md#current-phase---reconcile-the-plan).

- [x] Create `docs/remaining-configs` from main without carrying config changes.
- [x] Separate branch implementation from merged source and live validation.
- [x] Record every requested remaining config, its dependency, and next action.
- [x] Check local links and the docs-only diff; run the available local gate
  and record its failures and limitations below.
- [ ] Publish and merge the docs branch after separate authorization.

## Existing implementation

Snapshot: 2026-09-07. Main and remote main were `3aa004f`; foundation, Zsh,
Sheldon, and Starship are merged. Their live deployment is not established by
this documentation check. The branch heads below are not merged into that
main; listing them does not assert PR readiness or successful live testing.

| Scope | Branch | Inspected head | Status |
|---|---|---|---|
| Bash | `config/bash-foundation` | `f71d8b6` | Implemented, unmerged |
| Mise, Nix, udiskie, Zathura, gh, btop, shared tests | `config/tooling-apps` | `cc8649a` | Implemented, unmerged |
| Ghostty | `config/ghostty` | `01bf52f` | Implemented, unmerged |
| Fastfetch | `config/fastfetch` | `3b393f2` | Implemented, unmerged |
| Git | `config/git` | `0daf1a3` | Implemented, unmerged |
| Zed | `config/zed` | `467b4a2` | Implemented, unmerged |
| VSCodium | `config/vscodium` | `cb68de9` | Implemented, unmerged |

Plan: [shared applications](ROADMAP.md#phase-3---shared-applications).

- [ ] Reconcile each branch with the merged docs, run its checks, and obtain
  separate authorization for publishing or merging it. Keep status current here.
- [ ] Integrate the tooling branch's tests and native Mise ownership rules;
  keep the VSCodium extension hooks and Marketplace override disabled.
- [ ] Record authorized live testing per config and platform; retain pending
  status for untested systems instead of treating rendering as runtime proof.

## Next - 1Password, SSH, and gh

Plan: [1Password, SSH, and GitHub CLI](ROADMAP.md#phase-4---1password-ssh-and-github-cli).
Status: not implemented for SSH; gh is already on the tooling branch. The user
reports two existing 1Password keys. Real authentication needs the signed-in
app, agent enablement, and an authorized destination.

- [ ] Explain the agent and map the existing keys to GitHub and homelab roles.
- [ ] Design the private 1Password SSH-config document, agent selection, and
  Linux/macOS socket paths without exporting private keys.
- [ ] Implement and test feature gating, permissions, missing prerequisites,
  and locked-vault handling without printing secrets.
- [ ] Explain the existing gh config and its separate API login; verify GitHub
  and homelab access with the user before retiring any working setup.
- [ ] Review the separate recovery-key plan without generating or deleting
  keys implicitly. Record the private backup/recovery procedure in README.

## Next - Neovim

Plan: [Neovim](ROADMAP.md#phase-5---neovim).
Status: not started; no dependency on the new desktop installation.

- [ ] Build the small advanced-Vim baseline with explained settings and keys.
- [ ] Validate isolated startup and basic editing, including optional tools
  being absent; record Linux and macOS evidence separately.
- [ ] Choose incremental IDE additions only after the baseline is understood.

## Waiting - Desktop installation

Plan: [Linux desktop](ROADMAP.md#phase-6---linux-desktop).
Status: full revamp waits for the installed system. The optional starter can
be prepared earlier, but remains unverified until run in a real session.

- [ ] If requested, confirm the Hyprland version and build a minimal starter.
- [ ] Compare existing Niri/DMS settings and agree common actions and shortcuts
  for Niri and Hyprland before implementing each native config.
- [ ] Test Hyprland with Noctalia before splitting shared and shell-specific files.
- [ ] Configure Noctalia through its GUI, then capture reviewed portable
  preferences and verify theme ownership without tracking generated state.
- [ ] Adopt and test Niri and DMS individually; enable their reserved profile
  gates only when the corresponding configurations are maintained.
- [ ] Test session controls and the recovery path on the installed system.

## Waiting - Webapp and background choices

Plan: [webapps and backgrounds](ROADMAP.md#phase-7---webapps-and-backgrounds).
Status: waiting on the user's selection, not necessarily installation.

- [ ] Review existing entries and assets; select webapps, icons, and backgrounds.
- [ ] Implement the selected set with duplicate and private-URL checks, correct
  Nimbus gating, and validation of launch paths and assets.
- [ ] Verify the resulting launcher and backgrounds in the installed desktop.

## Waiting - Topgrade

Plan: [Topgrade](ROADMAP.md#phase-8---topgrade).
Status: waits until the selected installed tools and desktop work.

- [ ] Inventory update owners and agree non-overlapping user-scope steps.
- [ ] Validate the config and preview for both Nimbus and standalone use.
- [ ] With explicit update permission, test a real run and document native
  failure recovery; do not claim system snapshots protect user tools.

## Deferred - Platforms

Plan: [platform validation and Windows](ROADMAP.md#phase-9---platform-validation-and-windows).

- [ ] Verify shared macOS behavior on the MacBook as configurations are adopted.
- [ ] Resume Windows-specific work only when the user requests it; verify native
  paths and runtime behavior rather than relying on existing scaffold wrappers.

## Evidence and limitations

- Branch inspection found a clean starting worktree; remote main matched the
  local base. This branch changes repository documentation only.
- The gh config on `config/tooling-apps` contains SSH preference, editor
  prompting, and the `co` alias for PR checkout. No login was performed.
- Main has no `tests/` tree although its old README referenced
  `tests/zsh-foundation.zsh`. The tooling branch contains the replacement
  Python runner and Zsh checks; integrating and running them remains pending.
- Local link/anchor and whitespace checks passed for all 25 local links in
  the four changed documents. `git diff --check` passed; no files below `home/`
  changed, and the only new file is this task list.
- `chezmoi managed`, `chezmoi status`, and `chezmoi diff` exited 0.
  `chezmoi verify` exited 1 with unapplied Zsh, Sheldon, and Starship
  differences present. Status, diff, and verify warned that the local config
  template has changed. No apply or live config regeneration was performed.
- App behavior, SSH authentication, desktop recovery, macOS, and Windows were
  not tested in this docs-only phase. Other worktrees were not modified.

Mark implementation and live verification separately. Commit, push, PR, merge,
installation, update, and apply require their own explicit authorization.
