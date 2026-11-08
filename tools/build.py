"""Baut den statischen Prototyp nach site/ aus content/.

Aufruf (aus dem Repo-Root):
    python3 tools/images.py   # einmalig bzw. wenn neue Bilder dazukommen
    python3 tools/build.py
"""
import html
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENT = os.path.join(ROOT, 'content')
SITE = os.path.join(ROOT, 'site')

site = json.load(open(os.path.join(CONTENT, 'site.json')))
data = json.load(open(os.path.join(CONTENT, 'projekte', 'projekte.json')))
manifest = json.load(open(os.path.join(SITE, 'img', 'manifest.json')))
PROJECTS = data['projekte']
BY_SLUG = {p['slug']: p for p in PROJECTS}

e = html.escape


def asset_version(rel):
    import hashlib
    return hashlib.md5(open(os.path.join(SITE, rel), 'rb').read()).hexdigest()[:10]


CSS_V = asset_version('css/style.css')
JS_V = asset_version('js/main.js')

# ---------------------------------------------------------------------------
# Leistungen: Schlüssel, Labels, Seitendateien, Originaltexte
# ---------------------------------------------------------------------------
SVC_DATA = json.load(open(os.path.join(CONTENT, 'leistungen.json')))['leistungen']
# Tupel: key, label, kurz, seite, md-datei, bild (slug, index)
SERVICES = [(d['key'], d['label'], d['kurz'], d['seite'], d['original_md'], tuple(d['bild'])) for d in SVC_DATA]
SVC = {s[0]: s for s in SERVICES}
INFO = {d['key']: d for d in SVC_DATA}
TEASER = {d['key']: d['teaser'] for d in SVC_DATA}


def read_md(name):
    raw = open(os.path.join(CONTENT, 'pages', name), encoding='utf-8').read()
    body = raw.split('---', 2)[2]
    body = re.sub(r'<!--.*?-->', '', body, flags=re.S)
    body = body.split('## Bilder')[0]
    lines = [l.strip() for l in body.strip().splitlines()]
    return [l for l in lines if l and l not in ('...', '…', 'welcome', 'Start', 'Gallerie')]


# ---------------------------------------------------------------------------
# Bausteine
# ---------------------------------------------------------------------------
ICON_ARROW = '<svg viewBox="0 0 16 16" fill="none" aria-hidden="true"><path d="M3 8h10m-4-4 4 4-4 4" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>'
ICON_EXT = '<svg viewBox="0 0 16 16" fill="none" aria-hidden="true"><path d="M5 11 11 5m-5 0h5v5" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>'
ICON_CHEV = '<svg viewBox="0 0 10 10" fill="none" aria-hidden="true"><path d="m2 3.5 3 3 3-3" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/></svg>'

LOGO_MARK = ('<svg class="logo__mark" viewBox="0 0 40 40" aria-hidden="true">'
             '<circle cx="20" cy="20" r="20" fill="#f5f5f7"/>'
             '<path d="M12.2 30 20 9.5 27.8 30" fill="none" stroke="#0b0b0c" stroke-width="2.6" stroke-linejoin="round"/>'
             '<path d="M19.4 23.2h6" stroke="#0b0b0c" stroke-width="2.4"/></svg>')
LOGO = (f'<a class="logo" href="index.html" aria-label="ART AND MEDIA – Startseite">{LOGO_MARK}'
        '<span class="logo__word"><b>A</b>RT <small>AND</small> <b>M</b>EDIA</span></a>')


def img_tag(rel, sizes='100vw', alt='', eager=False, extra=''):
    m = manifest[rel]
    srcset = ', '.join(f"img/{m['name']}-{w}.webp {w}w" for w in m['sizes'])
    src = f"img/{m['name']}-{[w for w in m['sizes'] if w <= 1600][-1]}.webp"
    load = 'fetchpriority="high"' if eager else 'loading="lazy"'
    return (f'<img src="{src}" srcset="{srcset}" sizes="{sizes}" width="{m["w"]}" height="{m["h"]}" '
            f'alt="{e(alt)}" decoding="async" {load} {extra}>')


def media(rel, sizes='100vw', alt='', eager=False, cls='', style='', img_extra=''):
    m = manifest[rel]
    return (f'<div class="media {cls}" style="--c:{m["color"]};{style}">'
            f'{img_tag(rel, sizes, alt, eager, img_extra)}</div>')


def full_src(rel):
    m = manifest[rel]
    return f"img/{m['name']}-{m['sizes'][-1]}.webp"


def card(p, sizes='(max-width: 639px) 100vw, (max-width: 1023px) 50vw, 33vw', delay=0):
    keys = ' '.join(p['leistung_keys'])
    tags = ' · '.join(SVC[k][2] for k in p['leistung_keys'])
    alt = f"{p['kunde']} – {p['titel']}"
    return f'''<a class="card" href="projekt-{p['slug']}.html" data-l="{keys}" data-vt data-reveal style="--d:{delay}">
  <figure class="card__media media" style="--c:{manifest[p['cover']]['color']}">{img_tag(p['cover'], sizes, alt)}</figure>
  <div class="card__overlay" aria-hidden="true"><span class="card__client">{e(p['kunde'])}</span><span class="card__title">{e(p['titel'])}</span></div>
  <span class="card__tags" aria-hidden="true">{e(tags)}</span>
  <div class="card__caption"><span class="c">{e(p['kunde'])}</span><span class="t">{e(p['titel'])}</span></div>
</a>'''


