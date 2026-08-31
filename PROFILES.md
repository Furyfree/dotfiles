# Profiles

Chezmoi uses a flat local profile list until Nimbus can supply one. Profiles
select user configuration only; they do not install software or change system
state.

## Platform profiles

These are derived from `.chezmoi.os`:

| Profile | Applies to |
|---|---|
| `common` | Every machine |
| `unix` | Linux and macOS |
| `linux` | Linux |
| `macos` | macOS (`darwin` in Chezmoi) |
| `windows` | Windows |

## Active Linux desktop profile

A Linux machine may select this desktop stack or none:

| Profile | User configuration |
|---|---|
| `hyprland-noctalia` | Hyprland and Noctalia |

The profile does not imply a greeter. Greeters and system integration belong
to Nimbus.

Selecting no desktop stack excludes only Hyprland and Noctalia. Other Linux
user configuration still follows the `linux` profile.

## Deferred Linux desktop profiles

These names are reserved but disabled in the initial setup:

```text
# niri-noctalia
# niri-dms
# hyprland-dms
```

They are not valid prompt choices. Niri and DMS paths remain ignored until
their configs are maintained.

## Rules

- Store one resolved list; do not add imports, aliases, or dependencies.
- Do not add `all`, `desktop`, `laptop`, or `nimbus` profiles.
- Add a profile only when it changes managed files.
- Reconcile these names with Nimbus before Nimbus supplies the list.

Examples:

```text
Linux desktop: common, unix, linux, hyprland-noctalia
Linux only:    common, unix, linux
MacBook:       common, unix, macos
Windows:       common, windows
```
