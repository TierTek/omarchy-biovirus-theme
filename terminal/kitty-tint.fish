# BioVirus: random background tint per kitty window (fish).
#
# Each new kitty window gets its background shaded toward one accent colour of
# the CURRENT Omarchy theme (color1-6 / color9-14), mixed TINT_PCT% into the
# theme's own background. Read from the theme file every time, so it follows
# `omarchy theme set` with no edits here.
#
# Set via OSC 11, which changes only this window (no remote control needed) and
# leaves background_opacity alone. Opt-in (a theme cannot run code):
#   ln -s ~/.config/omarchy/themes/biovirus/terminal/kitty-tint.fish ~/.config/fish/conf.d/biovirus-tint.fish
# Tune: set -U KITTY_TINT_PCT 18   (default 12; 0 disables)

status is-interactive; or return
set -q KITTY_WINDOW_ID; or return
set -q SSH_CONNECTION; and return
set -q TMUX; and return
# Only the first shell in a window; nested fish keeps the window's tint.
set -q __kitty_tint_done; and return
set -gx __kitty_tint_done 1

function __kitty_random_tint
    set -l theme ~/.local/state/omarchy/current/theme/kitty.conf
    test -r $theme; or return

    set -l pct 12
    set -q KITTY_TINT_PCT; and set pct $KITTY_TINT_PCT
    test "$pct" -gt 0 2>/dev/null; or return

    set -l bg
    set -l accents
    while read -l key val
        switch $key
            case background
                set bg $val
            case color1 color2 color3 color4 color5 color6 color9 color10 color11 color12 color13 color14
                set -a accents $val
        end
    end <$theme
    test -n "$bg"; and test (count $accents) -gt 0; or return

    set -l acc $accents[(random 1 (count $accents))]
    set -l out '#'
    for i in 2 4 6
        set -l b (math "0x"(string sub -s $i -l 2 -- $bg))
        set -l a (math "0x"(string sub -s $i -l 2 -- $acc))
        set out $out(printf '%02x' (math "round($b + ($a - $b) * $pct / 100)"))
    end
    printf '\e]11;%s\e\\' $out
end

__kitty_random_tint
functions -e __kitty_random_tint