def split_words(text, gold_words=()):
    out = []
    for w in text.split(' '):
        cls = 'w gold' if w.strip('.,–') in gold_words else 'w'
        out.append(f'<span class="{cls}">{e(w)}</span>')
    return ' '.join(out)


def lines(*ls):
    return ''.join(f'<span class="line"><span style="--i:{i}">{l}</span></span>' for i, l in enumerate(ls))


def nav(active):
    def a(href, label, key):
        cur = ' aria-current="page"' if key == active else ''
        return f'<a class="nav__link" href="{href}"{cur}>{label}</a>'
    panel = ''.join(f'<a href="{s[3]}">{e(s[1])}<span>{i:02d}</span></a>' for i, s in enumerate(SERVICES, 1))
    lcur = ' aria-current="page"' if active == 'leistungen' else ''
    return f'''<header class="header{' is-solid' if active in ('legal',) else ''}">
  <div class="wrap header__inner">
    {LOGO}
    <nav class="nav" aria-label="Hauptnavigation">
      {a('projekte.html', 'Projekte', 'projekte')}
      <div class="nav__drop">
        <a class="nav__link nav__drop-btn" href="index.html#leistungen"{lcur}>Leistungen {ICON_CHEV}</a>
        <div class="nav__panel">{panel}</div>
      </div>
      {a('kontakt.html', 'Kontakt', 'kontakt')}
      <a class="nav__link" href="https://artandmedia.shop" target="_blank" rel="noopener">Shop ↗</a>
      <a class="btn btn--small" href="kontakt.html#anfrage">Projekt anfragen</a>
    </nav>
    <button class="burger" type="button" aria-expanded="false" aria-controls="menu" aria-label="Menü öffnen"><span></span><span></span></button>
  </div>
</header>
<div class="menu" id="menu">
  <ul class="menu__list">
    <li><a href="index.html" style="--i:0">Home</a></li>
    <li><a href="projekte.html" style="--i:1">Projekte</a></li>
    <li><a href="index.html#leistungen" style="--i:2">Leistungen</a>
      <div class="menu__sub">{''.join(f'<a href="{s[3]}" style="--i:{i+3}">{e(s[1])}</a>' for i, s in enumerate(SERVICES))}</div></li>
    <li><a href="kontakt.html" style="--i:8">Kontakt</a></li>
    <li><a href="https://artandmedia.shop" target="_blank" rel="noopener" style="--i:9">Shop ↗</a></li>
  </ul>
  <div class="menu__foot">
    <a href="tel:+491716103816">+49 171 6103816</a>
    <a href="mailto:{site['email']}">{site['email']}</a>
    <span>Gärtringen · Schönaich</span>
  </div>
</div>'''


def footer():
    hq, br = site['standorte']
    svc = ''.join(f'<a href="{s[3]}">{e(s[1])}</a>' for s in SERVICES)
    return f'''<footer class="footer">
  <div class="wrap">
    <div class="footer__grid">
      <div class="footer__col"><h3>Kontakt</h3>
        <a href="tel:+491716103816">+49 171 6103816</a>
        <a href="mailto:{site['email']}">{site['email']}</a>
        <span>Mo – Fr 9:00 – 17:00</span></div>
      <div class="footer__col"><h3>Hauptsitz</h3><span>ART AND MEDIA</span><span>{hq['strasse']}</span><span>{hq['plz']} {hq['ort']}</span>
        <h3 style="margin-top:1.25rem">Niederlassung</h3><span>{br['strasse']}</span><span>{br['plz']} {br['ort']}</span></div>
      <div class="footer__col"><h3>Leistungen</h3>{svc}</div>
      <div class="footer__col"><h3>Mehr</h3><a href="projekte.html">Projekte</a><a href="kontakt.html">Kontakt</a>
        <a href="https://artandmedia.shop" target="_blank" rel="noopener">Shop ↗</a><a href="impressum.html">Impressum</a><a href="datenschutz.html">Datenschutz</a></div>
    </div>
    <div class="footer__word" aria-hidden="true"><b>A</b>RT <small>AND</small> <b>M</b>EDIA</div>
    <div class="footer__bottom"><span>2000 – 2026 Copyright © ART AND MEDIA, alle Rechte vorbehalten.</span>
      <nav aria-label="Rechtliches"><a href="sortierung.html">Bildsortierung (Prototyp)</a><a href="impressum.html">Impressum</a><a href="datenschutz.html">Datenschutz</a></nav></div>
  </div>
</footer>
<a class="proto-badge" href="sortierung.html" title="Projektnamen und Texte sind Arbeitstitel – zur Bildsortierung">Prototyp · Bildsortierung</a>'''


