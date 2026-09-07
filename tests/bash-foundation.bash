#!/usr/bin/env bash
# PATH changes are deliberately isolated to each test subshell.
# shellcheck disable=SC2030,SC2031,SC2178,SC2128,SC1090,SC1091,SC2034
set -euo pipefail

repo=$(builtin cd -- "${BASH_SOURCE[0]%/*}/.." && pwd)
for file in "$repo"/home/dot_bash* "$repo"/home/dot_blerc \
  "$repo"/home/dot_config/bash/{bashrc,profile,blerc,logout} \
  "$repo"/home/dot_config/bash/conf.d/*.bash; do
  bash -n "$file"
done
shellcheck -s bash -e SC1090,SC1091,SC2034 \
  "$repo"/home/dot_bash* "$repo"/home/dot_blerc \
  "$repo"/home/dot_config/bash/{bashrc,profile,blerc,logout} \
  "$repo"/home/dot_config/bash/conf.d/*.bash

test_dir=$(mktemp -d)
trap 'command rm -rf -- "$test_dir"' EXIT
mkdir -p "$test_dir"/{bin,config,cache,data,state,work}
ln -s "$repo/home/dot_config/bash" "$test_dir/config/bash"
for tool in mkdir chmod cat readlink mktemp rm; do
  ln -s "$(type -P "$tool")" "$test_dir/bin/$tool"
done
cp "$repo/tests/fixtures/bash-tool" "$test_dir/tool"
chmod +x "$test_dir/tool"
export XDG_CONFIG_HOME="$test_dir/config" XDG_CACHE_HOME="$test_dir/cache"
export XDG_DATA_HOME="$test_dir/data" XDG_STATE_HOME="$test_dir/state"
export TEST_CLIPBOARD="$test_dir/clipboard" TEST_YAZI_CWD="$test_dir/work"
export TMPDIR="$test_dir"

# Tests use only isolated state and a deliberately sparse executable path.
(
  export PATH="$test_dir/bin"
  unset EDITOR VISUAL PAGER PROMPT_COMMAND
  source "$XDG_CONFIG_HOME/bash/conf.d/env.bash"
  [[ -z ${EDITOR-} && -z ${PAGER-} ]]
  EDITOR=custom VISUAL=visual PAGER=pager
  source "$XDG_CONFIG_HOME/bash/conf.d/env.bash"
  [[ $EDITOR == custom && $VISUAL == visual && $PAGER == pager ]]

  source "$XDG_CONFIG_HOME/bash/conf.d/history.bash"
  [[ $HISTFILE == "$test_dir/state/bash/history" && $HISTSIZE == 20000 && $HISTFILESIZE == 10000 ]]
  [[ $PROMPT_COMMAND == dotfiles_bash_history ]]
  source "$XDG_CONFIG_HOME/bash/conf.d/history.bash"
  [[ $PROMPT_COMMAND == dotfiles_bash_history ]]
  if (exit 7); then :; else
    if dotfiles_bash_history; then exit 1; else [[ $? == 7 ]]; fi
  fi
  PROMPT_COMMAND='printf existing'
  source "$XDG_CONFIG_HOME/bash/conf.d/history.bash"
  [[ $PROMPT_COMMAND == 'dotfiles_bash_history; printf existing' ]]
  PROMPT_COMMAND=('printf one' 'printf two')
  source "$XDG_CONFIG_HOME/bash/conf.d/history.bash"
  [[ ${#PROMPT_COMMAND[@]} == 3 && ${PROMPT_COMMAND[1]} == 'printf one' ]]

  source "$XDG_CONFIG_HOME/bash/conf.d/functions.bash"
  copy </dev/null && exit 1
  clip-paste unexpected && exit 1
  y && exit 1
  source "$XDG_CONFIG_HOME/bash/conf.d/aliases.bash"
  [[ $(alias h) == "alias h='history'" && $(alias mkdir) == "alias mkdir='mkdir -p'" ]]
)
mode() {
  case $OSTYPE in
    darwin*) stat -f %Lp "$1" ;;
    *) stat -c %a "$1" ;;
  esac
}
[[ $(mode "$test_dir/state/bash") == 700 ]]
chmod 755 "$test_dir/state/bash"
(
  source "$XDG_CONFIG_HOME/bash/conf.d/history.bash"
)
[[ $(mode "$test_dir/state/bash") == 700 ]]
for tool in mkdir chmod; do
  mv "$test_dir/bin/$tool" "$test_dir/bin/$tool.saved"
  ln -s "$(type -P false)" "$test_dir/bin/$tool"
  (
    export PATH="$test_dir/bin"
    source "$XDG_CONFIG_HOME/bash/conf.d/history.bash" && exit 1
    [[ -z ${HISTFILE+x} ]]
  )
  rm "$test_dir/bin/$tool"
  mv "$test_dir/bin/$tool.saved" "$test_dir/bin/$tool"
done

for tool in pbcopy pbpaste wl-copy wl-paste xclip yazi mise zoxide starship; do
  ln -s "$test_dir/tool" "$test_dir/bin/$tool"
done
printf 'first' > "$test_dir/first"
printf 'second' > "$test_dir/second"
ln -s first "$test_dir/link"
(
  export PATH="$test_dir/bin"
  source "$XDG_CONFIG_HOME/bash/conf.d/functions.bash"
  for platform in linux-gnu darwin; do
    OSTYPE=$platform
    export WAYLAND_DISPLAY=test DISPLAY=:test
    copy "$test_dir/first" "$test_dir/second"
    [[ $(clip-paste) == firstsecond ]]
    copy "$test_dir/first" "$test_dir/missing" && exit 1
    [[ $(clip-paste) == firstsecond ]]
    copypath "$test_dir/link"
    [[ $(clip-paste) == "$test_dir/first" ]]
  done
  OSTYPE=linux-gnu
  unset WAYLAND_DISPLAY
  printf fallback | copy
  [[ $(clip-paste) == fallback ]]
  y
  [[ $PWD == "$TEST_YAZI_CWD" ]]
  TEST_YAZI_STATUS=9
  export TEST_YAZI_STATUS
  if y; then exit 1; else [[ $? == 9 ]]; fi
  for module in mise zoxide prompt; do
    source "$XDG_CONFIG_HOME/bash/conf.d/$module.bash" || true
    [[ -z ${dotfiles_bad_eval-} ]]
  done
)

(
  source "$XDG_CONFIG_HOME/bash/conf.d/functions.bash"
  builtin cd -- "$repo/home"
  croot
  [[ $PWD == "$repo" ]]
  croot unexpected && exit 1
  builtin cd -- "$test_dir"
  croot && exit 1
  [[ $PWD == "$test_dir" ]]
)
if compgen -G "$test_dir/yazi-cwd.*" >/dev/null; then
  printf '%s\n' 'Yazi temporary file leaked' >&2
  exit 1
fi

# No optional installed tools or real history are used by startup checks.
PATH="$test_dir/bin" /bin/bash --noprofile --norc -ic '
  source "$XDG_CONFIG_HOME/bash/bashrc"
  before=${PROMPT_COMMAND[*]}
  source "$XDG_CONFIG_HOME/bash/bashrc"
  [[ ${PROMPT_COMMAND[*]} == "$before" && $dotfiles_bash_loaded == yes ]]
  unset HISTFILE
'
PATH="$test_dir/bin" /bin/bash --noprofile --norc -c '
  source "$XDG_CONFIG_HOME/bash/bashrc"
  [[ -z ${dotfiles_bash_loaded-} ]]
  source "$XDG_CONFIG_HOME/bash/profile"
  [[ $PATH == "$HOME/.local/bin:"* ]]
'

# Preserved .profile files can load .bashrc before their own PATH additions.
# Test both a missing user-local path and one already supplied by the parent.
login_home="$test_dir/login-home"
mkdir -p "$login_home/.local/bin"
ln -s "$repo/home/dot_bash_profile" "$login_home/.bash_profile"
ln -s "$repo/home/dot_bashrc" "$login_home/.bashrc"
ln -s "$repo/tests/fixtures/bash-login-profile" "$login_home/.profile"
ln -s "$test_dir/tool" "$login_home/.local/bin/mise"
for local_path in '' "$login_home/.local/bin:"; do
  HOME="$login_home" PATH="$local_path$test_dir/bin" \
    TEST_MISE_SUCCESS_PATH="$login_home/.local/bin/mise" \
    /bin/bash --noprofile --norc -ic '
      # Do not load installed completions during this isolated startup test.
      BASH_COMPLETION_VERSINFO=(test)
      source "$HOME/.bash_profile"
      set -e
      [[ $TEST_PROFILE_LOADED == yes && $dotfiles_bash_loaded == yes ]]
      [[ ${test_mise_activations:-0} == 1 ]]
      [[ $PATH == "$HOME/.local/bin:$TMPDIR/bin" ]]
      before=${PROMPT_COMMAND[*]}
      source "$HOME/.bashrc"
      [[ ${test_mise_activations:-0} == 1 && ${PROMPT_COMMAND[*]} == "$before" ]]
      unset HISTFILE
    '
done
printf '%s\n' 'Bash foundation checks passed.'
