#!/usr/bin/env python3
"""Generate butikk.html car grid + per-car detail pages from cars.json."""
import json, re, html, os

ROOT = "/Users/daodilyas/Desktop/automk"
cars = json.load(open(os.path.join(ROOT, ".firecrawl/cars.json"), encoding="utf-8"))

def nb(n):
    """Norwegian thousands grouping with non-breaking space."""
    if n is None:
        return ""
    return f"{n:,}".replace(",", " ")

def esc(s):
    return html.escape(s or "", quote=True)

# newest first by default
cars_sorted = sorted(cars, key=lambda c: (c["sold"], -(c["year"] or 0)))

FUEL_CLASS = {"Elektrisk": "fuel-el"}

# ---------- shop cards ----------
def card(c):
    fuel = c["fuel"] or "Bensin"
    fcls = FUEL_CLASS.get(fuel, "")
    sold = c["sold"]
    imgs = c["images"]
    photoct = len(imgs)
    sub = c["subtitle"] or c["model"]
    gear = c["gear"] or "—"
    href = f"bil-{c['id']}.html"
    sold_flag = '<span class="sold-flag">Solgt</span>\n            ' if sold else ''
    return f'''        <article class="scar{' is-sold' if sold else ''}" data-id="{c['id']}"
          data-name="{esc(c['title'])} {esc(sub)}" data-brand="{esc(c['brand'])}"
          data-body="{esc(c['body'])}" data-fuel="{esc(fuel)}" data-gear="{esc(c['gear'])}"
          data-year="{c['year'] or 0}" data-km="{c['km'] or 0}" data-price="{c['price'] or 0}"
          data-sold="{1 if sold else 0}">
          <div class="ci">
            <a href="{href}" aria-label="Se {esc(c['title'])}"><img src="images/{c['id']}/1.jpg" alt="{esc(c['title'])} {esc(sub)}" loading="lazy" width="700" height="525"></a>
            {sold_flag}<span class="photocount" aria-hidden="true">&#9635; {photoct}</span>
          </div>
          <div class="cb">
            <h3>{esc(c['title'])}</h3>
            <div class="sub">{esc(sub)}</div>
            <div class="sspecs">
              <div class="sp"><span class="sv">{c['year'] or '—'}</span><span class="sk">Modellår</span></div>
              <div class="sp"><span class="sv">{nb(c['km'])} km</span><span class="sk">Kilometer</span></div>
              <div class="sp"><span class="sv">{esc(fuel)}</span><span class="sk">Drivstoff</span></div>
              <div class="sp"><span class="sv">{esc(gear)}</span><span class="sk">Girkasse</span></div>
            </div>
            <div class="cf">
              <span class="price">{nb(c['price'])}<span class="cur">kr</span></span>
              <a class="go" href="{href}">Se bil &rarr;</a>
            </div>
          </div>
        </article>'''

cards_html = "\n".join(card(c) for c in cars_sorted)

# facet chips from real data, ordered by frequency
def facet(key):
    from collections import Counter
    cnt = Counter(c[key] for c in cars if c[key])
    return [v for v, _ in cnt.most_common()]

brands = facet("brand")
bodies = facet("body")
fuels = facet("fuel")
gears = facet("gear")

def chips(values, fkey):
    out = []
    for v in values:
        out.append(f'                <button type="button" class="chip" data-val="{esc(v)}" aria-pressed="false">{esc(v)}</button>')
    return "\n".join(out)

