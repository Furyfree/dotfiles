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

### Desktop setup audit, 2026-09-12

- [x] Hide the agreed 26 launcher entries, including mpv, through user desktop
  overrides, preserving commands, file types and actions. Keep DOSBox and
  Protontricks visible; DOSBox package removal is not authorized.
- [x] Apply the agreed MIME defaults, with Nautilus handling archives and
  Celluloid handling media. Retain application URL registrations. PDFs prefer
  Zathura's Poppler handler, with Brave as the fallback when it is absent.
  The owner installed the matching 2026.07.18 PDF plugin; native MIME queries
  now select Zathura. An isolated viewer loaded the plugin and opened a sample
  PDF using a private Broadway display, with no live document history changes.
- [x] Keep Super+1-9/0 and Super+Shift+1-9/0 for ten local workspace slots
  on each desktop monitor. Only the first five are persistent; optional slots
  are created when selected. Show names 1-5 on both bars while retaining
  unique IDs. Both labels were visually verified, and native selection of
  slots 6 and 10 creates nonpersistent workspaces on the correct monitor.
  Empty optional workspaces disappear after leaving; the other monitor stays
  unchanged. Existing windows were not moved.
- [x] Add Super+Ctrl+C for the Crashes panel, live and in the source keymap.
  Native IPC opens the expected panel without launching an agent.
- [x] Add Super+Shift+W to the live Hyprland keymap and its template. Native
  validation and reload pass; the wallpaper panel opens through Noctalia IPC.
- [x] Set the requested seven Files bookmarks and hidden-file preferences
  live. Prepare the same bookmarks and user GSettings hook for future applies.
  GTK 4 reports recent-file tracking disabled. Starred remains because
  Nautilus 50.3 has no supported hide setting.
- [x] Repair Fastmail discovery by changing the live server URL to `/dav/`.
  The existing unlocked keyring credential discovers all four calendars;
  the calendar panel displays an event. Credentials were not exported.
