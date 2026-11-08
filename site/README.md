# ART AND MEDIA – Website-Prototyp

Statische Seite ohne Framework (HTML/CSS/Vanilla-JS), erzeugt aus `content/`.

## Ansehen
```bash
cd site && python3 -m http.server 8080
```
→ http://localhost:8080 · Bildsortierung: http://localhost:8080/sortierung.html

## Neu bauen
```bash
python3 tools/images.py   # WebP-Varianten (480/960/1600/2400 px) + Farb-Platzhalter
python3 tools/build.py    # alle Seiten aus content/ erzeugen
```
Projektdaten pflegen in `content/projekte/projekte.json` (Kunde, Titel, Leistungen, Bilder, Text, Ort, Jahr).

## Seiten
- `index.html` – Startseite
- `projekte.html` – alle Projekte, Filter nach Leistung (`?leistung=3d`)
- `projekt-<slug>.html` – 22 Projektseiten
- `leistung-*.html` – 5 Leistungsseiten (Originaltexte)
- `kontakt.html`, `impressum.html`, `datenschutz.html`
- `sortierung.html` – Arbeitsstand Bildsortierung (nicht für Livegang)

## UX & Motion
- **Hero:** Bild öffnet sich beim Scrollen von der Karte zum Vollbild (sticky + clip-path), Headline zeilenweise eingeblendet
- **Statement:** Wort-für-Wort-Aufhellung beim Scrollen
- **Projekt-Raster (LIGANOVA-Prinzip):** randlos; Hover → Bild entsättigt, Kunde + Projekt erscheinen; auf Touch-Geräten Beschriftung dauerhaft unter dem Bild
- **Projektseiten:** Parallax-Hero, Galerie nach Bildformat, Vorhang-Reveal, Lightbox (Tastatur, Wischen, nach unten wischen schließt)
- **Leistungen:** Sticky-Bühne mit Bildwechsel (Desktop), Karten mit Bild (Mobil)
- **Filter:** FLIP-Animation, Zähler, URL-Parameter
- **Seitenübergänge:** View Transitions API – angeklicktes Projektbild morpht in den Hero der Projektseite (Chrome, Edge, Safari 18+)
- Header: Glas-Effekt, blendet beim Runterscrollen aus und beim Hochscrollen ein
- `prefers-reduced-motion` wird vollständig respektiert
- Schrift Inter Tight selbst gehostet (keine Verbindung zu Google → DSGVO)

## Offene Punkte vor Livegang
- Projektnamen und Texte sind Arbeitstitel → Bestätigung / Freigabe der Kundennamen
- Neue Leistungstexte (content/leistungen.json: intro, liefern) sind Entwürfe → vom Kunden bestätigen
- Vorschaubild beim Teilen: site/og-image.png (Logo). Beim Vercel-Deploy setzt tools/og-base.mjs die absolute Adresse; für die echte Domain in Vercel SITE_URL=https://artand.media setzen
- Hosting: Vercel Hobby ist nur für nicht-kommerzielle Nutzung → für den Livegang Vercel Pro, Cloudflare Pages oder Netlify
- Fakten „26 Jahre“ (aus „2000 – 2026 Copyright“ abgeleitet) bestätigen
- Kontaktformular braucht Versand (z. B. PHP-Mailer beim Hoster oder Formular-Dienst)
- Impressum und Datenschutz rechtlich aktualisieren
- Logo als Vektordatei (SVG) vom Kunden; derzeit nachgebaut
