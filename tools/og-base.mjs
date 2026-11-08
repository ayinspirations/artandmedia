// Läuft beim Vercel-Deploy: setzt in den Vorschau-Tags (og:url, og:image, twitter:image)
// die tatsächliche Adresse des Deployments ein. Ohne Vercel-Variablen bleibt artand.media stehen.
import { readdirSync, readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';

const env = process.env;
const host = env.SITE_URL?.replace(/^https?:\/\//, '')
  || (env.VERCEL_ENV === 'production' ? env.VERCEL_PROJECT_PRODUCTION_URL : env.VERCEL_BRANCH_URL || env.VERCEL_URL);

if (!host) {
  console.log('og-base: keine Deploy-Adresse gefunden, Vorschau-Tags bleiben auf https://artand.media');
  process.exit(0);
}
const base = `https://${host.replace(/\/$/, '')}`;
const dir = new URL('../site/', import.meta.url).pathname;
const re = /((?:property|name)="(?:og:url|og:image|twitter:image)" content=")https:\/\/artand\.media/g;
let n = 0;
for (const f of readdirSync(dir).filter(f => f.endsWith('.html'))) {
  const p = join(dir, f);
  const html = readFileSync(p, 'utf8');
  const out = html.replace(re, `$1${base}`);
  if (out !== html) { writeFileSync(p, out); n++; }
}
console.log(`og-base: ${n} Seiten auf ${base} gesetzt`);
