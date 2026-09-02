# Profiles

Chezmoi derives platform profiles from `.chezmoi.os` and receives machine
profiles from Nimbus or from the user. Profiles select user configuration
only; they do not install software or change system state.

## Nimbus handoff

Nimbus passes three values to `chezmoi init` through Chezmoi's native prompt
flags:

```sh
chezmoi init \
  --promptString Machine=desktop \
  --promptBool ManagedByNimbus=true \
  --promptMultichoice 'Profiles=common/development/hyprland-noctalia' \
  <repo>
```

Each flag key is the template's prompt text. The multichoice value is the
selected list, slash-separated and in Nimbus order. The template stores the
values in the generated config as:

| Data key | Meaning |
| --- | --- |
| `machine` | Nimbus machine ID, or a user-chosen name without Nimbus |
| `managed_by_nimbus` | `true` only when Nimbus performed the handoff |
| `Profiles` | The machine profiles as supplied |
| `profiles` | Resolved list: `common`, platform profiles, machine profiles |

The `prompt*Once` functions persist the values, so a later `chezmoi init`
without Nimbus keeps them. Direct `chezmoi init` prompts for the machine name
(default: hostname) and profiles; `managed_by_nimbus` defaults to `false` and
is never asked on macOS or Windows. The 1Password SSH prompt is a user choice
on every path and is not part of the handoff.

`managed_by_nimbus` gates only targets that call Nimbus, such as the
`windows-vm` desktop entry for `nimbus windows connect`. It never gates
Hyprland, Noctalia, or other user configuration that works on Linux without
Nimbus. The profile is not named `windows` because that is the platform profile.

## Platform profiles

Derived from `.chezmoi.os`:

| Profile | Applies to |
| --- | --- |
| `common` | Every machine |
| `unix` | Linux and macOS |
| `linux` | Linux |
| `macos` | macOS (`darwin` in Chezmoi) |
| `windows` | Windows |

## Machine profiles

Shared vocabulary; the Nimbus machine manifest selects them:

| Profile | User configuration |
| --- | --- |
| `common` | Base user configuration |
| `development` | Development tool configuration (no managed files yet) |
| `gaming` | Gaming tool configuration (no managed files yet) |
| `hyprland-noctalia` | Hyprland and Noctalia |
| `windows-vm` | Windows guest integration, gated with `managed_by_nimbus` |

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
- Do not add `all`, `desktop`, `laptop`, or `nimbus` profiles. Machine identity
  is the `machine` value, and Nimbus presence is `managed_by_nimbus`.
- Add a profile only when it changes managed files.

Examples:

```text
Nimbus desktop: common, development, hyprland-noctalia
  resolved:     common, unix, linux, development, hyprland-noctalia
Direct Linux:  common, unix, linux
MacBook:       common, unix, macos
Windows:       common, windows
```