def page(filename, title, desc, body, active='', og_img=None):
    og = f'<meta property="og:image" content="{og_img}">' if og_img else ''
    doc = f'''<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<meta name="theme-color" content="#0b0b0c">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:type" content="website">
{og}
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="preload" href="fonts/inter-tight-latin-wght-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="css/style.css?v={CSS_V}">
<script>document.documentElement.classList.add('js')</script>
</head>
<body>
<a class="skip" href="#main">Zum Inhalt springen</a>
{nav(active)}
<main id="main">
{body}
</main>
{footer()}
<script src="js/main.js?v={JS_V}" defer></script>
</body>
</html>
'''
    open(os.path.join(SITE, filename), 'w', encoding='utf-8').write(doc)
    print('  ', filename)


def cta(title='Sie haben die Idee.<br>Wir setzen sie um.'):
    return f'''<section class="section">
  <div class="wrap cta">
    <span class="eyebrow eyebrow--gold" data-reveal>Projekt anfragen</span>
    <h2 class="display" data-split>{lines(*title.split('<br>'))}</h2>
    <p class="lead muted" data-reveal style="--d:200;max-width:34ch">Erzählen Sie uns von Ihrem Vorhaben – wir melden uns zeitnah mit einer ersten Einschätzung.</p>
    <div class="cta__actions" data-reveal style="--d:300">
      <a class="btn btn--gold" href="kontakt.html#anfrage">Projekt anfragen</a>
      <a class="btn btn--ghost" href="tel:+491716103816">0171 6103816</a>
    </div>
  </div>
</section>'''


