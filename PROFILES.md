# Profiles

Chezmoi derives platform profiles from `.chezmoi.os` and receives machine
profiles from Nimbus. Profiles select user configuration only; they do not
install software or change system state.

## Supplying machine profiles

Nimbus passes the resolved profile selection to `chezmoi init` through
Chezmoi's native `--promptMultichoice` flag:

```sh
chezmoi init \
  --promptMultichoice 'Profiles=common/development/hyprland-noctalia' \
  <repo>
```

The flag value is the selected list, slash-separated. Its key must match the
template's prompt text exactly, which is `Profiles`. The config template
consumes the selection with `promptMultichoiceOnce` and persists it in the
generated config, so a later `chezmoi init` without Nimbus restores the same
selection. Direct `chezmoi init` prompts for the same profiles interactively.

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
| `gaming` | Gaming tool configuration (no managed files yet) |
| `hyprland-noctalia` | Hyprland and Noctalia |

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
- Add a profile only when it changes managed files.

Examples:

```text
Nimbus desktop: common, development, hyprland-noctalia
  resolved:     common, unix, linux, development, hyprland-noctalia
Direct Linux:  common, unix, linux
MacBook:       common, unix, macos
Windows:       common, windows
```
