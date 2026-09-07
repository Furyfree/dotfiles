# Tasks

[ROADMAP.md](ROADMAP.md) owns order and design; this file owns actionable status
and evidence. Commands live in [README.md](README.md).

## Current phase - Desktop preparation and platform validation

Plan: [desktop preparation and platform validation](ROADMAP.md#current-phase---desktop-preparation-and-platform-validation).

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

The 2026-09-07 VM Cargo retry exposed missing system development headers and
the library-only `tinymist` crate. Nimbus now selects the build prerequisites;
the Cargo fragment selects the `tinymist-cli` binary package from upstream Git
release `v0.15.6`. The after-apply script emits marked setup notes before Mise,
so Nimbus can repeat them after a failed or successful init. Real completion
of the corrected VM tool installation was verified later the same day.

The next retry installed cargo-update, Sheldon, and VM Curator. Typst and
Tinymist hit Fedora's `/tmp` user quota during compilation. Nimbus now selects
Terra's Typst RPM, and this repository removes its duplicate Cargo declaration.
Tinymist's native Mise `install_env` uses `TMPDIR=/var/tmp` for installation
and upgrades. A native Mise probe with fake Cargo verified those options and
failure propagation without installing anything. The subsequent VM check found
all selected tools installed, including Tinymist, with no managed-file drift.
The owner has since restored the VM for the final COPR installation drill.

The owner published this repository on 2026-09-07 after Gitleaks found no
secrets in current files or reachable Git history. The MIT license branch is
published; the integration checkout includes its text and preserves upstream
Hyprland and third-party icon notices. The new Fedora 44 CI workflow runs
`just check` with native Chezmoi, Neovim, shell, Lua, and SSH test tools.
Native desktop/application checks remain conditional on tool availability;
GUI and live plugin-download checks remain opt-in. Hosted CI is still pending.

The exact Fedora container gate passes locally: 115 tests, with 25 optional
checks skipped, plus the Bash suite and whitespace check. Initial container
runs exposed missing PyYAML and ShellCheck test dependencies; both are now
installed by the workflow. An unnamed container UID also prevented native SSH
tests from running; the final check uses the same named root account as the CI
container, with all test homes still temporary. No workstation apply ran.

Snapshot: 2026-09-07. Foundation, Zsh, Sheldon, and Starship are merged, as are
the application PRs below. The passthrough starts from main `70bcece`, with
the existing uncommitted Hyprland Lua starter preserved.
Merged source and isolated checks do not establish live deployment.

| Scope | PR | Status |
| --- | --- | --- |
| Bash | #3 | Merged, including login PATH fix |
| Mise, Nix, udiskie, Zathura, gh, btop, shared tests | #4 | Merged, including Mise discovery fix |
| Ghostty | #5 | Merged, including GUI-first Noctalia selection |
| Fastfetch | #6 | Merged, including terminal-foreground logo fix |
| Git | #7 | Merged, including repository-context test fix |
| Zed | #8 | Merged, including exported Noctalia theme-name fix |
| VSCodium | #9 | Merged; installers and Marketplace override remain disabled |
| 1Password SSH references | #11 | Merged; live authorization remains pending |
| Neovim | #12 | Merged; parsers and native platform testing remain pending |
| Webapps | #13 | Merged; launchers remain disabled pending Nimbus helper testing |
| Niri, DMS, and Topgrade | #14 | Merged; live session and update testing remain pending |

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
Status: Niri and DMS are merged on main, without live application evidence.
A minimal Hyprland starter is also prepared; Noctalia
preferences remain GUI-managed. See [starter usage](README.md#hyprland-starter).

- [x] Prepare a Hyprland 0.55+ Lua starter with Ghostty, Brave Origin, and
  Noctalia 5 daemon startup.
- [x] Compare live and Niriland configs; prepare modular Niri with native
  actions, one keybind source, and no Nirius dependency.
- [x] Curate DMS preferences against the current upstream settings format;
  keep generated colors and runtime state out of Chezmoi ownership.
- [ ] Verify native Hyprland and Noctalia behavior in the installed VM before
  splitting shared and shell-specific files.
- [ ] Configure Noctalia through its GUI, then capture reviewed portable
  preferences and verify theme ownership without tracking generated state.
- [x] Enable only the maintained `niri-dms` user-config profile on Linux.
- [ ] Add Nimbus's Niri/DMS system profile and verify prerequisites before
  migration; this dotfiles branch does not provision the session.
- [ ] Test Niri input, monitor layout, shortcuts, generated colors, DMS panels,
  lock/idle/resume, and startup in an installed session. See
  [desktop setup and recovery](README.md#niri-and-dankmaterialshell).
- [ ] Test session controls and the recovery path on the installed system.

## Prepared - Webapps; backgrounds waiting

Plan: [webapps and backgrounds](ROADMAP.md#phase-7---webapps-and-backgrounds).
Status: Google Maps and FotMob launchers and icons are prepared but
ignored until Nimbus implements and tests its webapp helper. Backgrounds are
still undecided. See [setup and validation](README.md#webapps).

- [x] Select the two webapps and vendor icons; prepare native desktop entries
  with Nimbus/platform gating and offline validation.
- [x] Remove the prepared Fastmail webapp in favor of Nimbus's stable Flatpak
  selection; installation and default mail handling still need a live test.
- [ ] Test Nimbus's helper and enable the prepared entries on managed Linux.
- [ ] Choose backgrounds separately; do not import the old collection wholesale.
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

## Repository passthrough, 2026-09-07

- Preserved the local Hyprland Lua starter and reconciled the plan with merged
  main. Clarified standalone Niri selection and native Mise ownership.
- `just check`: 114 Python tests complete with three skips, plus the Bash suite and
  `git diff --check HEAD`. Hyprland is unavailable; Neovim's download test and
  Zathura's GUI test are opt-in. The separate
  `DOTFILES_NVIM_INTEGRATION=1 python3 tests/neovim.py
  Neovim.test_real_plugins_in_disposable_home` run passes.
- Isolated `chezmoi managed`, `status`, and `diff` pass. Full `verify` reports
  the deliberately pending tool-install script; `verify --exclude=scripts`
  passes for rendered files and permissions. No live apply was run.
- Nimbus now preserves the SSH prompt answer in refresh commands and refuses
  changed checkout trust during approval. Managed handoff profiles remain
  exactly the manifest selection. Source-only Gitleaks scans are clean.
- Two Claude Code Fable 5.1 audits completed. The final targeted peer pass
  hit the provider session limit; main-agent diff inspection and local gates
  cover the closing fixes, without a final peer verdict.

## Phase 5 integration validation, 2026-09-07

- Local history is consolidated on `integrate/phase5`, with main retained.
  All former local branch heads are reachable from the integration branch.
  Eight clean auxiliary worktrees were removed. Unfinished work in
  `~/git/dotfiles-ghostty` is preserved in detached state; it is not the
  accepted Noctalia configuration.
- The native Chezmoi handoff regression uses the real template, initial
  answers, refreshed machine/profile data, the SSH opt-in, and two applies
  with fake Mise in a disposable home. It verifies repair without installing
  tools or reading a vault. Real installation still requires the Fedora VM.
- The pending source and test edits remain uncommitted. Remote branches and
  repository visibility are unchanged.
- Validation: `just check` passes 115 Python tests with three skips plus the
  Bash suite. The focused native handoff test also passes.
