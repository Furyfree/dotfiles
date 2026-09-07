# Tasks

[ROADMAP.md](ROADMAP.md) owns order and design; this file owns actionable status
and evidence. Commands live in [README.md](README.md).

## Current phase - Branch integration

Plan: [reconcile the plan](ROADMAP.md#current-phase---reconcile-the-plan).

- [x] Create `docs/remaining-configs` from main without carrying config changes.
- [x] Separate branch implementation from merged source and live validation.
- [x] Record every requested remaining config, its dependency, and next action.
- [x] Check local links and the docs-only diff; run the available local gate
  and record its failures and limitations below.
- [x] Publish and merge the docs branch after separate authorization.
- [x] Reconcile the remaining Nimbus handoff branch with current ownership,
  preserving development helpers and future launcher notes.
- [x] Finish Ghostty's Noctalia theme selection while leaving Noctalia GUI
  settings and generated palettes unmanaged.

## Existing implementation

Snapshot: 2026-09-07. Foundation, Zsh, Sheldon, and Starship are merged, as are
the application PRs below. The integration starts from main `77457d9`.
Merged source and isolated checks do not establish live deployment.

| Scope | PR | Status |
| --- | --- | --- |
| Bash | #3 | Merged, including login PATH fix |
| Mise, Nix, udiskie, Zathura, gh, btop, shared tests | #4 | Merged, including Mise discovery fix |
| Ghostty | #5 | Merged baseline; GUI-first Noctalia selection completed in this integration |
| Fastfetch | #6 | Merged, including terminal-foreground logo fix |
| Git | #7 | Merged, including repository-context test fix |
| Zed | #8 | Merged, including exported Noctalia theme-name fix |
| VSCodium | #9 | Merged; installers and Marketplace override remain disabled |

Plan: [shared applications](ROADMAP.md#phase-3---shared-applications).

- [x] Reconcile each branch with the merged docs, run its checks, and obtain
  separate authorization for publishing or merging it. Keep status current here.
- [x] Integrate the tooling branch's tests and native Mise ownership rules;
  keep the VSCodium extension hooks and Marketplace override disabled.
- [ ] Record authorized live testing per config and platform; retain pending
  status for untested systems instead of treating rendering as runtime proof.

## Waiting for installation - 1Password, SSH, and gh

Plan: [1Password, SSH, and GitHub CLI](ROADMAP.md#phase-4---1password-ssh-and-github-cli).
Status: Linux/macOS SSH wiring is prepared behind the opt-in toggle. Offline
checks use fake data; the real document and keys have not been retrieved.
Live setup and testing wait for the new machine. Windows remains deferred;
gh is already merged. See [setup and recovery](README.md#1password-ssh).

- [x] Explain the agent and map the existing keys to GitHub and homelab roles.
- [x] Design the private 1Password SSH-config document, agent selection, and
  Linux/macOS socket paths without exporting private keys.
- [x] Implement and test feature gating, permissions, missing prerequisites,
  and simulated retrieval failures without printing secrets.
- [ ] On the new setup, confirm the document, enable app integrations, authorize
  destination public keys, and test real retrieval and SSH on Linux and macOS.
- [ ] Explain the existing gh config and its separate API login; verify GitHub
  and homelab access with the user before retiring any working setup.
- [ ] Review the separate recovery-key plan without generating or deleting
  keys implicitly. Record the private backup/recovery procedure in README.

## In progress - Neovim

Plan: [Neovim](ROADMAP.md#phase-5---neovim).
Status: baseline implemented on `config/neovim-foundation`, not applied.
Five feature plugins plus lazy.nvim; Windows and language tooling remain
deferred. See [usage and migration](README.md#neovim).

- [x] Build the small advanced-Vim baseline with explained settings and keys.
- [x] Split the loader, options, plugin manager, and individual plugin settings
  into Lua modules without changing the selected features or shortcuts.
- [x] Validate isolated Linux startup and basic editing, including missing
  Git/parsers, failed bootstrap, private undo, and pinned plugin startup.
- [ ] Supply the Tree-sitter CLI and test parser installation, interactive
  shortcuts, clipboard, and theme contrast on the new Linux setup.
- [ ] Verify native macOS operation separately; rendering is covered offline.
- [ ] Choose incremental IDE additions only after the baseline is understood.

## Prepared - Niri and DMS; desktop testing waiting

Plan: [Linux desktop](ROADMAP.md#phase-6---linux-desktop).
Status: Niri and DMS are prepared on `config/topgrade-niri-dms`, without
applying them. Hyprland and Noctalia remain separate future work.

- [ ] If requested, confirm the Hyprland version and build a minimal starter.
- [x] Compare live and Niriland configs; prepare modular Niri with native
  actions, one keybind source, and no Nirius dependency.
- [x] Curate DMS preferences against the current upstream settings format;
  keep generated colors and runtime state out of Chezmoi ownership.
- [ ] Test Hyprland with Noctalia before splitting shared and shell-specific files.
- [ ] Configure Noctalia through its GUI, then capture reviewed portable
  preferences and verify theme ownership without tracking generated state.
- [x] Enable only the maintained `niri-dms` user-config profile on Linux.
- [ ] Add Nimbus's Niri/DMS system profile and verify prerequisites before
  migration; this dotfiles branch does not provision the session.
- [ ] Test Niri input, monitor layout, shortcuts, generated colors, DMS panels,
  lock/idle/resume, and startup in an installed session. See
  [desktop setup and recovery](README.md#niri-and-dankmaterialshell).
- [ ] Test session controls and the recovery path on the installed system.

## Waiting - Webapp and background choices

Plan: [webapps and backgrounds](ROADMAP.md#phase-7---webapps-and-backgrounds).
Status: waiting on the user's selection, not necessarily installation.

- [ ] Review existing entries and assets; select webapps, icons, and backgrounds.
- [ ] Implement the selected set with duplicate and private-URL checks, correct
  Nimbus gating, and validation of launch paths and assets.
- [ ] Verify the resulting launcher and backgrounds in the installed desktop.

## Prepared - Topgrade; live updates waiting

Plan: [Topgrade](ROADMAP.md#phase-8---topgrade).
Status: user-scope configuration is prepared for Linux/macOS. No update was run.

- [x] Inventory update owners; use Mise for its runtimes and Cargo tools,
  with separate native steps for gh extensions, Sheldon plugins, and tldr data.
- [x] Validate the config and native commands in isolated homes with fake
  updaters; platform rendering covers Linux/macOS, Windows remains ignored.
- [ ] Implement and test Nimbus's system-update recovery and Topgrade handoff
  in Nimbus. Snapshots must precede/follow the system phase, not pretend to
  protect home-directory tools. See [update ownership](README.md#topgrade).
- [ ] With explicit update permission, test a real run and document native
  failure recovery; do not claim system snapshots protect user tools.

## Deferred - Platforms

Plan: [platform validation and Windows](ROADMAP.md#phase-9---platform-validation-and-windows).

- [ ] Verify shared macOS behavior on the MacBook as configurations are adopted.
- [ ] Resume Windows-specific work only when the user requests it; verify native
  paths and runtime behavior rather than relying on existing scaffold wrappers.

## Evidence and limitations

- Niri/DMS/Topgrade, 2026-09-07: the complete gate passes 108 Python tests
  (106 passed, opt-in Neovim download and Zathura GUI checks skipped), plus
  the Bash suite and whitespace checks. Native Niri 26.04 validates absent,
  valid, and invalid generated palettes. Topgrade 17.9.0 tests use fake
  updaters, including failure reporting and exclusion of automatic hook
  fragments with an explicit config. DMS's 59 selected top-level settings
  were checked against upstream 1.6.0; DMS itself was not started.
- All 50 local documentation links pass. Chezmoi managed/status/diff exit 0;
  verify exits 1 for unapplied differences, with the existing config-template
  warning. No live init, apply, compositor reload, authentication, system
  update, or snapshot creation occurred. Niri/DMS startup and locking,
  hardware behavior, and real updates remain installed-system checks.
- The handoff reconciliation keeps `Machine` / `ManagedByNimbus`, unknown
  profile passthrough, and every-apply Mise installation. It does not restore
  the old fixed profile validation, VM Curator profile gate, or obsolete
  development-only installer. Machine manifests remain solely in Nimbus.
- The old branch's Just helpers now invoke the complete Python and Bash gate;
  previews preserve `chezmoi verify` failures. Its Markdown configuration is
  retained for an optional style report, which still reports existing table
  formatting and line-length issues rather than blocking regression checks.
- The pending Ghostty changes were reconciled with the later GUI-first choice:
  theme selection and isolated tests are retained, but the old uncommitted
  `noctalia/templates.toml` is not deployed. The original worktree is preserved.
- The integration checks passed: 71 Python tests passed, one optional Zathura
  GUI test skipped, and the separate Bash suite passed. The seven Ghostty tests
  include profile/Nimbus combinations, native parsing, unchanged shortcuts,
  and palette changes using temporary generated-theme stand-ins.
- No real Noctalia rendering, GUI reload, extension/tool installation, live
  configuration apply, authentication, or native macOS/Windows testing occurred.
  Chezmoi previews still encounter unapplied differences and a local
  config-template warning; these do not establish a deployed working system.
- CodeRabbit's included quota was exhausted during this integration cycle.
  Earlier full local reviews and approved review fixes are recorded in the PRs.
  One full native local review of this integration found no actionable issues.
- All 39 local Markdown links and whitespace checks passed. Chezmoi managed,
  status, and diff exited 0; verify and the preview helper exited 1 for the
  known unapplied differences. No live config regeneration was performed.

Mark implementation and live verification separately. Commit, push, PR, merge,
installation, update, and apply require their own explicit authorization.
