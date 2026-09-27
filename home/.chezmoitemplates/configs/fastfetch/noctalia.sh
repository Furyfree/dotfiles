# The native package's running process is named noctalia. Installation alone
# does not establish that this shell is running.
if pgrep -u "$(id -u)" -x noctalia >/dev/null 2>&1; then
  # `noctalia --version` prints "noctalia v5.1.0"; keep the plain label otherwise.
  version=$(noctalia --version 2>/dev/null)
  version=${version#noctalia v}
  case $version in
    '' | *[!0-9.]*) printf 'Noctalia (desktop shell)' ;;
    *) printf 'Noctalia %s (desktop shell)' "$version" ;;
  esac
fi
