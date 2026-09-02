# Run the available local checks.
check:
    git diff --check HEAD
    if command -v markdownlint >/dev/null 2>&1; then markdownlint '*.md'; else echo 'markdownlint not installed: skipped'; fi

# Read-only Chezmoi view of this checkout against the current home. Never
# applies. Requires a generated Chezmoi config; see README.md.
preview:
    chezmoi --source {{justfile_directory()}} managed
    chezmoi --source {{justfile_directory()}} status
    chezmoi --source {{justfile_directory()}} diff
    -chezmoi --source {{justfile_directory()}} verify
