#!/bin/bash

# install.sh - Main installation script for dotfiles
# Usage: ./install.sh

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
    echo -e "${WHITE}  🚀 Dotfiles Installation${NC}"
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

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPTS_DIR="$SCRIPT_DIR/scripts"

print_header

# Check if paru is installed
print_step "Checking for paru..."
if ! command -v paru &>/dev/null; then
    print_error "paru is not installed. Please install paru first."
    echo -e "${WHITE}Install paru with:${NC}"
    echo -e "${YELLOW}  git clone https://aur.archlinux.org/paru.git${NC}"
    echo -e "${YELLOW}  cd paru${NC}"
    echo -e "${YELLOW}  makepkg -si${NC}"
    echo -e "${YELLOW}  cd && rm -rf paru${NC}"
    exit 1
else
    print_success "paru found"
fi

# Set up pacman configuration
print_step "Setting up pacman configuration..."
if [[ -x "$SCRIPTS_DIR/setup-pacman" ]]; then
    "$SCRIPTS_DIR/setup-pacman"
    print_success "Pacman configured"
else
    print_error "setup-pacman script not found or not executable"
    exit 1
fi

# Set up XDG user directories
print_step "Setting up XDG user directories..."
if [[ -x "$SCRIPTS_DIR/setup-xdg-dirs" ]]; then
    "$SCRIPTS_DIR/setup-xdg-dirs"
    print_success "XDG directories configured"
else
    print_error "setup-xdg-dirs script not found or not executable"
    exit 1
fi

# Install packages
print_step "Installing packages..."
if [[ -x "$SCRIPTS_DIR/install-packages" ]]; then
    "$SCRIPTS_DIR/install-packages"
    print_success "Packages installed"
else
    print_error "install-packages script not found or not executable"
    exit 1
fi

# Set up common configurations
print_step "Setting up common configurations..."
if [[ -x "$SCRIPTS_DIR/setup-common" ]]; then
    "$SCRIPTS_DIR/setup-common"
    print_success "Common configurations linked"
else
    print_error "setup-common script not found or not executable"
    exit 1
fi

# Set up Linux-specific configurations
print_step "Setting up Linux configurations..."
if [[ -x "$SCRIPTS_DIR/setup-linux" ]]; then
    "$SCRIPTS_DIR/setup-linux"
    print_success "Linux configurations linked"
else
    print_error "setup-linux script not found or not executable"
    exit 1
fi

# Set up desktop entries
print_step "Setting up desktop entries..."
if [[ -x "$SCRIPTS_DIR/setup-desktop-entries" ]]; then
    "$SCRIPTS_DIR/setup-desktop-entries"
    print_success "Desktop entries configured"
else
    print_error "setup-desktop-entries script not found or not executable"
    exit 1
fi

# Set up system theme
print_step "Setting up system theme..."
if [[ -x "$SCRIPTS_DIR/set-system-theme" ]]; then
    "$SCRIPTS_DIR/set-system-theme"
    print_success "System theme configured"
else
    print_error "set-system-theme script not found or not executable"
    exit 1
fi

print_success "Dotfiles installation completed!"
echo -e "${WHITE}You may need to restart some applications for all changes to take effect.${NC}"
