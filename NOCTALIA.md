# Noctalia profile integration

The Fedora 44 VM completed installation in 7m56s, then booted kernel 7.1.13
and logged into Hyprland/Noctalia successfully on 2026-09-08. Nimbus owns the
system installation evidence and remaining Phase 6 gates. This document owns
the user configuration captured from Noctalia 5.0.1 and its app-theme mapping.
The published 0.2.0 installation and password login also passed. The follow-up
toolkit and application selectors below still need a fresh-login visual trial.

## Configuration and ownership

The VM's GUI choices live in `~/.local/state/noctalia/settings.toml`, not a
legacy `settings.json`. The portable theme source, tonal-spot scheme, bundled
wallpaper, selected integrations and enabled plugins are now in
`home/dot_config/noctalia/config.toml`, enabled only on Linux with the canonical
`hyprland-noctalia` profile. No monitor-specific lockscreen placement,
`Virtual-1`, usage counts, last-wallpaper state, migration marker, downloaded
catalog, agent state, keyring or other private data was copied.

Noctalia reads `~/.config/noctalia/*.toml`, then applies GUI overrides from its
state directory. Existing overrides therefore still win. Reset individual
settings through the GUI when returning to the curated defaults; do not delete
all state. A normal Chezmoi apply does not erase GUI experiments. Selecting both
desktop profiles does not switch application themes with the active compositor.
Disabling the profile stops management but does not remove deployed files.

Chezmoi owns portable preferences and fixed application selections/includes.
Noctalia owns rendered colors, community downloads and its native reload hooks.
No theme generation runs during Chezmoi preview or tool installation. Apps
without a native activation hook use a one-time theme choice in their own
settings; Chezmoi does not rewrite their runtime configuration. Community
hooks execute as the logged-in user when Noctalia generates a palette; enabling
a template is therefore more than downloading passive colors.

The screenshot's Starship, Fastfetch and Neovim catalog toggles are deliberately
omitted from the managed list. These applications already inherit the terminal
ANSI palette, which themed Ghostty supplies. The Starship/Fastfetch hooks would
rewrite Chezmoi-owned files with generated RGB values; Neovim's hook would add a
second theme plugin. Terminal inheritance preserves their existing behavior and
avoids competing writers or another dependency. Existing GUI template overrides
must also omit those three to use this ownership model.

## Native capabilities checked

Use Noctalia's supported configuration before adding scripts:

| Capability | Native mechanism and our boundary |
|---|---|
| Session controls | The existing session panel owns lock, logout, lock-and-suspend, reboot and shutdown. A row can override its command; Super+M opens this panel. |
| Idle and locking | Native idle actions lock after ten minutes and turn screens off after fifteen, respecting inhibitors. No automatic suspend or second idle daemon is configured. |
| Plugins | Declarative enabled IDs select plugins; Noctalia fetches and updates built-in sources. Bar widgets require placement separately. |
| App themes | Built-in/community templates render colors and run their own hooks. GTK's shipped hook imports CSS and changes live appearance; apps without activation hooks need native selection once. |
| Authentication UI | Noctalia provides an optional polkit agent. This is distinct from GNOME Keyring and PAM login unlocking; do not start competing polkit agents. |
| Greeter appearance | Native greeter sync exists with its installed helper and privilege requirements. User dotfiles do not write greetd or enable privileged sync automatically. |
| Configuration | Hand-written TOML supplies defaults; GUI overrides remain in Noctalia state. Keep caches, credentials and monitor-specific experiments out of Chezmoi. |

These are supported capabilities, not a claim that every feature is enabled or
tested here. The installed version is 5.0.1. Its tagged session runner and IPC
implementation were inspected because online documentation tracks newer code;
the logout IPC difference is recorded below. The existing template manifests
also confirm that OBS, Prism, Heroic and Discord/Vesktop only write theme files.

## Enabled plugins

On 2026-09-08 the VM had 17 enabled plugins, each with a materialized native
manifest. The exact IDs and order are captured in `[plugins].enabled` in
`home/dot_config/noctalia/config.toml`. This includes AI Usage Bar and Git
Companion; it does not enable the remaining planned plugins automatically.

