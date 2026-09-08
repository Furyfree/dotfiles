# Noctalia profile integration

The Fedora 44 VM completed installation in 7m56s, then booted kernel 7.1.13
and logged into Hyprland/Noctalia successfully on 2026-09-08. Nimbus owns the
system installation evidence and remaining Phase 6 gates. This document owns
the user configuration captured from Noctalia 5.0.1 and its app-theme mapping.
The newly captured Chezmoi configuration still needs a separate live trial.

## Configuration and ownership

The VM's GUI choices live in `~/.local/state/noctalia/settings.toml`, not a
legacy `settings.json`. The portable theme source, tonal-spot scheme, bundled
wallpaper and selected integrations are now in
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
No theme generation runs during Chezmoi preview or tool installation. Community
hooks execute as the logged-in user when Noctalia generates a palette; enabling
a template is therefore more than downloading passive colors.

The screenshot's Starship, Fastfetch and Neovim catalog toggles are deliberately
omitted from the managed list. These applications already inherit the terminal
ANSI palette, which themed Ghostty supplies. The Starship/Fastfetch hooks would
rewrite Chezmoi-owned files with generated RGB values; Neovim's hook would add a
second theme plugin. Terminal inheritance preserves their existing behavior and
avoids competing writers or another dependency. Existing GUI template overrides
must also omit those three to use this ownership model.

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
| Qt / `qt` | `.config/qt5ct/colors/noctalia.conf` and `.config/qt6ct/colors/noctalia.conf`; toolkit/style selection needs a live check. |
| Starship | Uses Ghostty's ANSI colors; no generated Starship configuration. |
| Fastfetch | Uses Ghostty's ANSI colors; no generated RGB merge into managed JSON. |
| Neovim | Existing `vim` colorscheme with `termguicolors=false` follows Ghostty; no base16 plugin. |
| Bat / `bat` | `.config/bat/themes/noctalia.tmTheme`; hook selects it and rebuilds Bat's cache. |
| fzf / `fzf` | `.config/fzf/themes/noctalia.sh` and `noctalia.fish`; managed Bash/Zsh profile modules source the shell file when present. Fish remains unmanaged. |
| Herdr / `herdr` | `.config/herdr/noctalia-colors.toml`; hook needs existing Herdr config, merges custom colors and requests reload. Launch/configure Herdr first. |
| Lazygit / `lazygit` | `.config/lazygit/themes/noctalia.yml`; native hook merges colors into its otherwise unmanaged config. |
| Brave Origin / `brave-origin` | `.cache/noctalia/brave-origin-theme/manifest.json`; hook requires `.config/BraveSoftware/Brave-Origin`. Launch Brave Origin first; verify activation in browser. Plain `brave` is not selected. |
| Claude Code / `claude-code` | `.claude/themes/noctalia.json`; generated theme only, select it in the application. No authentication or agent settings imported. |
| Codex / `codex` | `.codex/themes/noctalia.tmTheme`; generated theme only, select it in the application. No agent configuration is managed. |
| OpenCode / `opencode` | `.config/opencode/themes/matugen.json`; select `matugen` in the application. |
| Vesktop / `discord` | `.config/vesktop/themes/noctalia.theme.css` and alternate styles; enable the desired local theme in Vesktop. The catalog also renders other Discord-client paths. |
| LibreOffice / `libreoffice` | `.local/state/noctalia/libreoffice-theme-staging/Theme_Colors.xcu`; native hook installs/activates user theme data. Verify after app restart. |
| Obsidian / `obsidian` | Dynamic vault snippet paths; native hook discovers configured vaults. Open/create vaults first, including the selected Flatpak, then verify snippet activation. Vault contents are never copied. |
| VSCodium / `vscode` | `.vscode-oss/extensions/noctalia.noctaliatheme-0.0.5-universal/themes/NoctaliaTheme-color-theme.json`; install the declared theme extension first. Managed settings already select `NoctaliaTheme`. |
| Zed / `zed` | `.config/zed/themes/noctalia.json`; managed settings select `Noctalia Light` / `Noctalia Dark`. Restart if needed. |
| Heroic / `heroiclauncher` | `.config/heroic/themes/matugen.css`; create the app profile first and select its custom theme. Catalog also supports Flatpak. |
| Prism Launcher / `prismlauncher` | `.local/share/PrismLauncher/themes/Matugen/theme.json`; select `Matugen` in the app. |
| Steam / `steam` | `.steam/steam/steamui/skins/Material-Theme/css/main/colors/matugen.css`; requires a compatible Material-Theme skin installation. This change does not install a Steam modification. |
| OBS / `obs` | `.config/obs-studio/themes/matugen.obt`; select the theme in OBS. |
| Zathura / `zathura` | `.config/zathura/noctaliarc`; managed config includes it after fallback colors. Restart/reload to check generation. |
| Hyprtoolkit / `hyprtoolkit` | `.config/hypr/hyprtoolkit.conf`; verify native toolkit applications consume it. |
| Papirus / `papirus-icons` | Community template cache `colors-final`; native hook updates folder colors. Requires the icon theme/helper and a live visual check. |

Built-ins reside in `/usr/share/noctalia/assets/templates/builtin.toml` with
adjacent input files and hooks. Community manifests reside below
`~/.local/state/noctalia/community-templates/<id>/template.toml`; these are
upstream-managed downloads, not vendored repository files. Catalog contents can
change independently, particularly extension-version paths and app hooks.

## Keyring and remaining checks

The white prompt asked to create a new **Default keyring**. It was not merely
an unlock dialog. The VM had GNOME Keyring but lacked `gnome-keyring-pam`, even
though greetd's PAM configuration referenced its module. Nimbus must supply the
package and test login-keyring creation/unlocking during password login.
Existing default keyrings may need a user-approved password/default adjustment.
Do not automate password collection, use an empty password, or copy keyring data.
Autologin, fingerprint-only login and password changes need separate handling.

The dialog's colors are a separate GTK integration check. Noctalia's GTK hook
selects `adw-gtk3` / `adw-gtk3-dark` only when installed; merely generating CSS
does not prove every process uses it. Verify the actual prompt provider,
installed GTK theme, desktop appearance propagation and a new login. Nimbus
owns any missing packages/PAM changes; Chezmoi owns user appearance integration.

Offline checks cover profile exclusion, portable TOML, optional first-start
includes, shell palette loading and isolated Chezmoi managed/status/diff/verify.
Native Noctalia 5.0.1 config validation and Hyprland 0.56.2 config validation
also passed in disposable VM directories. The Hyprland check asserted that the
generated sibling module was discoverable and exported `apply_theme`.
These checks do not prove every app's light/dark rendering, reload behavior, keyring
unlocking, portal file picking or screen sharing. Application prerequisites in
the table remain explicit follow-up work, not completed installation claims.
Use the preview, application and recovery instructions in [README.md](README.md).

Sources: [Noctalia configuration](https://docs.noctalia.dev/noctalia/configuration/),
[app theming](https://docs.noctalia.dev/noctalia/theming/app-theming/),
[5.0.1 built-ins](https://github.com/noctalia-dev/noctalia/tree/v5.0.1/assets/templates),
[community templates](https://github.com/noctalia-dev/community-templates),
and [GTK/Qt integration](https://docs.noctalia.dev/noctalia/templates/official/gtk-qt/).
