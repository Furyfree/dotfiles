#!/bin/bash

# install-linux.sh - Linux-specific installation script for dotfiles (symlinks only)
# Usage: ./install-linux.sh

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${PURPLE}═══════════════════════════════════════${NC}"
    echo -e "${WHITE}  🐧 Linux Dotfiles Symlink Setup${NC}"
    echo -e "${PURPLE}═══════════════════════════════════════${NC}"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Get script directory and dotfiles root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOTFILES_DIR="$SCRIPT_DIR"
COMMON_DIR="$DOTFILES_DIR/common"
LINUX_DIR="$DOTFILES_DIR/linux"

# Create symlink function
create_symlink() {
    local source="$1"
    local target="$2"
    local target_dir="$(dirname "$target")"

    # Create target directory if it doesn't exist
    if [[ ! -d "$target_dir" ]]; then
        mkdir -p "$target_dir"
        print_success "Created directory: $target_dir"
    fi

    # Remove existing file/symlink if it exists
    if [[ -e "$target" || -L "$target" ]]; then
        if [[ -L "$target" ]]; then
            print_warning "Removing existing symlink: $target"
        else
            print_warning "Backing up existing file: $target -> $target.backup"
            mv "$target" "$target.backup"
        fi
        rm -f "$target"
    fi

    # Create symlink
    ln -sf "$source" "$target"
    print_success "Linked: $target -> $source"
}

# Function to setup configurations from a directory
setup_configs() {
    local config_dir="$1"
    local config_name="$2"

    if [[ ! -d "$config_dir" ]]; then
        print_warning "$config_name directory not found: $config_dir"
        return 0
    fi

    print_step "Setting up $config_name configurations..."

    # Walk through all files in the config directory
    find "$config_dir" -type f | while read -r item; do
        # Get relative path from config directory
        relative_path="${item#$config_dir/}"

        # Target path in home directory
        target="$HOME/$relative_path"

        # Create symlink for files
        create_symlink "$item" "$target"
    done

    print_success "$config_name configuration setup completed!"
}

# Check if running on Linux
check_linux() {
    if [[ "$(uname)" != "Linux" ]]; then
        print_error "This script is designed for Linux only!"
        exit 1
    fi
    print_success "Running on Linux"
}

# Main installation process
main() {
    print_header

    # Check if we're on Linux
    check_linux

    # Setup common configurations
    if [[ -d "$COMMON_DIR" ]]; then
        setup_configs "$COMMON_DIR" "common"
    else
        print_warning "Common directory not found: $COMMON_DIR"
    fi

    # Setup Linux-specific configurations
    if [[ -d "$LINUX_DIR" ]]; then
        setup_configs "$LINUX_DIR" "Linux-specific"
    else
        print_warning "Linux directory not found: $LINUX_DIR"
    fi

    echo ""
    echo -e "${PURPLE}═══════════════════════════════════════${NC}"
    print_success "Linux dotfiles symlink setup completed!"
    echo -e "${WHITE}All configurations have been symlinked to your home directory.${NC}"
    echo -e "${YELLOW}You may need to restart your terminal or applications for changes to take effect.${NC}"
    echo -e "${PURPLE}═══════════════════════════════════════${NC}"
}

# Run main function
main "$@"
