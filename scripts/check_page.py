#!/usr/bin/env python3
"""Check a feynman-lab page for common mistakes before publishing.

Usage:  python3 check_page.py path/to/page.html
Exit code 0 means no errors (warnings may still print); 1 means errors were found.

Checks: leftover placeholders, JSON blocks (glossary, quiz), glossary terms that are used
but undefined, level variants, external resources the published page would block,
duplicate ids, file size, and a JavaScript syntax check of every inline script (needs node).
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from html.parser import HTMLParser

LEVELS = {"simple", "student", "deep"}
SCRIPT_HOSTS = ("https://cdnjs.cloudflare.com/", "https://cdn.jsdelivr.net/npm/",
                "https://cdn.tailwindcss.com/", "https://code.jquery.com/")
STYLE_HOSTS = ("https://fonts.googleapis.com/",)
MAX_BYTES = 16 * 1024 * 1024


class Collector(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.scripts = []          # (attrs, text, line)
        self._script = None
        self._buf = []
        self.lvl = []              # (tokens, line)
        self.terms = []            # (key, line)
        self.ids = []              # (id, line)
        self.ext_scripts = []
        self.ext_styles = []
        self.remote_media = []
        self.html_lang = None

    def handle_starttag(self, tag, attrs):
        a = {k: (v or "") for k, v in attrs}
        line = self.getpos()[0]
        if tag == "html":
            self.html_lang = a.get("lang")
        if "id" in a:
            self.ids.append((a["id"], line))
        classes = a.get("class", "").split()
        if "lvl" in classes:
            self.lvl.append((a.get("data-level", "").split(), line))
        if "term" in classes:
            self.terms.append((a.get("data-term", ""), line))
        if tag == "script":
            if a.get("src"):
                self.ext_scripts.append(a["src"])
            self._script = (a, line)
            self._buf = []
        if tag == "link" and "stylesheet" in a.get("rel", ""):
            self.ext_styles.append(a.get("href", ""))
        if tag in ("img", "video", "audio", "source", "iframe", "image"):
            src = a.get("src") or a.get("href") or ""
            if re.match(r"https?://", src):
                self.remote_media.append(src)

    def handle_endtag(self, tag):
        if tag == "script" and self._script is not None:
            attrs, line = self._script
            self.scripts.append((attrs, "".join(self._buf), line))
            self._script = None

    def handle_data(self, data):
        if self._script is not None:
            self._buf.append(data)


def main(path):
    errors, warnings = [], []
    with open(path, encoding="utf-8") as f:
        html = f.read()

    if os.path.getsize(path) > MAX_BYTES:
        errors.append("file is over 16 MB")

    leftovers = [(html.count("\n", 0, m.start()) + 1, m.group(0))
                 for m in re.finditer(r"FILL|\{\{[A-Z_]+\}\}", html)]
    for line, tok in leftovers[:12]:
        errors.append(f"line {line}: leftover placeholder {tok!r}")
    if len(leftovers) > 12:
        errors.append(f"...and {len(leftovers) - 12} more leftover placeholders")

    c = Collector()
    c.feed(html)

    if not c.html_lang:
        warnings.append("<html> has no lang attribute")

    seen = {}
    for i, line in c.ids:
        if i in seen:
            errors.append(f"line {line}: duplicate id {i!r} (first on line {seen[i]})")
        else:
            seen[i] = line

    data = {}
    for attrs, text, line in c.scripts:
        if attrs.get("type") == "application/json":
            try:
                data[attrs.get("id")] = json.loads(text)
            except json.JSONDecodeError as e:
                errors.append(f"line {line}: #{attrs.get('id')} is not valid JSON ({e})")

    # Glossary
    gloss = data.get("glossary-data", {})
    if not isinstance(gloss, dict):
        errors.append("#glossary-data must be an object")
        gloss = {}
    for key, val in gloss.items():
        if isinstance(val, dict):
            bad = set(val) - LEVELS
            if bad:
                errors.append(f"glossary {key!r}: unknown level keys {sorted(bad)}")
        elif not isinstance(val, str):
            errors.append(f"glossary {key!r}: value must be a string or a level object")
    used = set()
    for key, line in c.terms:
        used.add(key)
        if not key:
            errors.append(f"line {line}: .term without data-term")
        elif key not in gloss:
            errors.append(f"line {line}: term {key!r} has no glossary entry")
    for key in sorted(set(gloss) - used):
        warnings.append(f"glossary entry {key!r} is never used in the page")

    # Quiz
    quiz = data.get("quiz-data", [])
    if not isinstance(quiz, list) or not quiz:
        errors.append("#quiz-data must be a non-empty list")
        quiz = []
    for n, q in enumerate(quiz, 1):
        if not isinstance(q, dict):
            errors.append(f"quiz #{n}: must be an object")
            continue
        opts = q.get("options")
        if not q.get("q"):
            errors.append(f"quiz #{n}: missing question text 'q'")
        if not isinstance(opts, list) or len(opts) < 2:
            errors.append(f"quiz #{n}: needs at least 2 options")
            opts = []
        ans = q.get("answer")
        if not isinstance(ans, int) or not 0 <= ans < len(opts):
            errors.append(f"quiz #{n}: 'answer' must be an index into options (0 to {len(opts) - 1})")
        lv = str(q.get("level", "all"))
        if lv != "all" and not set(lv.split()) <= LEVELS:
            errors.append(f"quiz #{n}: level must be 'all' or from {sorted(LEVELS)}")
        if not q.get("why"):
            warnings.append(f"quiz #{n}: no 'why' explanation")
    for level in sorted(LEVELS):
        count = sum(1 for q in quiz if isinstance(q, dict) and
                    (str(q.get("level", "all")) == "all" or level in str(q.get("level")).split()))
        if quiz and count < 3:
            warnings.append(f"only {count} quiz question(s) show at the {level!r} level")

    # Level variants
    counts = {lv: 0 for lv in LEVELS}
    for toks, line in c.lvl:
        if not toks:
            errors.append(f"line {line}: .lvl element without data-level")
        for t in toks:
            if t not in LEVELS:
                errors.append(f"line {line}: unknown level {t!r}")
            else:
                counts[t] += 1
    if len(set(counts.values())) > 1:
        warnings.append(f"level variants are unbalanced {counts}; check every section has all three")

    # External resources
    for src in c.ext_scripts:
        if not src.startswith(SCRIPT_HOSTS):
            errors.append(f"script host will be blocked when published: {src}")
        elif re.search(r"@latest|@\^|@~", src) or not re.search(r"\d+\.\d+\.\d+", src):
            errors.append(f"script URL is not pinned to an exact version: {src}")
    for href in c.ext_styles:
        if href and not href.startswith(STYLE_HOSTS):
            errors.append(f"stylesheet will be blocked when published: {href}")
    for src in c.remote_media:
        errors.append(f"remote media will be blocked when published (inline it instead): {src}")
    if re.search(r"fetch\(\s*['\"`]https?://", html):
        warnings.append("page calls fetch() on a remote URL; published pages block this")

    # JavaScript syntax
    node = shutil.which("node")
    inline = [(t, line) for a, t, line in c.scripts
              if not a.get("src") and a.get("type", "") in ("", "text/javascript", "module")]
    if node:
        for text, line in inline:
            with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as tmp:
                tmp.write(text)
            try:
                r = subprocess.run([node, "--check", tmp.name], capture_output=True, text=True)
                if r.returncode != 0:
                    msg = r.stderr.strip().splitlines()
                    detail = " | ".join(m for m in msg if m.strip())[:400]
                    errors.append(f"script starting on line {line} has a syntax error: {detail}")
            finally:
                os.unlink(tmp.name)
    else:
        warnings.append("node not found; skipped the JavaScript syntax check")

    for w in warnings:
        print("WARN ", w)
    for e in errors:
        print("ERROR", e)
    print(f"\n{len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
