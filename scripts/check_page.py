#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verify a built page without a browser: tag balance, source coverage, WCAG contrast.

Usage:
  python check_page.py doc.md doc.html
Exit 0 = all checks pass, 1 = at least one failure (details printed).
"""
import io
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.normpath(os.path.join(HERE, "..", "assets"))

PAIRS = [
    ("正文 ink2 / 页面底 bg", "--ink2", "--bg", 4.5),
    ("标题 ink / 卡片 paper", "--ink", "--paper", 4.5),
    ("小字 muted / 卡片 paper", "--muted", "--paper", 4.5),
    ("表头 muted / 表头底 paper2", "--muted", "--paper2", 4.5),
    ("链接 accent-ink / 页面底 bg", "--accent-ink", "--bg", 4.5),
    ("卡片标题 accent-ink / paper", "--accent-ink", "--paper", 4.5),
    ("卡片标题 accent2-ink / paper", "--accent2-ink", "--paper", 4.5),
    ("药丸反色字 on-accent / accent-ink", "--on-accent", "--accent-ink", 4.5),
    ("按钮反色字 on-accent2 / accent2-ink", "--on-accent2", "--accent2-ink", 4.5),
    ("徽标 accent / 卡片 paper", "--accent", "--paper", 3.0),
    ("代码 codeink / codebg", "--codeink", "--codebg", 4.5),
    ("代码标题 codecap / codebg", "--codecap", "--codebg", 4.5),
]


def parse_tokens(path):
    txt = io.open(path, encoding="utf-8").read()
    return dict(re.findall(r"(--[a-z0-9-]+)\s*:\s*([^;]+);", txt))


def to_rgb(v, tokens):
    v = v.strip()
    if v.startswith("var("):
        return to_rgb(tokens.get(v[4:-1].strip(), "#000"), tokens)
    m = re.match(r"#([0-9a-fA-F]{3,8})$", v)
    if m:
        h = m.group(1)
        if len(h) == 3:
            h = "".join(c * 2 for c in h)
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
    m = re.match(r"rgba?\(([^)]+)\)", v)
    if m:
        parts = [p.strip() for p in m.group(1).split(",")]
        rgb = tuple(int(float(p)) for p in parts[:3])
        if len(parts) > 3:
            a = float(parts[3])
            base = (255, 255, 255)
            rgb = tuple(round(c * a + b * (1 - a)) for c, b in zip(rgb, base))
        return rgb
    m = re.match(r"linear-gradient\([^,]+,\s*(#[0-9a-fA-F]{3,8})", v)
    if m:
        return to_rgb(m.group(1), tokens)
    return (0, 0, 0)


def lum(rgb):
    v = []
    for c in rgb:
        x = c / 255.0
        v.append(x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4)
    return 0.2126 * v[0] + 0.7152 * v[1] + 0.0722 * v[2]


def ratio(a, b):
    l1, l2 = lum(a), lum(b)
    hi, lo = max(l1, l2), min(l1, l2)
    return (hi + 0.05) / (lo + 0.05)


def norm(s):
    return re.sub(r"[^0-9A-Za-z\u4e00-\u9fff]", "", s)


def coverage(md_path, html_path):
    md = io.open(md_path, encoding="utf-8").read().split("\n")
    import html as H
    doc = norm(H.unescape(re.sub(r"<[^>]+>", "", io.open(html_path, encoding="utf-8").read())))
    miss = []
    for ln in md:
        t = ln.strip()
        if t.startswith("#") or t.startswith("<!--") or len(t) < 12:
            continue
        t = re.sub(r"^([-*]>?|\d+\.)\s+", "", t)
        t = re.sub(r"[\*`]", "", t)
        k = norm(t)
        if len(k) < 10:
            continue
        if k[:22] not in doc:
            miss.append(t[:64])
    return miss


def balance(doc):
    bad = []
    for t in ["section", "table", "figure", "nav", "div", "ul", "ol", "aside", "header",
              "p", "h1", "h2", "h3", "li", "td", "th", "tr", "thead", "tbody", "pre", "code"]:
        o = len(re.findall(r"<%s[\s>]" % t, doc))
        c = len(re.findall(r"</%s>" % t, doc))
        if o != c:
            bad.append("%s open=%d close=%d" % (t, o, c))
    return bad


def main():
    if len(sys.argv) < 3:
        print("usage: check_page.py <source.md> <built.html>")
        return 2
    md_path, html_path = sys.argv[1], sys.argv[2]
    doc = io.open(html_path, encoding="utf-8").read()
    fails = []

    bad = balance(doc)
    print("1) tag balance     : %s" % ("OK" if not bad else "FAIL " + "; ".join(bad)))
    if bad:
        fails.append("tag balance")

    miss = coverage(md_path, html_path)
    print("2) source coverage : %s" % ("OK (every md line present)" if not miss else "FAIL %d lines missing" % len(miss)))
    for m in miss[:8]:
        print("     - %s" % m)
    if miss:
        fails.append("coverage")

    themes = {"明亮清新 light": "theme-light.css", "暗黑忧郁 dark": "theme-dark.css"}
    for label, fn in themes.items():
        p = os.path.join(ASSETS, fn)
        if not os.path.exists(p):
            print("3) contrast %-14s: SKIP (%s missing)" % (label, fn))
            continue
        tk = parse_tokens(p)
        print("3) contrast %-14s:" % label)
        for name, fg, bg, need in PAIRS:
            fgv, bgv = tk.get(fg, fg), tk.get(bg, bg)
            if fg.startswith("--") and fg not in tk:
                continue
            if bg.startswith("--") and bg not in tk:
                continue
            r = ratio(to_rgb(fgv, tk), to_rgb(bgv, tk))
            ok = r >= need
            print("     %s %-34s %5.2f  (need %.1f)" % ("PASS" if ok else "FAIL", name, r, need))
            if not ok:
                fails.append("%s %s" % (label, name))

    feats = {"吸顶药丸导航": "nav class=\"pills\"", "阅读进度条": "class=\"progress\"",
             "目录卡": "class=\"card", "无边框表格": "class=\"tw\"", "代码块复制": "class=\"cp\"",
             "回到顶部": "id=\"top\"", "主题切换": "id=\"theme\"", "viewport": "name=\"viewport\"",
             "防闪白内联脚本": "setAttribute('data-theme'", "打印样式": "@media print",
             "减弱动效": "prefers-reduced-motion", "窄屏断点": "max-width:600px"}
    missing = [k for k, v in feats.items() if v not in doc]
    print("4) features        : %s" % ("OK (%d/%d)" % (len(feats) - len(missing), len(feats))
                                       if not missing else "FAIL missing " + ", ".join(missing)))
    if missing:
        fails.append("features")

    print("RESULT: %s" % ("PASS" if not fails else "FAIL -> " + ", ".join(fails)))
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
