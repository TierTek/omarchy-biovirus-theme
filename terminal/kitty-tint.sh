# BioVirus: random background tint per kitty window (bash and zsh).
#
# Each new kitty window gets its background shaded toward one accent colour of
# the CURRENT Omarchy theme (color1-6 / color9-14), mixed KITTY_TINT_PCT% into
# the theme's own background. The theme file is read every time, so it follows
# `omarchy theme set`. Set via OSC 11: only this window changes, no kitty
# remote control is needed, and background_opacity is left alone.
#
# Opt-in (a theme cannot run code): add to ~/.bashrc or ~/.zshrc
#   [ -r ~/.config/omarchy/themes/biovirus/terminal/kitty-tint.sh ] && . ~/.config/omarchy/themes/biovirus/terminal/kitty-tint.sh
# Tune: export KITTY_TINT_PCT=18 before the source line (default 12; 0 = off).

__biovirus_kitty_tint() {
  case $- in *i*) ;; *) return ;; esac
  [ -n "$KITTY_WINDOW_ID" ] && [ -z "$SSH_CONNECTION" ] && [ -z "$TMUX" ] || return
  # Only the first shell in a window; a nested shell keeps the window's tint.
  [ -z "$__kitty_tint_done" ] || return
  export __kitty_tint_done=1

  local theme=$HOME/.local/state/omarchy/current/theme/kitty.conf
  [ -r "$theme" ] || return
  local pct=${KITTY_TINT_PCT:-12}
  case $pct in '' | *[!0-9]*) return ;; esac
  [ "$pct" -gt 0 ] || return

  # One pass, uniform random pick (reservoir sampling), no arrays: bash and zsh
  # disagree on array indexing and word splitting.
  local key val rest bg='' acc='' n=0
  while read -r key val rest; do
    case $key in
      background) bg=$val ;;
      color[1-6] | color9 | color1[0-4])
        n=$((n + 1))
        [ $((RANDOM % n)) -eq 0 ] && acc=$val
        ;;
    esac
  done <"$theme"
  [ -n "$bg" ] && [ -n "$acc" ] || return

  local out='#' i b a
  for i in 1 3 5; do
    b=$((16#${bg:$i:2})) a=$((16#${acc:$i:2}))
    out=$out$(printf '%02x' $(((b * 100 + (a - b) * pct + 50) / 100)))
  done
  printf '\e]11;%s\e\\' "$out"
}
__biovirus_kitty_tint
unset -f __biovirus_kitty_tint