# ---------------------------------------------------------------------------
# Seiten
# ---------------------------------------------------------------------------
def build_index():
    hero_rel = BY_SLUG['amg-petronas-f1']['bilder'][0]
    featured = ['amg-petronas-f1', 'mercedes-trophy', 'hugo-rb', 'mercedes-amg-affalterbach', 'mercedes-winterwelt',
                'hugo-boss-awards', 'mercedes-claims', 'westwing', 'tegut']
    cards = '\n'.join(card(BY_SLUG[s], delay=(i % 3) * 90) for i, s in enumerate(featured))

    svc_items, svc_frames = [], []
    for i, (key, label, short, href, md, (pslug, pidx)) in enumerate(SERVICES):
        rel = BY_SLUG[pslug]['bilder'][pidx]
        svc_items.append(f'''<div class="svc__item">
      {media(rel, '(max-width: 899px) 100vw, 1px', label, cls='svc__img-inline')}
      <span class="svc__num">{i+1:02d}</span>
      <h3 class="h2">{e(label)}</h3>
      <p>{e(TEASER[key])}</p>
      <a class="link-arrow" href="{href}">Mehr erfahren {ICON_ARROW}</a>
    </div>''')
        svc_frames.append(f'<div class="svc__frame">{media(rel, "(max-width: 899px) 1px, 58vw", label)}</div>')

    clients = ['Mercedes-AMG PETRONAS F1 Team', 'Mercedes-Benz', 'Mercedes-AMG', 'HUGO BOSS', 'Westwing', 'tegut…',
               'EDEKA', 'Bosch', 'Global Rent-a-Car', 'MercedesTrophy']
    marquee = ''.join(f'<span>{e(c)}</span>' for c in clients * 2)

    steps = [('Idee', 'Sie haben die Idee – wir hören zu, beraten und finden gemeinsam die beste Lösung für Ihren Auftritt.'),
             ('Planung', 'Gestaltung, Materialwahl und technische Planung – abgestimmt mit Ihnen, Architekten und Bauherren.'),
             ('Produktion', 'Wir sind Hersteller und Dienstleister: Standbau, Möbel, Schilder, Schriften, Drucke und Lichtwerbung.'),
             ('Montage', 'Fach- und termingerecht vor Ort – an Fassade, im Store, auf der Messe oder im Gebäude.')]
    steps_html = ''.join(f'<div class="step" data-reveal style="--d:{i*90}"><span class="step__n">{i+1:02d}</span><h3 class="h3">{t}</h3><p>{d}</p></div>'
                         for i, (t, d) in enumerate(steps))

    statement = ('ART AND MEDIA ist Gestalter, Ideenfinder und Produzent. '
                 'Wir bauen Messestände, gestalten Stores, fertigen Möbel nach Maß und setzen Marken mit Werbetechnik ins Licht – alles aus einer Hand.')

    body = f'''
<section class="hero hero--logo-top" aria-label="Einleitung">
  <div class="hero__sticky">
    <div class="hero__text wrap">
      <span class="eyebrow eyebrow--plain">Messebau · Storegestaltung · Möbelbau · Werbetechnik</span>
      <h1 class="display hero__title">{lines('Wir setzen Marken', 'ins Licht.')}</h1>
    </div>
    <div class="hero__media">{media(hero_rel, '100vw', 'Leuchtende 3D-Logos von Mercedes-Benz und Mercedes-AMG PETRONAS Formula One Team an einer Gebäudefassade', eager=True)}</div>
    <div class="hero__caption wrap">
      <p class="h3">Messebau, Storegestaltung, Möbelbau und Werbetechnik aus Gärtringen und Schönaich.</p>
      <a class="btn btn--ghost" href="projekte.html">Alle Projekte ansehen</a>
    </div>
    <span class="hero__scroll" aria-hidden="true"></span>
  </div>
</section>

<section class="section">
  <div class="wrap wrap--text">
    <p class="statement">{split_words(statement, ('Messestände,', 'Stores,', 'Möbel'))}</p>
  </div>
</section>

<section class="section--tight" id="projekte" style="padding-top:0">
  <div class="wrap section-head">
    <div class="section-head__text">
      <span class="eyebrow" data-reveal>Ausgewählte Projekte</span>
      <h2 class="h2" data-split>{lines('Arbeiten, die man', 'nicht übersieht.')}</h2>
    </div>
    <a class="link-arrow" href="projekte.html" data-reveal>Alle {len(PROJECTS)} Projekte {ICON_ARROW}</a>
  </div>
  <div class="grid">
{cards}
  </div>
</section>

<section class="section" id="leistungen">
  <div class="wrap">
    <div class="section-head">
      <div class="section-head__text">
        <span class="eyebrow" data-reveal>Leistungen</span>
        <h2 class="h2" data-split>{lines('Alles aus einer Hand.', 'Von der Idee bis zur Montage.')}</h2>
      </div>
    </div>
    <div class="svc">
      <div class="svc__list">{''.join(svc_items)}</div>
      <div class="svc__stage" aria-hidden="true">{''.join(svc_frames)}</div>
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="section-head"><div class="section-head__text">
      <span class="eyebrow" data-reveal>So arbeiten wir</span>
      <h2 class="h2" data-split>{lines('Vier Schritte.', 'Ein Ansprechpartner.')}</h2>
    </div></div>
    <div class="steps">{steps_html}</div>
  </div>
</section>

<section class="section--tight" style="padding-top:0">
  <div class="wrap">
    <div class="facts">
      <div class="fact" data-reveal><span class="fact__num"><span data-count="26">26</span><small>Jahre</small></span><span class="fact__label">Seit 2000 Partner für Werbetechnik in der Region Stuttgart.</span></div>
      <div class="fact" data-reveal style="--d:100"><span class="fact__num"><span data-count="2">2</span><small>Standorte</small></span><span class="fact__label">Hauptsitz in Gärtringen, Niederlassung in Schönaich.</span></div>
      <div class="fact" data-reveal style="--d:200"><span class="fact__num"><span data-count="6">6</span><small>Disziplinen</small></span><span class="fact__label">Messebau, Storegestaltung, Möbelbau, Lichtwerbung, Gebäude, Leitsysteme.</span></div>
    </div>
  </div>
</section>

<section class="section--tight" aria-label="Kunden">
  <div class="wrap" style="margin-bottom:var(--stack-m)"><span class="eyebrow" data-reveal>Für Marken wie</span></div>
  <div class="marquee"><div class="marquee__track">{marquee}</div></div>
</section>

{cta()}
'''
    page('index.html', 'ART AND MEDIA – Messebau, Storegestaltung, Möbelbau und Werbetechnik',
         'ART AND MEDIA aus Gärtringen und Schönaich: Messebau, Storegestaltung, Möbelbau nach Maß, 3D- und LED-Buchstaben, Lichtwerbung und Leitsysteme – alles aus einer Hand.',
         body, og_img=full_src(hero_rel))


def build_projekte():
    chips = ['<button class="chip" type="button" data-key="alle" aria-pressed="true">Alle<sup>%d</sup></button>' % len(PROJECTS)]
    for key, label, *_ in SERVICES:
        n = sum(key in p['leistung_keys'] for p in PROJECTS)
        chips.append(f'<button class="chip" type="button" data-key="{key}" aria-pressed="false">{e(label)}<sup>{n}</sup></button>')
    cards = '\n'.join(card(p, delay=(i % 3) * 90) for i, p in enumerate(PROJECTS))
    body = f'''
<section class="page-head wrap">
  <span class="eyebrow" data-reveal>Projekte</span>
  <h1 class="display" data-split>{lines('Arbeiten, die', 'man sieht.')}</h1>
  <p class="lead" data-reveal style="--d:200">Eine Auswahl aus Store, Lichtwerbung, Gebäude, Leitsystemen, Messe und Event – für Marken, die gesehen werden wollen.</p>
</section>
<div class="filter">
  <div class="wrap filter__inner">
    <div class="filter__chips" role="group" aria-label="Nach Leistung filtern">{''.join(chips)}</div>
    <span class="filter__count" aria-live="polite">{len(PROJECTS)} Projekte</span>
  </div>
</div>
<section style="padding-bottom:var(--section)">
  <div class="grid">
{cards}
  </div>
</section>
{cta()}
'''
    page('projekte.html', 'Projekte – ART AND MEDIA', 'Referenzen von ART AND MEDIA: Store und POS, 3D- und LED-Buchstaben, Gebäudegestaltung, Leitsysteme, Messe und Event.', body, 'projekte')


