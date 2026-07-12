#!/usr/bin/env python3
"""Zero-external-asset-host gate for FFC-EX static sites.

Fails CI if any *asset* (stylesheet, script, image, font, media, poster,
preload/prefetch target, or CSS url()) is loaded from a host other than the
repository itself. Outbound <a> hyperlinks to other organizations are allowed
and ignored; a small allowlist of embed/social hosts is permitted because they
appear only as iframes or links, never as page-blocking assets.

Usage: python scripts/check_assets.py [root_dir]   (default: repo root = ".")
Exit code 0 = clean, 1 = external asset host(s) found.
"""
import os
import re
import sys
from html.parser import HTMLParser
from urllib.parse import urlparse

ROOT = sys.argv[1] if len(sys.argv) > 1 else "."

# Hosts that are allowed to appear (as iframe embeds / outbound links only).
# These never load render-blocking assets into the page.
ALLOWED_EMBED_HOSTS = {
    "www.youtube.com", "youtube.com", "youtu.be", "www.youtube-nocookie.com",
    "youtube-nocookie.com", "player.vimeo.com", "vimeo.com",
    "www.facebook.com", "facebook.com", "web.facebook.com",
    "www.google.com", "google.com", "docs.google.com", "forms.gle",
    "calendar.google.com", "maps.google.com", "www.instagram.com",
    "platform.twitter.com",
}

# Asset-bearing attributes we police.
ASSET_ATTRS = {"src", "srcset", "poster", "data-src", "data-srcset"}

problems = []


class AssetParser(HTMLParser):
    def __init__(self, path):
        super().__init__(convert_charrefs=True)
        self.path = path

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        # <link> is an asset only for stylesheet/preload/prefetch/icon/font
        if tag == "link":
            rel = (d.get("rel") or "").lower()
            if any(k in rel for k in ("stylesheet", "preload", "prefetch", "icon", "font")):
                self._check(d.get("href"), tag, "href")
            return
        # <a> hyperlinks are outbound navigation, not assets — ignore href.
        if tag == "a":
            return
        for attr, val in d.items():
            if attr in ASSET_ATTRS:
                self._check(val, tag, attr)

    def _check(self, val, tag, attr):
        if not val:
            return
        # srcset: multiple "url size" candidates
        candidates = []
        if "srcset" in attr:
            for part in val.split(","):
                u = part.strip().split(" ")[0].strip()
                if u:
                    candidates.append(u)
        else:
            candidates.append(val.strip())
        for u in candidates:
            _flag(u, self.path, f"<{tag} {attr}>")


CSS_URL_RE = re.compile(r"url\(\s*['\"]?([^)'\"]+)['\"]?\s*\)")
CSS_IMPORT_RE = re.compile(r"@import\s+['\"]([^'\"]+)['\"]")


def _flag(u, path, ctx):
    u = u.strip()
    if not u or u.startswith(("data:", "#", "mailto:", "tel:", "javascript:", "blob:", "about:")):
        return
    p = urlparse(u)
    if not p.netloc:
        return  # relative / same-repo path
    host = p.netloc.lower()
    if host in ALLOWED_EMBED_HOSTS:
        return
    problems.append(f"{path}: external asset host '{host}'  ({ctx})  {u}")


def scan_html(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        try:
            AssetParser(path).feed(f.read())
        except Exception as e:  # noqa: BLE001
            print(f"WARN: parse error in {path}: {e}")


def scan_css(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        css = f.read()
    for m in CSS_URL_RE.finditer(css):
        _flag(m.group(1), path, "css url()")
    for m in CSS_IMPORT_RE.finditer(css):
        _flag(m.group(1), path, "css @import")


for dirpath, dirnames, filenames in os.walk(ROOT):
    if ".git" in dirpath.split(os.sep):
        continue
    for fn in filenames:
        full = os.path.join(dirpath, fn)
        low = fn.lower()
        if low.endswith((".html", ".htm")):
            scan_html(full)
        elif low.endswith(".css"):
            scan_css(full)

if problems:
    print("FAIL: external asset hosts found (must be localized):\n")
    for p in sorted(set(problems)):
        print("  " + p)
    print(f"\n{len(set(problems))} external asset reference(s).")
    sys.exit(1)

print("OK: zero external asset hosts.")
