# -*- coding: utf-8 -*-
"""
Regenerate the profile artwork.

    python tools/build.py

Writes assets/hero.svg and assets/stack.svg. Deterministic (fixed seeds), so
re-running gives byte-identical output. Everything is self-contained, pure
SMIL/CSS animated SVG - no JavaScript, no external references - so it renders
and animates when GitHub serves it through its image proxy.

Tweak colors / text / waveforms here, then re-run and commit the assets.
"""
import math, random, io, os

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "..", "assets")

# ---- palette (shared) : cool blue instrument, one warm accent ----
C1, C2, C3, C4 = "#4d9fff", "#34c8f2", "#9d8cff", "#6f92cf"   # azure / cyan-blue / violet / steel(pose)
PT_C, AMBER = "#48b4ff", "#f2b45c"                             # blue / warm accent (actuator, INT8)
DIM, BRIGHT, LABEL, RED = "#6f8fc0", "#d8e8ff", "#4d6a99", "#ff6b6b"


# ============================ waveform generators ============================
def _path(pts):
    d = "M %.1f %.1f" % pts[0]
    for p in pts[1:]:
        d += " L %.1f %.1f" % p
    return d


def emg(center, half, bursts, seed, x0, x1, n, base_noise=1.6):
    r = random.Random(seed)
    pts = []
    for i in range(n):
        x = x0 + (x1 - x0) * i / (n - 1)
        t = i / (n - 1)
        y = r.uniform(-base_noise, base_noise)
        for pos, width, amp, freq in bursts:
            env = math.exp(-((t - pos) ** 2) / (2 * width * width))
            y += env * half * amp * (math.sin(t * freq * 2 * math.pi + seed) + r.uniform(-0.35, 0.35))
        y = max(-half, min(half, y))
        pts.append((x, center - y))
    return _path(pts)


def pose(center, half, x0, x1, n):
    pts = []
    for i in range(n):
        x = x0 + (x1 - x0) * i / (n - 1)
        t = i / (n - 1)
        y = (half * 0.62) * math.sin(t * 2.1 * 2 * math.pi + 0.4) + (half * 0.22) * math.sin(t * 4.7 * 2 * math.pi + 1.1)
        pts.append((x, center - y))
    return _path(pts)


def square(center, half, x0, x1, n, period=0.14):
    pts = []
    for i in range(n):
        x = x0 + (x1 - x0) * i / (n - 1)
        t = i / (n - 1)
        y = half * 0.8 if (int(t / period) % 2 == 0) else -half * 0.8
        pts.append((x, center - y))
    return _path(pts)


def sine(center, half, freq, x0, x1, n):
    pts = []
    for i in range(n):
        x = x0 + (x1 - x0) * i / (n - 1)
        t = i / (n - 1)
        y = half * 0.78 * math.sin(t * freq * 2 * math.pi) + half * 0.15 * math.sin(t * freq * 2.3 * 2 * math.pi + 1)
        pts.append((x, center - y))
    return _path(pts)


def staircase(center, half, steps, x0, x1, n):
    pts = []
    for i in range(n):
        x = x0 + (x1 - x0) * i / (n - 1)
        t = i / (n - 1)
        phase = (t * 2.0) % 1.0
        lvl = math.floor(phase * steps) / (steps - 1)
        pts.append((x, center - (lvl * 2 - 1) * half * 0.85))
    return _path(pts)


