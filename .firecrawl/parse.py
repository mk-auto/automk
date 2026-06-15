#!/usr/bin/env python3
import re, json, os, glob

D = "/Users/daodilyas/Desktop/automk/.firecrawl/cars"
IDS = open("/Users/daodilyas/Desktop/automk/.firecrawl/ids.txt").read().split()
# Cars currently listed on the dealer's Finn page. Anything published but not in
# this set is treated as sold/removed (kept on site, badged "Solgt", sorted last).
_active_path = "/Users/daodilyas/Desktop/automk/.firecrawl/active_ids.txt"
ACTIVE = set(open(_active_path).read().split()) if os.path.exists(_active_path) else set(IDS)

SPEC_LABELS = [
    "Omregistrering","Pris eksl. omreg.","Merke","Modellår","Modell","Karosseri",
    "Drivstoff","Effekt","Slagvolum","CO₂-utslipp","Kilometerstand","Girkasse",
    "Maksimal tilhengervekt","Hjuldrift","Vekt","Seter","Farge","Bilen står i",
    "Avgiftsklasse","Registreringsnummer","Chassis nr. (VIN)","Salgsform",
]

def clean_num(s):
    return int(re.sub(r"[^\d]", "", s)) if re.search(r"\d", s) else None

def parse_spec(block):
    out = {}
    for line in block.splitlines():
        line = line.strip()
        if not line:
            continue
        # strip markdown links
        line = re.sub(r"\[.*?\]\(.*?\)", "", line).strip()
        for lab in SPEC_LABELS:
            if line.startswith(lab):
                val = line[len(lab):].strip()
                if lab not in out:  # first wins (longest-label ordering handled below)
                    out[lab] = val
                break
    return out

# order labels longest-first so "Modellår" matches before "Modell"
SPEC_LABELS.sort(key=len, reverse=True)

cars = []
for cid in IDS:
    md = open(os.path.join(D, cid + ".md"), encoding="utf-8").read()
    html = open(os.path.join(D, cid + ".html"), encoding="utf-8").read()

    # spec block
    m = re.search(r"## Spesifikasjoner(.*?)(##|\Z)", md, re.S)
    spec = parse_spec(m.group(1)) if m else {}

    brand = spec.get("Merke", "").strip()
    model = spec.get("Modell", "").strip()
    title = (brand + " " + model).strip()

    # total price: the "## N kr" after Totalpris, fallback Pris eksl omreg + omreg
    price = None
    pm = re.search(r"Totalpris\s*\n+##\s*([\d\s ]+)\s*kr", md)
    if pm:
        price = clean_num(pm.group(1))
    if price is None and spec.get("Pris eksl. omreg."):
        base = clean_num(spec["Pris eksl. omreg."])
        omr = clean_num(spec.get("Omregistrering", "0")) or 0
        price = (base or 0) + omr if base else None

    # subtitle/teaser: line between real title heading and "Modellår"
    sub = ""
    tm = re.search(r"#\s+" + re.escape(title) + r"\s*\n(.*?)\nModellår", md, re.S)
    if not tm and model:
        tm = re.search(r"#\s+[^\n]*\n(.*?)\nModellår", md, re.S)
    if tm:
        cand = tm.group(1).strip().replace("\\-", "-")
        cand = re.sub(r"\s+", " ", cand).strip()
        if 0 < len(cand) < 120 and not cand.lower().startswith("modellår"):
            sub = cand

    # description
    dm = re.search(r"## Beskrivelse(.*?)(## Spesifikasjoner|## Utstyr)", md, re.S)
    desc = ""
    if dm:
        raw = dm.group(1).strip()
        # collapse, keep paragraphs; strip markdown bold/escapes
        raw = raw.replace("\\-", "-")
        paras = [re.sub(r"\s+", " ", p).strip(" *") for p in re.split(r"\n\s*\n", raw)]
        paras = [p for p in paras if p and len(p) > 1]
        desc = "\n\n".join(paras)

    # equipment
    em = re.search(r"## Utstyr(.*?)(##|\Z)", md, re.S)
    equip = []
    if em:
        equip = [re.sub(r"\s+", " ", x).strip() for x in re.findall(r"^\s*-\s+(.+)$", em.group(1), re.M)]
        equip = [e for e in equip if e]

    # images: unique 1600w uuids in order of appearance
    seen, imgs = set(), []
    for um in re.finditer(r"images\.finncdn\.no/dynamic/1600w/item/" + cid + r"/([a-f0-9-]+)", html):
        u = um.group(1)
        if u not in seen:
            seen.add(u); imgs.append(u)

    # Finn's sold badge is "SOLGT" alone on its own line (optionally wrapped in
    # markdown emphasis/heading). Match only that — NOT "SOLGT" inside seller
    # prose like "VITO VURDERES SOLGT DA ...", which is a false positive.
    sold = bool(re.search(r"(?m)^\W*SOLGT\W*$", md)) or (cid not in ACTIVE)

    cars.append({
        "id": cid,
        "brand": brand,
        "model": model,
        "title": title,
        "subtitle": sub,
        "year": clean_num(spec.get("Modellår","")) ,
        "km": clean_num(spec.get("Kilometerstand","")),
        "price": price,
        "fuel": spec.get("Drivstoff","").strip(),
        "gear": spec.get("Girkasse","").strip(),
        "body": spec.get("Karosseri","").strip(),
        "power": clean_num(spec.get("Effekt","")) ,
        "drive": spec.get("Hjuldrift","").strip(),
        "color": spec.get("Farge","").strip(),
        "seats": clean_num(spec.get("Seter","")),
        "vin": spec.get("Chassis nr. (VIN)","").strip(),
        "reg": spec.get("Registreringsnummer","").strip(),
        "description": desc,
        "equipment": equip,
        "images": imgs,
        "sold": sold,
        "finn_url": f"https://www.finn.no/mobility/item/{cid}",
    })