Noctalia owns fetching and activating these plugins from its built-in official
and community sources. Chezmoi manages the selection, not downloaded code,
plugin data, credentials or source caches. Source and update settings retain
Noctalia's defaults. The VM has no custom plugin settings or bar placements in
its GUI overrides to capture. Plugin widgets still need placement through the
bar editor when wanted; enabling a plugin does not add its widget to a bar.

The existing VM's `[plugins].enabled` GUI override matches the captured list.
Future GUI changes continue to override the managed selection. The VM-specific
`Virtual-1` lockscreen layout remains local. Plugin functionality and first-run
downloads on a clean machine still need a live test; enabled state and config
validation alone do not verify external tools or accounts.

## LibrePods and keymap

Hyprland starts `librepods --hide` once on its startup event when the command
is available and `/sys/class/bluetooth/hci*` contains an adapter. Launch LibrePods
manually if an adapter is connected after login. The startup guards are tested locally;
its next-login behavior still needs verification. Do not also enable
LibrePods' own autostart setting; use one startup owner. Reloading Hyprland
only reloads the bindings, not the startup event. Every binding
has a native `description`, including mouse actions and generated workspace
bindings, for Noctalia's keymap display.

The installed Terra package is `librepods-0.2.5-1.fc44`; its regular background
application is not the patched daemon required by `harveywuk/airpods`.
The plugin's installed README requires `harveywuk/librepods`, a status JSON
file and additional control verbs. Running the existing binary does not prove
plugin compatibility. Resolve that package/source difference through Nimbus
before claiming AirPods battery and listening controls work. Chezmoi does not
build or replace system packages. No Bluetooth device data is imported.

The earlier starter's VM apply passed native Hyprland validation, Chezmoi apply/verify and empty
status/diff. After reload, `hyprctl -j binds` reports descriptions for all 35
bindings and no config errors. LibrePods was started through Hyprland and is
running with `--hide`; the expected plugin status file is still absent.
The installed controller lists only the four noise-mode commands, confirming
the interface mismatch. An initial `--help` probe started the GUI application
instead of printing help; that exact probe process was stopped before the
normal hidden start. Source/target backups are under
`~/.local/state/nimbus/noctalia-keymap.mnp5ebk8/`. The complete local gate passed
with 126 tests and the same three optional/native skips.

## Selected applications

Paths below are relative to `~` unless they start with `/`. They were inspected
in the installed 5.0.1 built-in catalog and the VM's downloaded community
catalog. Template generation does not install applications or their extensions.

