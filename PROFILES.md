# Profiles

Chezmoi derives platform profiles from `.chezmoi.os` and receives machine
profiles from Nimbus. Profiles select user configuration only; they do not
declare system packages or change system state. On Linux and macOS, every full
apply invokes Mise for the user tools declared in its native config, independent
of machine profiles and `ManagedByNimbus`.

## The Nimbus handoff

Nimbus performs the first `chezmoi init` once and passes four values through
Chezmoi's prompt flags, whose keys are the template's prompt texts:

```sh
chezmoi init \
  --promptString Machine=<machine id> \
  --promptBool ManagedByNimbus=true \
  --promptBool 'Enable 1Password SSH integration=false' \
  --promptMultichoice 'Profiles=common/development/hyprland-noctalia' \
  <repo>
```

| Key | Meaning |
|---|---|
| `Machine` | The Nimbus machine ID, such as `desktop` |
| `ManagedByNimbus` | `true` when Nimbus performed the initialization |
| `Profiles` | The ordered Nimbus profile IDs, slash-separated |
| `Enable 1Password SSH integration` | `false` on a fresh Nimbus init; explicitly opt in with `--onepassword-ssh` |

Existing initialized sources keep their stored SSH integration choice. A fresh
Nimbus init therefore never needs to ask about 1Password.

The template consumes them with the `prompt*Once` functions and stores them
in the generated config as `Machine`, `ManagedByNimbus`, and `Profiles`, which
`chezmoi data` shows. The profile list is stored as sent, without checking it
against a fixed set, so a new Nimbus profile never breaks the handoff.
`hyprland-noctalia` selects desktop files and the Noctalia preferences and app
theme integrations and enabled plugins. It also selects Files bookmarks and
the user GSettings hook described in [README.md](README.md#files).
`niri-dms` selects the separate Niri
and DankMaterialShell configuration. Targets that call Nimbus are gated on
`ManagedByNimbus`;
other Linux application configs deploy independently of machine profiles.

Direct `chezmoi init --prompt` asks the same questions: the machine name
defaults to the hostname, `ManagedByNimbus` to `false`, and the profiles are
chosen from the list below.

When Nimbus's profile selection changes later, Nimbus prints the refresh
command, which supplies every value so the `Once` prompts do not reuse their
stored answers:

```sh
chezmoi init --prompt \
  --promptString Machine=<machine id> \
  --promptBool ManagedByNimbus=true \
  --promptBool 'Enable 1Password SSH integration=<current>' \
  --promptMultichoice 'Profiles=<id>/<id>/...'
```

## Platform profiles

Derived from `.chezmoi.os`:

| Profile | Applies to |
|---|---|
| `common` | Every machine |
| `unix` | Linux and macOS |
| `linux` | Linux |
| `macos` | macOS (`darwin` in Chezmoi) |
| `windows` | Windows |

## Machine profiles

Nimbus vocabulary; the machine manifest selects them:

| Profile | User configuration |
|---|---|
| `common` | Base user configuration |
| `development` | Development tool configuration (no managed files yet) |
| `virtualization` | No additional profile-gated files; VM Curator defaults are managed on all Linux machines |
| `gaming` | ProtonPlus update preferences through its GSettings hook |
| `laptop-gaming` | Light gaming configuration (no managed files yet) |
| `hyprland-noctalia` | Hyprland Lua starter, portable Noctalia preferences, selected app templates and palette includes; see [NOCTALIA.md](NOCTALIA.md) |
| `niri-dms` | Modular Niri and curated DankMaterialShell settings on Linux; generated shell state stays unmanaged |
| `windows-vm` | The Windows guest entries (no managed files yet) |

The profile does not imply a greeter. Greeters and system integration belong
to Nimbus.

Hyprland's monitor and workspace templates use the existing `Machine = "desktop"`
value for the owner's two-display layout. Each display has local slots 1-10;
only slots 1-5 persist. Unique IDs keep their matching labels independent. Other
machines keep automatic outputs and five persistent workspaces without monitor
assignments. This machine-specific setting does not add a `desktop` profile
or change the Nimbus handoff.

Noctalia's Lid Guard plugin and its Hyprland shortcut use `Machine = "laptop"`.
They are absent on other machines. Battery visibility stays automatic on all
machines; `laptop-gaming` remains a software profile, not a hardware selector.

`niri-dms` is available for standalone Chezmoi selection. A Nimbus-managed
source must keep its stored machine profiles equal to the machine manifest;
adding dotfiles-only profiles makes that handoff stale. It does not install
Niri or DMS, and Nimbus still needs a corresponding system profile before it
can provision this session. Selecting both desktop profiles keeps both sets of
user files available; it does not start both sessions or switch editor themes
when logging into a different compositor. See [desktop setup](README.md#niri-and-dankmaterialshell).

GPU hardware is not a profile. Nimbus inspection detects hardware; a selected
graphics component declares the desired capability.

## Deferred machine profiles

These names are reserved but disabled in the initial setup:

```text
# niri-noctalia
# hyprland-dms
```

They are not valid prompt choices. Only the maintained `niri-dms` combination
enables the Niri and DMS files; other combinations remain future work.

## Rules

- Store one resolved list in the generated config; do not add imports,
  aliases, or dependencies.
- Consume Nimbus-supplied IDs unchanged.
- Do not add `all`, `desktop`, `laptop`, or `nimbus` profiles.
- The vocabulary is Nimbus's; gate files on a profile only when it changes
  managed files.

Examples:

```text
Nimbus desktop: common, development, hyprland-noctalia
  resolved:     common, unix, linux, development, hyprland-noctalia
Direct Linux:  common, unix, linux
MacBook:       common, unix, macos
Windows:       common, windows
```
