#!/usr/bin/env python3
"""Independent audit: re-derive each car's fields from the raw source .md and
compare against cars.json. Flags mismatches, missing fields, and price errors.
Uses ONLY local files (no scraping)."""
import re, json, os

D = "/Users/daodilyas/Desktop/automk/.firecrawl/cars"
cars = json.load(open("/Users/daodilyas/Desktop/automk/.firecrawl/cars.json", encoding="utf-8"))

def num(s):
    return int(re.sub(r"[^\d]", "", s)) if s and re.search(r"\d", s) else None

# Pull a labeled spec value straight from the raw markdown line, independently.
def raw_spec(md, label):
    # match "Label<value>" possibly with markdown link noise stripped
    for line in md.splitlines():
        line = re.sub(r"\[.*?\]\(.*?\)", "", line).strip()
        if line.startswith(label):
            rest = line[len(label):].strip()
            # ensure it's not a longer label (e.g. "Modell" vs "Modellår")
            if rest and not rest[0].isalpha() or label in ("Merke","Modell","Drivstoff","Girkasse","Karosseri","Farge","Hjuldrift","Salgsform"):
                return rest
            return rest
    return None

issues = []
ok = 0

for c in cars:
    cid = c["id"]
    md = open(os.path.join(D, cid + ".md"), encoding="utf-8").read()
    probs = []

    # --- price: independently grab Totalpris ## N kr ---
    pm = re.search(r"Totalpris\s*\n+##\s*([\d\s ]+)\s*kr", md)
    raw_total = num(pm.group(1)) if pm else None
    if raw_total is None:
        # fallback: base + omreg
        base = re.search(r"Pris eksl\. omreg\.\s*([\d\s ]+)\s*kr", md)
        omr = re.search(r"Omregistrering\s*([\d\s ]+)\s*kr", md)
        if base:
            raw_total = (num(base.group(1)) or 0) + (num(omr.group(1)) if omr else 0)
    if raw_total != c["price"]:
        probs.append(f"PRICE json={c['price']} raw={raw_total}")

    # --- year (Modellår) ---
    ym = re.search(r"Modellår\s*(\d{4})", md)
    if ym and int(ym.group(1)) != c["year"]:
        probs.append(f"YEAR json={c['year']} raw={ym.group(1)}")
    if not ym and c["year"]:
        probs.append(f"YEAR json={c['year']} raw=NOTFOUND")

    # --- km (Kilometerstand) ---
    km = re.search(r"Kilometerstand\s*([\d\s ]+)\s*km", md)
    raw_km = num(km.group(1)) if km else None
    if raw_km != c["km"]:
        probs.append(f"KM json={c['km']} raw={raw_km}")

    # --- brand (Merke) ---
    bm = re.search(r"\bMerke\s*([^\n]+)", md)
    if bm:
        rawb = bm.group(1).strip()
        if rawb.lower() not in c["brand"].lower() and c["brand"].lower() not in rawb.lower():
            probs.append(f"BRAND json={c['brand']} raw={rawb}")

    # --- fuel present? ---
    if not c["fuel"]:
        probs.append("FUEL empty")

    # --- required fields non-empty ---
    for f in ("title", "year", "km", "price"):
        if c[f] in (None, "", 0):
            probs.append(f"{f.upper()} missing/zero")

    # --- images exist on disk ---
    n_json = len(c["images"])
    img_dir = f"/Users/daodilyas/Desktop/automk/images/{cid}"
    n_disk = len([f for f in os.listdir(img_dir) if f.endswith(".jpg")]) if os.path.isdir(img_dir) else 0
    if n_disk == 0:
        probs.append("NO IMAGES on disk")

    # --- SOLGT consistency ---
    raw_sold = bool(re.search(r"\bSOLGT\b", md))
    if raw_sold != c["sold"]:
        probs.append(f"SOLD json={c['sold']} raw={raw_sold}")

    if probs:
        issues.append((cid, c["title"], probs))
    else:
        ok += 1
    # always print a one-line confirmation row
    print(f"{cid} | {c['title'][:26]:<26} | {str(c['year'])} | {str(c['km'])+'km':<10} | {str(c['price'])+'kr':<11} | {c['fuel']:<7} | {(c['gear'] or '-'):<8} | imgs={n_disk}  {'OK' if not probs else 'CHECK'}")

print("\n==================== AUDIT SUMMARY ====================")
print(f"Clean: {ok}/{len(cars)}")
if issues:
    print(f"Cars with flags: {len(issues)}")
    for cid, title, probs in issues:
        print(f"\n  {cid}  {title}")
        for p in probs:
            print(f"     - {p}")
else:
    print("No data mismatches found.")