- [x] Separate automatic tool installation from first-login authorization in
  [the README](README.md#first-login-and-setup-ownership). Add reminders to the
  existing Nimbus handoff output; no sign-in commands run during apply.
- [x] Review Bash history at `~/.local/state/bash/history` and native package
  history without importing either. Recorded manual categories include GitHub
  CLI authentication, Tailscale setup, SSH server enablement, Mise setup and
  two native package installs. History is evidence of commands, not success.
- [x] Capture reviewed Hyprland gaps, animations, window rules, monitor focus,
  clipboard/notification/T3 shortcuts and the half/full-width move behavior.
  Keep the shared floating tag, monitor-local workspaces and laptop-only Lid
  Guard. Capture Ghostty close behavior, Zed project-window settings, Noctalia
  bar/panel preferences and desktop-only lockscreen geometry.
- [x] Capture the non-secret Fastmail account template, with its username in
  local Chezmoi data and the password still in the keyring. Add project
  checkout links, three wallpaper assets and custom directory creation.
- [x] Preserve ProtonPlus hourly/boot/launch update preferences through
  GSettings. Its own application initializes and owns the user timer.
- [x] Avoid the cheatsheet 0.2.7 explicit-path parser bug by scanning the
  bindings file directly; use numbered headings and named descriptions.
- [x] Keep the existing private 1Password directory and Zed settings modes;
  move the guarded Noctalia theme include to the root file its hook recognizes.
- [x] Preserve scrolling width when moving to an empty workspace; use half
  width when the destination is occupied. Native tests cover workspace and
  monitor moves, custom widths, no-op moves, floating and fullscreen windows.
- [ ] Complete package delivery and installation of ble.sh, the LibrePods
  fork and the prepared Copilot helper in the COPR/Nimbus repositories.
- [ ] Publish the captured configuration on main. The owner subsequently
  authorized commits and pushes, with no pull request or hosted review.
- [ ] Deliver the Nimbus 0.4.1 engine and handle the package-owned XDG defaults
  file's ownership migration. Normal Nimbus sync is blocked by the intentional
  dirty checkouts. No system state changed through that failed preflight.

The requested new Windows 11 VM is deferred by the owner's latest instruction.
Only the Dockur image was downloaded before the pause; no VM, container or
guest storage was created. OpenLogi is not selected for the attached G560
speakers because upstream does not list that hardware as supported.

Final validation: `just check` passes 137 tests with four optional skips, the
Bash suite and whitespace gate. `just check-desktop`, live Hyprland/Noctalia
validation and ShellCheck on both preference hooks pass. The full authorized
Chezmoi apply succeeded: all 29 Mise tools and 52 VSCodium extensions were
already installed. Managed/status/diff/verify ran against this desktop; status
and diff are empty and verify passes with scripts excluded. Scripts run after
every apply by design. No secret target contents were printed.

The cheatsheet now reports 80 bindings in eight categories, no unreadable-file
warnings and no Other rows. Native MIME queries match the selected applications,
custom XDG paths resolve correctly, Files shows hidden items, ProtonPlus keeps
its active hourly timer, and Fastmail metadata remains configured. Both GitHub
repositories were reachable through their SSH remotes. Gitleaks scanned both
repositories' tracked and nonignored untracked files with no findings. No
commit, push, package publication, system-file mutation or VM creation occurred.
Optional Lua execution, Niri, Neovim download and Zathura GUI checks remain
skipped; isolated PDF opening was verified earlier as recorded above.

The 2026-09-07 COPR VM installation completed, but source builds made the
first run slow. The Linux CLI tools now use upstream stable binaries through
native Mise Aqua and GitHub backends in `linux-tools.toml`. VM Curator uses
GitHub with a native `linux/x64` restriction because upstream has no ARM
binary. Typst stays on Terra, and cargo-update is not declared. No deployed
installation needs a provider migration, so there is no migration cleanup.
`.chezmoiremove` remains a comment-only placeholder for future migrations.
Nimbus's `docs/SECURITY.md` still describes obsolete-provider cleanup and
needs reconciliation there.

An isolated native installation downloaded Tinymist 0.15.6, Sheldon 0.8.5,
resvg 0.48.1, Caligula 0.5.0, and VM Curator 1.4.0; all five binaries answered
`--version`. This is tool validation on the workstation in temporary data
and configuration directories, not a completed clean VM installation drill.
The Nimbus handoff now supplies the disabled 1Password SSH answer for fresh
init; direct initialization and existing opt-ins remain supported. The Mise
hook can append its native output and timings to Nimbus's private per-run log,
with tests for failed installation, unsafe paths, failed logging, and retry.
The current local `just check` passes 121 tests with three optional skips, plus
the Bash suite and whitespace gate. The rendered hook passes ShellCheck.
Native Chezmoi managed/status/diff/verify ran against an empty temporary home;
verify correctly reports that its files have not been applied.
The integrated read-only Fable 5.1 review and primary validation finished
without outstanding findings. This follow-up is prepared for pull-request publication; the next clean VM
drill requires the reviewed Nimbus release and COPR build.

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
| VSCodium | #9 | Merged; installers and Marketplace override enabled locally; native Windows installer testing pending |
| 1Password SSH references | #11 | Merged; live authorization remains pending |
| Neovim | #12 | Merged; parsers and native platform testing remain pending |
| Webapps | #13 | Merged; launchers enabled locally; VM validation awaits the Nimbus release |
| Niri, DMS, and Topgrade | #14 | Merged; live session and update testing remain pending |

Plan: [shared applications](ROADMAP.md#phase-3---shared-applications).

- [x] Reconcile each branch with the merged docs, run its checks, and obtain
  separate authorization for publishing or merging it. Keep status current here.
- [x] Integrate the tooling branch's tests and native Mise ownership rules.
- [x] Enable the VSCodium extension hooks and Marketplace override as requested.
- [ ] Record authorized live testing per config and platform; retain pending
  status for untested systems instead of treating rendering as runtime proof.

## 1Password, SSH, and gh - remaining platform verification

Plan: [1Password, SSH, and GitHub CLI](ROADMAP.md#phase-4---1password-ssh-and-github-cli).
Status: the desktop's opt-in Linux configuration now renders from 1Password,
with private keys staying in the agent. Both repository remotes passed read-only
SSH access checks. Git identity and SSH signing settings are present; creating
or pushing a signed commit was not part of the final no-commit audit. macOS
live validation and Windows support remain deferred. See [setup and recovery](README.md#1password-ssh).

- [x] Explain the agent and map the existing keys to GitHub and homelab roles.
- [x] Design the private 1Password SSH-config document, agent selection, and
  Linux/macOS socket paths without exporting private keys.
- [x] Implement and test feature gating, permissions, missing prerequisites,
  and simulated retrieval failures without printing secrets.
- [x] Keep Git signing in the managed XDG template under the existing SSH
  option, using the GitHub public-key selector and Linux/macOS helper paths.
  Isolated checks cover disabled and legacy data, Windows exclusion, failed
  signing without an unsigned commit, and repair preserving personal identity.
  Actual commit signing and GitHub signature verification remain untested.
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
A minimal Hyprland starter and portable Noctalia preferences are prepared. See [starter usage](README.md#hyprland-starter).

- [x] Prepare a Hyprland 0.55+ Lua starter with Ghostty, Brave Origin, and
  Noctalia 5 daemon startup.
- [x] Compare live and Niriland configs; prepare modular Niri with native
  actions, one keybind source, and no Nirius dependency.
- [x] Curate DMS preferences against the current upstream settings format;
  keep generated colors and runtime state out of Chezmoi ownership.
- [x] Verify normal reboot and Hyprland/Noctalia login in the Fedora VM
  (2026-09-08, Noctalia 5.0.1). Recovery-session login remains untested.
- [x] Capture reviewed portable Noctalia preferences and app template selections
  from the VM; document ownership and prerequisites in [NOCTALIA.md](NOCTALIA.md).
- [x] Capture the VM's 17 enabled plugins as profile-scoped Noctalia config;
  retain plugin downloads, data and monitor-specific lockscreen state locally.
- [ ] Verify plugin downloads on a clean login and add wanted bar widgets;
  exercise plugins with their required tools and accounts.
- [x] Validate the captured config with Noctalia 5.0.1 and Hyprland 0.56.2
  in disposable VM directories; run isolated Chezmoi previews and `just check`.
- [ ] Test the newly captured profile on the VM: generation, light/dark changes,
  app reloads, and repeat Chezmoi previews without generated-color drift.
- [x] Verify secure first-login keyring initialization and password-login
  unlocking with Nimbus 0.2.0 (VM journal, 2026-09-08); no extra prompt.
- [x] Prepare GTK/Qt settings, session environment propagation, native Brave GTK
  theming; use Noctalia hooks and native app theme selection without custom
  configuration-rewriting scripts.
- [x] Run the follow-up complete local gate: 126 Python tests (three skips),
  Bash checks and diff checks; native VM Noctalia/Hyprland validators pass.
- [x] Apply the simplified desktop config to the VM with scoped backups;
  verify zero Chezmoi drift, disable Brave templates, and confirm Noctalia
  reloads with exactly 17 enabled plugins (2026-09-08).
- [x] Research native Noctalia capabilities and the 5.0.1 IPC differences;
  replace the logout helper with Noctalia's session menu and a direct,
  explicit-session logind command. Missing session IDs fail closed.
- [x] Describe every Hyprland binding and start LibrePods hidden once per
  session through the existing compositor startup hook.
- [ ] Resolve the AirPods plugin's patched-LibrePods requirement; the installed
  Terra 0.2.5 package lacks the published status interface.
- [x] Install the prepared system dependencies (`adw-gtk3-theme`, `qt5ct`)
  through the Nimbus candidate (2026-09-09). Its native Noctalia GTK hook
  selected `adw-gtk3-dark` and `prefer-dark`; the owner confirmed it works.
  Selected desktop managed/status/diff/verify checks passed without drift.
- [ ] Research native Hyprland session integration and UWSM in Nimbus. The
  owner deferred UWSM adoption and accepted plain Hyprland for this release;
  its graphical target and portal remain inactive.
- [ ] Verify toolkit colors and keyring dialog appearance after a fresh login
  with the follow-up config; test native logout/relogin,
  portal activation, dark/light changes and Brave with **Use GTK** selected.
- [ ] Complete app-specific setup in NOCTALIA.md, including VSCodium's theme
  extension and applications that require a profile, vault or skin first.
- [x] Enable only the maintained `niri-dms` user-config profile on Linux.
- [ ] Add Nimbus's Niri/DMS system profile and verify prerequisites before
  migration; this dotfiles branch does not provision the session.
- [ ] Test Niri input, monitor layout, shortcuts, generated colors, DMS panels,
  lock/idle/resume, and startup in an installed session. See
  [desktop setup and recovery](README.md#niri-and-dankmaterialshell).
- [ ] Test session controls and the recovery path on the installed system.

## Prepared - Webapps; backgrounds waiting

Plan: [webapps and backgrounds](ROADMAP.md#phase-7---webapps-and-backgrounds).
Status: Google Maps and FotMob launchers and icons are enabled on managed Linux.
The user reports Nimbus's Brave Origin detection fixed; the release and VM
installation are pending. Backgrounds are still undecided.
See [setup and validation](README.md#webapps).

- [x] Select the two webapps and vendor icons; prepare native desktop entries
  with Nimbus/platform gating and offline validation.
- [x] Remove the prepared Fastmail webapp in favor of Nimbus's stable Flatpak
  selection; installation and default mail handling still need a live test.
- [x] Enable the prepared entries on managed Linux after the user reported
  Nimbus's Brave Origin detection fixed.
- [ ] Validate launching in the VM after installing Nimbus with the fix.
- [ ] Choose backgrounds separately; do not import the old collection wholesale.
- [ ] Verify the resulting launcher and backgrounds in the installed desktop.

## Prepared - Topgrade; live updates waiting

Plan: [Topgrade](ROADMAP.md#phase-8---topgrade).
Status: unified update configuration is prepared for Linux/macOS. Only fake
updaters have run; no live update was performed.

- [x] Inventory update owners; use Mise for its runtimes and Cargo tools,
  with separate native steps for gh extensions, Sheldon plugins, and tldr data.
- [x] Validate the config and native commands in isolated homes with fake
  updaters; platform rendering covers Linux/macOS, Windows remains ignored.
- [x] Make Topgrade call Nimbus first on managed Linux and prove failure stops
  all user steps. Preserve standalone native system updaters and platform gates.
- [x] Prepare this configuration for the local, unreleased `nimbus upgrade`
  entry point. Nimbus's wrapper uses normal Topgrade configuration and keeps
  the system callback as `nimbus upgrade --system`, without syncing definitions.
- [x] Delegate Copilot application updates to its installed COPR helper, keeping
  native prompts and testing failure propagation without real updates.
- [ ] Add WoWUp updates after its COPR helper provides a standalone command.
- [ ] Deploy the matching Nimbus engine before applying this configuration.
- [ ] With explicit update permission, test a real run and document native
  failure recovery and selected Nimbus Snapper protection. Use TTY repair for
  a broken desktop. See [update ownership](README.md#topgrade).

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
