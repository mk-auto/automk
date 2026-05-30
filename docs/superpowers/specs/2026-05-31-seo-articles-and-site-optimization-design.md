# SEO Articles + Site-wide SEO Optimization — Design

**Date:** 2026-05-31
**Project:** MK Auto (static Norwegian car-dealership site, Oslo)
**Status:** Approved design, pending implementation plan

## Goal

Make SEO the website's strongest asset. Two parts:

1. Publish 4 genuinely useful, human-written Norwegian articles (bokmål) targeting
   what a car buyer actually searches for — easy to read, no AI slop.
2. Retrofit the entire existing site with full technical SEO.

Primary business outcome: rank for relevant searches and convert national readers
into local (Oslo) buyers at MK Auto.

## Constraints & context

- Static HTML/CSS/JS site. No framework, no build step beyond `.firecrawl/gen.py`.
- Existing design system in `styles.css`: Geist font, pure-white backgrounds,
  run-in header pattern (`.runin`), `.container`/`.section` layout, card styling.
- Car detail pages (`bil-*.html`, 25 of them) are GENERATED from
  `.firecrawl/cars.json` via `.firecrawl/gen.py`. **Do not hand-edit generated HTML** —
  change the generator template and regenerate.
- All business data (domain, NAP, logo, social image) is PLACEHOLDER for now,
  structured for a one-line find-and-replace later.
  - Canonical domain placeholder: `https://www.mkauto.no`
  - NAP placeholders (reuse existing footer values): `Økernveien 00, 0580 Oslo`,
    `+47 20 00 00 00`, `post@mkauto.no`, `Org.nr 000 000 000`, hours Man–fre 09–17 / Lør 10–14.
  - Logo / social image: placeholder path (e.g. `images/og-default.jpg`), to be swapped.

## Scope

### A. New content (4 articles + 1 hub)

**Hub page — `guider.html`**
- Title: "Guider og råd · MK Auto"
- "Råd & guider" landing page: intro + card grid linking to the 4 articles.
- Reuses existing card styling.
- Hosts `AutoDealer`/`LocalBusiness` + `BreadcrumbList` JSON-LD.

**Articles (readable slugs):**
1. `kjope-bruktbil-trygt.html` — "Slik kjøper du bruktbil trygt" (pillar piece)
2. `sjekkliste-kjop-av-bruktbil.html` — "Sjekkliste: dette ser du etter når du kjøper brukt bil"
3. `kommisjon-eller-selge-selv.html` — "Kommisjon eller selge selv?" (links to kommisjon-formidling.html)
4. `elbil-eller-bensin-diesel-bruktbil.html` — "Elbil eller bensin/diesel når du kjøper brukt?"

### B. Site-wide SEO retrofit

- Hand-authored pages (`index.html`, `butikk.html`, `kommisjon-formidling.html`):
  canonical, OG/Twitter, refined `<title>`/meta description, JSON-LD
  (`Organization` + `WebSite` + `AutoDealer` on homepage; `Breadcrumb` where relevant).
- Car pages: add SEO block to `gen.py` template, then regenerate all 25.
  Per car: keyword `<title>`, meta description, canonical, OG (the car's own image),
  and `Vehicle`/`Product` + `Offer` JSON-LD (price, mileage, year, fuel).
- Site files: `sitemap.xml` (all pages incl. car listings + articles + hub),
  `robots.txt` (allow all + sitemap reference).

## SEO targeting

Local + national blend: articles read nationally, naturally reference Oslo / MK Auto
where relevant. Target keyword themes per article (buy-intent + local):
- "kjøpe bruktbil", "bruktbil Oslo", "trygt bilkjøp"
- "sjekkliste bruktbil", "hva sjekke brukt bil"
- "selge bil kommisjon", "kommisjon vs selge selv"
- "brukt elbil eller bensin", "elbil vs diesel bruktbil"

## Per-page technical SEO checklist (every new page)

- `<title>` ≤60 chars, keyword-led.
- Meta description ~150 chars, written to earn the click.
- `<link rel="canonical">` with placeholder domain.
- Open Graph (`og:title/description/image/url`, `type=article`) + Twitter Card.
- JSON-LD: `Article`, `FAQPage` (3–5 real Q&As), `BreadcrumbList`.
- Semantic HTML: single `<h1>`, logical `<h2>/<h3>`, `<article>`, `<time datetime>`,
  descriptive `alt`, `lang="nb"`.

## Content & voice (anti-slop)

- Plain, direct bokmål. Short sentences. Concrete examples, kr-amounts, model years.
- Norwegian specifics: EU-kontroll, NAF-test, Statens vegvesen, vinterdekk-krav,
  omregistreringsavgift, garanti/reklamasjon.
- Honest, slightly opinionated brand voice ("Bruktbil, gjort ordentlig", "fra folk
  som kjører dem selv"). Advice from people who actually trade cars — not a listicle.
- Banned: filler phrases ("i dagens digitale verden", "det er viktig å huske at"),
  generic intros, padding.
- Per-article structure: `<h1>` → ingress → `<time>` → scannable `<h2>` sections →
  checklist where it fits → soft contextual CTA to shop/kommisjon → FAQ (3–5 Q&A).
- Length: ~900–1,400 words each.

## Navigation & internal linking

- Add "Guider" to header nav across all pages (`index.html`, `butikk.html`,
  `kommisjon-formidling.html`, hub, articles) and `gen.py` car-page template.
- Add "Guider" link/column to footer site-wide (incl. `gen.py`).
- Each article links contextually to `butikk.html`, `kommisjon-formidling.html`,
  and 1–2 sibling articles.

## Visual / design

- Reuse existing design system; add a focused `.article` prose block to `styles.css`:
  readable measure (~68ch), generous line-height, styled lists/blockquotes/FAQ,
  hero using existing image assets.
- Run mandated design pipeline on article/hub layout:
  taste-skill → impeccable → emil-design-eng → web-design-guidelines.

## Build approach

Hand-author each page from a shared article template (Approach A). Standalone HTML
files reusing header/footer/design system. No new generator for articles
(only 4; prose quality matters most). Car-page SEO via `gen.py` template edit.

## Out of scope

- Real domain/NAP/logo wiring (placeholders only).
- Analytics / Search Console setup.
- New article-generation tooling.
- Unrelated refactors.

## Success criteria

- 4 articles + hub live, internally linked, valid JSON-LD (passes Rich Results test logic).
- All existing pages have canonical + OG + refined meta + relevant JSON-LD.
- `sitemap.xml` + `robots.txt` present and correct.
- Car-page SEO regenerated from `gen.py` (not hand-edited).
- Articles read as genuine human Norwegian; no AI-slop phrasing.
- Design pipeline run; no console errors; responsive verified in preview.
