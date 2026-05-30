# SEO Articles + Site-wide SEO Optimization — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish 4 human-written Norwegian SEO articles + a "Guider" hub, and retrofit the entire MK Auto site with full technical SEO (meta, canonical, Open Graph, JSON-LD, sitemap, robots).

**Architecture:** Static HTML/CSS. New article + hub pages are hand-authored standalone HTML reusing the existing design system (`styles.css`, Geist, run-in pattern). Car detail pages (`bil-*.html`) are regenerated from `.firecrawl/gen.py` after editing its template — never hand-edited. A new `.article` prose block is added to `styles.css`. SEO is verified by parsing JSON-LD with Python and previewing pages in the browser.

**Tech Stack:** HTML5, CSS (existing design system), Python 3 (`gen.py` generator), Claude Preview for browser verification.

**Note on "tests":** This codebase has no unit-test framework. Verification = (a) `grep`/structural assertions, (b) parsing JSON-LD blocks with `python3 -c "import json,..."` to prove they're valid, (c) Claude Preview snapshot/console checks. These are real checks that fail on real defects.

**Note on prose:** Article *scaffolding* (head, schema, headings, FAQ questions, CTAs, internal links, word counts) is fully specified below. The *prose paragraphs* are written during execution following the voice rules in the spec, with the design pipeline loaded (taste-skill → impeccable → emil-design-eng). Do not pre-fill prose with filler — write genuine bokmål per the voice spec.

---

## Shared conventions (read before any task)

**Placeholder constants** — used verbatim everywhere, marked so they're one find-and-replace later:
- Canonical/OG base URL: `https://www.mkauto.no`
- Default social image: `https://www.mkauto.no/images/og-default.jpg`
- Publisher logo: `https://www.mkauto.no/images/mk-logo.png`
- NAP (reuse existing footer values): name `MK Auto AS`, street `Økernveien 00`, postal `0580`, city `Oslo`, phone `+4720000000`, email `post@mkauto.no`, org `000 000 000`, hours Mo-Fr 09:00-17:00 / Sa 10:00-14:00.
- Publish date for all 4 articles: `2026-05-31` (display "31. mai 2026").

**Reusable JSON-LD publisher block** (used inside `Article` schema on every article):
```json
"publisher": {
  "@type": "Organization",
  "name": "MK Auto AS",
  "logo": { "@type": "ImageObject", "url": "https://www.mkauto.no/images/mk-logo.png" }
}
```

**Reusable `<head>` SEO block template** (fill the `{{...}}` per page; place AFTER the `<title>`/description lines, BEFORE the icon line):
```html
  <link rel="canonical" href="https://www.mkauto.no/{{slug}}.html" />
  <meta property="og:type" content="{{ogtype}}" />
  <meta property="og:site_name" content="MK Auto" />
  <meta property="og:locale" content="nb_NO" />
  <meta property="og:title" content="{{ogtitle}}" />
  <meta property="og:description" content="{{ogdesc}}" />
  <meta property="og:url" content="https://www.mkauto.no/{{slug}}.html" />
  <meta property="og:image" content="{{ogimage}}" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{{ogtitle}}" />
  <meta name="twitter:description" content="{{ogdesc}}" />
  <meta name="twitter:image" content="{{ogimage}}" />
```

**Nav `<li>` to add site-wide** (after the "Biler" item): `<li><a href="{{prefix}}guider.html">Guider</a></li>` where `{{prefix}}` is `""` on root-level pages (all pages live in repo root, so prefix is always empty — use `guider.html`).

**Mobile-menu link to add** (after "Biler"): `<a href="guider.html">Guider</a>`

**Footer link to add** (inside the `Kontakt` column `<ul>`, as first `<li>`): `<li><a href="guider.html">Guider &amp; råd</a></li>`

---

## Task 1: Add article + hub styles to `styles.css`

**Files:**
- Modify: `styles.css` (append at end)

- [ ] **Step 1: Append the article/hub CSS block**