| Application / template | Generated output and activation |
|---|---|
| Btop / `btop` | `.config/btop/themes/noctalia.theme`; managed config selects `noctalia`; upstream signals running Btop. |
| GTK 3 / `gtk3` | `.config/gtk-3.0/noctalia.css`; native hook adds `gtk.css` import and updates desktop appearance. |
| GTK 4 / `gtk4` | `.config/gtk-4.0/noctalia.css`; same native hook. Check dialog and Flatpak behavior live. |
| Ghostty / `ghostty` | `.config/ghostty/themes/noctalia`; existing managed theme selection, native reload hook. |
| Hyprland / `hyprland` | `.config/hypr/noctalia.lua`; managed starter loads it when available. |
| KDE / `kcolorscheme` | `.local/share/color-schemes/noctalia.colors`; native KDE color-scheme action. |
| Qt / `qt` | `.config/qt5ct/colors/noctalia.conf` and `.config/qt6ct/colors/noctalia.conf`; managed qt5ct/qt6ct configuration selects these palettes with Fusion. |
| Starship | Uses Ghostty's ANSI colors; no generated Starship configuration. |
| Fastfetch | Uses Ghostty's ANSI colors; no generated RGB merge into managed JSON. |
| Neovim | Existing `vim` colorscheme with `termguicolors=false` follows Ghostty; no base16 plugin. |
| Bat / `bat` | `.config/bat/themes/noctalia.tmTheme`; hook selects it and rebuilds Bat's cache. |
| fzf / `fzf` | `.config/fzf/themes/noctalia.sh` and `noctalia.fish`; managed Bash/Zsh profile modules source the shell file when present. Fish remains unmanaged. |
| Herdr / `herdr` | `.config/herdr/noctalia-colors.toml`; native hook updates custom colors and requests reload. Herdr must have initialized its own config first; choose its terminal theme fallback natively when needed. |
| Lazygit / `lazygit` | `.config/lazygit/themes/noctalia.yml`; native hook merges colors into its otherwise unmanaged config. |
| Brave Origin / GTK | Select **Use GTK** in Brave Appearance settings to consume the native GTK theme supplied by Noctalia. No browser-specific template or extension. |
| Claude Code / `claude-code` | `.claude/themes/noctalia.json`; generated theme only, select it in the application. No authentication or agent settings imported. |
| Codex / `codex` | `.codex/themes/noctalia.tmTheme`; generated theme only, select it in the application. No agent configuration is managed. |
| OpenCode / `opencode` | `.config/opencode/themes/matugen.json`; select `matugen` in the application. |
| Vesktop / `discord` | `.config/vesktop/themes/noctalia.theme.css`; enable this stylesheet once in Vesktop/Vencord theme settings; Noctalia owns subsequent file updates. |
| LibreOffice / `libreoffice` | `.local/state/noctalia/libreoffice-theme-staging/Theme_Colors.xcu`; native hook installs/activates user theme data while LibreOffice is closed; regenerate with it closed if skipped, then reopen. |
| Obsidian / `obsidian` | Native hook searches below HOME for vaults, limited to four directory levels; open/create vaults first and verify snippet activation, including Flatpak/external vaults. Vault contents are never copied. |
| VSCodium / `vscode` | `.vscode-oss/extensions/noctalia.noctaliatheme-0.0.5-universal/themes/NoctaliaTheme-color-theme.json`; install the declared theme extension first. Managed settings already select `NoctaliaTheme`. |
| Zed / `zed` | `.config/zed/themes/noctalia.json`; managed settings select `Noctalia Light` / `Noctalia Dark`. Restart if needed. |
| Heroic / `heroiclauncher` | `.config/heroic/themes/matugen.css`; launch Heroic once, set its custom theme directory to this themes folder, and select matugen.css in Heroic. Regenerate after first launch. Catalog also supports Flatpak. |
| Prism Launcher / `prismlauncher` | `.local/share/PrismLauncher/themes/Matugen/theme.json`; select Matugen in Prism Launcher theme settings once. |
| Steam / `steam` | `.steam/steam/steamui/skins/Material-Theme/css/main/colors/matugen.css`; requires a compatible Material-Theme skin installation. This change does not install a Steam modification. |
| OBS / `obs` | `.config/obs-studio/themes/matugen.obt`; select the generated Matugen theme in OBS Appearance settings once; enable automatic theme reload there if available. |
| Zathura / `zathura` | `.config/zathura/noctaliarc`; managed config includes it after fallback colors. Restart/reload to check generation. |
| Hyprtoolkit / `hyprtoolkit` | `.config/hypr/hyprtoolkit.conf`; verify native toolkit applications consume it. |
| Papirus / `papirus-icons` | Community template cache `colors-final`; native hook updates folder colors. Requires the icon theme/helper and a live visual check. |

Built-ins reside in `/usr/share/noctalia/assets/templates/builtin.toml` with
adjacent input files and hooks. Community manifests reside below
`~/.local/state/noctalia/community-templates/<id>/template.toml`; these are
upstream-managed downloads, not vendored repository files. Catalog contents can
change independently, particularly extension-version paths and app hooks.

## Toolkit defaults and session environment

The profile supplies GTK 3/4 `settings.ini` and qt5ct/qt6ct configuration.
GTK3 has an `adw-gtk3-dark` first-start fallback. Noctalia's existing GTK hook
sets the live theme and GNOME `color-scheme` when colors change. GTK4 has no
forced GTK3 theme, and neither file pins `gtk-application-prefer-dark-theme`.
Noctalia owns CSS imports and generated palettes, so a Chezmoi rerun does not
undo a light/dark switch. Nimbus supplies Fedora's `adw-gtk3-theme` and both
Qt configuration plugins. Standalone users must supply those packages.

