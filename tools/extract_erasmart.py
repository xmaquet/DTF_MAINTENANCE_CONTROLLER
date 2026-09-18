from pathlib import Path
p = Path(r"C:\InkONE\PrintExp_X64_5.8.1.1.29_Unicode_20240508\Log\main\Log[2026_09_18].txt")
text = p.read_text(encoding="utf-16")
hits = [ln for ln in text.splitlines() if "ERASMART" in ln.upper()]
out = Path(r"C:\Users\User\DTF_Maintenance_Controller\logs\erasmart-lines.txt")
out.write_text("\n".join(hits), encoding="utf-8")
print("hits", len(hits))