# ================================== hero ====================================
def build_hero():
    T = "5s"
    CH = [
        (emg(140, 25, [(0.16, 0.05, 0.9, 46), (0.54, 0.06, 1.0, 52), (0.83, 0.045, 0.8, 44)], 11, 96, 1440, 300),
         140, C1, "CH1", "FDS", "EMG", "0.51 mV", "p1"),
        (emg(213, 25, [(0.30, 0.055, 0.85, 40), (0.68, 0.05, 0.95, 48)], 23, 96, 1440, 300),
         213, C2, "CH2", "EDC", "EMG", "0.38 mV", "p2"),
        (emg(286, 25, [(0.44, 0.05, 0.9, 50), (0.90, 0.04, 0.7, 42)], 37, 96, 1440, 300),
         286, C3, "CH3", "APB", "EMG", "0.44 mV", "p3"),
        (pose(359, 25, 96, 1440, 300), 359, C4, "CH4", "POSE", "VID", "23 fps", "p4"),
    ]
    s = io.StringIO(); W = s.write
    W('<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
      'viewBox="0 0 1600 430" width="1600" height="430" role="img" aria-labelledby="ti de" '
      'preserveAspectRatio="xMidYMid meet" '
      'font-family="ui-monospace, SFMono-Regular, Menlo, \'Courier New\', \'Malgun Gothic\', monospace">\n')
    W('<title id="ti">Hoijun Kim - biosignal and edge-AI researcher</title>\n')
    W('<desc id="de">A dark laboratory oscilloscope reading four looping biosignal channels - three '
      'forearm EMG channels (FDS, EDC, APB) and one video pose channel - with a sweeping scan bar and a '
      'prosthetic gripper that flexes in response, representing muscle signals decoded into motion.</desc>\n')
    W('<defs>\n')
    W('<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#080f1e"/>'
      '<stop offset="0.55" stop-color="#0b1526"/><stop offset="1" stop-color="#05080f"/></linearGradient>\n')
    W('<radialGradient id="crt" cx="0.5" cy="0.44" r="0.75"><stop offset="0" stop-color="#12345c" stop-opacity="0.35"/>'
      '<stop offset="0.7" stop-color="#080f1e" stop-opacity="0.05"/>'
      '<stop offset="1" stop-color="#03060f" stop-opacity="0.85"/></radialGradient>\n')
    W('<linearGradient id="sweep" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#4da3ff" stop-opacity="0"/>'
      '<stop offset="0.78" stop-color="#4da3ff" stop-opacity="0.06"/>'
      '<stop offset="1" stop-color="#cfe4ff" stop-opacity="0.30"/></linearGradient>\n')
    W('<filter id="glow" x="-8%" y="-45%" width="116%" height="190%"><feGaussianBlur stdDeviation="1.35" result="b"/>'
      '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>\n')
    W('<pattern id="grid" width="26" height="26" patternUnits="userSpaceOnUse">'
      '<path d="M26 0H0V26" fill="none" stroke="#183a63" stroke-width="0.6" opacity="0.5"/></pattern>\n')
    W('<clipPath id="screen"><rect x="22" y="98" width="1556" height="304" rx="7"/></clipPath>\n')
    W('<clipPath id="namewipe"><rect x="34" y="28" width="0" height="58">'
      f'<animate attributeName="width" values="0;640;640;640" keyTimes="0;0.34;0.94;1" dur="{T}" '
      'repeatCount="indefinite" calcMode="spline" keySplines="0.2 0.7 0.2 1;0 0 1 1;0 0 1 1"/></rect></clipPath>\n')
    W('</defs>\n')
    W('<rect x="0" y="0" width="1600" height="430" rx="18" fill="#03060d"/>\n')
    W('<rect x="5" y="5" width="1590" height="420" rx="15" fill="url(#bg)" stroke="#1c4066" stroke-width="1.3"/>\n')
    W('<g clip-path="url(#namewipe)">')
    W('<text x="36" y="55" font-size="23" font-weight="700" letter-spacing="1" fill="%s" filter="url(#glow)">'
      'biosignal ML researcher</text>' % BRIGHT)
    W('<text x="37" y="78" font-size="12.5" letter-spacing="0.5" fill="%s">'
      'decoding muscle signals into motion  /  근육 신호를 동작으로</text>' % DIM)
    W('</g>\n')
    W('<text x="1498" y="39" font-size="13" font-weight="700" letter-spacing="1.5" fill="%s">REC</text>' % RED)
    W('<circle cx="1552" cy="34.5" r="4.5" fill="%s"><animate attributeName="opacity" '
      'values="1;1;0.12;0.12;1" keyTimes="0;0.45;0.5;0.55;1" dur="1.6s" repeatCount="indefinite"/></circle>\n' % RED)
    W('<g text-anchor="end">')
    W('<text x="1560" y="62" font-size="12" letter-spacing="0.5" fill="%s">OpenVINO / Lunar Lake NPU</text>' % LABEL)
    W('<text x="1560" y="80" font-size="12" letter-spacing="1" fill="%s">inference '
      '<tspan fill="%s" font-weight="700">LIVE</tspan></text>' % (LABEL, C2))
    W('</g>\n')
    W('<rect x="22" y="98" width="1556" height="304" rx="7" fill="#060e1d"/>\n')
    W('<g clip-path="url(#screen)">\n')
    W('  <rect x="22" y="98" width="1556" height="304" fill="url(#grid)"/>\n')
    for d, cy, col, code, mus, kind, val, pid in CH:
        W('  <line x1="90" y1="%d" x2="1440" y2="%d" stroke="#26497a" stroke-width="0.7" '
          'stroke-dasharray="2 5" opacity="0.6"/>\n' % (cy, cy))
    W('  <rect x="22" y="0" width="1556" height="34" fill="#a9ccff" opacity="0.035">'
      '<animateTransform attributeName="transform" type="translate" values="0,90;0,410;0,90" '
      'dur="7s" repeatCount="indefinite"/></rect>\n')
    for d, cy, col, code, mus, kind, val, pid in CH:
        W('  <path id="%s" d="%s" fill="none" stroke="%s" stroke-width="1.7" stroke-linejoin="round" '
          'stroke-linecap="round" pathLength="1" stroke-dasharray="1 1" stroke-dashoffset="1" filter="url(#glow)">'
          '<animate attributeName="stroke-dashoffset" values="1;0" dur="%s" repeatCount="indefinite" '
          'calcMode="linear"/></path>\n' % (pid, d, col, T))
        W('  <circle r="2.7" fill="#eaf3ff" filter="url(#glow)">'
          '<animateMotion dur="%s" repeatCount="indefinite" calcMode="linear" keyPoints="0;1" keyTimes="0;1">'
          '<mpath xlink:href="#%s"/></animateMotion></circle>\n' % (T, pid))
    W('  <g><rect x="-140" y="98" width="140" height="304" fill="url(#sweep)"/>'
      '<line x1="0" y1="98" x2="0" y2="402" stroke="#d3e6ff" stroke-width="1.1" opacity="0.55"/>'
      '<animateTransform attributeName="transform" type="translate" values="90,0;1440,0" dur="%s" '
      'repeatCount="indefinite" calcMode="linear"/></g>\n' % T)
    W('</g>\n')
    W('<rect x="22" y="98" width="1556" height="304" rx="7" fill="url(#crt)" pointer-events="none"/>\n')
    W('<rect x="22" y="98" width="1556" height="304" rx="7" fill="none" stroke="#2a5688" stroke-width="1"/>\n')
    for d, cy, col, code, mus, kind, val, pid in CH:
        W('<text x="34" y="%d" font-size="12.5" font-weight="700" letter-spacing="0.5" fill="%s">%s</text>' % (cy - 3, col, code))
        W('<text x="34" y="%d" font-size="9" letter-spacing="0.5" fill="%s">%s %s</text>\n' % (cy + 9, LABEL, mus, kind))
        W('<text x="1494" y="%d" text-anchor="end" font-size="10.5" fill="%s">%s</text>\n' % (cy + 3, col, val))
    W('<text x="36" y="392" font-size="10.5" letter-spacing="0.5" fill="%s">'
      '20 mV/div   500 ms/div   fs 2 kHz   TRIG auto</text>\n' % LABEL)
    W('<line x1="1500" y1="110" x2="1500" y2="390" stroke="#1e4270" stroke-width="1" opacity="0.7"/>\n')
    W('<text x="1538" y="132" text-anchor="middle" font-size="9" letter-spacing="1" fill="%s">DECODE</text>\n' % LABEL)
    W('<text x="1538" y="146" text-anchor="middle" font-size="8.5" letter-spacing="0.5" fill="%s">-&gt; GRIP</text>\n' % AMBER)
    W('<g transform="translate(1538,250)" stroke-linecap="round">\n')
    W('  <line x1="0" y1="36" x2="0" y2="16" stroke="%s" stroke-width="5"/>\n' % DIM)
    W('  <rect x="-8" y="8" width="16" height="8" rx="4" fill="%s"/>\n' % DIM)
    W('  <circle cx="0" cy="12" r="3" fill="%s"/>\n' % AMBER)
    W('  <g transform="rotate(0 0 12)"><line x1="0" y1="12" x2="-13" y2="-14" stroke="%s" stroke-width="4.5"/>'
      '<line x1="-13" y1="-14" x2="-20" y2="-30" stroke="%s" stroke-width="4"/>'
      '<animateTransform attributeName="transform" type="rotate" values="0 0 12;0 0 12;26 0 12;26 0 12;0 0 12" '
      'keyTimes="0;0.42;0.56;0.82;1" dur="%s" repeatCount="indefinite" calcMode="spline" '
      'keySplines="0.4 0 0.2 1;0.4 0 0.2 1;0.4 0 0.2 1;0.4 0 0.2 1"/></g>\n' % (AMBER, AMBER, T))
    W('  <g transform="rotate(0 0 12)"><line x1="0" y1="12" x2="13" y2="-14" stroke="%s" stroke-width="4.5"/>'
      '<line x1="13" y1="-14" x2="20" y2="-30" stroke="%s" stroke-width="4"/>'
      '<animateTransform attributeName="transform" type="rotate" values="0 0 12;0 0 12;-26 0 12;-26 0 12;0 0 12" '
      'keyTimes="0;0.42;0.56;0.82;1" dur="%s" repeatCount="indefinite" calcMode="spline" '
      'keySplines="0.4 0 0.2 1;0.4 0 0.2 1;0.4 0 0.2 1;0.4 0 0.2 1"/></g>\n' % (AMBER, AMBER, T))
    W('</g>\n')
    W('<text x="1538" y="372" text-anchor="middle" font-size="9" letter-spacing="1" fill="%s">ACTUATOR</text>\n' % LABEL)
    W('</svg>\n')
    return s.getvalue()