def build_project(i, p):
    nxt = PROJECTS[(i + 1) % len(PROJECTS)]
    imgs = p['bilder']
    hero = imgs[0]
    # Galerie: Querformate breit/voll im Wechsel, Hochformate paarweise nebeneinander
    rest = imgs[1:]
    portrait = lambda r: manifest[r]['h'] > manifest[r]['w'] * 1.05
    rows, queue = [], list(rest)
    while queue:
        r = queue.pop(0)
        if portrait(r):
            partner = next((q for q in queue if portrait(q)), None)
            if partner:
                queue.remove(partner); rows.append(('half', [r, partner]))
            else:
                rows.append(('narrow', [r]))
        else:
            rows.append(('wide' if sum(k != 'half' for k, _ in rows) % 2 == 0 else 'full', [r]))
    gal, j = [], 0
    for kind, rels in rows:
        for n, rel in enumerate(rels):
            m = manifest[rel]
            cls = 'gallery__item' + ('' if kind == 'full' else f' gallery__item--{kind}')
            sizes = {'half': '(max-width: 767px) 100vw, 50vw', 'narrow': '(max-width: 767px) 85vw, 50vw'}.get(kind, '(max-width: 767px) 100vw, 85vw')
            alt = f"{p['kunde']} – {p['titel']}, Bild {j+2}"
            ar = f"--ar:{m['w']} / {m['h']}"
            gal.append(f'<figure class="{cls}" role="button" tabindex="0" aria-label="Bild vergrößern" data-full="{full_src(rel)}" data-reveal="media" style="--d:{n * 120}">'
                       f'{media(rel, sizes, alt, style=ar)}</figure>')
            j += 1
    # Lightbox enthält auch das Hero-Bild nicht – bewusst: Galerie = Detailbilder
    leistungen = ', '.join(f'<a href="{SVC[k][3]}">{e(SVC[k][1])}</a>' for k in p['leistung_keys'])
    body = f'''
<section class="p-hero">
  {media(hero, '100vw', f"{p['kunde']} – {p['titel']}", eager=True, img_extra='style="view-transition-name:project-media"')}
  <div class="p-hero__text wrap">
    <span class="eyebrow eyebrow--gold">{e(p['kunde'])}</span>
    <h1 class="h1" data-split>{lines(e(p['titel']))}</h1>
  </div>
</section>
<div class="wrap">
  <dl class="p-meta">
    <div data-reveal><dt>Kunde</dt><dd>{e(p['kunde'])}</dd></div>
    <div data-reveal style="--d:80"><dt>Leistungen</dt><dd>{leistungen}</dd></div>
    <div data-reveal style="--d:160"><dt>Ort</dt><dd>{e(p['ort'] or 'folgt')}</dd></div>
    <div data-reveal style="--d:240"><dt>Jahr</dt><dd>{e(str(p['jahr'] or 'folgt'))}</dd></div>
  </dl>
</div>
<section class="p-intro wrap wrap--text">
  <p class="lead" data-reveal>{e(p['text_entwurf'])}</p>
</section>
{'<section class="wrap" style="padding-bottom:var(--section)"><div class="gallery">' + ''.join(gal) + '</div></section>' if len(imgs) > 1 else ''}
<a class="next" href="projekt-{nxt['slug']}.html" data-vt>
  {media(nxt['cover'], '100vw', '')}
  <span class="next__text"><span class="eyebrow eyebrow--plain">Nächstes Projekt</span><span class="h1">{e(nxt['titel'])}</span><span class="eyebrow eyebrow--gold eyebrow--plain">{e(nxt['kunde'])}</span></span>
</a>
<div class="wrap" style="padding-block:var(--stack-l);text-align:center"><a class="link-arrow" href="projekte.html">Alle Projekte {ICON_ARROW}</a></div>

<div class="lb" role="dialog" aria-modal="true" aria-label="Bildansicht">
  <img class="lb__img" alt="">
  <button class="lb__btn lb__close" type="button" aria-label="Schließen"><svg viewBox="0 0 16 16" fill="none"><path d="m3 3 10 10M13 3 3 13" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg></button>
  <button class="lb__btn lb__prev" type="button" aria-label="Vorheriges Bild"><svg viewBox="0 0 16 16" fill="none"><path d="M10 3 5 8l5 5" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg></button>
  <button class="lb__btn lb__next" type="button" aria-label="Nächstes Bild"><svg viewBox="0 0 16 16" fill="none"><path d="m6 3 5 5-5 5" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg></button>
  <span class="lb__count"></span>
</div>
'''
    page(f"projekt-{p['slug']}.html", f"{p['kunde']} – {p['titel']} | ART AND MEDIA", p['text_entwurf'], body, 'projekte', og_img=full_src(hero))


