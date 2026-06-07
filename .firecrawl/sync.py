#!/usr/bin/env python3
"""One-command Finn -> website sync for MK Auto.

  python3 .firecrawl/sync.py            review-first: sync locally + report, NO push
  python3 .firecrawl/sync.py --publish  also commit & push to main (site redeploys)

Steps:
  1. Scrape the dealer's Finn listing  -> current car IDs (active inventory)
  2. New cars (on Finn, not yet on site): scrape detail page + download photos
  3. Cars gone from Finn: kept on site, auto-marked "Solgt", sorted to the end
  4. Regenerate butikk.html, bil-*.html, and the homepage carousel
  5. (--publish only) commit & push to main

After a plain run, review the result in the local preview, then publish with
--publish (or just `git push`). New cars with no body type on Finn are flagged
below — add them to BODY_INFER in parse.py if needed before publishing.
"""
import os, re, sys, json, subprocess, html as H

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FC   = os.path.join(ROOT, ".firecrawl")
ORG_ID = "3440242"
LISTING_URL = f"https://www.finn.no/mobility/search/car?orgId={ORG_ID}"
ITEM_URL    = "https://www.finn.no/mobility/item/{id}"
IDS_PATH    = os.path.join(FC, "ids.txt")
ACTIVE_PATH = os.path.join(FC, "active_ids.txt")

def sh(cmd, **kw):
    return subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, **kw)

def read_ids(path):
    return [l.strip() for l in open(path).read().split() if l.strip()] if os.path.exists(path) else []

def firecrawl(url, fmts, wait):
    out = os.path.join(FC, "_sync_tmp.json")
    r = sh(["firecrawl", "scrape", url, "--format", fmts, "--wait-for", str(wait), "-o", out])
    if r.returncode != 0 or not os.path.exists(out):
        raise RuntimeError(f"firecrawl scrape failed for {url}\n{r.stderr[-400:]}")
    d = json.load(open(out)); os.remove(out)
    # CLI may nest under "data"
    return d.get("data", d) if isinstance(d, dict) else d

def scrape_listing_ids():
    d = firecrawl(LISTING_URL, "markdown,links", 4000)
    ids = set(re.findall(r"(?:item/|finnkode=)(\d{8,10})", json.dumps(d)))
    if not ids:
        raise RuntimeError("listing scrape returned 0 car IDs — Finn layout may have changed")
    return sorted(ids)

def scrape_car(cid):
    d = firecrawl(ITEM_URL.format(id=cid), "markdown,rawHtml", 3500)
    md   = d.get("markdown", "")
    html = d.get("rawHtml") or d.get("html", "")
    if "## Spesifikasjoner" not in md:
        raise RuntimeError(f"car {cid}: no spec block — scrape likely incomplete")
    open(os.path.join(FC, "cars", f"{cid}.md"),   "w", encoding="utf-8").write(md)
    open(os.path.join(FC, "cars", f"{cid}.html"), "w", encoding="utf-8").write(html)

def download_images(cid):
    cars = {c["id"]: c for c in json.load(open(os.path.join(FC, "cars.json"), encoding="utf-8"))}
    c = cars.get(cid)
    if not c or not c["images"]:
        return 0
    os.makedirs(os.path.join(ROOT, "images", cid), exist_ok=True)
    for n, uuid in enumerate(c["images"], 1):
        url = f"https://images.finncdn.no/dynamic/1280w/item/{cid}/{uuid}"
        sh(["curl", "-sS", "-L", "-o", os.path.join(ROOT, "images", cid, f"{n}.jpg"), url])
    return len(c["images"])

def run(script):
    r = sh([sys.executable, os.path.join(FC, script)])
    if r.returncode != 0:
        raise RuntimeError(f"{script} failed:\n{r.stderr[-600:]}")
    return r.stdout

# ---- homepage carousel: 6 newest cars for sale ----
def nb(n): return f"{int(n):,}".replace(",", " ") if n is not None else ""
def esc(s): return H.escape(s or "", quote=True)

