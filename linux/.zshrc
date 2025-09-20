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

# Pyenv
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init --path)"
eval "$(pyenv init -)"

# Turn on vim-mode terminal
bindkey -v

# Starship
export STARSHIP_CONFIG=$HOME/.config/starship/starship.toml
eval "$(starship init zsh)"

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

# System Utilities
alias c='clear'
alias e='exit'
alias f='fastfetch'
alias help='tldr'
alias copy="wl-copy"
alias paste="wl-paste"

# Development Tools
alias nvimconfig="cd ~/.config/nvim && nvim ."
alias lg='lazygit'
alias ld='lazydocker'

# Search and Find
alias fman='compgen -c | fzf | xargs man'
alias fzf-find='fd --type f | fzf'
alias find='fd'

# Terminal/Session Management
alias tm="tmux attach -t main 2>/dev/null || tmux new -s main"  # attach/create main

# Network/VPN
alias dtuvpn='sudo openconnect --useragent=AnyConnect --user=s224338 vpn.dtu.dk'

# System Maintenance
alias updategrub='sudo grub-mkconfig -o /boot/grub/grub.cfg'

#######################################
# COMPLETION
#######################################
autoload -Uz compinit
compinit