def build_leistung(svc):
    key, label, short, href, md, (pslug, pidx) = svc
    info = INFO[key]
    text = (read_md(md) if md else []) + info['intro']
    rel = BY_SLUG[pslug]['bilder'][pidx]
    projs = [p for p in PROJECTS if key in p['leistung_keys']]
    cards = '\n'.join(card(p, delay=(i % 3) * 90) for i, p in enumerate(projs))
    first, rest = text[0], text[1:]
    others = ''.join(f'<a href="{s[3]}"><span>{i:02d}</span><strong>{e(s[1])}</strong></a>'
                     for i, s in enumerate(SERVICES, 1) if s[0] != key)
    body = f'''
<section class="l-hero wrap">
  <span class="eyebrow" data-reveal>Leistung {SERVICES.index(svc)+1:02d}</span>
  <h1 class="display" style="margin-top:var(--stack-m)" data-split>{lines(e(label))}</h1>
  <div class="l-hero__media" data-reveal="media">{media(rel, '(max-width: 1440px) 100vw, 1440px', label, eager=True, style='position:absolute;inset:0')}</div>
</section>
<section class="section wrap">
  <div class="l-text">
    <p class="eyebrow eyebrow--gold" data-reveal>{e(short)}</p>
    <div>
      <p class="lead" data-reveal>{e(first)}</p>
      {''.join(f'<p class="prose" style="margin-top:var(--stack-m)" data-reveal>{e(t)}</p>' for t in rest)}
      <h2 class="eyebrow eyebrow--plain" style="margin-top:var(--stack-l)" data-reveal>Das liefern wir</h2>
      <ul class="deliver">{''.join(f'<li data-reveal style="--d:{(i % 2) * 70}">{e(x)}</li>' for i, x in enumerate(info['liefern']))}</ul>
      <div style="margin-top:var(--stack-l);display:flex;gap:.75rem;flex-wrap:wrap" data-reveal>
        <a class="btn btn--gold" href="kontakt.html#anfrage">Projekt anfragen</a>
        <a class="btn btn--ghost" href="projekte.html?leistung={key}">Alle Projekte dieser Leistung</a>
      </div>
    </div>
  </div>
</section>
<section style="padding-bottom:var(--section)">
  <div class="wrap section-head"><div class="section-head__text">
    <span class="eyebrow" data-reveal>Projekte</span>
    <h2 class="h2" data-split>{lines(e(short) + ' in der Praxis.')}</h2>
  </div></div>
  <div class="grid">
{cards}
  </div>
</section>
<section class="section--tight wrap">
  <span class="eyebrow" data-reveal style="margin-bottom:var(--stack-m)">Weitere Leistungen</span>
  <nav class="l-nav" data-reveal aria-label="Weitere Leistungen">{others}</nav>
</section>
{cta()}
'''
    page(href, f'{label} – ART AND MEDIA', ' '.join(text)[:155], body, 'leistungen', og_img=full_src(rel))


def build_kontakt():
    text = read_md('07-kontakt.md')
    intro = text[1]
    hq, br = site['standorte']
    topics = ''.join(f'<input type="checkbox" id="t-{s[0]}" name="thema" value="{e(s[1])}"><label for="t-{s[0]}">{e(s[1])}</label>' for s in SERVICES)
    maps = lambda a: 'https://www.google.com/maps/search/?api=1&query=' + re.sub(r'\s+', '+', f"{a['strasse']}, {a['plz']} {a['ort']}")
    body = f'''
<section class="page-head wrap">
  <span class="eyebrow" data-reveal>Kontakt</span>
  <h1 class="display" data-split>{lines('Ihr Kontakt', 'zu uns.')}</h1>
</section>
<section class="wrap" style="padding-bottom:var(--section)">
  <div class="contact">
    <div class="contact__info">
      <p class="lead muted" data-reveal>{e(intro)}</p>
      <div class="contact__block" data-reveal><h3>Direkt</h3>
        <a class="contact__big" href="tel:+491716103816">+49 171 6103816</a>
        <a class="contact__big" href="mailto:{site['email']}">{site['email']}</a></div>
      <div class="contact__block" data-reveal><h3>Hauptsitz</h3><span>ART AND MEDIA</span><span>{hq['strasse']}</span><span>{hq['plz']} {hq['ort']}, Germany</span>
        <a class="link-arrow" style="margin-top:.5rem" href="{maps(hq)}" target="_blank" rel="noopener">Route planen {ICON_EXT}</a></div>
      <div class="contact__block" data-reveal><h3>Niederlassung</h3><span>ART AND MEDIA</span><span>{br['strasse']}</span><span>{br['plz']} {br['ort']}, Germany</span>
        <a class="link-arrow" style="margin-top:.5rem" href="{maps(br)}" target="_blank" rel="noopener">Route planen {ICON_EXT}</a></div>
      <div class="contact__block" data-reveal><h3>Bürozeiten</h3><div class="hours"><span>Mo – Fr</span><span>9:00 – 17:00 Uhr</span><span>Sa – So</span><span>Geschlossen</span></div></div>
    </div>
    <form class="form" id="anfrage" novalidate data-reveal style="--d:150">
      <h2 class="h3">Kontaktieren Sie uns bitte</h2>
      <div class="form__row">
        <div class="field"><input id="f-name" name="name" type="text" autocomplete="name" placeholder=" " required><label for="f-name">Name*</label><span class="field__err">Bitte geben Sie Ihren Namen an.</span></div>
        <div class="field"><input id="f-tel" name="telefon" type="tel" autocomplete="tel" placeholder=" "><label for="f-tel">Telefon</label></div>
      </div>
      <div class="field"><input id="f-mail" name="email" type="email" autocomplete="email" placeholder=" " required><label for="f-mail">E-Mail*</label><span class="field__err">Bitte geben Sie eine gültige E-Mail-Adresse an.</span></div>
      <fieldset><legend>Worum geht es? (optional)</legend><div class="topics">{topics}</div></fieldset>
      <div class="field"><textarea id="f-msg" name="nachricht" placeholder=" " required></textarea><label for="f-msg">Nachricht*</label><span class="field__err">Bitte schreiben Sie uns kurz, worum es geht.</span></div>
      <label class="check"><input type="checkbox" name="datenschutz"><span>Ich habe die <a href="datenschutz.html">Datenschutzerklärung</a> gelesen und bin mit der Verarbeitung meiner Angaben zur Beantwortung der Anfrage einverstanden.*</span></label>
      <button class="btn btn--gold" type="submit">Anfrage senden</button>
      <p class="form__note">* Pflichtfelder · Prototyp: Das Formular sendet noch nicht.</p>
      <div class="form__success" role="status">
        <svg viewBox="0 0 64 64" fill="none" aria-hidden="true"><circle cx="32" cy="32" r="30" stroke="currentColor" stroke-width="2"/><path d="m20 33 8 8 16-17" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
        <h2 class="h3">Vielen Dank!</h2><p class="muted">Wir setzen uns zeitnah mit Ihnen in Verbindung.</p>
      </div>
    </form>
  </div>
</section>
'''
    page('kontakt.html', 'Kontakt – ART AND MEDIA', 'Kontakt zu ART AND MEDIA in Gärtringen und Schönaich: Telefon +49 171 6103816, mail@artand.media.', body, 'kontakt')


