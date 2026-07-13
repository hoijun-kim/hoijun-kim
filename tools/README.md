# tools

Asset pipeline for the profile artwork.

```sh
python tools/build.py
```

Regenerates `assets/hero.svg` and `assets/stack.svg` from code. Deterministic
(fixed seeds) - same input, byte-identical output. The SVGs are self-contained
and animate with pure SMIL / CSS (no JavaScript, no external references), which
is what lets them animate when GitHub serves them through its image proxy.

Edit colors, text, or waveforms at the top of `build.py`, re-run, and commit
the regenerated `assets/`.

- `hero.svg` - EMG oscilloscope: 3 forearm EMG channels (FDS / EDC / APB) + a
  video pose channel, a sweeping scan bar, and a prosthetic gripper that flexes
  on each burst (muscle signal -> motion).
- `stack.svg` - "probe bank": each technology drawn as a channel whose waveform
  encodes its character (Go = square wave, OpenVINO/NPU = INT8 staircase, etc).

Preview locally by opening an SVG in a browser (animations play), or render a
still frame with headless Chrome.
