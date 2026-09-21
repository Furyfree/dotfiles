# Run the complete local regression gate.
check:
    python3 -c 'import sys; sys.exit("Python 3.14+ is required" if sys.version_info < (3, 14) else 0)'
    ruff check tests
    python3 tests/check.py --self-test
    python3 tests/check.py
    bash tests/bash-foundation.bash
    git diff --check HEAD

# Run on a Hyprland/Noctalia machine; missing native validators fail this gate.
check-desktop:
    command -v Hyprland >/dev/null
    command -v chezmoi >/dev/null
    command -v noctalia >/dev/null
    python3 tests/hyprland.py Hyprland.test_native_config
    python3 tests/noctalia.py Noctalia.test_native_config

# Optional style report; existing Markdown formatting is not part of the gate.
lint-docs:
    markdownlint '*.md'

# Preview this checkout without applying; requires initialized Chezmoi.
preview:
    chezmoi --source '{{justfile_directory()}}' managed
    chezmoi --source '{{justfile_directory()}}' status
    chezmoi --source '{{justfile_directory()}}' diff
    chezmoi --source '{{justfile_directory()}}' verify
