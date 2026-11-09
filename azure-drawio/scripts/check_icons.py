#!/usr/bin/env python3
"""Check icon paths against the icons actually bundled in the installed draw.io.

A wrong icon path is silent: the XML is valid, the validator passes, and the
diagram renders with a grey broken-image placeholder where the icon should be.
This reads the shape list straight out of draw.io's app.asar and tells you which
paths do not exist, with the closest real alternatives.

Usage:
    python3 check_icons.py                  # check reference/icons.md
    python3 check_icons.py diagram.drawio   # check a generated diagram too
    python3 check_icons.py --list storage   # list bundled icons matching a term

Requires the draw.io desktop app. Exit 0 = all paths resolve, 1 = some do not,
2 = draw.io not found (skipped, not a failure).
"""

# Windows consoles/pipes default to a legacy code page; force UTF-8 so labels and
# messages containing arrows, middots or Norwegian letters never raise UnicodeEncodeError.
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
import difflib
import json
import os
import re
import struct
import sys

ASAR_CANDIDATES = [
    "/Applications/draw.io.app/Contents/Resources/app.asar",
    os.path.expanduser("~/Applications/draw.io.app/Contents/Resources/app.asar"),
    "/opt/homebrew/lib/node_modules/drawio/app.asar",
    "C:/Program Files/draw.io/resources/app.asar",
]
HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)


def find_asar():
    for p in ASAR_CANDIDATES:
        if os.path.isfile(p):
            return p
    env = os.environ.get("DRAWIO_ASAR")
    return env if env and os.path.isfile(env) else None


def bundled_icons(asar_path):
    """Parse the asar header (a JSON blob at a known offset) and list img/lib SVGs."""
    with open(asar_path, "rb") as f:
        header = f.read(16)
        json_len = struct.unpack("<I", header[12:16])[0]
        meta = json.loads(f.read(json_len).decode("utf-8"))

    def walk(node, prefix=""):
        for name, val in node.get("files", {}).items():
            path = f"{prefix}/{name}" if prefix else name
            if "files" in val:
                yield from walk(val, path)
            else:
                yield path

    out = set()
    for entry in walk(meta):
        i = entry.find("img/lib/")
        if i != -1 and entry.endswith(".svg"):
            out.add(entry[i:])
    return out


def referenced_paths(target):
    text = open(target, encoding="utf-8").read()
    if target.endswith((".drawio", ".xml")):
        return sorted(set(re.findall(r"image=([^;\"]+\.svg)", text)))
    return sorted(set(re.findall(r"`(img/lib/[^`]+\.svg)`", text)))


def suggest(path, have):
    stem = path.rsplit("/", 1)[-1].replace(".svg", "")
    key = stem.lower().rstrip("s")
    hits = sorted(h for h in have if key in h.rsplit("/", 1)[-1].lower())
    return hits[:5] or difflib.get_close_matches(path, have, n=5, cutoff=0.55)


def main(argv):
    asar = find_asar()
    if not asar:
        print("draw.io not found — skipping icon check.")
        print("Install the desktop app, or set DRAWIO_ASAR to its app.asar path.")
        return 2

    have = bundled_icons(asar)

    if "--list" in argv:
        term = argv[argv.index("--list") + 1].lower()
        for h in sorted(h for h in have if term in h.lower()):
            print(" ", h)
        return 0

    targets = [a for a in argv[1:] if not a.startswith("--")]
    if not targets:
        targets = [os.path.join(SKILL, "reference", "icons.md")]

    failed = False
    for target in targets:
        used = referenced_paths(target)
        bad = [p for p in used if p not in have]
        rel = os.path.relpath(target, SKILL)
        print(f"== {rel}  ({len(used)} icon paths, {len(have)} bundled)")
        for p in bad:
            failed = True
            print(f"  ERROR   '{p}' is not bundled with draw.io")
            for s in suggest(p, have):
                print(f"          did you mean: {s}")
        if not bad:
            print("  OK      every icon path resolves")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
