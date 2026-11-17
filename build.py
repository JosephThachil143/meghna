#!/usr/bin/env python3
"""Generates the static German pages (/de/index.html, /de/cv.html) from the English sources.
Every translated element carries data-en / data-de; data-de-<attr> localises attributes.
Run: python3 build.py   (CI runs it before publishing; de/ is not committed)."""
import html, re, shutil, sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).parent
SITE = "https://meghnajosephgeorge.com"
PAGES = {"index": "/de/", "cv": "/de/cv.html"}
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
errors = []


class Localizer(HTMLParser):
    def __init__(self, name):
        super().__init__(convert_charrefs=False)
        self.name, self.out, self.skip, self.depth = name, [], None, 0

    def tag(self, tag, attrs, selfclose=False):
        parts = []
        for k, v in attrs:
            if k in ("data-en", "data-de"):
                continue
            if k.startswith("data-de-"):
                base = k[len("data-de-"):]
                parts = [(a, b) for a, b in parts if a != base] + [(base, v)]
                continue
            if any(a == k for a, _ in parts):
                continue
            parts.append((k, v))
        s = "<" + tag
        for k, v in parts:
            s += f" {k}" if v is None else f' {k}="{html.escape(v, quote=True)}"'
        return self.links(s + (" />" if selfclose else ">"))

    def links(self, s):
        if 'hreflang="en"' in s:
            return s
        def fix(m):
            path, _, frag = m.group(1).partition("#")
            if path.startswith("/de/") or path == "/de":
                return m.group(0)
            if path == "/" or path.endswith(".html"):
                path = "/de/" if path == "/" else "/de" + path
                return f'href="{path}{"#" + frag if frag else ""}"'
            return m.group(0)
        return re.sub(r'href="(/(?!/)[^"]*)"', fix, s)

    def start(self, tag, attrs, selfclose):
        if self.skip:
            if tag == self.skip and tag not in VOID and not selfclose:
                self.depth += 1
            return
        d = dict(attrs)
        if ("data-en" in d) != ("data-de" in d):
            errors.append(f"{self.name}: <{tag}> has only one of data-en/data-de near {self.getpos()}")
        if "data-en" in d and "data-de" in d:
            self.out.append(self.tag(tag, attrs))
            self.out.append(d["data-de"])
            if tag not in VOID:
                self.skip, self.depth = tag, 1
            return
        if any(k.startswith("data-de-") for k in d):
            self.out.append(self.tag(tag, attrs, selfclose))
        else:
            self.out.append(self.links(self.get_starttag_text()))

    def handle_starttag(self, tag, attrs): self.start(tag, attrs, False)
    def handle_startendtag(self, tag, attrs): self.start(tag, attrs, True)

    def handle_endtag(self, tag):
        if self.skip:
            if tag == self.skip:
                self.depth -= 1
                if self.depth == 0:
                    self.out.append(f"</{tag}>")
                    self.skip = None
            return
        self.out.append(f"</{tag}>")

    def handle_data(self, data):
        if not self.skip: self.out.append(data)
    def handle_entityref(self, name):
        if not self.skip: self.out.append(f"&{name};")
    def handle_charref(self, name):
        if not self.skip: self.out.append(f"&#{name};")
    def handle_decl(self, decl): self.out.append(f"<!{decl}>")


def build():
    out_dir = ROOT / "de"
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir()
    for name, url in PAGES.items():
        src = (ROOT / f"{name}.html").read_text(encoding="utf-8")
        p = Localizer(name)
        p.feed(src)
        p.close()
        body = "".join(p.out)
        body = re.sub(r'<html lang="[a-z]+"', '<html lang="de"', body, count=1)
        en_url = SITE + ("/" if name == "index" else "/cv.html")
        body = body.replace(f'<link rel="canonical" href="{en_url}" />', f'<link rel="canonical" href="{SITE + url}" />')
        (out_dir / f"{name}.html").write_text(body, encoding="utf-8")
        if re.search(r"\sdata-(en|de)(-\w+)?=", body):
            errors.append(f"de/{name}.html: leftover data-en/data-de")
        for href in re.findall(r'(?:href|src)="(/[^"]*)"', body):
            path = href.split("#")[0].split("?")[0]
            if path.startswith("//"):
                continue
            target = ROOT / path.lstrip("/")
            if path.endswith("/"):
                target = target / "index.html"
            if not target.exists() and path not in PAGES.values():
                errors.append(f"de/{name}.html: broken link {href}")


if __name__ == "__main__":
    build()
    if errors:
        print("BUILD FAILED")
        for e in errors: print(" -", e)
        sys.exit(1)
    print("Build OK -> de/")
