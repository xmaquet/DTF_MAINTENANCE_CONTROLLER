"""Lecture seule : encodage et taille du log PrintExp."""
from pathlib import Path

p = Path(r"C:\InkONE\PrintExp_X64_5.8.1.1.29_Unicode_20240508\Log\main\Log[2026_09_18].txt")
raw = p.read_bytes()
print("size", len(raw))
print("head_hex", raw[:32].hex())
print("bom", raw[:4])

def try_dec(enc):
    try:
        t = raw.decode(enc)
        print(enc, "len_chars", len(t), "prn", t.lower().count(".prn"), "erasmart", t.upper().count("ERASMART"))
        return t
    except Exception as e:
        print(enc, "FAIL", e)
        return ""

utf16 = try_dec("utf-16")
try_dec("utf-16-le")
try_dec("utf-8")
lat = try_dec("latin-1")

text = utf16 or lat
for needle in ("ERASMART", "OpenFiles", "GO-Print", ".prn", "PRN"):
    n = text.upper().count(needle.upper()) if text else 0
    print("count", needle, n)

lines = text.splitlines() if text else []
print("nlines", len(lines))
if lines:
    print("first", repr(lines[0][:200]))
    print("last", repr(lines[-1][:200]))
    for ln in lines:
        if "ERASMART" in ln.upper() or "OpenFile" in ln:
            print("HIT", ln[:300])
