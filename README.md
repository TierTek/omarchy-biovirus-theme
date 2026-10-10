# BioVirus — an Omarchy theme

Dark cyberpunk, containment-breach motif: near-black backgrounds, a
`#4bffa5` spore-green accent, and five wallpaper plates drawn as still
frames of a lab that is not quite under control.

![BioVirus](preview.png)

## Install

```bash
omarchy theme install https://github.com/TierTek/omarchy-biovirus-theme
```

That clones the theme into `~/.config/omarchy/themes/biovirus` and applies
it. Switch back and forth later with `omarchy theme set biovirus`, and cycle
the plates with `omarchy theme bg next`.

## What's in the box

| File | Themes |
|---|---|
| `colors.toml` | The palette. Everything Omarchy generates (terminals, Hyprland borders, the shell) comes from here. |
| `btop.theme` | A hand-tuned btop palette: green gauges shading to amber and red as load climbs, used instead of the generated one. |
| `backgrounds/` | Five 2880×1800 plates: containment, virions, mitosis, sequencer, outbreak. |
| `shell.*.toml` | Lock, launcher, menu and notification styling for the Omarchy shell. |
| `icons.theme` | Icon theme name. |
| `unlock.png`, `preview*.png` | Lock-screen mark and gallery previews. |
| `neovim.lua`, `vscode.json` | Editor colourschemes. See the note below. |
| `terminal/kitty-tint.*` | Optional random background tint per kitty window. See below. |

`tools/make-plates.py` is the generator for the plates (Pillow only). Pass it
another theme's `colors.toml` with `--colors` to render the same five plates
in a sibling palette.

## Optional: a random tint for each kitty window

`terminal/` holds a small opt-in script that opens each new kitty window with its
background faintly shaded (12%) toward a random accent of the active theme —
green in one window, amber or violet in the next. It is set with an OSC 11
escape, so only that window changes and transparency is untouched, and it reads
the current theme at startup, so it keeps working after `omarchy theme set`
(with any theme, not just this one). It skips SSH sessions, tmux and nested
shells.

A theme cannot run code, so turn it on yourself. bash or zsh — add to
`~/.bashrc` or `~/.zshrc`:

```bash
[ -r ~/.config/omarchy/themes/biovirus/terminal/kitty-tint.sh ] && . ~/.config/omarchy/themes/biovirus/terminal/kitty-tint.sh
```

fish:

```fish
ln -s ~/.config/omarchy/themes/biovirus/terminal/kitty-tint.fish ~/.config/fish/conf.d/biovirus-tint.fish
```

`KITTY_TINT_PCT` sets the strength (`export KITTY_TINT_PCT=18`, or
`set -U KITTY_TINT_PCT 18` in fish); `0` turns it off. The
[animated version](https://github.com/TierTek/omarchy-biovirus) installs this
for you with `--hud`.

## Note on `neovim.lua` and `vscode.json`

Omarchy 4 does not run code from a theme installed by `omarchy theme install`:
`*.lua`, the terminal configs and `vscode.json` are dropped from a cloned theme
and regenerated from `colors.toml`. You lose nothing visible — the generated
files use the same palette — but if you want the hand-written versions, copy
the theme by hand instead:

```bash
git clone https://github.com/TierTek/omarchy-biovirus-theme /tmp/biovirus
rm -rf /tmp/biovirus/.git
cp -r /tmp/biovirus ~/.config/omarchy/themes/biovirus
omarchy theme set biovirus
```

## Animated version

The plates are the still frames of four animated scenes (drifting virions,
mitosis, a DNA sequencer, an outbreak map) that run on the desktop and the lock
screen, plus a matching SDDM login greeter. That lives in a separate repo
because it forks two of Omarchy's shell plugins and needs an install script:
[TierTek/omarchy-biovirus](https://github.com/TierTek/omarchy-biovirus).

## License

MIT — see [LICENSE](LICENSE).
