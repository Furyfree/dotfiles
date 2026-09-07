# Run the complete local regression gate.
check:
    python3 tests/check.py
    bash tests/bash-foundation.bash
    git diff --check HEAD

# Optional style report; existing Markdown formatting is not part of the gate.
lint-docs:
    markdownlint '*.md'

# Preview this checkout without applying; requires initialized Chezmoi.
preview:
    chezmoi --source '{{justfile_directory()}}' managed
    chezmoi --source '{{justfile_directory()}}' status
    chezmoi --source '{{justfile_directory()}}' diff
    chezmoi --source '{{justfile_directory()}}' verify
