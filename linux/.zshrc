#######################################
# ENVIRONMENT VARIABLES
#######################################
export EDITOR=nvim
export PATH="$HOME/.local/share/JetBrains/Toolbox/scripts:$PATH"
# export TERM=xterm-256color

# Pyenv
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init --path)"
eval "$(pyenv init -)"
# eval "$(pyenv virtualenv-init -)"  # Uncomment if needed

# Turn on vim-mode terminal
bindkey -v

# NVM
# source /usr/share/nvm/init-nvm.sh

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
[ -f /usr/share/fzf/key-bindings.zsh ] && source /usr/share/fzf/key-bindings.zsh
[ -f /usr/share/fzf/completion.zsh ] && source /usr/share/fzf/completion.zsh

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

# General tools
alias y='yazi'
alias ls='eza --icons --grid --group-directories-first'
alias ll='eza -lah --icons --group-directories-first'
alias lt='eza --tree --icons --group-directories-first'
alias la='eza -a --icons --grid --group-directories-first'
alias cat='bat'
alias c='clear'
alias e='exit'
alias copy="wl-copy"
alias paste="wl-paste"
alias f='fastfetch'
alias help='tldr'
alias history='history 1'
alias mkdir='mkdir -p'
alias cd='z'
alias nvimconfig="cd ~/.config/nvim && nvim ."

# DTU VPN
alias dtuvpn='sudo openconnect --useragent=AnyConnect --user=s224338 vpn.dtu.dk'

# Finder and SSH
alias fman='compgen -c | fzf | xargs man'
alias fzf-find='fd --type f | fzf'
alias find='fd'
alias sshkit="TERM=xterm-256color ssh"

# Tmux aliases
alias tm="tmux attach -t main 2>/dev/null || tmux new -s main"  # attach/create main
alias ta='tmux attach -t'    # attach to a named session
alias tls='tmux ls'          # list all tmux sessions
alias t='tmux attach'        # attach (will prompt if no -t)

# Git
alias gt="git"
alias ga="git add ."
alias gs="git status -s"
alias gc='git commit -m'
alias glog='git log --oneline --graph --all'

# Generic Maven aliases
alias mvn-build='mvn clean package'
alias mvn-run='java -cp target/classes $(grep -oPm1 "(?<=<mainClass>)[^<]+" pom.xml)'
alias mvn-clean='mvn clean'
alias mvn-test='mvn test'
alias mvn-install='mvn install'

# Paru shortcuts
alias s='paru -Ss'
alias i='paru -S'
alias r='paru -Rns'
alias u='paru -Syu'
alias q='paru -Q'
alias qi='paru -Qi'

# Spring Boot Maven (uses ./mvnw)
alias sb-run='./mvnw spring-boot:run'
alias sb-clean='./mvnw clean'
alias sb-test='./mvnw test'
alias sb-package='./mvnw package'
alias sb-install='./mvnw install'
alias sb-compile='./mvnw compile'

# Git and Docker
alias lg='lazygit'
alias ld='lazydocker'

# Ladybird
alias ladybird='(cd ~/git/ladybird && PYTHONPATH=. python3 Meta/ladybird.py run ladybird)'

# Brightness
alias bright25='ddcutil --bus=14 setvcp 10 25 && ddcutil --bus=15 setvcp 10 25'
alias bright50='ddcutil --bus=14 setvcp 10 50 && ddcutil --bus=15 setvcp 10 50'
alias bright75='ddcutil --bus=14 setvcp 10 75 && ddcutil --bus=15 setvcp 10 75'
alias bright100='ddcutil --bus=14 setvcp 10 100 && ddcutil --bus=15 setvcp 10 100'

# Maintenance
alias updategrub='sudo grub-mkconfig -o /boot/grub/grub.cfg'

#######################################
# CUSTOM FUNCTIONS
#######################################
check_timeshift_sizes() {
  MOUNT="/mnt/timeshift"
  DEVICE="/dev/nvme3n1p2"
  sudo mkdir -p "$MOUNT"
  sudo mount "$DEVICE" "$MOUNT" && \
  echo "Timeshift snapshot-størrelser:" && \
  sudo du -sh "$MOUNT/timeshift-btrfs/snapshots/"* && \
  sudo umount "$MOUNT"
}

maintenance() {
  echo "Er du sikker på du vil køre maintenance? ([Y]/n)"
  read confirm
  if [[ "${confirm:l}" == "n" ]]; then
    echo "Annulleret."
  else
    bash ~/maintenance.sh
  fi
}

#######################################
# Completion
#######################################
autoload -Uz compinit
compinit

# Added by LM Studio CLI (lms)
export PATH="$PATH:/home/pby/.lmstudio/bin"
# End of LM Studio CLI section

export PATH="$PATH:$HOME/.dotnet/tools"
