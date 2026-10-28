#!/usr/bin/env python3
"""Build compact, greppable API indexes from Blizzard_APIDocumentationGenerated.

Usage (run from anywhere; use -I because the input files are untrusted data):
    python -I tools/build_index.py

Reads  <flavour>/BlizzardInterfaceCode/Interface/AddOns/Blizzard_APIDocumentationGenerated/*Documentation.lua
Writes index/<flavour>/{functions,events,enums,structures,constants}.txt  (one record per line)

The input files are plain Lua table constructors, so they are parsed with a small
purpose-built parser (no Lua interpreter needed, nothing is executed).
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FLAVOURS = ["Retail", "Forever"]
DOC_DIR = "BlizzardInterfaceCode/Interface/AddOns/Blizzard_APIDocumentationGenerated"

TOKEN = re.compile(
    r"""\s+|--\[\[.*?\]\]|--[^\n]*
    |(?P<str>"(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')
    |(?P<long>\[\[.*?\]\])
    |(?P<num>-?(?:0[xX][0-9a-fA-F]+|\d+\.?\d*(?:[eE][-+]?\d+)?))
    |(?P<id>[A-Za-z_][A-Za-z_0-9.]*)
    |(?P<op>[-+*/%])
    |(?P<p>[{}=,;:\[\]()])
    """,
    re.X | re.S,
)


def tokenize(text):
    pos, out = 0, []
    while pos < len(text):
        m = TOKEN.match(text, pos)
        if not m:
            raise ValueError("bad token at %d: %r" % (pos, text[pos:pos + 30]))
        pos = m.end()
        if m.lastgroup:
            out.append((m.lastgroup, m.group(m.lastgroup)))
    return out


def unquote(s):
    return s[1:-1].encode("utf-8").decode("unicode_escape") if "\\" in s else s[1:-1]


class Raw(str):
    """Unquoted Lua identifier/expression (e.g. a constant name used as a default)."""


class Table:
    def __init__(self, arr, rec):
        self.arr, self.rec = arr, rec

    def get(self, k, d=None):
        return self.rec.get(k, d)

    def __bool__(self):
        return bool(self.arr or self.rec)


class Parser:
    def __init__(self, toks):
        self.t, self.i = toks, 0

    def peek(self, k=0):
        return self.t[self.i + k] if self.i + k < len(self.t) else (None, None)

    def value(self):
        first = self.primary()
        if self.peek()[0] != "op":
            return first
        parts = [lit(first)]  # arithmetic such as "A + B": keep the expression text verbatim
        while self.peek()[0] == "op":
            parts.append(self.t[self.i][1])
            self.i += 1
            parts.append(lit(self.primary()))
        return Raw(" ".join(parts))

    def primary(self):
        kind, val = self.t[self.i]
        if kind == "p" and val == "{":
            return self.table()
        self.i += 1
        if kind == "str":
            return unquote(val)
        if kind == "long":
            return val[2:-2]
        if kind == "num":
            if val.lower().startswith(("0x", "-0x")) or not re.search(r"[.eE]", val):
                return int(val, 0)
            return float(val)
        if kind == "id":
            return {"true": True, "false": False, "nil": None}.get(val, Raw(val))
        raise ValueError("unexpected %r" % (val,))

    def table(self):
        self.i += 1  # {
        arr, rec = [], {}
        while True:
            kind, val = self.peek()
            if kind == "p" and val == "}":
                self.i += 1
                break
            if kind == "p" and val in ",;":
                self.i += 1
                continue
            if kind == "id" and self.peek(1) == ("p", "="):
                self.i += 2
                rec[val] = self.value()
            elif kind == "p" and val == "[":
                self.i += 1
                key = self.value()
                self.i += 2  # ] =
                rec[key] = self.value()
            else:
                arr.append(self.value())
        return Table(arr, rec)


def parse_file(path):
    toks = tokenize(path.read_text(encoding="utf-8", errors="replace"))
    for idx, tok in enumerate(toks):  # first '{' after 'local X ='
        if tok == ("p", "{"):
            return Parser(toks[idx:]).table()
    raise ValueError("no table")


# ---------- rendering ----------

STRUCTURAL = {"Name", "Type", "Arguments", "Returns", "Payload", "Documentation", "Namespace",
              "LiteralName", "Fields", "Values", "NumValues", "MinValue", "MaxValue"}
FIELD_STRUCTURAL = {"Name", "Type", "Nilable", "Default", "Mixin", "InnerType", "KeyType", "EnumValue", "Value"}
EMPTY = Table([], {})


def lit(v):
    if isinstance(v, Raw):
        return str(v)
    if isinstance(v, str):
        return '"%s"' % v
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    return str(v)


def extras(rec, skip):
    out = []
    for k, v in rec.items():
        if k in skip or v is False or v is None or isinstance(v, Table):
            continue
        out.append(k if v is True else "%s=%s" % (k, v))
    return out


def typestr(f):
    t = f.get("Type", "?")
    inner, key, mixin = f.get("InnerType"), f.get("KeyType"), f.get("Mixin")
    if inner and key:
        t += "<%s,%s>" % (key, inner)
    elif inner:
        t += "<%s>" % inner
    if mixin:
        t += "(%s)" % mixin
    return t


def doctext(rec):
    d = rec.get("Documentation")
    return " ".join(map(str, d.arr)) if isinstance(d, Table) and d.arr else ""


def field(f):
    s = "%s%s: %s" % (f.get("Name"), "?" if f.get("Nilable") is True else "", typestr(f))
    if "Default" in f.rec:
        s += " = " + lit(f.get("Default"))
    ex = extras(f.rec, FIELD_STRUCTURAL)
    if doctext(f.rec):
        ex.append('doc="%s"' % doctext(f.rec))
    if ex:
        s += " {%s}" % ", ".join(ex)
    return s


def fields(t):
    return ", ".join(field(f) for f in t.arr) if isinstance(t, Table) else ""


def flags(rec):
    ex = extras(rec, STRUCTURAL)
    return " [%s]" % ", ".join(ex) if ex else ""


def doc(rec):
    d = doctext(rec)
    return " -- " + d if d else ""


def render(tbl, src, out):
    ns = tbl.get("Namespace")
    env = tbl.get("Environment")
    tag = " @" + src

    for fn in (tbl.get("Functions") or EMPTY).arr:
        name = "%s.%s" % (ns, fn.get("Name")) if ns else fn.get("Name")
        line = "%s(%s)" % (name, fields(fn.get("Arguments")))
        rets = fields(fn.get("Returns"))
        if rets:
            line += " -> " + rets
        extra = flags(fn.rec)
        if env and env != "All" and "Environment" not in fn.rec:
            extra += " [Environment=%s]" % env
        out["functions"].append(line + extra + doc(fn.rec) + tag)

    for ev in (tbl.get("Events") or EMPTY).arr:
        line = "%s(%s)" % (ev.get("LiteralName"), fields(ev.get("Payload")))
        out["events"].append(line + flags(ev.rec) + doc(ev.rec) + tag)

    for t in (tbl.get("Tables") or EMPTY).arr:
        ty, name = t.get("Type"), t.get("Name")
        if ty == "Enumeration":
            vals = sorted((t.get("Fields") or EMPTY).arr, key=lambda f: f.get("EnumValue", 0))
            out["enums"].append("%s = %s%s" % (name, ", ".join("%s:%s" % (v.get("Name"), v.get("EnumValue")) for v in vals), tag))
        elif ty == "Structure":
            out["structures"].append("%s { %s }%s%s" % (name, fields(t.get("Fields")), doc(t.rec), tag))
        elif ty == "CallbackType":
            out["structures"].append("callback %s(%s)%s" % (name, fields(t.get("Arguments")), tag))
        elif ty == "Constants":
            for v in (t.get("Values") or EMPTY).arr:
                out["constants"].append("%s.%s: %s = %s%s" % (name, v.get("Name"), v.get("Type"), lit(v.get("Value")), tag))
        else:
            out["structures"].append("# unhandled Type=%s Name=%s%s" % (ty, name, tag))


def build(flavour):
    docdir = ROOT / flavour / DOC_DIR
    out = {k: [] for k in ("functions", "events", "enums", "structures", "constants")}
    files = sorted(docdir.glob("*Documentation.lua"))
    fails = 0
    for p in files:
        src = p.name[: -len("Documentation.lua")]
        try:
            render(parse_file(p), src, out)
        except Exception as e:  # report, never silently skip
            fails += 1
            print("  PARSE FAILURE %s: %s" % (p.name, e), file=sys.stderr)
    dest = ROOT / "index" / flavour
    dest.mkdir(parents=True, exist_ok=True)
    for k, lines in out.items():
        lines.sort(key=str.lower)
        (dest / (k + ".txt")).write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print("%s: %d files, %d failures; %s" % (flavour, len(files), fails, ", ".join("%s=%d" % (k, len(v)) for k, v in out.items())))
    return fails


if __name__ == "__main__":
    sys.exit(1 if sum(build(f) for f in FLAVOURS) else 0)
