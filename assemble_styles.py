#!/usr/bin/env python3
"""Assemble styles/NN-*.svg (one 189 x 72 pt label each) onto the Avery 30-up sheet.

Writes label-styles.svg next to this script: US Letter, 3 columns x 10 rows,
column pitch 198 pt, row pitch 72 pt. Each label is clipped to its die shape.
"""
import glob
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 189.0, 72.0
X0, Y0, PX, PY = 13.5, 36.0, 198.0, 72.0


def inner(svg_text):
    text = re.sub(r"<\?xml.*?\?>", "", svg_text, flags=re.S)
    text = re.sub(r"<!DOCTYPE.*?>", "", text, flags=re.S)
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    m = re.search(r"<svg\b[^>]*>(.*)</svg\s*>", text, flags=re.S)
    if not m:
        raise ValueError("no <svg> root")
    return m.group(1).strip()


def build():
    files = sorted(glob.glob(os.path.join(HERE, "styles", "[0-9][0-9]-*.svg")))
    clips, labels, outlines, names = [], [], [], []
    for n, path in enumerate(files):
        slug = os.path.splitext(os.path.basename(path))[0]
        x, y = X0 + (n % 3) * PX, Y0 + (n // 3) * PY
        clips.append(f'<clipPath id="die{n + 1:02d}"><rect x="0" y="0" width="{W}" height="{H}" rx="6.75"/></clipPath>')
        with open(path) as f:
            body = inner(f.read())
        labels.append(f'<g id="L{slug}" transform="translate({x} {y})"><g clip-path="url(#die{n + 1:02d})">{body}</g></g>')
        outlines.append(f'<rect x="{x}" y="{y}" width="{W}" height="{H}" rx="6.75" fill="none" stroke="#9AA0A6" stroke-width="0.5"/>')
        names.append(slug)
    svg = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<svg xmlns="http://www.w3.org/2000/svg" width="612" height="792" viewBox="0 0 612 792">\n'
           f'<defs>{"".join(clips)}</defs>\n'
           '<g id="Designs">\n' + "\n".join(labels) + '\n</g>\n'
           '<g id="Die-lines">\n' + "\n".join(outlines) + '\n</g>\n</svg>\n')
    return svg, names


if __name__ == "__main__":
    svg, names = build()
    out = os.path.join(HERE, "label-styles.svg")
    with open(out, "w") as f:
        f.write(svg)
    print("wrote", out, "with", len(names), "labels")
    for n in names:
        print(" ", n)