# ================================== stack ===================================
def build_stack():
    T = "4.5s"
    ROWS = [
        ("PY",  "Python",         "signal / ML",       C1,   emg(92, 13, [(0.35, 0.08, 0.9, 22), (0.7, 0.07, 0.9, 22)], 7, 340, 1020, 200, 1.1), 92,  "burst"),
        ("PT",  "PyTorch",        "deep learning",     PT_C, emg(132, 13, [(0.25, 0.06, 0.9, 34), (0.55, 0.05, 0.9, 34), (0.82, 0.05, 0.9, 34)], 15, 340, 1020, 200, 1.1), 132, "dense"),
        ("GO",  "Go",             "systems / desktop", C2,   square(172, 13, 340, 1020, 200), 172, "square"),
        ("TS",  "Svelte + TS",    "reactive UI",       C4,   sine(212, 13, 3.0, 340, 1020, 200), 212, "sine"),
        ("AI",  "OpenVINO / NPU", "edge inference",    AMBER, staircase(252, 13, 7, 340, 1020, 200), 252, "INT8"),
        ("WEB", "SCSS / Web",     "frontend",          C3,   sine(292, 13, 2.2, 340, 1020, 200), 292, "sine"),
    ]
    s = io.StringIO(); W = s.write
    W('<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
      'viewBox="0 0 1200 330" width="1200" height="330" role="img" aria-labelledby="ti de" '
      'preserveAspectRatio="xMidYMid meet" '
      'font-family="ui-monospace, SFMono-Regular, Menlo, \'Courier New\', \'Malgun Gothic\', monospace">\n')
    W('<title id="ti">Tech stack - probe bank</title>\n')
    W('<desc id="de">An oscilloscope probe bank where each technology is a channel with a mini signal: '
      'Python and PyTorch as EMG-style bursts, Go as a square wave, Svelte and TypeScript as a smooth sine, '
      'OpenVINO NPU as an INT8 quantization staircase, and SCSS web as a soft sine.</desc>\n')
    W('<defs>')
    W('<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#080f1e"/>'
      '<stop offset="1" stop-color="#05080f"/></linearGradient>')
    W('<filter id="glow" x="-6%" y="-60%" width="112%" height="220%"><feGaussianBlur stdDeviation="1.15" result="b"/>'
      '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')
    W('<pattern id="grid" width="26" height="26" patternUnits="userSpaceOnUse">'
      '<path d="M26 0H0V26" fill="none" stroke="#183a63" stroke-width="0.6" opacity="0.4"/></pattern>')
    W('<clipPath id="scr"><rect x="290" y="66" width="760" height="248" rx="4"/></clipPath>')
    W('</defs>\n')
    W('<rect x="0" y="0" width="1200" height="330" rx="16" fill="#03060d"/>\n')
    W('<rect x="5" y="5" width="1190" height="320" rx="13" fill="url(#bg)" stroke="#1c4066" stroke-width="1.2"/>\n')
    W('<text x="26" y="42" font-size="17" font-weight="700" letter-spacing="2" fill="%s">PROBE BANK</text>\n' % BRIGHT)
    W('<text x="176" y="42" font-size="12" letter-spacing="0.5" fill="%s">/ tech stack /  기술 스택</text>\n' % DIM)
    W('<text x="1174" y="42" text-anchor="end" font-size="11" letter-spacing="1" fill="%s">6 CHANNELS</text>\n' % LABEL)
    W('<rect x="290" y="66" width="760" height="248" rx="4" fill="#060e1d" stroke="#1e4270" stroke-width="0.8"/>\n')
    W('<g clip-path="url(#scr)">')
    W('<rect x="290" y="66" width="760" height="248" fill="url(#grid)"/>')
    for probe, tech, note, col, d, cy, sig in ROWS:
        W('<line x1="330" y1="%d" x2="1030" y2="%d" stroke="#26497a" stroke-width="0.6" stroke-dasharray="2 5" opacity="0.5"/>' % (cy, cy))
    for i, (probe, tech, note, col, d, cy, sig) in enumerate(ROWS):
        dly = "%.2fs" % (i * 0.22)
        W('<path d="%s" fill="none" stroke="%s" stroke-width="1.6" stroke-linejoin="round" stroke-linecap="round" '
          'pathLength="1" stroke-dasharray="1 1" stroke-dashoffset="1" filter="url(#glow)">'
          '<animate attributeName="stroke-dashoffset" values="1;0" dur="%s" begin="%s" repeatCount="indefinite" calcMode="linear"/></path>'
          % (d, col, T, dly))
    W('</g>\n')
    for probe, tech, note, col, d, cy, sig in ROWS:
        W('<rect x="26" y="%d" width="36" height="20" rx="3" fill="#0b1d34" stroke="%s" stroke-width="0.9"/>' % (cy - 10, col))
        W('<text x="44" y="%d" text-anchor="middle" font-size="11" font-weight="700" fill="%s">%s</text>' % (cy + 4, col, probe))
        W('<text x="78" y="%d" font-size="14.5" font-weight="700" fill="%s">%s</text>' % (cy + 1, BRIGHT, tech))
        W('<text x="78" y="%d" font-size="9" letter-spacing="0.3" fill="%s">%s</text>' % (cy + 14, LABEL, note))
        W('<text x="1174" y="%d" text-anchor="end" font-size="10.5" letter-spacing="0.5" fill="%s">%s</text>\n' % (cy + 4, col, sig))
    W('</svg>\n')
    return s.getvalue()


def main():
    os.makedirs(ASSETS, exist_ok=True)
    for name, data in (("hero.svg", build_hero()), ("stack.svg", build_stack())):
        p = os.path.join(ASSETS, name)
        with open(p, "w", encoding="utf-8") as f:
            f.write(data)
        print("wrote", os.path.normpath(p), len(data), "bytes")


if __name__ == "__main__":
    main()
