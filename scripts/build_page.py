#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Markdown -> single-file HTML page in the "简洁风格" design system.

Ships BOTH themes in one file (light = 明亮清新, dark = 暗黑忧郁) plus a
tri-state toggle (浅色 / 深色 / 跟随系统) remembered in localStorage.
--theme only decides which one paints first.

Usage:
  python build_page.py doc.md -o doc.html [--theme light|dark|auto] [--fragment]
                        [--title "标题"] [--store-key my-doc-theme]

Directives (HTML comments in the source .md, all optional):
  <!-- hero-kicker: 暖纸编辑风 -->
  <!-- hero-lede: 一句话导语 -->
  <!-- chips: 标签一 | 标签二 -->
  <!-- cards: 01|标题|说明|#s2|a -->   one per line, 5th field a|b = accent colour
  <!-- foot: 页脚一行字 -->
Heading suffixes: "## 3. 检验过程 {pill:验收}" sets the pill label, "{alt}"
switches that section to the second accent colour.

Supported markdown subset: # / ## / ### headings, | tables |, ``` fences,
- and 1. lists with indented continuation lines, > notes, --- dividers,
**bold**, `code`, [text](url).
"""
import argparse
import html
import io
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "..", "assets")
CN = ["一", "二", "三", "四", "五", "六", "七", "八", "九", "十",
      "十一", "十二", "十三", "十四", "十五", "十六", "十七", "十八", "十九", "二十"]


def esc(t):
    return html.escape(t, quote=False)


def inline(t):
    """Escape, then apply **bold** / `code` / [t](u). Code spans are split out
    first so their contents never see markdown substitution."""
    out = []
    for i, part in enumerate(re.split(r"`([^`]+)`", t)):
        if i % 2:
            out.append("<code>%s</code>" % esc(part))
            continue
        p = esc(part)
        p = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", r'<a href="\2">\1</a>', p)
        p = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", p)
        out.append(p)
    return "".join(out)


def cells(row):
    return [c.strip() for c in row.strip().strip("|").split("|")]


def is_sep(row):
    return set(row.replace("|", "").replace(" ", "")) <= {"-", ":"} and "-" in row


def directives(md):
    """Pull the optional <!-- key: value --> directives out of the source."""
    d = {"cards": []}
    src = re.sub(r"(?ms)^```.*?^```", "", md)
    for m in re.finditer(r"<!--\s*([a-z-]+)\s*:\s*(.*?)\s*-->", src, re.S):
        k, v = m.group(1), m.group(2).strip()
        if k == "cards":
            d["cards"].append([c.strip() for c in v.split("|")])
        elif k == "chips":
            d["chips"] = [c.strip() for c in v.split("|") if c.strip()]
        else:
            d[k] = v
    return d


def md_to_body(md):
    lines = md.split("\n")
    i, n = 0, len(lines)
    out, sections = [], []
    cur_title = ""
    while i < n:
        s = lines[i].strip()

        if not s or s.startswith("<!--"):
            i += 1
            continue

        m = re.match(r"^(`{3,})(\w*)\s*$", s)
        if m:
            fence, lang = m.group(1), m.group(2)
            i += 1
            buf = []
            while i < n and lines[i].strip() != fence:
                buf.append(lines[i])
                i += 1
            i += 1
            cap = cur_title or (lang or "text")
            out.append(
                '<figure class="code"><figcaption><span>%s</span>'
                '<button class="cp" type="button" aria-label="复制代码">复制</button></figcaption>'
                "<pre><code>%s</code></pre></figure>" % (esc(cap), esc("\n".join(buf)))
            )
            continue

        if s.startswith("# ") and not s.startswith("## "):
            i += 1
            continue

        if s.startswith("## "):
            t = s[3:].strip()
            alt = bool(re.search(r"\{alt\}", t))
            pm = re.search(r"\{pill:([^}]+)\}", t)
            pill = pm.group(1).strip() if pm else ""
            t = re.sub(r"\s*\{(alt|pill:[^}]+)\}", "", t).strip()
            num = re.match(r"^(\d+)[.、]\s*(.*)$", t)
            title = num.group(2) if num else t
            badge = CN[len(sections)] if len(sections) < len(CN) else str(len(sections) + 1)
            if re.match(r"^附录\s*[A-Z]?", title):
                alt = True
                badge = title.split()[0][:3]
            sid = "s%d" % (len(sections) + 1)
            sections.append((sid, badge, pill or title[:6]))
            cur_title = title
            out.append('<section id="%s" class="sec%s"><h2><span class="badge">%s</span>'
                       "<span>%s</span></h2>" % (sid, " alt" if alt else "", esc(badge), inline(title)))
            i += 1
            continue

        if s.startswith("### "):
            out.append("<h3>%s</h3>" % inline(s[4:].strip()))
            i += 1
            continue

        if s.startswith(">"):
            buf = []
            while i < n and lines[i].strip().startswith(">"):
                buf.append(lines[i].strip().lstrip(">").strip())
                i += 1
            out.append('<aside class="note">%s</aside>' % "<br>".join(inline(b) for b in buf if b))
            continue

        if re.fullmatch(r"-{3,}", s):
            out.append('<div class="dotrule" role="separator"><span>&middot; &middot; &middot;</span></div>')
            i += 1
            continue

        if s.startswith("|"):
            rows = []
            while i < n and lines[i].strip().startswith("|"):
                rows.append(lines[i].strip())
                i += 1
            body = [r for r in rows if not is_sep(r)]
            if not body:
                continue
            head = cells(body[0])
            align = cells(rows[1]) if len(rows) > 1 and is_sep(rows[1]) else []
            th = "".join('<th%s>%s</th>' % (' class="r"' if align[k:k + 1] and ":" in align[k] else "", inline(c))
                         for k, c in enumerate(head))
            trs = []
            for r in body[1:]:
                cs = cells(r) + [""] * len(head)
                trs.append("<tr>" + "".join("<td>%s</td>" % inline(c) for c in cs[:len(head)]) + "</tr>")
            out.append('<div class="tw"><table><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>'
                       % (th, "".join(trs)))
            continue

        mli = re.match(r"^([-*]|\d+\.)\s+(.*)$", s)
        if mli:
            ordered = mli.group(1) != "-" and mli.group(1) != "*"
            tag = "ol" if ordered else "ul"
            items = [[mli.group(2), []]]          # seed with the first item: easy to lose
            i += 1
            while i < n:
                cs = lines[i].strip()
                mm = re.match(r"^([-*]|\d+\.)\s+(.*)$", cs)
                if mm and ((mm.group(1) not in "-*") == ordered):
                    items.append([mm.group(2), []])
                    i += 1
                    continue
                if cs and lines[i].startswith((" ", "\t")) and not cs.startswith("|"):
                    items[-1][1].append(cs)       # indented continuation
                    i += 1
                    continue
                if not cs:
                    nxt = next((x for x in lines[i:] if x.strip()), "")
                    if nxt.startswith((" ", "\t")) and not re.match(r"^([-*]|\d+\.)\s+", nxt.strip()):
                        i += 1
                        continue
                break
            lis = []
            for main_txt, subs in items:
                h = inline(main_txt)
                if subs:
                    h += "".join('<span class="sub">%s</span>' % inline(x) for x in subs)
                lis.append("<li>%s</li>" % h)
            out.append("<%s>%s</%s>" % (tag, "".join(lis), tag))
            continue

        para = [s]
        i += 1
        while i < n:
            nx = lines[i].strip()
            if (not nx or nx.startswith(("#", ">", "|", "```", "<!--")) or re.fullmatch(r"-{3,}", nx)
                    or re.match(r"^([-*]|\d+\.)\s+", nx)):
                break
            para.append(nx)
            i += 1
        out.append("<p>%s</p>" % "<br>".join(inline(p) for p in para))

    final, opened = [], False
    for blk in out:
        if blk.startswith("<section id="):
            if opened:
                final.append("</section>")
            opened = True
        final.append(blk)
    if opened:
        final.append("</section>")
    return "\n".join(final), sections


JS_TMPL = r"""
(function(){
  var K="__KEY__", root=document.documentElement, btn=document.getElementById("theme");
  var mq=window.matchMedia("(prefers-color-scheme: dark)");
  var mode="__DEFAULT__"; try{ mode=localStorage.getItem(K)||"__DEFAULT__"; }catch(e){}
  function paint(){
    var dark = mode==="auto" ? mq.matches : mode==="dark";
    root.setAttribute("data-theme", dark?"dark":"light");
    btn.textContent = mode==="auto" ? "跟随系统" : (dark?"深色":"浅色");
    btn.classList.toggle("act", mode!=="light");
  }
  btn.onclick=function(){ mode = mode==="light"?"dark":(mode==="dark"?"auto":"light");
    try{ mode==="light"?localStorage.removeItem(K):localStorage.setItem(K,mode); }catch(e){} paint(); };
  if(mq.addEventListener) mq.addEventListener("change",function(){ if(mode==="auto") paint(); });
  paint();

  var bar=document.querySelector(".progress i"), topBtn=document.getElementById("top");
  function onScroll(){
    var max=root.scrollHeight-root.clientHeight, y=root.scrollTop||document.body.scrollTop;
    bar.style.width=(max>0?y/max*100:0)+"%";
    topBtn.classList.toggle("show",y>480);
  }
  addEventListener("scroll",onScroll,{passive:true}); addEventListener("resize",onScroll); onScroll();
  topBtn.onclick=function(){ scrollTo({top:0,behavior:"smooth"}); };

  Array.prototype.forEach.call(document.querySelectorAll("figure.code"),function(f){
    var b=f.querySelector(".cp"); if(!b) return;
    b.onclick=function(){
      var t=f.querySelector("code").innerText;
      function ok(){ b.textContent="已复制"; b.classList.add("ok");
        setTimeout(function(){ b.textContent="复制"; b.classList.remove("ok"); },1500); }
      function fb(){ var r=document.createRange(); r.selectNodeContents(f.querySelector("code"));
        var s=getSelection(); s.removeAllRanges(); s.addRange(r);
        try{ document.execCommand("copy"); ok(); }catch(e){ b.textContent="请手动复制"; }
        s.removeAllRanges(); }
      (navigator.clipboard&&navigator.clipboard.writeText)?navigator.clipboard.writeText(t).then(ok,fb):fb();
    };
  });

  var links=Array.prototype.slice.call(document.querySelectorAll("nav.pills a[data-t]"));
  var byId={}; links.forEach(function(l){ byId[l.getAttribute("href").slice(1)]=l; });
  if("IntersectionObserver" in window){
    var io=new IntersectionObserver(function(es){
      var hit=null;
      es.forEach(function(e){ if(e.isIntersecting && (hit===null || e.boundingClientRect.top<hit.boundingClientRect.top)) hit=e; });
      if(hit && byId[hit.target.id]){
        links.forEach(function(l){ l.classList.remove("on"); });
        byId[hit.target.id].classList.add("on");
      }
    },{rootMargin:"-14% 0px -70% 0px",threshold:0});
    Array.prototype.forEach.call(document.querySelectorAll("section.sec"),function(s){ io.observe(s); });
  }
})();
"""


def read_assets():
    css = []
    for name in ("theme-light.css", "theme-dark.css", "components.css"):
        p = os.path.normpath(os.path.join(ASSETS, name))
        with io.open(p, encoding="utf-8") as f:
            css.append(f.read().strip())
    return "\n".join(css)


def page(d, body, sections, args):
    title = args.title or d.get("hero-title") or "页面"
    kicker = d.get("hero-kicker", "CLEAN STYLE EDITION")
    lede = d.get("hero-lede", "")
    chips = d.get("chips", [])
    cards = d["cards"]
    if not cards:
        cards = [[("0%d" % (k + 1)), s[2], "", "#%s" % s[0], ("a" if k % 2 == 0 else "b")]
                 for k, s in enumerate(sections[:4])]
    pilots = "".join('<a href="#%s" data-t="%s">%s</a>' % (sid, esc(badge), esc(short))
                     for sid, badge, short in sections)
    cardhtml = "".join(
        '<a class="card %s" href="%s"><span class="n">%s</span><span class="t">%s</span>'
        '<span class="d">%s</span></a>'
        % (esc(c[4] if len(c) > 4 else "a"), esc(c[3] if len(c) > 3 else "#"),
           esc(c[0]), esc(c[1]), esc(c[2] if len(c) > 2 else ""))
        for c in cards)
    chiphtml = "".join('<span class="chip">%s</span>' % inline(c) for c in chips)
    ledehtml = '<p class="lede">%s</p>' % inline(lede) if lede else ""
    foothtml = '<div class="foot">%s</div>' % inline(d["foot"]) if d.get("foot") else ""

    inner = (
        '<div class="progress"><i></i></div>\n'
        '<nav class="pills" aria-label="章节导航">%s\n'
        '<span class="tools"><button class="tbtn" id="theme" type="button">浅色</button></span></nav>\n'
        '<div class="wrap">\n'
        '<header class="hero">\n<div class="kicker"><i></i>%s</div>\n<h1>%s</h1>\n%s\n'
        '<div class="chips">%s</div>\n</header>\n'
        '<div class="cards">%s</div>\n%s\n%s\n</div>\n'
        '<button id="top" type="button" aria-label="回到顶部">&uarr;</button>'
        % (pilots, esc(kicker), inline(title), ledehtml, chiphtml, cardhtml, body, foothtml)
    )
    css = read_assets()
    js = JS_TMPL.replace("__KEY__", args.store_key).replace("__DEFAULT__", args.theme)
    if args.fragment:
        return "<style>%s</style>\n%s\n<script>%s</script>" % (css, inner, js)
    boot = ("try{var m=localStorage.getItem('%s')||'%s';"
            "var d=(m==='dark')||(m==='auto'&&window.matchMedia('(prefers-color-scheme: dark)').matches);"
            "document.documentElement.setAttribute('data-theme',d?'dark':'light')}catch(e){}"
            % (args.store_key, args.theme if args.theme in ("light", "dark") else "light"))
    return ("<!DOCTYPE html>\n<html lang=\"zh-CN\" data-theme=\"light\">\n<head>\n"
            '<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
            '<meta name="color-scheme" content="light dark">\n'
            '<meta name="theme-color" media="(prefers-color-scheme: light)" content="#FFFCF6">\n'
            '<meta name="theme-color" media="(prefers-color-scheme: dark)" content="#101318">\n'
            "<title>%s</title>\n<style>%s</style>\n</head>\n<body>\n<script>%s</script>\n%s\n"
            "<script>%s</script>\n</body>\n</html>"
            % (esc(title), css, boot, inner, js))


def balance(doc):
    tags = ["section", "table", "figure", "nav", "div", "ul", "ol", "aside", "header", "p", "h2", "h3", "li", "td", "th", "tr"]
    bad = []
    for t in tags:
        o = len(re.findall(r"<%s[\s>]" % t, doc))
        c = len(re.findall(r"</%s>" % t, doc))
        if o != c:
            bad.append("%s %d/%d" % (t, o, c))
    return bad


def main():
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("src")
    ap.add_argument("-o", "--out")
    ap.add_argument("--theme", choices=["light", "dark", "auto"], default="light",
                    help="which theme paints first (default: light = 明亮清新)")
    ap.add_argument("--fragment", action="store_true", help="emit a chat-embeddable fragment, no <html>")
    ap.add_argument("--title")
    ap.add_argument("--store-key", default="clean-style-theme")
    args = ap.parse_args()

    try:
        with io.open(args.src, encoding="utf-8") as f:
            md = f.read()
    except OSError as e:
        print("ERROR cannot read source: %s" % e)
        return 2

    out = args.out or os.path.splitext(args.src)[0] + ".html"
    d = directives(md)
    body, sections = md_to_body(md)
    doc = page(d, body, sections, args)
    with io.open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write(doc)

    bad = balance(doc)
    print("built: %s (%d bytes)" % (out, len(doc.encode("utf-8"))))
    print("theme default: %s | sections: %d | tables: %d | code blocks: %d"
          % (args.theme, len(sections), doc.count("<table>"), doc.count("<figure class=\"code\"")))
    print("tag balance: %s" % ("OK" if not bad else "MISMATCH " + ", ".join(bad)))
    if not sections:
        print("WARN no '## ' headings found: pill nav and cards will be empty")
    return 0


if __name__ == "__main__":
    sys.exit(main())
