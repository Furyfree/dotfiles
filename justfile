# Run the complete local regression gate.
check:
    python3 tests/check.py
    bash tests/bash-foundation.bash
    git diff --check HEAD

# Run on a Hyprland/Noctalia machine; missing native validators fail this gate.
check-desktop:
    Hyprland --verify-config --config '{{justfile_directory()}}/home/dot_config/hypr/hyprland.lua'
    noctalia config validate '{{justfile_directory()}}/home/dot_config/noctalia/config.toml'

# Optional style report; existing Markdown formatting is not part of the gate.
lint-docs:
    markdownlint '*.md'

# Preview this checkout without applying; requires initialized Chezmoi.
preview:
    chezmoi --source '{{justfile_directory()}}' managed
    chezmoi --source '{{justfile_directory()}}' status
    chezmoi --source '{{justfile_directory()}}' diff
    chezmoi --source '{{justfile_directory()}}' verify