maxprice = max(c["price"] for c in cars if c["price"])
price_cap = ((maxprice // 50000) + 1) * 50000  # round up to 50k

shop_count = len(cars)

# ---------- read existing butikk.html, replace dynamic regions ----------
butikk = open(os.path.join(ROOT, "butikk.html"), encoding="utf-8").read()

# rebuild filter chip groups
brand_block = f'''            <div class="fgroup">
              <span class="glabel" id="lb-merke">Merke</span>
              <div class="chips" role="group" aria-labelledby="lb-merke" data-filter="brand">
{chips(brands,"brand")}
              </div>
            </div>'''
body_block = f'''            <div class="fgroup">
              <span class="glabel" id="lb-body">Karosseri</span>
              <div class="chips" role="group" aria-labelledby="lb-body" data-filter="body">
{chips(bodies,"body")}
              </div>
            </div>'''
fuel_block = f'''            <div class="fgroup">
              <span class="glabel" id="lb-fuel">Drivstoff</span>
              <div class="chips" role="group" aria-labelledby="lb-fuel" data-filter="fuel">
{chips(fuels,"fuel")}
              </div>
            </div>'''
gear_block = f'''            <div class="fgroup">
              <span class="glabel" id="lb-gear">Girkasse</span>
              <div class="chips" role="group" aria-labelledby="lb-gear" data-filter="gear">
{chips(gears,"gear")}
              </div>
            </div>'''
price_block = f'''            <div class="fgroup">
              <label class="glabel" for="maxpris">Maks pris</label>
              <div class="slider-head"><span>inntil</span><span><b id="maxprisLabel">{nb(price_cap)} kr</b></span></div>
              <input type="range" id="maxpris" min="0" max="{price_cap}" step="20000" value="{price_cap}">
            </div>'''

filter_body = f'''          <div class="fbody" id="filterBody">
            <div class="fgroup">
              <label class="glabel" for="q">Søk</label>
              <input class="txt" id="q" type="search" autocomplete="off" placeholder="Modell eller merke …">
            </div>
{brand_block}
{body_block}
{fuel_block}
{gear_block}
{price_block}
          </div>'''

# replace #filterBody block
butikk = re.sub(r'          <div class="fbody" id="filterBody">.*?\n          </div>',
                filter_body, butikk, flags=re.S)

# replace grid contents — match the whole grid region up to the shop-empty
# marker (robust against the 10-space </div>s inside each card)
grid_block = f'''          <div class="shop-grid" id="grid">
{cards_html}
          </div>

          '''
butikk = re.sub(r'          <div class="shop-grid" id="grid">.*?</div>\s*(?=<div class="shop-empty")',
                grid_block, butikk, flags=re.S)

# active-pills container before shop-bar? insert after shop-bar. Add if missing.
if 'id="activePills"' not in butikk:
    butikk = butikk.replace(
        '          <div class="shop-grid" id="grid">',
        '          <div class="active-pills" id="activePills" aria-live="polite"></div>\n          <div class="shop-grid" id="grid">')

# fix count
butikk = re.sub(r'<b id="count">\d+</b>', f'<b id="count">{shop_count}</b>', butikk)

open(os.path.join(ROOT, "butikk.html"), "w", encoding="utf-8").write(butikk)
print("Wrote butikk.html:", shop_count, "cards")

# ---------- detail pages ----------
HEAD = '''<!DOCTYPE html>
<html lang="nb">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta name="theme-color" content="#ffffff" />
  <title>{title} {year} · MK Auto</title>
  <meta name="description" content="{metadesc}" />
  <link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='6' fill='%23231f1b'/%3E%3Ctext x='16' y='22' font-family='Geist,Arial,sans-serif' font-size='14' font-weight='800' text-anchor='middle' fill='%23a8662e'%3EMK%3C/text%3E%3C/svg%3E" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Geist:wght@100..900&family=Geist+Mono:wght@100..900&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="styles.css" />
</head>
<body>
  <a class="skip-link" href="#bil">Hopp til innhold</a>

  <header class="site-header is-scrolled" id="header">
    <div class="container">
      <nav class="nav" aria-label="Hovedmeny">
        <a class="brand" href="index.html#top" translate="no" aria-label="MK Auto – til forsiden"><span class="mk">MK</span><span class="auto">Auto</span><span class="dot">.</span></a>
        <ul class="nav-links">
          <li><a href="butikk.html">Biler</a></li>
          <li><a href="index.html#tjenester">Tjenester</a></li>
          <li><a href="index.html#finn">Finn din bil</a></li>
          <li><a class="btn btn--ghost" href="index.html#finn">Kontakt oss</a></li>
        </ul>
        <button class="nav-toggle" id="navToggle" aria-label="Åpne meny" aria-expanded="false" aria-controls="mobileMenu"><span></span><span></span><span></span></button>
      </nav>
    </div>
    <div class="mobile-menu" id="mobileMenu">
      <a href="butikk.html">Biler</a>
      <a href="index.html#tjenester">Tjenester</a>
      <a href="index.html#finn">Finn din bil</a>
      <a class="btn" href="index.html#finn">Kontakt oss</a>
    </div>
  </header>
'''

FOOT = '''  <footer class="site-footer">
    <div class="container">
      <div class="footer-top">
        <div class="footer-brand">
          <a class="brand" href="index.html#top" translate="no"><span class="mk">MK</span><span class="auto">Auto</span><span class="dot">.</span></a>
          <p>Bruktbiler gjort ordentlig, fra folk som kjører dem selv. Besøk oss på Økern i Oslo.</p>
        </div>
        <div class="footer-col"><h4>Tjenester</h4><ul>
          <li><a href="index.html#tjenester">Kjøp</a></li><li><a href="index.html#tjenester">Selg</a></li><li><a href="kommisjon-formidling.html">Kommisjon &amp; formidling</a></li><li><a href="index.html#tjenester">Innbytte</a></li>
        </ul></div>
        <div class="footer-col"><h4>Besøk oss</h4><ul>
          <li>Økernveien 00, 0580 Oslo</li><li>Man–fre 09–17</li><li>Lør 10–14</li>
        </ul></div>
        <div class="footer-col"><h4>Kontakt</h4><ul>
          <li><a href="tel:+4720000000">+47 20 00 00 00</a></li><li><a href="mailto:post@mkauto.no">post@mkauto.no</a></li><li><a href="index.html#finn">Finn din bil</a></li>
        </ul></div>
      </div>
      <div class="footer-bottom">
        <span>© <span id="year">2026</span> MK Auto AS · Org.nr 000 000 000</span>
        <span class="legal"><a href="#">Personvern</a><a href="#">Vilkår</a><a href="#">Salgsbetingelser</a></span>
      </div>
    </div>
  </footer>

  <script src="detail.js"></script>
</body>
</html>
'''

def render_desc(desc):
    if not desc:
        return '<p>Ta kontakt for mer informasjon om denne bilen.</p>'
    paras = [p for p in desc.split("\n\n") if p.strip()]
    out = []
    for p in paras:
        p = esc(p)
        # **bold** -> <strong>
        p = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', p)
        out.append(f'<p>{p}</p>')
    return "\n        ".join(out)

def spec_rows(c):
    rows = [
        ("Modellår", c["year"]),
        ("Kilometerstand", f"{nb(c['km'])} km" if c["km"] else None),
        ("Drivstoff", c["fuel"]),
        ("Girkasse", c["gear"]),
        ("Karosseri", c["body"]),
        ("Effekt", f"{c['power']} hk" if c["power"] else None),
        ("Hjuldrift", c["drive"]),
        ("Farge", c["color"]),
        ("Seter", c["seats"]),
        ("Reg.nr", c["reg"]),
        ("Chassisnr (VIN)", c["vin"]),
    ]
    out = []
    for k, v in rows:
        if v in (None, "", 0):
            continue
        out.append(f'          <div class="row"><span class="k">{esc(k)}</span><span class="v">{esc(str(v))}</span></div>')
    return "\n".join(out)

def thumbs(c):
    out = []
    for i, _ in enumerate(c["images"], 1):
        cur = ' aria-current="true"' if i == 1 else ''
        out.append(f'          <button class="gthumb" type="button" data-src="images/{c["id"]}/{i}.jpg"{cur} aria-label="Bilde {i}"><img src="images/{c["id"]}/{i}.jpg" alt="" loading="lazy" width="200" height="150"></button>')
    return "\n".join(out)

def equip(c):
    if not c["equipment"]:
        return ""
    items = "\n".join(f'          <li>{esc(e)}</li>' for e in c["equipment"])
    return f'''      <section class="dblock">
        <h2>Utstyr</h2>
        <ul class="equip-list">
{items}
        </ul>
      </section>'''

def detail(c):
    fuel = c["fuel"] or "Bensin"
    sold = c["sold"]
    sub = c["subtitle"] or c["model"]
    gear = c["gear"] or "—"
    tag = ('<span class="tag sold">Solgt</span>' if sold
           else f'<span class="tag {FUEL_CLASS.get(fuel,"")}">{esc(fuel)}</span>')
    soldban = '<div class="soldban">Denne bilen er solgt</div>\n          ' if sold else ''
    metadesc = f"{c['title']} {sub}, {c['year']}, {nb(c['km'])} km, {esc(fuel)}. Til salgs hos MK Auto i Oslo."
    metadesc = re.sub(r' ', ' ', metadesc)
    head = HEAD.format(title=esc(c["title"]), year=c["year"] or "", metadesc=esc(metadesc))

    keyspecs = f'''            <div class="keyspecs">
              <div class="ks"><div class="v">{c['year'] or '—'}</div><div class="k">Modellår</div></div>
              <div class="ks"><div class="v">{nb(c['km'])} km</div><div class="k">Kilometer</div></div>
              <div class="ks"><div class="v">{esc(fuel)}</div><div class="k">Drivstoff</div></div>
              <div class="ks"><div class="v">{esc(gear)}</div><div class="k">Girkasse</div></div>
            </div>'''

    body = f'''
  <main class="detail" id="bil">
    <div class="container">
      <a class="back-link" href="butikk.html">&larr; Alle biler</a>
      <div class="detail-grid">
        <div>
          <div class="gallery">
            <div class="gmain">
              <img id="gmain" src="images/{c['id']}/1.jpg" alt="{esc(c['title'])} {esc(sub)}" width="900" height="675">
              {tag}
            </div>
            <div class="gthumbs">
{thumbs(c)}
            </div>
          </div>
        </div>

        <aside>
          <div class="dsum">
            {soldban}<div class="dsum-body">
              <div class="brandline">{esc(c['brand'])}</div>
              <h1>{esc(c['title'])}</h1>
              <div class="variant">{esc(sub)}</div>
              <div class="dprice">{nb(c['price'])} <span class="cur">kr</span></div>
              <div class="dprice-note">Totalpris inkl. omregistrering</div>
{keyspecs}
              <div class="dcta">
                <a class="btn" href="index.html#finn">Kontakt om bilen</a>
                <a class="btn btn--ghost" href="tel:+4720000000">Ring oss &middot; +47 20 00 00 00</a>
              </div>
              <a class="finn-link" href="{esc(c['finn_url'])}" target="_blank" rel="noopener">Se annonsen på Finn &rarr;</a>
            </div>
          </div>
        </aside>
      </div>

      <section class="dblock desc">
        <h2>Beskrivelse</h2>
        {render_desc(c['description'])}
      </section>

      <section class="dblock">
        <h2>Spesifikasjoner</h2>
        <div class="spec-table">
{spec_rows(c)}
        </div>
      </section>

{equip(c)}

      <div class="dealer-card">
        <div>
          <h3>Vil du se den i virkeligheten?</h3>
          <p>Kom innom Økern for en titt og en prøvekjøring, eller ta kontakt så finner vi et tidspunkt.</p>
        </div>
        <a class="btn" href="index.html#finn">Avtal visning</a>
      </div>
    </div>
  </main>

'''
    return head + body + FOOT

for c in cars:
    fn = os.path.join(ROOT, f"bil-{c['id']}.html")
    open(fn, "w", encoding="utf-8").write(detail(c))
print("Wrote", len(cars), "detail pages")