def legal_html(lines_):
    out, para = [], []
    url = re.compile(r'(https?://[^\s]+)')

    def flush():
        if para:
            sep = '<br>' if all(len(x) < 60 for x in para) else ' '
            txt = sep.join(e(x) for x in para)
            out.append('<p>' + url.sub(lambda m: f'<a href="{m.group(1).rstrip(".")}" rel="noopener">{m.group(1)}</a>', txt) + '</p>')
            para.clear()
    for l in lines_:
        is_head = (len(l) < 70 and not l.endswith(('.', ',', ';')) and not l.startswith(('T ', 'M ', 'Ust', 'ART AND', 'Tilo', 'Seestr', '71', 'Nelly', 'Finanzamt', 'mail@', 'http'))) or l.endswith(':')
        if is_head and len(l) < 90:
            flush()
            out.append(f'<h3>{e(l.rstrip(":"))}</h3>')
        else:
            para.append(l)
            if l.endswith(('.', ':')) or len(l) > 90:
                flush()
    flush()
    return '\n'.join(out)


def build_legal():
    imp = read_md('08-impressum.md')[1:]  # erste Zeile "Impressum" ist der Seitentitel
    ds = read_md('09-datenschutz.md')
    ds = ds[:ds.index('Kontakt')] if 'Kontakt' in ds else ds
    note = '<p class="note">Hinweis Prototyp: Texte 1:1 von der bisherigen Website übernommen. Vor dem Livegang rechtlich aktualisieren (u. a. DDG statt TMG, aktuelle Dienste).</p>'
    for fn, title, ls in [('impressum.html', 'Impressum', imp), ('datenschutz.html', 'Datenschutz', ds)]:
        body = f'''
<section class="page-head wrap wrap--text"><span class="eyebrow" data-reveal>Rechtliches</span><h1 class="h1" data-split>{lines(title)}</h1></section>
<section class="legal section"><div class="wrap wrap--text"><div class="prose">{note}{legal_html(ls)}</div></div></section>
'''
        page(fn, f'{title} – ART AND MEDIA', f'{title} von ART AND MEDIA.', body)


def build_favicon():
    open(os.path.join(SITE, 'favicon.svg'), 'w').write(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40"><circle cx="20" cy="20" r="20" fill="#0b0b0c"/>'
        '<path d="M12.2 30 20 9.5 27.8 30" fill="none" stroke="#f5f5f7" stroke-width="2.6" stroke-linejoin="round"/>'
        '<path d="M19.4 23.2h6" stroke="#bfac83" stroke-width="2.4"/></svg>')