Hyprland retains the inherited PATH, using a standard system fallback when it
is empty. It adds missing `~/.local/bin` and Mise shim paths for GUI-launched
apps, respecting `MISE_DATA_DIR` and `XDG_DATA_HOME`. It does not source shell
profiles. GTK and Qt prefer Wayland with X11 fallback; cursors use Nimbus's
Bibata Modern Ice theme at size 24, and
`EDITOR`/`VISUAL` default to Neovim while preserving inherited choices.
Optional renderer, hardware, and reference-specific environment settings are
commented out in `environment.lua`.
`QT_QPA_PLATFORMTHEME=qt5ct` selects Qt5's plugin; Qt6ct explicitly accepts this
compatibility name too. Both configs use Noctalia's generated palette and Fusion.
Hyprland natively exports the display, desktop, toolkit and PATH variables
to D-Bus/systemd activation before signalling readiness. The earlier plain
Hyprland session left `graphical-session.target` inactive, blocking Fedora's
portal service. On 2026-09-10 the VM was running through UWSM, with the graphical
session target and both the portal frontend and Hyprland backend active.
No custom session manager or duplicate environment-import hook is added.
The change needs a fresh session; Chezmoi does not change the running desktop.
Super+M opens Noctalia's own session panel. Its Logout row calls logind's
`loginctl terminate-session "${XDG_SESSION_ID:?No graphical login session}"`.
This targets the login inherited by Noctalia, not all sessions of the user;
missing or empty session IDs fail without invoking loginctl. UWSM documents
this as a supported shutdown path and binds its units to the login lifetime.
It also worked with the VM's earlier plain Hyprland login. The separate logout
script and compositor-exit fallback have been removed. Other menu rows retain
the native actions. GUI row overrides still take precedence.

Noctalia 5.0.1's `session logout` IPC creates a built-in action and bypasses
row command overrides; current online docs describe newer behavior. Use the
session panel for this version, not a direct logout IPC shortcut. Actual
UWSM teardown remains deferred; the owner tested plain logout/relogin.

The native-menu correction was applied to the VM and reloaded successfully.
Both source and deployed copies of the old helper were removed after exact
content checks, with backups under
`~/.local/state/nimbus/noctalia-native-session.c4gj29d2/`. Chezmoi verify and
empty status/diff, native Noctalia/Hyprland validators and live Hyprland
config-error checks passed. Noctalia's inherited session ID was verified to
identify the owner's local graphical login without terminating it. Super+M
is registered as a Lua binding; Hyprland IPC exposes its Lua callback ID,
so its command is verified by the isolated Lua test rather than an IPC string
comparison. The native session-panel toggle was accepted; actual logout was
left for the user to test.

## Brave GTK theme

In Brave **Settings > Appearance**, select **Use GTK**. Brave then consumes
GTK appearance through the same toolkit integration as other GTK applications.
Chezmoi supplies the profile-scoped GTK defaults; Noctalia generates the theme
and updates live GTK appearance. Browser preferences remain browser-owned.
Verify Brave's dark/light rendering after a fresh login and theme switch.

The `brave-origin` community template stays disabled. Existing Noctalia GUI
overrides must also omit that ID so its browser-preference hook does not run.
No custom Chromium theme, extension or developer-mode setup is needed.

## Keyring and remaining checks

On 2026-09-08 the published VM installation booted kernel 7.1.13, started greetd,
and logged into Hyprland/Noctalia. The installed `gnome-keyring-pam` created the
login keyring; the journal reports it started and unlocked successfully, with
no additional keyring prompt. No keyring data was read or copied. Autologin,
fingerprint-only login and password changes still need separate tests.

Dialog colors, GTK/Qt application rendering, portal appearance reporting and
Flatpak theming need a fresh-login visual trial with these toolkit defaults.
App-specific skins, vaults and extensions in the table remain prerequisites;
there is no generic safe configuration that installs or activates all of them.

The follow-up passes the complete local `just check`: 126 Python tests
(three optional/native checks skipped) and Bash foundation checks. Isolated
Chezmoi managed/status/diff/verify cover profile exclusion and generated-color
ownership. Custom application-config rewriting scripts were removed in favor
of Noctalia hooks and native one-time theme selections. Native Noctalia
5.0.1 and Hyprland 0.56.2 config validation also passed in disposable VM
directories. The Hyprland checks covered a missing PATH environment and
asserted that the generated sibling module was discoverable and exported
`apply_theme`.
The simplified follow-up was applied to seven desktop targets on the VM on
2026-09-08, with scoped source/target backups under
`~/.local/state/nimbus/noctalia-apply.NB7EoROR/`. Chezmoi apply/verify passed
and subsequent status/diff were empty. Native config validation passed;
Noctalia reloaded successfully using the active Wayland session socket and
reports exactly the 17 captured plugins enabled. Both Brave template IDs are
absent from the effective selection. The initial SSH reload lacked the Wayland
display and failed to find Noctalia; retrying with `wayland-1` succeeded.