Append to the end of `styles.css`:
```css
/* ===================== ARTICLES / GUIDER ===================== */
.article-main { padding: clamp(5rem, 9vw, 8rem) 0 clamp(4rem, 7vw, 6rem); }
.breadcrumb { font: 500 0.82rem/1.4 "Geist Mono", monospace; letter-spacing: .02em; color: var(--ink-soft, #6b6258); margin-bottom: 2.2rem; display: flex; gap: .55rem; flex-wrap: wrap; }
.breadcrumb a { color: inherit; text-decoration: none; border-bottom: 1px solid transparent; }
.breadcrumb a:hover { border-color: currentColor; }
.breadcrumb span[aria-hidden] { opacity: .5; }

.article { max-width: 68ch; margin: 0 auto; }
.article-head { margin-bottom: clamp(2.2rem, 4vw, 3.2rem); }
.article-head h1 { font-size: clamp(2.1rem, 5vw, 3.4rem); line-height: 1.04; letter-spacing: -0.02em; font-weight: 800; margin: 0 0 1.1rem; }
.article-lede { font-size: clamp(1.12rem, 2vw, 1.32rem); line-height: 1.5; color: var(--ink-soft, #4a443c); margin: 0 0 1.3rem; }
.article-meta { font: 500 0.82rem/1 "Geist Mono", monospace; letter-spacing: .04em; text-transform: uppercase; color: var(--ink-soft, #8a8175); }

.article-body { font-size: 1.08rem; line-height: 1.72; color: var(--ink, #231f1b); }
.article-body h2 { font-size: clamp(1.45rem, 3vw, 1.95rem); line-height: 1.12; letter-spacing: -0.01em; font-weight: 800; margin: 2.8rem 0 1rem; }
.article-body h3 { font-size: 1.2rem; font-weight: 700; margin: 1.8rem 0 .6rem; }
.article-body p { margin: 0 0 1.2rem; }
.article-body a { color: var(--accent, #a8662e); text-decoration: none; border-bottom: 1px solid color-mix(in srgb, var(--accent, #a8662e) 35%, transparent); transition: border-color .15s ease; }
.article-body a:hover { border-color: var(--accent, #a8662e); }
.article-body ul, .article-body ol { margin: 0 0 1.4rem; padding-left: 1.3rem; }
.article-body li { margin: 0 0 .55rem; }
.article-body strong { font-weight: 700; }
.article-body blockquote { margin: 1.8rem 0; padding: .2rem 0 .2rem 1.3rem; border-left: 3px solid var(--accent, #a8662e); font-size: 1.18rem; line-height: 1.5; color: var(--ink-soft, #4a443c); }

.checklist { list-style: none; padding: 0; margin: 1.6rem 0; border-top: 1px solid var(--line, #e7e2da); }
.checklist li { display: grid; grid-template-columns: 1.6rem 1fr; gap: .7rem; padding: .85rem 0; border-bottom: 1px solid var(--line, #e7e2da); margin: 0; }
.checklist li::before { content: "✓"; color: var(--accent, #a8662e); font-weight: 800; line-height: 1.7; }

.article-cta { margin: 3rem 0; padding: clamp(1.6rem, 3vw, 2.2rem); background: var(--ink, #231f1b); color: #fff; border-radius: 16px; }
.article-cta h2 { color: #fff; margin: 0 0 .6rem; font-size: 1.5rem; }
.article-cta p { color: rgba(255,255,255,.78); margin: 0 0 1.2rem; }

.article-faq { margin-top: 3.2rem; border-top: 1px solid var(--line, #e7e2da); padding-top: 1.4rem; }
.article-faq h2 { margin-top: 0; }
.faq-item { border-bottom: 1px solid var(--line, #e7e2da); padding: 1.1rem 0; }
.faq-item h3 { margin: 0 0 .5rem; font-size: 1.12rem; font-weight: 700; }
.faq-item p { margin: 0; color: var(--ink-soft, #4a443c); }

.related { max-width: 68ch; margin: 3.2rem auto 0; }
.related h2 { font-size: 1.1rem; text-transform: uppercase; letter-spacing: .04em; font-family: "Geist Mono", monospace; color: var(--ink-soft, #8a8175); margin: 0 0 1rem; }
.related-links { display: grid; gap: .7rem; }
.related-links a { display: flex; justify-content: space-between; gap: 1rem; padding: 1rem 1.2rem; border: 1px solid var(--line, #e7e2da); border-radius: 12px; text-decoration: none; color: var(--ink, #231f1b); font-weight: 600; transition: border-color .15s ease, transform .15s ease; }
.related-links a:hover { border-color: var(--accent, #a8662e); transform: translateY(-2px); }

/* Hub */
.guide-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: clamp(1rem, 2vw, 1.6rem); margin-top: clamp(2rem, 4vw, 3rem); }
.guide-card { display: flex; flex-direction: column; padding: clamp(1.4rem, 2.5vw, 1.9rem); border: 1px solid var(--line, #e7e2da); border-radius: 16px; text-decoration: none; color: var(--ink, #231f1b); transition: border-color .15s ease, transform .15s ease; }
.guide-card:hover { border-color: var(--accent, #a8662e); transform: translateY(-3px); }
.guide-card .gc-tag { font: 500 .75rem/1 "Geist Mono", monospace; letter-spacing: .06em; text-transform: uppercase; color: var(--accent, #a8662e); margin-bottom: .9rem; }
.guide-card h2 { font-size: 1.3rem; line-height: 1.15; font-weight: 800; margin: 0 0 .6rem; }
.guide-card p { font-size: .98rem; line-height: 1.5; color: var(--ink-soft, #4a443c); margin: 0 0 1.2rem; }
.guide-card .gc-go { margin-top: auto; font-weight: 600; color: var(--accent, #a8662e); }
```

- [ ] **Step 2: Verify the CSS parses and tokens exist**

Run: `grep -n "^:root" styles.css | head; grep -nE "\-\-ink\b|\-\-accent\b|\-\-line\b|\-\-paper\b" styles.css | head`
Expected: Confirm whether `--ink`, `--accent`, `--line`, `--ink-soft` exist. The CSS above uses fallbacks (e.g. `var(--accent, #a8662e)`) so it works regardless, but if the real token names differ, note them — they're harmless either way. Confirm no syntax error by counting braces:
Run: `python3 -c "s=open('styles.css').read();print('open',s.count('{'),'close',s.count('}'))"`
Expected: open count == close count.

- [ ] **Step 3: Commit** (skip if not a git repo)

```bash
git add styles.css && git commit -m "feat: add article and guide-hub styles"
```

---

## Task 2: Build the hub page `guider.html`

**Files:**
- Create: `guider.html`

- [ ] **Step 1: Create `guider.html`**