# ---- normalization ----
FUEL_MAP = {"Hybrid bensin": "Hybrid", "Hybrid diesel": "Hybrid",
            "Ladbar hybrid": "Hybrid", "El": "Elektrisk", "Bensin": "Bensin", "Diesel": "Diesel"}
BODY_MAP = {"SUV/Offroad": "SUV", "Sedan": "Sedan", "Kombi 5-dørs": "Kombi",
            "Kasse": "Varebil", "Stasjonsvogn": "Stasjonsvogn", "Flerbruksbil": "Varebil",
            "Cabriolet": "Cabriolet", "Coupe": "Coupe"}
BODY_INFER = {
    "449826093": "Kombi", "458704660": "SUV", "461762549": "Varebil",
    "461762728": "Kombi", "461774393": "Kombi", "464122276": "Kombi",
    "464876372": "SUV", "465707747": "SUV", "465716299": "SUV",
    "466765567": "SUV",
}
for c in cars:
    c["fuel"] = FUEL_MAP.get(c["fuel"], c["fuel"])
    if c["gear"] in ("", "Ikke oppgitt"):
        c["gear"] = ""
    b = c["body"]
    c["body"] = BODY_MAP.get(b, b) if b else BODY_INFER.get(c["id"], "")

# drop sold car with no photos (Volvo V50)
cars = [c for c in cars if c["images"]]

out = "/Users/daodilyas/Desktop/automk/.firecrawl/cars.json"
json.dump(cars, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("Parsed", len(cars), "cars ->", out)
# quick report
for c in cars:
    print(f"{c['id']} | {c['title']:<28} | {c['year']} | {str(c['km'])+' km':<12} | {str(c['price'])+' kr':<12} | {c['fuel']:<8} | {c['gear']:<8} | body={c['body'] or '-':<12} | imgs={len(c['images'])} | sold={c['sold']}")
