"""Erzeugt responsive WebP-Varianten fuer alle Projektbilder.
Aufruf: python3 tools/images.py  (aus dem Repo-Root)"""
import json, os
from PIL import Image, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'content', 'assets')
OUT = os.path.join(ROOT, 'site', 'img')
WIDTHS = [480, 960, 1600, 2400]

def process(rel, name):
    im = ImageOps.exif_transpose(Image.open(os.path.join(SRC, rel))).convert('RGB')
    w, h = im.size
    avg = im.resize((1, 1), Image.LANCZOS).getpixel((0, 0))
    sizes = []
    for tw in WIDTHS:
        if tw > w and sizes:
            break
        tw = min(tw, w)
        path = os.path.join(OUT, f'{name}-{tw}.webp')
        if not os.path.exists(path):
            im.resize((tw, round(h * tw / w)), Image.LANCZOS).save(path, 'WEBP', quality=80, method=6)
        sizes.append(tw)
    return {'w': w, 'h': h, 'sizes': sizes, 'color': '#%02x%02x%02x' % avg}

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    data = json.load(open(os.path.join(ROOT, 'content', 'projekte', 'projekte.json')))
    manifest = {}
    for p in data['projekte']:
        for i, rel in enumerate(p['bilder'], 1):
            name = f"{p['slug']}-{i:02d}"
            manifest[rel] = {'name': name, **process(rel, name)}
            print(name, manifest[rel]['w'], manifest[rel]['h'])
    for i, rel in enumerate(data.get('vermutlich_stockfotos', []), 1):
        manifest[rel] = {'name': f'stock-{i:02d}', **process(rel, f'stock-{i:02d}')}
    json.dump(manifest, open(os.path.join(OUT, 'manifest.json'), 'w'), indent=1)
