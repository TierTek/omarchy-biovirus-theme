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
| `colors.toml` | The palette. Everything Omarchy generates (terminals, Hyprland borders, btop, the shell) comes from here. |
| `backgrounds/` | Five 2880×1800 plates: containment, virions, mitosis, sequencer, outbreak. |
| `shell.*.toml` | Lock, launcher, menu and notification styling for the Omarchy shell. |
| `icons.theme` | Icon theme name. |
| `unlock.png`, `preview*.png` | Lock-screen mark and gallery previews. |
| `neovim.lua`, `vscode.json` | Editor colourschemes. See the note below. |

`tools/make-plates.py` is the generator for the plates (Pillow only). Pass it
another theme's `colors.toml` with `--colors` to render the same five plates
in a sibling palette.

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
