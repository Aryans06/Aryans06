#!/usr/bin/env python3
"""Generate a self-contained animated 'flight radar' SVG of the tech stack.

Logos are fetched from skillicons.dev (same names already used in the README)
and embedded as base64 data URIs so the SVG renders standalone on GitHub.
"""
import base64
import math
import urllib.request

CX, CY, R = 320, 330, 290  # radar center + radius

# category -> color
CATS = {
    "Languages":      "#F85D7F",
    "Frontend":       "#58A6FF",
    "Backend & DB":   "#39D353",
    "DevOps & Cloud": "#F8D866",
    "AI & Tooling":   "#BC8CFF",
}

# (skillicon name, label, category, angle_deg, radius_fraction)
ITEMS = [
    ("cpp",        "C++",        "Languages",      250, 0.50),
    ("ts",         "TS",         "Languages",      222, 0.78),
    ("python",     "Python",     "Languages",      238, 0.62),
    ("go",         "Go",         "Languages",      268, 0.86),
    ("rust",       "Rust",       "Languages",      205, 0.45),

    ("react",      "React",      "Frontend",       300, 0.55),
    ("nextjs",     "Next.js",    "Frontend",       325, 0.80),
    ("vue",        "Vue",        "Frontend",       290, 0.80),
    ("tailwind",   "Tailwind",   "Frontend",       345, 0.50),

    ("nodejs",     "Node",       "Backend & DB",    15, 0.55),
    ("express",    "Express",    "Backend & DB",    40, 0.80),
    ("mongodb",    "Mongo",      "Backend & DB",    65, 0.62),
    ("postgres",   "Postgres",   "Backend & DB",    30, 0.42),
    ("redis",      "Redis",      "Backend & DB",    75, 0.86),

    ("docker",     "Docker",     "DevOps & Cloud", 100, 0.55),
    ("kubernetes", "K8s",        "DevOps & Cloud", 125, 0.80),
    ("aws",        "AWS",        "DevOps & Cloud", 110, 0.42),
    ("gcp",        "GCP",        "DevOps & Cloud", 145, 0.70),

    ("tensorflow", "TensorFlow", "AI & Tooling",   165, 0.55),
    ("pytorch",    "PyTorch",    "AI & Tooling",   185, 0.78),
    ("git",        "Git",        "AI & Tooling",   158, 0.42),
]


def fetch_data_uri(name):
    url = f"https://skillicons.dev/icons?i={name}&theme=dark"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        raw = r.read()
    b64 = base64.b64encode(raw).decode()
    return f"data:image/svg+xml;base64,{b64}"


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def pos(angle_deg, rfrac):
    a = math.radians(angle_deg)
    return CX + R * rfrac * math.cos(a), CY - R * rfrac * math.sin(a)


