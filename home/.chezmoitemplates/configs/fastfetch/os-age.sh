# Fedora's retained installer-directory birth time is an estimate, not a clock
# started by dotfile application. Never substitute Nimbus setup or root age.
birth=$(stat -c %W /var/log/anaconda 2>/dev/null) || birth=
now=$(date +%s 2>/dev/null) || now=
case "$birth:$now" in
  *[!0-9:]*|:*|*:) printf 'not recorded'; exit 0 ;;
esac
if [ "$birth" -le 0 ] || [ "$birth" -gt "$now" ]; then
  printf 'not recorded'
else
  days=$(( (now - birth) / 86400 ))
  if [ "$days" -eq 0 ]; then printf '<1 day (estimate)'
  elif [ "$days" -eq 1 ]; then printf '~1 day'
  else printf '~%s days' "$days"
  fi
fi