def build_sortierung():
    badge = {'hoch': ('#30d158', 'sicher'), 'mittel': ('#ffd60a', 'wahrscheinlich'), 'niedrig': ('#ff9f0a', 'unsicher')}
    blocks = []
    for i, p in enumerate(PROJECTS, 1):
        col, lab = badge[p['zuordnung_sicherheit']]
        thumbs = ''.join(f'<a href="{full_src(r)}" target="_blank" class="media" style="--c:{manifest[r]["color"]};aspect-ratio:1;border-radius:8px">{img_tag(r, "160px", r)}</a>' for r in p['bilder'])
        leist = ' · '.join(SVC[k][1] for k in p['leistung_keys'])
        blocks.append(f'''<article class="sort" data-reveal>
  <header><span class="svc__num">{i:02d}</span><div><h2 class="h3">{e(p['kunde'])} – {e(p['titel'])}</h2>
  <p class="muted" style="font-size:.9375rem;margin-top:.35rem">{e(leist)} · {len(p['bilder'])} Bilder · <a href="projekt-{p['slug']}.html" style="color:var(--gold)">Projektseite ansehen</a></p></div>
  <span class="pill" style="--pc:{col}">Zuordnung {lab}</span></header>
  <div class="thumbs">{thumbs}</div>
  <p class="muted" style="font-size:.9375rem">Bitte prüfen: Kundenname korrekt und freigegeben? Projekttitel, Ort, Jahr, 1–3 Sätze Text. Gehören alle Bilder dazu?</p>
</article>''')
    stock = data.get('vermutlich_stockfotos', [])
    st_thumbs = ''.join(f'<a href="{full_src(r)}" target="_blank" class="media" style="--c:{manifest[r]["color"]};aspect-ratio:1;border-radius:8px">{img_tag(r, "160px", r)}</a>' for r in stock)
    body = f'''
<style>
.sort{{display:grid;gap:1.25rem;padding-block:2.5rem;border-top:1px solid var(--line)}}
.sort header{{display:grid;grid-template-columns:auto 1fr auto;gap:1.25rem;align-items:start}}
.thumbs{{display:grid;grid-template-columns:repeat(auto-fill,minmax(120px,1fr));gap:.5rem}}
.thumbs a{{transition:transform .5s var(--ease)}} .thumbs a:hover{{transform:scale(1.04)}}
.pill{{font-size:.75rem;font-weight:600;padding:.35rem .7rem;border-radius:999px;color:var(--pc);box-shadow:inset 0 0 0 1px var(--pc);white-space:nowrap}}
@media (max-width:639px){{.sort header{{grid-template-columns:auto 1fr}} .pill{{grid-column:2;justify-self:start}}}}
</style>
<section class="page-head wrap"><span class="eyebrow" data-reveal>Arbeitsstand</span>
  <h1 class="h1" data-split>{lines('Bildsortierung', 'zur Prüfung.')}</h1>
  <p class="lead" data-reveal>{len(PROJECTS)} Projektgruppen aus {sum(len(p['bilder']) for p in PROJECTS)} Bildern. Kundennamen sind aus sichtbaren Logos abgeleitet – bitte bestätigen oder korrigieren.</p>
</section>
<section class="wrap" style="padding-bottom:var(--section)">
{''.join(blocks)}
<article class="sort"><header><span class="svc__num">!</span><div><h2 class="h3">Vermutlich Stock- oder Musterfotos</h2>
<p class="muted" style="font-size:.9375rem;margin-top:.35rem">Im Prototyp nicht verwendet. Falls doch eigene Arbeiten: bitte Bescheid geben.</p></div></header>
<div class="thumbs">{st_thumbs}</div></article>
</section>'''
    page('sortierung.html', 'Bildsortierung – ART AND MEDIA Prototyp', 'Arbeitsstand der Bildsortierung.', body)


def build_404():
    body = f'''
<section class="page-head wrap" style="min-height:70vh;display:grid;align-content:center">
  <span class="eyebrow" data-reveal>Fehler 404</span>
  <h1 class="display" data-split>{lines('Diese Seite', 'gibt es nicht.')}</h1>
  <p class="lead" data-reveal style="--d:200">Vielleicht wurde sie verschoben. Hier geht es weiter:</p>
  <div class="cta__actions" style="justify-content:start;margin-top:var(--stack-m)" data-reveal>
    <a class="btn btn--gold" href="/index.html">Zur Startseite</a><a class="btn btn--ghost" href="/projekte.html">Projekte ansehen</a>
  </div>
</section>'''
    page('404.html', 'Seite nicht gefunden – ART AND MEDIA', 'Diese Seite gibt es nicht.', body)
    # 404 kann unter beliebigen Pfaden ausgeliefert werden → absolute Pfade
    f = os.path.join(SITE, '404.html')
    doc = open(f, encoding='utf-8').read()
    doc = re.sub(r'(href|src)="(?!https?:|mailto:|tel:|/|#)', r'\1="/', doc)
    open(f, 'w', encoding='utf-8').write(doc)


if __name__ == '__main__':
    print('Baue site/ …')
    build_favicon()
    build_index()
    build_projekte()
    for i, p in enumerate(PROJECTS):
        build_project(i, p)
    for s in SERVICES:
        build_leistung(s)
    build_kontakt()
    build_legal()
    build_sortierung()
    build_404()
    print('fertig.')