Use the existing page skeleton (copy the `<head>`/header/footer pattern from `kommisjon-formidling.html`, which uses `index.html#...` absolute links). Fill in:
- `<title>Guider og råd om bilkjøp og bilsalg · MK Auto</title>`
- description: `"Praktiske guider om kjøp og salg av bruktbil – sjekklister, råd om kommisjon og elbil kontra fossilbil. Ærlige råd fra MK Auto i Oslo."`
- Shared `<head>` SEO block with: `slug=guider`, `ogtype=website`, `ogtitle="Guider og råd · MK Auto"`, `ogdesc=`(same as description), `ogimage=https://www.mkauto.no/images/og-default.jpg`.
- Add the "Guider" nav `<li>`, mobile-menu link, and footer link per Shared conventions.

Main content:
```html
  <main class="article-main" id="innhold">
    <div class="container">
      <nav class="breadcrumb" aria-label="Sti"><a href="index.html">Hjem</a><span aria-hidden="true">›</span><span>Guider</span></nav>
      <div class="head" style="max-width:62ch">
        <h2 class="runin reveal"><b>Råd og guider for et tryggere bilkjøp.</b> Vi har samlet det vi får flest spørsmål om – fra sjekklisten på visning til hva som lønner seg når du skal selge.</h2>
      </div>
      <div class="guide-grid reveal">
        <a class="guide-card" href="kjope-bruktbil-trygt.html">
          <span class="gc-tag">Kjøpe bil</span>
          <h2>Slik kjøper du bruktbil trygt</h2>
          <p>Fra annonse til kontrakt: slik unngår du de vanligste fellene når du kjøper brukt.</p>
          <span class="gc-go">Les guiden →</span>
        </a>
        <a class="guide-card" href="sjekkliste-kjop-av-bruktbil.html">
          <span class="gc-tag">Sjekkliste</span>
          <h2>Dette ser du etter når du kjøper brukt bil</h2>
          <p>Punkt for punkt: rust, service, dekk, prøvekjøring og papirer.</p>
          <span class="gc-go">Se sjekklisten →</span>
        </a>
        <a class="guide-card" href="kommisjon-eller-selge-selv.html">
          <span class="gc-tag">Selge bil</span>
          <h2>Kommisjon eller selge selv?</h2>
          <p>Vi sammenligner privatsalg, kommisjon og formidling – tid, pris og trygghet.</p>
          <span class="gc-go">Les sammenligningen →</span>
        </a>
        <a class="guide-card" href="elbil-eller-bensin-diesel-bruktbil.html">
          <span class="gc-tag">Elbil vs fossil</span>
          <h2>Brukt elbil eller bensin/diesel?</h2>
          <p>Pris, rekkevidde, batterihelse og avgifter – hvem bør velge hva.</p>
          <span class="gc-go">Les guiden →</span>
        </a>
      </div>
    </div>
  </main>
```

- [ ] **Step 2: Add JSON-LD before `</head>`** (AutoDealer + Breadcrumb + ItemList of the 4 articles)

```html
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "AutoDealer",
    "name": "MK Auto AS",
    "url": "https://www.mkauto.no/",
    "image": "https://www.mkauto.no/images/og-default.jpg",
    "logo": "https://www.mkauto.no/images/mk-logo.png",
    "telephone": "+4720000000",
    "email": "post@mkauto.no",
    "address": { "@type": "PostalAddress", "streetAddress": "Økernveien 00", "postalCode": "0580", "addressLocality": "Oslo", "addressCountry": "NO" },
    "openingHoursSpecification": [
      { "@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday","Tuesday","Wednesday","Thursday","Friday"], "opens": "09:00", "closes": "17:00" },
      { "@type": "OpeningHoursSpecification", "dayOfWeek": "Saturday", "opens": "10:00", "closes": "14:00" }
    ],
    "areaServed": "Oslo"
  }
  </script>
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    "itemListElement": [
      { "@type": "ListItem", "position": 1, "name": "Hjem", "item": "https://www.mkauto.no/" },
      { "@type": "ListItem", "position": 2, "name": "Guider", "item": "https://www.mkauto.no/guider.html" }
    ]
  }
  </script>
```

- [ ] **Step 3: Verify structure + JSON-LD validity**

Run: `grep -c "guide-card" guider.html` → Expected: at least 4.
Run: `python3 -c "import re,json; s=open('guider.html').read(); [json.loads(b) for b in re.findall(r'<script type=\"application/ld\+json\">(.*?)</script>', s, re.S)]; print('JSON-LD OK')"`
Expected: prints `JSON-LD OK` (raises if any block is invalid JSON).

- [ ] **Step 4: Commit**

```bash
git add guider.html && git commit -m "feat: add guider hub page with AutoDealer schema"
```

---

## Tasks 3–6: Article pages

**Common to all four article tasks — the page scaffold:**

