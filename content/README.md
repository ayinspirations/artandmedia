# artand.media – Inhaltsarchiv für den Relaunch

Stand: Scrape vom 08.11.2026 von https://www.artand.media (alle Seiten aus der Sitemap + versteckte Datenschutzseite `/privacy`).

## Struktur

| Pfad | Inhalt |
|---|---|
| `site.json` | Stammdaten: Firma, Kontakt, Standorte, Bürozeiten, Steuerdaten, Navigation |
| `pages/*.md` | Eine Datei pro Seite, Originaltext wörtlich, SEO-Titel/Meta, Bilderliste |
| `assets/<seite>/` | Alle Bilder pro Seite (126 Dateien, meist 1920 px breit, teils Originale) |
| `assets/brand/` | Logo (`Logo_Start.png`) und Favicon |
| `assets/_vorlage-blog-stockfotos/` | Stockfotos der IONOS-Vorlage – **nicht übernehmen** |
| `_raw/` | Vollständige Rohdaten: gerenderter Text, Full-Page-Screenshots, `pages.json` (alle Links/Bild-URLs) |

## Seitenzuordnung alt → neu

| Navigation | Alte URL | Neue Datei |
|---|---|---|
| Home | `/` | `00-index.md` |
| Store / POS | `/in-store` | `01-store-pos.md` |
| 3D / LED Buchstaben | `/3d-buchstaben` | `02-3d-led-buchstaben.md` |
| Gebäude- und Objektgestaltung | `/in-building8cb93643` | `03-gebaeude-objektgestaltung.md` |
| Leit- und Orientierungssysteme | `/kopie-gebäude--und-objektgestaltung` | `04-leit-orientierungssysteme.md` |
| Messe & Event | `/kopie-gebäude--und-objektgestaltung32402ae8` | `05-messe-event.md` |
| Galerie | `/galerie` | `06-galerie.md` |
| Kontakt | `/kontakt` | `07-kontakt.md` |
| Impressum | `/impressum` | `08-impressum.md` |
| (Cookie-Banner „Mehr Infos“) | `/privacy` | `09-datenschutz.md` |
| Shop | extern: artandmedia.shop | – |

→ Für den Relaunch 301-Redirects von den alten URLs einplanen.

## Auffälligkeiten / Klärungsbedarf beim Relaunch

1. **E-Mail-Tippfehler im Header:** `maill@artand.media` (doppeltes l). Der Header-Button „Kontakt“ verlinkt auf `mymail@mailservice.com` (Vorlagen-Platzhalter).
2. **Impressum nennt andere Mail:** `mail@art-and-media.net` statt `mail@artand.media`.
3. **Zweite Telefonnummer** nur in der Datenschutzerklärung: `07031 262435`; Datenschutz nennt Schönaich als Adresse, Impressum Gärtringen.
4. **Telefonformat** `+49 0171 …` ist falsch (richtig: `+49 171 …`).
5. **Rechtstexte veraltet:** Impressum verweist auf TMG (seit 05/2024 DDG), Datenschutz von 07/2020 erwähnt Facebook-Plugins und Google Analytics. Für die neue Seite neu erstellen lassen (Generator oder Anwalt).
6. **Blog-Beiträge** (3 Stück, „Duda Owner IONOS, 15. April 2020“) sind reine Vorlagentexte → nicht übernehmen. Rohdaten liegen trotzdem unter `_raw/text/blog-*.txt`.
7. **Kaum Text** auf den Leistungsseiten (je 1 Absatz, Überschriften nur „…“). Galerie-Überschrift „Gallerie“ (Tippfehler). Leistungsseiten haben teils falsche Seitentitel (Galerie heißt „3D Buchstaben“).
8. **Keine Alt-Texte** an den Bildern, Bilddateinamen sind Kameranamen (IMG_xxxx).
9. Viele Referenzen zeigen Marken (Mercedes-Benz, AMG, Maybach, Petronas F1, Hugo Boss). Vor der Veröffentlichung klären, ob Referenzkunden namentlich genannt werden dürfen.

## Projekt-Sortierung (Stand Prototyp)
`projekte/projekte.json`: 22 Projektgruppen aus 100 Bildern, Kunden aus sichtbaren Logos abgeleitet, je Gruppe mit Sicherheit der Zuordnung (hoch/mittel/niedrig). 7 Bilder als vermutliche Stock- oder Musterfotos markiert (nicht verwendet), 3 Duplikate aussortiert. Visuelle Übersicht: `site/sortierung.html`.
