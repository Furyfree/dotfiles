# Machine manifests

Nimbus-owned machine manifests, tracked in this repository but outside the
Chezmoi source state (`home/` is the Chezmoi source root via `.chezmoiroot`).

- Nimbus owns the content of `machines/*.toml` and may edit a selected
  manifest after showing its diff.
- Chezmoi owns the surrounding checkout and all Git operations. Chezmoi never
  deploys or edits these files.
- Manifests are plain, versioned TOML, not templates.
- Nimbus creates `~/.config/nimbus/machine.toml` as a link to the selected
  manifest.

See the Nimbus repository's `SPEC.md` for the manifest schema.
