bindkey -e

# Use the terminal's Home, End, and Delete sequences when available.
if zmodload zsh/terminfo; then
  [[ -n ${terminfo[khome]-} ]] && bindkey "${terminfo[khome]}" beginning-of-line
  [[ -n ${terminfo[kend]-} ]] && bindkey "${terminfo[kend]}" end-of-line
  [[ -n ${terminfo[kdch1]-} ]] && bindkey "${terminfo[kdch1]}" delete-char
fi

# Common sequences also sent outside application-keypad mode.
bindkey '^[[H' beginning-of-line
bindkey '^[[F' end-of-line
bindkey '^[[3~' delete-char

bindkey '^[[1;5D' backward-word
bindkey '^[[1;5C' forward-word
bindkey '^[[3;5~' kill-word
bindkey '^W' backward-kill-word
bindkey '^[^?' backward-kill-word
