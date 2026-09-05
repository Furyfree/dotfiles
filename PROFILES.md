# Profiles

Chezmoi derives platform profiles from `.chezmoi.os` and receives machine
profiles from Nimbus. Profiles select user configuration only; they do not
install software or change system state.

## The Nimbus handoff

Nimbus performs the first `chezmoi init` once and passes three values through
Chezmoi's prompt flags, whose keys are the template's prompt texts:

```sh
chezmoi init \
  --promptString Machine=<machine id> \
  --promptBool ManagedByNimbus=true \
  --promptMultichoice 'Profiles=common/development/hyprland-noctalia' \
  <repo>
```

| Key | Meaning |
|---|---|
| `Machine` | The Nimbus machine ID, such as `desktop` |
| `ManagedByNimbus` | `true` when Nimbus performed the initialization |
| `Profiles` | The ordered Nimbus profile IDs, slash-separated |

The template consumes them with the `prompt*Once` functions and stores them
in the generated config as `Machine`, `ManagedByNimbus`, and `Profiles`, which
`chezmoi data` shows. The profile list is stored as sent, without checking it
against a fixed set, so a new Nimbus profile never breaks the handoff. Only
`hyprland-noctalia` and the targets that call Nimbus, gated on
`ManagedByNimbus`, depend on those values; every other Linux config deploys
unconditionally.

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
| `virtualization` | VM Curator configuration (no managed files yet) |
| `gaming` | Gaming tool configuration (no managed files yet) |
| `laptop-gaming` | Light gaming configuration (no managed files yet) |
| `hyprland-noctalia` | Hyprland and Noctalia |
| `windows-vm` | The Windows guest entries (no managed files yet) |

The profile does not imply a greeter. Greeters and system integration belong
to Nimbus.

GPU hardware is not a profile. Nimbus inspection detects hardware; a selected
graphics component declares the desired capability.

## Deferred machine profiles

These names are reserved but disabled in the initial setup:

```text
# niri-noctalia
# niri-dms
# hyprland-dms
```

They are not valid prompt choices. Niri and DMS paths remain ignored until
their configs are maintained.

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