Each article is a standalone HTML file built on the `kommisjon-formidling.html` skeleton (head/header/footer with `index.html#...` links). Each includes:
1. `<head>`: page `<title>` + meta description (below), shared SEO block (`ogtype=article`, `ogimage` = the article's hero image URL or `og-default.jpg`), icon/fonts/styles.
2. The "Guider" nav `<li>`, mobile link, footer link.
3. Three JSON-LD blocks before `</head>`: `Article`, `FAQPage`, `BreadcrumbList`.
4. Body structure:
```html
  <main class="article-main" id="innhold">
    <div class="container">
      <nav class="breadcrumb" aria-label="Sti"><a href="index.html">Hjem</a><span aria-hidden="true">›</span><a href="guider.html">Guider</a><span aria-hidden="true">›</span><span>{{kort tittel}}</span></nav>
      <article class="article">
        <header class="article-head">
          <h1>{{H1}}</h1>
          <p class="article-lede">{{ingress – 1–2 setninger}}</p>
          <p class="article-meta"><time datetime="2026-05-31">31. mai 2026</time> · MK Auto</p>
        </header>
        <div class="article-body">
          <!-- H2 sections per outline; prose written to voice spec, ~900–1400 ord -->
          <!-- contextual internal links inline per outline -->
          <!-- optional .checklist where specified -->
          <section class="article-cta">
            <h2>{{cta-tittel}}</h2>
            <p>{{cta-tekst}}</p>
            <a class="btn" href="{{cta-href}}">{{cta-knapp}}</a>
          </section>
          <section class="article-faq">
            <h2>Ofte stilte spørsmål</h2>
            <div class="faq-item"><h3>{{Q}}</h3><p>{{A}}</p></div>
            <!-- one .faq-item per FAQ Q&A; MUST match FAQPage JSON-LD exactly -->
          </section>
        </div>
      </article>
      <aside class="related">
        <h2>Les også</h2>
        <div class="related-links"><!-- per-article related links below --></div>
      </aside>
    </div>
  </main>
```

**`Article` JSON-LD template** (fill per article):
```html
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "Article",
    "headline": "{{H1}}",
    "description": "{{meta description}}",
    "datePublished": "2026-05-31",
    "dateModified": "2026-05-31",
    "inLanguage": "nb-NO",
    "author": { "@type": "Organization", "name": "MK Auto AS" },
    "publisher": { "@type": "Organization", "name": "MK Auto AS", "logo": { "@type": "ImageObject", "url": "https://www.mkauto.no/images/mk-logo.png" } },
    "image": "{{ogimage}}",
    "mainEntityOfPage": "https://www.mkauto.no/{{slug}}.html"
  }
  </script>
```

**`FAQPage` JSON-LD template** (one `mainEntity` per FAQ; text MUST match the rendered `.faq-item`):
```html
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": [
      { "@type": "Question", "name": "{{Q}}", "acceptedAnswer": { "@type": "Answer", "text": "{{A}}" } }
    ]
  }
  </script>
```

**`BreadcrumbList` JSON-LD template:**
```html
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    "itemListElement": [
      { "@type": "ListItem", "position": 1, "name": "Hjem", "item": "https://www.mkauto.no/" },
      { "@type": "ListItem", "position": 2, "name": "Guider", "item": "https://www.mkauto.no/guider.html" },
      { "@type": "ListItem", "position": 3, "name": "{{kort tittel}}", "item": "https://www.mkauto.no/{{slug}}.html" }
    ]
  }
  </script>
```

**Per-article verification (run for each of Tasks 3–6):**
- Run: `python3 -c "import re,json; s=open('{{slug}}.html').read(); b=re.findall(r'<script type=\"application/ld\+json\">(.*?)</script>', s, re.S); assert len(b)==3, b'need 3 blocks'; [json.loads(x) for x in b]; print('JSON-LD OK', len(b))"` → Expected: `JSON-LD OK 3`.
- Run: `grep -c "<h1" {{slug}}.html` → Expected: `1` (exactly one H1).
- Run: `grep -c "faq-item" {{slug}}.html` and confirm it equals the number of `Question` entries in the FAQPage block.
- Word-count check: `python3 -c "import re; s=open('{{slug}}.html').read(); t=re.sub(r'<[^>]+>',' ',s.split('article-body')[1]); print('approx words', len(t.split()))"` → Expected: roughly 900–1400.

---

### Task 3: Article 1 — `kjope-bruktbil-trygt.html`

**Files:** Create: `kjope-bruktbil-trygt.html`

- Title: `Slik kjøper du bruktbil trygt · MK Auto`
- Description: `Skal du kjøpe bruktbil? Slik unngår du de vanligste fellene – fra annonse og prøvekjøring til kontrakt og EU-kontroll. Praktiske råd fra MK Auto i Oslo.`
- Breadcrumb short title: `Kjøpe bruktbil trygt`
- Hero/og image: `https://www.mkauto.no/images/og-default.jpg`

- [ ] **Step 1: Write the page** using the common scaffold. H2 outline (write genuine prose per voice spec under each):
  1. `Begynn med behovet, ikke annonsen`
  2. `Les annonsen som en skeptiker`
  3. `Sjekk historikken før du reiser` (mention EU-kontroll, servicehistorikk, Statens vegvesen, heftelser/gjeld i Brønnøysund)
  4. `Prøvekjøringen: hva du faktisk skal kjenne etter`
  5. `Få en uavhengig kontroll` (NAF-test / verksted)
  6. `Kontrakten og papirene`
  7. `Betaling og omregistrering`
  8. `Etter kjøpet: garanti og reklamasjon` (forskjell forbrukerkjøp vs privatkjøp)
- Inline internal links: link "kontrollert bruktbil" / "se utvalget" → `butikk.html`; "egen sjekkliste" → `sjekkliste-kjop-av-bruktbil.html`; when mentioning selling/trade → `kommisjon-formidling.html`.
- CTA: title `Vil du slippe usikkerheten?`, text `Alle bilene våre er kontrollert og kommer med full historikk. Se dem i butikken eller kom innom på Økern.`, href `butikk.html`, button `Se bilene våre`.
- FAQ (4 — text identical in HTML and JSON-LD):
  - Q: `Hvor mye bør jeg sette av til uforutsette kostnader når jeg kjøper bruktbil?` A: (rule of thumb + omregistrering/forsikring/dekk)
  - Q: `Er det tryggere å kjøpe bruktbil fra forhandler enn privat?` A: (forbrukerkjøpsloven, reklamasjonsrett)
  - Q: `Hva er forskjellen på garanti og reklamasjonsrett?` A:
  - Q: `Bør jeg ta med noen som kan bil på visning?` A:
- Related links: `sjekkliste-kjop-av-bruktbil.html` ("Sjekkliste for kjøp av bruktbil"), `elbil-eller-bensin-diesel-bruktbil.html` ("Elbil eller bensin/diesel?").

- [ ] **Step 2: Verify** (run the per-article verification block above with `slug=kjope-bruktbil-trygt`).
- [ ] **Step 3: Commit** — `git add kjope-bruktbil-trygt.html && git commit -m "feat: add article – kjøpe bruktbil trygt"`

---

### Task 4: Article 2 — `sjekkliste-kjop-av-bruktbil.html`

**Files:** Create: `sjekkliste-kjop-av-bruktbil.html`

- Title: `Sjekkliste for kjøp av bruktbil · MK Auto`
- Description: `Punkt for punkt: dette sjekker du før du kjøper brukt bil – rust, service, dekk, prøvekjøring og papirer. Praktisk sjekkliste fra MK Auto i Oslo.`
- Breadcrumb short title: `Sjekkliste bruktbil`
- og image: `og-default.jpg`

- [ ] **Step 1: Write the page.** H2 outline:
  1. `Før du drar: dette gjør du hjemmefra`
  2. `Utvendig: lakk, panelgap og rust`
  3. `Under panseret`
  4. `Innvendig og elektronikk`
  5. `Dekk, bremser og understell`
  6. `Prøvekjøringen`
  7. `Papirsjekken`
  8. `Sjekklisten i kortform` — render as a `<ul class="checklist">` with ~10–14 concrete items (one-liners).
- Inline links: "hele kjøpsprosessen" → `kjope-bruktbil-trygt.html`; "kontrollerte biler" → `butikk.html`.
- CTA: title `Slipp sjekklisten – vi har gjort jobben`, text `Hver bil hos oss er gjennomgått punkt for punkt før den legges ut. Se utvalget i butikken.`, href `butikk.html`, button `Se bilene`.
- FAQ (3):
  - Q: `Hva er de største faresignalene på en brukt bil?`
  - Q: `Bør jeg ta med en mekaniker på visning?`
  - Q: `Hvor mye rust er greit på en eldre bil?`
- Related: `kjope-bruktbil-trygt.html`, `kommisjon-eller-selge-selv.html`.

- [ ] **Step 2: Verify** (`slug=sjekkliste-kjop-av-bruktbil`; also `grep -c "checklist" ...` ≥ 1).
- [ ] **Step 3: Commit** — `git commit -m "feat: add article – sjekkliste kjøp av bruktbil"`

---

### Task 5: Article 3 — `kommisjon-eller-selge-selv.html`

**Files:** Create: `kommisjon-eller-selge-selv.html`

- Title: `Kommisjon eller selge bilen selv? · MK Auto`
- Description: `Lønner det seg å selge bilen selv, eller la noen gjøre det for deg? Vi sammenligner privatsalg, kommisjon og formidling – tid, pris og trygghet.`
- Breadcrumb short title: `Kommisjon eller selge selv`
- og image: `og-default.jpg`

- [ ] **Step 1: Write the page.** H2 outline:
  1. `Tre måter å selge bilen på`
  2. `Selge selv: full kontroll, alt ansvaret`
  3. `Kommisjon: vi selger i vårt navn`
  4. `Formidling: vi gjør jobben, du står som selger`
  5. `Hva koster det – og hva sitter du igjen med?`
  6. `Tid, trygghet og ansvar`
  7. `Hva passer for deg?`
- Inline links: "kommisjon og formidling i detalj" → `kommisjon-formidling.html` (link prominently, this is the conversion path); "hva bilen er verdt" → `index.html#finn`.
- CTA: title `Vil du selge uten styret?`, text `Vi tar oss av annonse, visning, prøvekjøring og oppgjør. Les hvordan kommisjon og formidling fungerer.`, href `kommisjon-formidling.html`, button `Slik fungerer det`.
- FAQ (3):
  - Q: `Hva er forskjellen på kommisjon og formidling?`
  - Q: `Får jeg mer for bilen ved å selge den selv?`
  - Q: `Hvor lang tid tar et kommisjonssalg?`
- Related: `kommisjon-formidling.html` ("Kommisjon & formidling – slik fungerer det"), `kjope-bruktbil-trygt.html`.

- [ ] **Step 2: Verify** (`slug=kommisjon-eller-selge-selv`).
- [ ] **Step 3: Commit** — `git commit -m "feat: add article – kommisjon eller selge selv"`

---

### Task 6: Article 4 — `elbil-eller-bensin-diesel-bruktbil.html`

**Files:** Create: `elbil-eller-bensin-diesel-bruktbil.html`

- Title: `Brukt elbil eller bensin/diesel? · MK Auto`
- Description: `Bør du kjøpe brukt elbil eller fossilbil? Vi går gjennom pris, rekkevidde, batterihelse, lading, avgifter og hvem som bør velge hva.`
- Breadcrumb short title: `Elbil eller fossil`
- og image: `og-default.jpg`

- [ ] **Step 1: Write the page.** H2 outline:
  1. `Prisbildet på bruktmarkedet`
  2. `Rekkevidde og hverdagen`
  3. `Batterihelse: det viktigste på en brukt elbil` (SoH, garanti på batteri)
  4. `Lading hjemme og på farten`
  5. `Avgifter, forsikring og verdifall`
  6. `Når bensin eller diesel gir mest mening`
  7. `Hvem bør velge hva`
- Inline links: "se elbilene våre" → `butikk.html` (note: shop filters on `Elektrisk` fuel); "trygt bilkjøp" → `kjope-bruktbil-trygt.html`; "sjekkliste" → `sjekkliste-kjop-av-bruktbil.html`.
- CTA: title `Usikker på hva som passer deg?`, text `Vi har både elbiler og bensin/diesel på lager, og hjelper deg å finne riktig. Se utvalget eller ta kontakt.`, href `butikk.html`, button `Se bilene`.
- FAQ (3):
  - Q: `Hvor lenge holder batteriet på en brukt elbil?`
  - Q: `Lønner det seg fortsatt å kjøpe elbil?`
  - Q: `Hva koster det å lade kontra å fylle bensin?`
- Related: `kjope-bruktbil-trygt.html`, `sjekkliste-kjop-av-bruktbil.html`.

- [ ] **Step 2: Verify** (`slug=elbil-eller-bensin-diesel-bruktbil`).
- [ ] **Step 3: Commit** — `git commit -m "feat: add article – elbil eller bensin/diesel"`

---

## Task 7: Site-wide nav + footer "Guider" link (hand-authored pages)

**Files:**
- Modify: `index.html`, `butikk.html`, `kommisjon-formidling.html`

- [ ] **Step 1: Add "Guider" to each page's desktop nav**

In each file, find the `<ul class="nav-links">` and insert after the `<li>...Biler...</li>`:
`<li><a href="guider.html">Guider</a></li>`

- [ ] **Step 2: Add "Guider" to each mobile menu**

In each file's `<div class="mobile-menu" ...>`, insert after the Biler link:
`<a href="guider.html">Guider</a>`

- [ ] **Step 3: Add footer link**

In each file's footer `Kontakt` column `<ul>`, add as first `<li>`:
`<li><a href="guider.html">Guider &amp; råd</a></li>`

- [ ] **Step 4: Verify**

Run: `for f in index.html butikk.html kommisjon-formidling.html; do echo "$f: $(grep -c 'guider.html' $f)"; done`
Expected: each file shows at least `3` (nav + mobile + footer).

- [ ] **Step 5: Commit** — `git commit -m "feat: link guider hub in nav and footer"`

---

## Task 8: Retrofit SEO meta + JSON-LD on hand-authored pages

**Files:**
- Modify: `index.html`, `butikk.html`, `kommisjon-formidling.html`

- [ ] **Step 1: Add the shared `<head>` SEO block to each page**

Insert after the existing `<meta name="description" ...>` line (values below). Use `ogtype=website` for all three.
- `index.html`: slug `` (root) → use `og:url`/canonical `https://www.mkauto.no/`; ogtitle `MK Auto · Bruktbiler i Oslo`; ogdesc = existing description; ogimage `og-default.jpg`. (For the homepage, set `<link rel="canonical" href="https://www.mkauto.no/" />` and `og:url` to the same.)
- `butikk.html`: canonical/og:url `https://www.mkauto.no/butikk.html`; ogtitle `Bruktbiler til salgs · MK Auto`; ogdesc = existing description; ogimage `og-default.jpg`.
- `kommisjon-formidling.html`: canonical/og:url `https://www.mkauto.no/kommisjon-formidling.html`; ogtitle `Kommisjon & formidling · MK Auto`; ogdesc = existing description; ogimage `og-default.jpg`.

- [ ] **Step 2: Add JSON-LD before `</head>`**

`index.html` — Organization + WebSite + AutoDealer (full AutoDealer block from Task 2 Step 2, plus):
```html
  <script type="application/ld+json">
  { "@context": "https://schema.org", "@type": "WebSite", "name": "MK Auto", "url": "https://www.mkauto.no/", "inLanguage": "nb-NO" }
  </script>
```
(Include the same `AutoDealer` block used on the hub.)

`butikk.html` — BreadcrumbList (Hjem › Biler) + `CollectionPage`:
```html
  <script type="application/ld+json">
  { "@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
    { "@type": "ListItem", "position": 1, "name": "Hjem", "item": "https://www.mkauto.no/" },
    { "@type": "ListItem", "position": 2, "name": "Biler", "item": "https://www.mkauto.no/butikk.html" } ] }
  </script>
```

`kommisjon-formidling.html` — BreadcrumbList (Hjem › Kommisjon & formidling) using the same pattern with position 2 name `Kommisjon & formidling`, item `https://www.mkauto.no/kommisjon-formidling.html`.

- [ ] **Step 3: Verify JSON-LD validity per file**

Run: `for f in index.html butikk.html kommisjon-formidling.html; do python3 -c "import re,json,sys; s=open('$f').read(); [json.loads(b) for b in re.findall(r'<script type=\"application/ld\+json\">(.*?)</script>', s, re.S)]; print('$f JSON-LD OK')"; done`
Expected: prints `... JSON-LD OK` for each.
Run: `for f in index.html butikk.html kommisjon-formidling.html; do echo "$f canonical: $(grep -c 'rel=\"canonical\"' $f), og: $(grep -c 'og:title' $f)"; done`
Expected: canonical `1`, og `1` each.

- [ ] **Step 4: Commit** — `git commit -m "feat: add canonical, Open Graph and JSON-LD to core pages"`

---

## Task 9: Car-page SEO via `gen.py` + regenerate

**Files:**
- Modify: `.firecrawl/gen.py` (HEAD template + nav/footer + detail() schema)

- [ ] **Step 1: Add the "Guider" nav + footer link to the `HEAD`/`FOOT` constants in `gen.py`**

In `HEAD` (lines ~176-189), add after the Biler `<li>`: `<li><a href="guider.html">Guider</a></li>`, and in the mobile menu after the Biler link: `<a href="guider.html">Guider</a>`.
In `FOOT` (the `Kontakt` column `<ul>`, ~line 207-209), add as first `<li>`: `<li><a href="guider.html">Guider &amp; råd</a></li>`.

- [ ] **Step 2: Add canonical + OG block to the `HEAD` template**

`HEAD` is `.format()`-ed with `title`, `year`, `metadesc`. Add new format fields `{slug}` and `{ogimage}`. Insert after the `<meta name="description" .../>` line in `HEAD`:
```html
  <link rel="canonical" href="https://www.mkauto.no/{slug}.html" />
  <meta property="og:type" content="product" />
  <meta property="og:site_name" content="MK Auto" />
  <meta property="og:locale" content="nb_NO" />
  <meta property="og:title" content="{title} {year} · MK Auto" />
  <meta property="og:description" content="{metadesc}" />
  <meta property="og:url" content="https://www.mkauto.no/{slug}.html" />
  <meta property="og:image" content="https://www.mkauto.no/{ogimage}" />
  <meta name="twitter:card" content="summary_large_image" />
```
Note: `title`/`metadesc` come pre-escaped via `esc()`. `{` and `}` literals elsewhere in HEAD: there are none in the static markup, but verify the `.format()` call still works (Step 4). Update the `head = HEAD.format(...)` call in `detail()` (line ~284) to pass `slug=f"bil-{c['id']}"` and `ogimage=f"images/{c['id']}/1.jpg"`.

- [ ] **Step 3: Add `Vehicle` + `Offer` JSON-LD inside `detail()`**

Build a JSON-LD string in `detail()` (before `return head + body + FOOT`) and inject it into the page. Add a placeholder `{schema}` token at the end of the `HEAD` template (just before `</head>`), or simpler: append the script to `head` after `.format()`. Use this exact Python:
```python
    import json as _json
    fuel_map = {"Elektrisk": "Electric", "Bensin": "Gasoline", "Diesel": "Diesel", "Hybrid": "Hybrid"}
    vehicle = {
        "@context": "https://schema.org",
        "@type": "Car",
        "name": f"{c['title']} {sub}",
        "brand": {"@type": "Brand", "name": c["brand"]},
        "model": c.get("model") or c["title"],
        "vehicleModelDate": c["year"],
        "mileageFromOdometer": {"@type": "QuantitativeValue", "value": c["km"], "unitCode": "KMT"} if c["km"] else None,
        "fuelType": fuel_map.get(fuel, fuel),
        "vehicleTransmission": c["gear"],
        "color": c["color"],
        "vehicleIdentificationNumber": c["vin"],
        "image": f"https://www.mkauto.no/images/{c['id']}/1.jpg",
        "url": f"https://www.mkauto.no/bil-{c['id']}.html",
        "offers": {
            "@type": "Offer",
            "price": c["price"],
            "priceCurrency": "NOK",
            "availability": "https://schema.org/SoldOut" if sold else "https://schema.org/InStock",
            "itemCondition": "https://schema.org/UsedCondition",
            "seller": {"@type": "AutoDealer", "name": "MK Auto AS", "areaServed": "Oslo"}
        } if c["price"] else None,
    }
    vehicle = {k: v for k, v in vehicle.items() if v is not None}
    schema_block = '  <script type="application/ld+json">\n  ' + _json.dumps(vehicle, ensure_ascii=False) + '\n  </script>\n'
    head = head.replace("</head>", schema_block + "</head>")
```

- [ ] **Step 4: Run the generator and confirm it succeeds**

Run: `cd /Users/daodilyas/Desktop/automk && python3 .firecrawl/gen.py`
Expected: prints `Wrote butikk.html: 25 cards` and `Wrote 25 detail pages`, no traceback.
**Important:** `gen.py` also rewrites `butikk.html`. Re-run Tasks 7 & 8 edits for `butikk.html` if they were done before this step, OR do Task 9 before Tasks 7–8 for butikk. **Resolution: do the `butikk.html` nav/footer/SEO edits (Tasks 7–8) AFTER running `gen.py`**, since the generator only touches the `#filterBody`, grid, count regions and the nav/footer/head of butikk are static — confirm by diffing. To be safe, run `gen.py` first in this task, then apply Task 7/8 butikk edits.

- [ ] **Step 5: Verify a sample car page**

Run: `python3 -c "import re,json; s=open('bil-447397423.html').read(); b=re.findall(r'<script type=\"application/ld\+json\">(.*?)</script>', s, re.S); d=json.loads(b[0]); print('type',d['@type'],'price',d['offers']['price'],'canonical',('canonical' in s))"`
Expected: `type Car price 309532 canonical True`.
Run: `grep -c 'guider.html' bil-447397423.html` → Expected ≥ 2 (nav + footer).

- [ ] **Step 6: Commit** — `git add .firecrawl/gen.py bil-*.html butikk.html && git commit -m "feat: add Vehicle/Offer schema and SEO meta to generated car pages"`

---

## Task 10: `sitemap.xml` + `robots.txt`

**Files:**
- Create: `robots.txt`, `sitemap.xml` (generated)

- [ ] **Step 1: Create `robots.txt`**
```
User-agent: *
Allow: /

Sitemap: https://www.mkauto.no/sitemap.xml
```

- [ ] **Step 2: Generate `sitemap.xml` with a small script**

Run this one-off (it enumerates static pages + all car pages from `cars.json`):
```bash
cd /Users/daodilyas/Desktop/automk && python3 - <<'PY'
import json, datetime
base = "https://www.mkauto.no/"
today = datetime.date.today().isoformat()
static = ["", "butikk.html", "kommisjon-formidling.html", "guider.html",
          "kjope-bruktbil-trygt.html", "sjekkliste-kjop-av-bruktbil.html",
          "kommisjon-eller-selge-selv.html", "elbil-eller-bensin-diesel-bruktbil.html"]
cars = json.load(open(".firecrawl/cars.json", encoding="utf-8"))
urls = static + [f"bil-{c['id']}.html" for c in cars]
out = ['<?xml version="1.0" encoding="UTF-8"?>',
       '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for u in urls:
    pr = "1.0" if u == "" else ("0.8" if u in ("butikk.html","guider.html") else "0.6")
    out.append(f"  <url><loc>{base}{u}</loc><lastmod>{today}</lastmod><priority>{pr}</priority></url>")
out.append("</urlset>")
open("sitemap.xml","w",encoding="utf-8").write("\n".join(out)+"\n")
print("Wrote sitemap.xml with", len(urls), "urls")
PY
```
Expected: `Wrote sitemap.xml with 33 urls` (8 static + 25 cars).

- [ ] **Step 3: Verify well-formed XML**

Run: `python3 -c "import xml.dom.minidom as m; m.parse('sitemap.xml'); print('sitemap OK')"`
Expected: `sitemap OK`.

- [ ] **Step 4: Commit** — `git add robots.txt sitemap.xml && git commit -m "feat: add sitemap.xml and robots.txt"`

---

## Task 11: Design pipeline audit + browser verification

**Files:** none (review only; fix forward into the relevant files if issues found)

- [ ] **Step 1: Run the mandated design pipeline on the article/hub layout**

Load and apply, in order: `taste-skill`, `impeccable` (run `audit` + `polish` on `guider.html` and one article), `emil-design-eng`. Apply fixes to `styles.css`/article markup as recommended.

- [ ] **Step 2: Run `web-design-guidelines` audit**

Review `guider.html` and the 4 article pages against the Web Interface Guidelines (a11y, responsive, anti-patterns). Fix issues found.

- [ ] **Step 3: Browser verification with Claude Preview**

Start preview, then for `guider.html` and each article:
- `preview_console_logs` → Expected: no errors.
- `preview_snapshot` → confirm H1, sections, FAQ, CTA, related links render.
- `preview_resize` to mobile width → confirm nav, article measure, guide-grid reflow.
- `preview_screenshot` of `guider.html` + article 1 to share as proof.

- [ ] **Step 4: Cross-link + canonical sanity sweep**

Run: `grep -L 'guider.html' index.html butikk.html kommisjon-formidling.html` → Expected: no output (all contain it).
Run: `for f in guider.html kjope-bruktbil-trygt.html sjekkliste-kjop-av-bruktbil.html kommisjon-eller-selge-selv.html elbil-eller-bensin-diesel-bruktbil.html; do echo "$f canonical=$(grep -c 'rel=\"canonical\"' $f)"; done` → Expected: each `1`.

- [ ] **Step 5: Final commit** — `git commit -am "polish: design audit fixes for articles and hub"`

---

## Self-review notes (author)

- **Spec coverage:** hub (T2), 4 articles (T3–T6), nav/footer linking (T7, T9), core-page SEO retrofit (T8), car-page SEO via gen.py + regenerate (T9), sitemap+robots (T10), design pipeline + a11y audit + preview (T11), article CSS (T1). All spec sections mapped.
- **Generated-HTML rule:** car-page SEO is done in `gen.py` then regenerated (T9), never hand-edited — matches the project memory + spec.
- **Ordering caveat:** `gen.py` rewrites `butikk.html` regions. T9 Step 4 flags this — run `gen.py` before applying the `butikk.html` nav/footer/SEO edits, or re-apply after. The generator only rewrites `#filterBody`/grid/count, but apply static edits after regen to be safe.
- **FAQ consistency:** every article's visible `.faq-item` text must match its `FAQPage` JSON-LD `name`/`text` exactly — verification step counts them; reviewer must confirm text equality.
- **Placeholders:** domain/NAP/logo/og-image are intentional placeholders per spec, all under `https://www.mkauto.no` and `images/og-default.jpg` / `images/mk-logo.png` for one-shot find-replace.