def patch_carousel():
    cars = json.load(open(os.path.join(FC, "cars.json"), encoding="utf-8"))
    feat = sorted([c for c in cars if not c["sold"]], key=lambda c: (-(c["year"] or 0), c["id"]))[:6]
    def card(c):
        sub = esc(c.get("subtitle") or c["model"] or c["title"])
        return (f'          <article class="ecar">\n'
                f'            <div class="ei"><img class="eimg" src="images/{c["id"]}/1.jpg" alt="{esc(c["title"])}" width="1280" height="960" loading="lazy" decoding="async"><span class="pill-tag">Til salgs</span></div>\n'
                f'            <div class="ec"><h3>{esc(c["title"])}</h3><div class="sub">{sub}</div>\n'
                f'              <div class="erow"><div><div class="v">{c["year"]}</div><div class="k">Årsmodell</div></div><div><div class="v">{nb(c["km"])}</div><div class="k">km</div></div><div><div class="v">{esc(c["fuel"])}</div><div class="k">Drivstoff</div></div></div>\n'
                f'              <div class="ebuy"><span class="price">{nb(c["price"])}<span class="cur">kr</span></span><a class="btn" href="bil-{c["id"]}.html">Se bilen &rarr;</a></div></div>\n'
                f'          </article>')
    track = '        <div class="car-track" id="carTrack">\n' + "\n".join(card(c) for c in feat) + "\n        </div>"
    idx = os.path.join(ROOT, "index.html")
    src = open(idx, encoding="utf-8").read()
    src2, n = re.subn(r'        <div class="car-track" id="carTrack">.*?\n        </div>', lambda m: track, src, count=1, flags=re.S)
    if n != 1:
        raise RuntimeError("carousel block (#carTrack) not found in index.html")
    open(idx, "w", encoding="utf-8").write(src2)
    return [c["id"] for c in feat]

def git_publish(added, sold_now):
    sh(["git", "add", "-A"])
    msg = (f"feat: sync inventory from Finn ({len(added)} new, {len(sold_now)} sold)\n\n"
           f"new: {', '.join(added) or 'none'}\nsold: {', '.join(sold_now) or 'none'}")
    c = sh(["git", "commit", "-m", msg])
    if c.returncode != 0:
        print(c.stdout + c.stderr); return
    p = sh(["git", "push", "origin", "main"])
    print(p.stdout + p.stderr)
    print("Pushed — Vercel will redeploy.")

def main():
    publish = "--publish" in sys.argv
    print(f"Scraping Finn listing (orgId={ORG_ID}) …")
    active = scrape_listing_ids()
    published = read_ids(IDS_PATH)
    prev_active = set(read_ids(ACTIVE_PATH)) or set(published)

    new      = [i for i in active if i not in set(published)]
    sold_now = [i for i in prev_active if i not in set(active)]
    print(f"  on Finn now: {len(active)} | published: {len(published)} | new: {len(new)} | newly sold: {len(sold_now)}")

    for cid in new:
        print(f"  scraping new car {cid} …")
        scrape_car(cid)

    # ids.txt accumulates (sold cars stay); active_ids.txt = current Finn set
    open(IDS_PATH, "w").write("\n".join(published + [i for i in new if i not in set(published)]) + "\n")
    open(ACTIVE_PATH, "w").write("\n".join(active) + "\n")

    print(run("parse.py").strip().splitlines()[0])
    for cid in new:
        print(f"  {cid}: downloaded {download_images(cid)} photos")
    run("gen.py")
    feat = patch_carousel()
    print(f"Regenerated butikk + detail pages; carousel: {', '.join(feat)}")

    # warn about new cars missing a body type
    cars = {c["id"]: c for c in json.load(open(os.path.join(FC, "cars.json"), encoding="utf-8"))}
    noflag = [i for i in new if cars.get(i) and not cars[i]["body"]]
    if noflag:
        print(f"  NOTE: no body type for {noflag} — add to BODY_INFER in parse.py if you want a filter match")

    if not new and not sold_now:
        print("No inventory changes. Pages regenerated (idempotent).")
    if publish:
        git_publish(new, sold_now)
    else:
        print("\nReview-first: open the local preview, then publish with:")
        print("  python3 .firecrawl/sync.py --publish")

if __name__ == "__main__":
    main()
