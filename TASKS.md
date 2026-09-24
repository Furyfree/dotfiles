# Tasks

- [ ] Test Voxtype on the RTX 3080 in a terminal and editor. Compare
  `large-v3-turbo` with `small` for accuracy, speed and GPU memory use.
- [ ] Install and apply the configuration on the MacBook. Verify shells,
  tools, editors and 1Password SSH/Git integration on macOS.

- [ ] Comment out `herdr = "latest"` in the Mise config, retaining the line
  for opt-in later. Keep the Noctalia `herdr` color template and the selected
  agent-proxy config; do not add removal rules or change its selection tests.
- [ ] After Mise install, prune tools removed from the managed config on
  apply/sync; warn without failing apply if pruning fails. Verify removal of
  the Mise Herdr CLI separately from Nimbus's proxy-bundled `herdr.service`,
  which Nimbus owns. Preserve declared tools and unrelated project installs.
- [ ] On the laptop, verify apply/sync removes the Mise Herdr CLI while
  retaining proxy config and colors. Coordinate with Nimbus's proxy removal
  and reboot trial; leave unrelated services and user lingering unchanged.
- [ ] In Obsidian, verify: a commit from the Git panel is signed through
  1Password; Ctrl+Shift+V still pastes plain text in Markdown; F2 renames with
  the header hidden; `preview.typ` renders in the Typst preview; Agent Client
  connects to Claude Code, Codex and Pi after Mise installs the adapters.

Use the [README](README.md) for installation and
[post-installation steps][setup] for application setup and recovery.

[setup]: https://github.com/Furyfree/docs/blob/main/POSTINSTALL.md