def main():
    W, H = 900, 660
    out = []
    out.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
        f'font-family="\'Courier New\', monospace">'
    )
    # defs
    out.append('<defs>')
    out.append(
        '<radialGradient id="bg" cx="50%" cy="50%" r="75%">'
        '<stop offset="0%" stop-color="#0d2018"/>'
        '<stop offset="100%" stop-color="#070b10"/></radialGradient>'
    )
    out.append(
        '<linearGradient id="sweep" x1="0" y1="0" x2="1" y2="0">'
        '<stop offset="0%" stop-color="#39D353" stop-opacity="0"/>'
        '<stop offset="100%" stop-color="#39D353" stop-opacity="0.35"/>'
        '</linearGradient>'
    )
    out.append(
        '<filter id="glow" x="-50%" y="-50%" width="200%" height="200%">'
        '<feGaussianBlur stdDeviation="2.2" result="b"/>'
        '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>'
        '</filter>'
    )
    out.append('</defs>')

    # backdrop panel
    out.append(f'<rect x="0" y="0" width="{W}" height="{H}" rx="18" fill="#070b10"/>')
    out.append(f'<circle cx="{CX}" cy="{CY}" r="{R+8}" fill="url(#bg)"/>')

    # range rings
    for i in range(1, 5):
        rr = R * i / 4
        out.append(
            f'<circle cx="{CX}" cy="{CY}" r="{rr:.1f}" fill="none" '
            f'stroke="#1f6f4d" stroke-opacity="0.55" stroke-width="1"/>'
        )
    out.append(
        f'<circle cx="{CX}" cy="{CY}" r="{R}" fill="none" '
        f'stroke="#39D353" stroke-opacity="0.45" stroke-width="2"/>'
    )

    # radial bearing lines every 30 deg
    for d in range(0, 360, 30):
        x, y = pos(d, 1.0)
        out.append(
            f'<line x1="{CX}" y1="{CY}" x2="{x:.1f}" y2="{y:.1f}" '
            f'stroke="#1f6f4d" stroke-opacity="0.35" stroke-width="1"/>'
        )

    # compass labels
    for d, lab in [(90, "N"), (0, "E"), (270, "S"), (180, "W")]:
        x, y = pos(d, 1.10)
        out.append(
            f'<text x="{x:.1f}" y="{y+4:.1f}" fill="#39D353" fill-opacity="0.8" '
            f'font-size="14" font-weight="bold" text-anchor="middle">{lab}</text>'
        )

    # rotating sweep (group rotates clockwise around center)
    sweep = []
    lx, ly = R, 0  # leading edge (local coords, center at origin)
    ex, ey = R * math.cos(math.radians(55)), R * math.sin(math.radians(55))
    sweep.append(
        f'<path d="M 0 0 L {lx:.1f} {ly:.1f} '
        f'A {R} {R} 0 0 1 {ex:.1f} {ey:.1f} Z" fill="url(#sweep)"/>'
    )
    sweep.append(
        f'<line x1="0" y1="0" x2="{R}" y2="0" stroke="#5dff9c" '
        f'stroke-width="2" filter="url(#glow)"/>'
    )
    out.append(f'<g transform="translate({CX},{CY})">')
    out.append("".join(sweep))
    out.append(
        f'<animateTransform attributeName="transform" type="rotate" '
        f'from="0 0 0" to="360 0 0" dur="5s" repeatCount="indefinite" additive="sum"/>'
    )
    out.append('</g>')

    # center hub
    out.append(f'<circle cx="{CX}" cy="{CY}" r="4" fill="#5dff9c" filter="url(#glow)"/>')

    # blips
    for idx, (name, label, cat, ang, rf) in enumerate(ITEMS):
        x, y = pos(ang, rf)
        color = CATS[cat]
        uri = fetch_data_uri(name)
        begin = f"{(idx % 7) * 0.4:.1f}s"
        out.append(f'<g>')
        # pulsing contact ring
        out.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="20" fill="none" '
            f'stroke="{color}" stroke-width="1.2">'
            f'<animate attributeName="stroke-opacity" values="0.7;0.1;0.7" '
            f'dur="3s" begin="{begin}" repeatCount="indefinite"/>'
            f'<animate attributeName="r" values="17;21;17" '
            f'dur="3s" begin="{begin}" repeatCount="indefinite"/></circle>'
        )
        # logo
        out.append(
            f'<image x="{x-15:.1f}" y="{y-15:.1f}" width="30" height="30" '
            f'xlink:href="{uri}"/>'
        )
        # label
        out.append(
            f'<text x="{x:.1f}" y="{y+30:.1f}" fill="{color}" font-size="10" '
            f'text-anchor="middle">{esc(label)}</text>'
        )
        out.append('</g>')

    # ---- right HUD panel ----
    px = 660
    out.append(f'<text x="{px}" y="70" fill="#F8D866" font-size="26" font-weight="bold">TECH RADAR</text>')
    out.append(f'<line x1="{px}" y1="84" x2="{W-30}" y2="84" stroke="#1f6f4d" stroke-width="1"/>')
    out.append(
        f'<circle cx="{px+6}" cy="108" r="5" fill="#39D353">'
        f'<animate attributeName="fill-opacity" values="1;0.2;1" dur="1.4s" repeatCount="indefinite"/></circle>'
    )
    out.append(f'<text x="{px+20}" y="113" fill="#39D353" font-size="14">STATUS: SCANNING</text>')
    out.append(f'<text x="{px}" y="142" fill="#8b949e" font-size="13">CONTACTS: {len(ITEMS)}</text>')

    out.append(f'<text x="{px}" y="186" fill="#c9d1d9" font-size="13" font-weight="bold">CLASSIFICATION</text>')
    ly = 214
    for cat, color in CATS.items():
        count = sum(1 for it in ITEMS if it[2] == cat)
        out.append(f'<rect x="{px}" y="{ly-11}" width="13" height="13" rx="2" fill="{color}"/>')
        out.append(f'<text x="{px+22}" y="{ly}" fill="#c9d1d9" font-size="12.5">{esc(cat)}</text>')
        out.append(f'<text x="{W-30}" y="{ly}" fill="#8b949e" font-size="12.5" text-anchor="end">{count:02d}</text>')
        ly += 30

    out.append(f'<text x="{px}" y="{ly+24}" fill="#8b949e" font-size="11" font-opacity="0.7">// full stack + ai operator</text>')
    out.append(f'<text x="{px}" y="{ly+44}" fill="#8b949e" font-size="11" font-opacity="0.7">// vector: hackathons</text>')

    out.append('</svg>')

    svg = "".join(out)
    with open("assets/tech-radar.svg", "w") as f:
        f.write(svg)
    print(f"wrote assets/tech-radar.svg ({len(svg)} bytes, {len(ITEMS)} contacts)")


if __name__ == "__main__":
    main()