The Nimbus candidate installed `adw-gtk3-theme` and `qt5ct` on 2026-09-09 and
configured the UWSM greeter default. Before that, Brave already selected GTK,
but the missing theme made Noctalia's native hook skip GTK theme activation.
GTK still reported Adwaita despite the `prefer-dark` desktop preference.
After installation, the native hook selected `adw-gtk3-dark` and `prefer-dark`;
the owner confirmed the result works. Selected desktop Chezmoi checks remain
free of drift. System changes belong to Nimbus, not a Chezmoi script.

The owner temporarily selected plain Hyprland and deferred UWSM on 2026-09-09.
A read-only check on 2026-09-10 found `wayland-wm@hyprland.desktop.service`
running through UWSM 0.26.7. `graphical-session.target`,
`xdg-desktop-portal.service`, and `xdg-desktop-portal-hyprland.service` were
active. The portal's D-Bus API reported ScreenCast source capabilities and
FileChooser version 4. No session configuration or services were changed by
this check. Interactive file picking and sharing still need a user check.

On 2026-09-10 the modular Hyprland configuration passed native validation with
Hyprland 0.56.2; Noctalia 5.0.1 also accepted the idle configuration. A disposable
nested compositor verified the lone full-width column, half-width columns when
another window opens, directional focus, width cycling, centering, fullscreen,
floating, persistent workspaces and moving a window between two outputs with
focus following. A test client using Noctalia's application ID matched the
floating settings rule. Shortcut actions were invoked from their registered
bindings; synthetic keyboard input did not trigger bindings in this nested
session. Physical keys, touchpad gestures, hardware controls, actual Noctalia
surfaces and idle lock/screen-off still need an interactive check. Autostart was
omitted only in the disposable copy; the running desktop configuration was not
applied or changed. The local gate passed 130 tests with three optional/native
skips, plus the Bash foundation checks.

These checks do not prove every app's light/dark rendering, reload behavior, keyring
unlocking, portal file picking or screen sharing. Application prerequisites in
the table remain explicit follow-up work, not completed installation claims.
Use the preview, application and recovery instructions in [README.md](README.md).

Sources: [LibrePods startup](https://github.com/kavishdevar/librepods/blob/main/linux/main.cpp),
[AirPods plugin requirements](https://github.com/noctalia-dev/community-plugins/tree/main/airpods),
[Hyprland binding descriptions](https://wiki.hypr.land/configuring/core/binds/flags/),
[Noctalia configuration](https://docs.noctalia.dev/noctalia/configuration/),
[session panel](https://docs.noctalia.dev/noctalia/configuration/shell/#session-panel),
[native idle actions](https://docs.noctalia.dev/noctalia/services/idle/),
[5.0.1 session runner](https://github.com/noctalia-dev/noctalia/blob/v5.0.1/src/shell/session/session_action_runner.cpp),
[5.0.1 session IPC](https://github.com/noctalia-dev/noctalia/blob/v5.0.1/src/shell/session/session_ipc.cpp),
[UWSM supported shutdown](https://github.com/Vladimir-csp/uwsm/tree/v0.26.7#how-to-stop),
[plugin configuration](https://docs.noctalia.dev/noctalia/plugins/),
[app theming](https://docs.noctalia.dev/noctalia/theming/app-theming/),
[5.0.1 built-ins](https://github.com/noctalia-dev/noctalia/tree/v5.0.1/assets/templates),
[community templates](https://github.com/noctalia-dev/community-templates),
[GTK/Qt integration](https://docs.noctalia.dev/noctalia/templates/official/gtk-qt/),
and [Brave native GTK selection](https://github.com/brave/brave-core/blob/master/app/settings_strings.grdp).
