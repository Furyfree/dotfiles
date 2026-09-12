# The native package's running process is named noctalia. Installation alone
# does not establish that this shell is running.
if pgrep -u "$(id -u)" -x noctalia >/dev/null 2>&1; then
  printf 'Noctalia (desktop shell)'
fi
