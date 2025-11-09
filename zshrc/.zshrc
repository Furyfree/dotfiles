#######################################
# ENVIRONMENT VARIABLES
#######################################
export EDITOR=nvim

# Consolidated PATH exports
export PATH="$HOME/.local/share/JetBrains/Toolbox/scripts:$PATH"
export PATH="$HOME/.local/bin:$PATH"
export PATH="$PATH:$HOME/.lmstudio/bin"
export PATH="$PATH:$HOME/.dotnet/tools"
export PATH="$PATH:$HOME/.local/share/omarchy/bin:$PATH"
export PATH=$PATH:$(go env GOPATH)/bin
. "$HOME/.local/share/../bin/env"

# Mise (Environment manager for multiple languages)
# eval "$(mise activate zsh)"

# Starship
export STARSHIP_CONFIG=$HOME/.config/starship/starship.toml
eval "$(starship init zsh)"

#######################################
# KEYBINDINGS (Bash-like behavior)
#######################################

bindkey -e                               # Use emacs-style keybindings (default in Bash)

# Navigation: Home / End
bindkey '^[[H' beginning-of-line         # Home -> jump to start of line
bindkey '^[[F' end-of-line               # End  -> jump to end of line

# Navigation: PageUp / PageDown
# Disable in ZLE so terminal handles scrollback instead of history search
bindkey '^[[5~' undefined-key            # PageUp
bindkey '^[[6~' undefined-key            # PageDown

# Editing: Delete / Backspace variations
bindkey '^[[3~' delete-char              # Delete -> remove character under cursor
bindkey '^H' backward-kill-word          # Ctrl+Backspace -> delete previous word
bindkey '^[[3;5~' kill-word              # Ctrl+Delete -> delete next word

# Word-wise navigation
bindkey '^[[1;5C' forward-word           # Ctrl+Right -> jump forward one word
bindkey '^[[1;5D' backward-word          # Ctrl+Left  -> jump backward one word

#######################################
# HISTORY CONFIG
#######################################
HISTSIZE=10000               # number of commands kept in memory
SAVEHIST=10000               # number of commands saved to file
HISTFILE=~/.zsh_history      # history file path

setopt APPEND_HISTORY         # append to history file, don't overwrite
setopt INC_APPEND_HISTORY     # write to history immediately
setopt SHARE_HISTORY          # share history across terminals

setopt HIST_IGNORE_DUPS       # ignore duplicate of the previous command
setopt HIST_IGNORE_ALL_DUPS   # remove older duplicate commands
setopt HIST_SAVE_NO_DUPS      # don't save dups in history file
setopt HIST_EXPIRE_DUPS_FIRST # expire duplicates before unique entries

setopt HIST_FIND_NO_DUPS      # skip duplicates when searching history
setopt HIST_IGNORE_SPACE      # don't record commands starting with space
setopt HIST_REDUCE_BLANKS     # remove superfluous blanks
setopt HIST_LEX_WORDS         # better parsing of complex/multiline commands
setopt HIST_VERIFY            # don't run recalled command immediately

#######################################
# ZINIT (PLUGIN MANAGER)
#######################################
if [[ ! -f $HOME/.local/share/zinit/zinit.git/zinit.zsh ]]; then
  echo "Installing Zinit..."
  mkdir -p "$HOME/.local/share/zinit" && chmod g-rwX "$HOME/.local/share/zinit"
  git clone https://github.com/zdharma-continuum/zinit "$HOME/.local/share/zinit/zinit.git" \
    && echo "Zinit installed." || echo "Failed to install Zinit."
fi

source "$HOME/.local/share/zinit/zinit.git/zinit.zsh"
autoload -Uz _zinit
(( ${+_comps} )) && _comps[zinit]=_zinit

# Plugins
zinit light zsh-users/zsh-autosuggestions
zinit light zsh-users/zsh-syntax-highlighting
zinit light zsh-users/zsh-completions
zinit light zsh-users/zsh-history-substring-search
zinit snippet OMZL::git.zsh
zinit snippet OMZP::git
zinit light Aloxaf/fzf-tab

#######################################
# FZF CONFIG
#######################################
source <(fzf --zsh)

export FZF_CTRL_R_OPTS="
  --bind 'ctrl-y:execute-silent(echo -n {2..} | wl-copy)+abort'
  --color header:italic
  --header 'Press CTRL-Y to copy command into clipboard'"

#######################################
# ZOXIDE (better cd)
#######################################
eval "$(zoxide init zsh)"

#######################################
# ALIASES
#######################################

# File and Directory Operations
alias y='yazi'
alias ls='eza --icons --grid --group-directories-first'
alias ll='eza -lah --icons --group-directories-first'
alias lt='eza --tree --icons --group-directories-first'
alias la='eza -a --icons --grid --group-directories-first'
alias cat='bat'
alias mkdir='mkdir -p'
alias cd='z'
alias ff="fzf --preview 'bat --style=numbers --color=always {}'"

# System Utilities
alias c='clear'
alias e='exit'
alias f='fastfetch'
alias help='tldr'
alias copy="wl-copy"
alias paste="wl-paste"

# Development Tools
alias nvimconfig="cd ~/.config/nvim && nvim ."
alias n="nvim"
alias lg='lazygit'
alias ld='lazydocker'

# Search and Find
alias fman='compgen -c | fzf | xargs man'
alias fzf-find='fd --type f | fzf'
alias find='fd'

# Terminal/Session Management
alias tm="tmux attach -t main 2>/dev/null || tmux new -s main"  # attach/create main

# Network/VPN
# DTU VPN
alias vpn-dtu-up='nmcli connection up dtu-vpn'
alias vpn-dtu-down='nmcli connection down dtu-vpn'

# Own VPN
alias vpn-up='nmcli connection up unifi-wg'
alias vpn-down='nmcli connection down unifi-wg'

# System Maintenance
alias updategrub='sudo grub-mkconfig -o /boot/grub/grub.cfg'

# Toggle pyenv (disable → enable)
function toggle-pyenv() {
  if [[ -n "$PYENV_ROOT" ]]; then
    echo "[INFO] Disabling pyenv"
    export ORIG_PATH="$PATH"
    unset PYENV_ROOT
    export PATH=$(echo "$PATH" | tr ':' '\n' | grep -v '\.pyenv' | command paste -sd ':' -)
    hash -r
  else
    echo "[INFO] Re-enabling pyenv"
    export PYENV_ROOT="$HOME/.pyenv"
    export PATH="$PYENV_ROOT/bin:$ORIG_PATH"
    eval "$(pyenv init --path)"
    eval "$(pyenv init -)"
    hash -r
  fi
}


#######################################
# COMPLETION
#######################################
autoload -Uz compinit
compinit
