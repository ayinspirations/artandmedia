/* ART AND MEDIA – Prototyp. Vanilla JS, keine Abhängigkeiten. */
(() => {
  'use strict';
  const doc = document.documentElement;
  doc.classList.add('js');
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
  const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
  const easeInOut = t => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);

  /* ---------- Bilder sanft einblenden ---------- */
  $$('.media img').forEach(img => {
    if (img.complete && img.naturalWidth) return;
    img.setAttribute('data-loading', '');
    const done = () => img.removeAttribute('data-loading');
    img.addEventListener('load', done, { once: true });
    img.addEventListener('error', done, { once: true });
  });

  /* ---------- Lade-Animation ---------- */
  const markLoaded = () => requestAnimationFrame(() => document.body.classList.add('is-loaded'));
  if (document.readyState === 'complete') markLoaded(); else window.addEventListener('load', markLoaded);
  setTimeout(markLoaded, 1200); // Fallback, falls ein Bild hängt

  /* ---------- Header: Glas-Effekt + Ausblenden beim Runterscrollen ---------- */
  const header = $('.header');
  let lastY = window.scrollY;
  const onHeader = () => {
    const y = window.scrollY;
    header.classList.toggle('is-scrolled', y > 8);
    const menuOpen = document.body.classList.contains('menu-open');
    if (!menuOpen && !reduce) {
      const threshold = window.innerHeight * 0.6;
      if (y > lastY + 4 && y > threshold) header.classList.add('is-hidden');
      else if (y < lastY - 4 || y < threshold) header.classList.remove('is-hidden');
    }
    lastY = y;
  };

  /* ---------- Mobile-Menü ---------- */
  const burger = $('.burger');
  const menu = $('.menu');
  const setMenu = open => {
    document.body.classList.toggle('menu-open', open);
    burger.setAttribute('aria-expanded', String(open));
    burger.setAttribute('aria-label', open ? 'Menü schließen' : 'Menü öffnen');
    menu.inert = !open;
    header.classList.remove('is-hidden');
    if (open) $('a', menu).focus({ preventScroll: true });
  };
  if (burger && menu) {
    menu.inert = true;
    burger.addEventListener('click', () => setMenu(!document.body.classList.contains('menu-open')));
    $$('a', menu).forEach(a => a.addEventListener('click', () => setMenu(false)));
    document.addEventListener('keydown', e => { if (e.key === 'Escape' && document.body.classList.contains('menu-open')) { setMenu(false); burger.focus(); } });
    window.matchMedia('(min-width: 1024px)').addEventListener('change', e => { if (e.matches) setMenu(false); });
  }

  /* ---------- Reveal beim Scrollen ---------- */
  const revealIO = new IntersectionObserver(entries => {
    entries.forEach(en => {
      if (!en.isIntersecting) return;
      en.target.classList.add('is-in');
      revealIO.unobserve(en.target);
    });
  }, { rootMargin: '0px 0px -12% 0px', threshold: 0.01 });
  $$('[data-reveal], [data-split]').forEach(el => revealIO.observe(el));

  /* ---------- Scroll-Scrubbing (Hero, Statement, Parallax) ---------- */
  const hero = $('.hero');
  const pHero = $('.p-hero');
  const statements = $$('.statement');
  statements.forEach(st => { st._words = $$('.w', st); });

  const scrub = () => {
    const vh = window.innerHeight;
    if (hero && !reduce) {
      const r = hero.getBoundingClientRect();
      const total = r.height - vh;
      const p = clamp(-r.top / (total * 0.85));
      hero.style.setProperty('--p', p.toFixed(4));
      hero.style.setProperty('--e', easeInOut(clamp(p * 1.15)).toFixed(4));
    }
    if (pHero && !reduce) {
      const r = pHero.getBoundingClientRect();
      pHero.style.setProperty('--p', clamp(-r.top / r.height).toFixed(4));
    }
    statements.forEach(st => {
      const r = st.getBoundingClientRect();
      if (r.bottom < 0 || r.top > vh) return;
      const p = reduce ? 1 : clamp((vh * 0.82 - r.top) / (r.height + vh * 0.35));
      const lit = Math.round(p * st._words.length);
      st._words.forEach((w, i) => w.classList.toggle('on', i < lit));
    });
  };

  let ticking = false;
  const onScroll = () => {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(() => { onHeader(); scrub(); ticking = false; });
  };
  window.addEventListener('scroll', onScroll, { passive: true });
  window.addEventListener('resize', onScroll, { passive: true });
  onHeader(); scrub();

  /* ---------- Leistungen: Sticky-Bühne ---------- */
  const svcItems = $$('.svc__item');
  const svcFrames = $$('.svc__frame');
  if (svcItems.length && svcFrames.length) {
    const setActive = i => {
      svcItems.forEach((el, j) => el.classList.toggle('is-active', i === j));
      svcFrames.forEach((el, j) => el.classList.toggle('is-active', i === j));
    };
    setActive(0);
    const io = new IntersectionObserver(entries => {
      entries.forEach(en => { if (en.isIntersecting) setActive(svcItems.indexOf(en.target)); });
    }, { rootMargin: '-45% 0px -45% 0px' });
    svcItems.forEach(el => io.observe(el));
  }

  /* ---------- Zahlen hochzählen ---------- */
  const countIO = new IntersectionObserver(entries => {
    entries.forEach(en => {
      if (!en.isIntersecting) return;
      countIO.unobserve(en.target);
      const el = en.target, to = +el.dataset.count, from = +(el.dataset.from || 0);
      if (reduce) { el.textContent = to; return; }
      const t0 = performance.now(), dur = 1600;
      const step = t => {
        const k = clamp((t - t0) / dur);
        el.textContent = Math.round(from + (to - from) * (1 - Math.pow(1 - k, 4)));
        if (k < 1) requestAnimationFrame(step);
      };
      requestAnimationFrame(step);
    });
  }, { threshold: 0.6 });
  $$('[data-count]').forEach(el => countIO.observe(el));

  /* ---------- Projekt-Filter mit FLIP-Animation ---------- */
  const filter = $('.filter');
  if (filter) {
    const chips = $$('.chip', filter);
    const cards = $$('.grid .card');
    const count = $('.filter__count', filter);
    const apply = (key, animate = true) => {
      const first = new Map(cards.map(c => [c, c.getBoundingClientRect()]));
      let n = 0;
      cards.forEach(c => {
        const show = key === 'alle' || c.dataset.l.split(' ').includes(key);
        c.classList.toggle('is-hidden', !show);
        if (show) { n++; c.classList.add('is-in'); }
      });
      chips.forEach(ch => ch.setAttribute('aria-pressed', String(ch.dataset.key === key)));
      if (count) count.textContent = `${n} ${n === 1 ? 'Projekt' : 'Projekte'}`;
      if (!animate || reduce) return;
      cards.forEach(c => {
        if (c.classList.contains('is-hidden')) return;
        const a = first.get(c), b = c.getBoundingClientRect();
        if (!a.width) { c.animate([{ opacity: 0, transform: 'scale(.96)' }, { opacity: 1, transform: 'none' }], { duration: 600, easing: 'cubic-bezier(.22,1,.36,1)' }); return; }
        const dx = a.left - b.left, dy = a.top - b.top;
        if (dx || dy) c.animate([{ transform: `translate(${dx}px,${dy}px)` }, { transform: 'none' }], { duration: 700, easing: 'cubic-bezier(.22,1,.36,1)' });
      });
    };
    chips.forEach(ch => ch.addEventListener('click', () => {
      const key = ch.dataset.key;
      apply(key);
      const url = new URL(location.href);
      if (key === 'alle') url.searchParams.delete('leistung'); else url.searchParams.set('leistung', key);
      history.replaceState(null, '', url);
      ch.scrollIntoView({ inline: 'nearest', block: 'nearest', behavior: reduce ? 'auto' : 'smooth' });
    }));
    const initial = new URLSearchParams(location.search).get('leistung');
    apply(chips.some(c => c.dataset.key === initial) ? initial : 'alle', false);
  }

  /* ---------- Lightbox ---------- */
  const items = $$('.gallery__item');
  if (items.length) {
    const lb = $('.lb');
    const img = $('.lb__img', lb);
    const cnt = $('.lb__count', lb);
    let idx = 0, lastFocus = null;
    const show = (i, instant) => {
      idx = (i + items.length) % items.length;
      const src = items[idx].dataset.full, alt = $('img', items[idx]).alt;
      const swap = () => { img.src = src; img.alt = alt; cnt.textContent = `${idx + 1} / ${items.length}`; };
      if (instant) { swap(); return; }
      img.classList.add('is-swapping');
      setTimeout(() => { swap(); img.onload = () => img.classList.remove('is-swapping'); if (img.complete) img.classList.remove('is-swapping'); }, 180);
      [idx + 1, idx - 1].forEach(k => { const it = items[(k + items.length) % items.length]; new Image().src = it.dataset.full; });
    };
    const open = i => { lastFocus = document.activeElement; show(i, true); lb.classList.add('is-open'); lb.inert = false; document.body.style.overflow = 'hidden'; $('.lb__close', lb).focus(); };
    const close = () => { lb.classList.remove('is-open'); lb.inert = true; document.body.style.overflow = ''; lastFocus && lastFocus.focus(); };
    lb.inert = true;
    items.forEach((it, i) => {
      it.addEventListener('click', () => open(i));
      it.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); open(i); } });
    });
    $('.lb__close', lb).addEventListener('click', close);
    $('.lb__prev', lb).addEventListener('click', () => show(idx - 1));
    $('.lb__next', lb).addEventListener('click', () => show(idx + 1));
    lb.addEventListener('click', e => { if (e.target === lb) close(); });
    document.addEventListener('keydown', e => {
      if (!lb.classList.contains('is-open')) return;
      if (e.key === 'Escape') close();
      if (e.key === 'ArrowRight') show(idx + 1);
      if (e.key === 'ArrowLeft') show(idx - 1);
    });
    let sx = 0, sy = 0;
    lb.addEventListener('pointerdown', e => { sx = e.clientX; sy = e.clientY; });
    lb.addEventListener('pointerup', e => {
      const dx = e.clientX - sx, dy = e.clientY - sy;
      if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy)) show(idx + (dx < 0 ? 1 : -1));
      else if (dy > 90 && Math.abs(dy) > Math.abs(dx)) close();
    });
  }

  /* ---------- Kontaktformular (Prototyp: nur Validierung) ---------- */
  const form = $('.form');
  if (form) {
    const fields = $$('.field', form);
    const validate = f => {
      const input = $('input, textarea', f);
      const ok = input.checkValidity();
      f.classList.toggle('is-invalid', !ok);
      return ok;
    };
    fields.forEach(f => {
      const input = $('input, textarea', f);
      input.addEventListener('blur', () => { if (input.value) validate(f); });
      input.addEventListener('input', () => { if (f.classList.contains('is-invalid')) validate(f); });
    });
    form.addEventListener('submit', e => {
      e.preventDefault();
      const bad = fields.filter(f => !validate(f));
      const consent = $('input[name="datenschutz"]', form);
      if (bad.length) { $('input, textarea', bad[0]).focus(); return; }
      if (!consent.checked) { consent.focus(); consent.closest('.check').animate([{ transform: 'translateX(0)' }, { transform: 'translateX(-6px)' }, { transform: 'translateX(6px)' }, { transform: 'translateX(0)' }], { duration: 360 }); return; }
      form.classList.add('is-sent');
      form.scrollIntoView({ block: 'center', behavior: reduce ? 'auto' : 'smooth' });
    });
  }

  /* ---------- View Transition: nur das angeklickte Bild morpht ---------- */
  $$('a[data-vt]').forEach(a => a.addEventListener('click', () => {
    const m = $('img', a);
    if (m) m.style.viewTransitionName = 'project-media';
  }));
  window.addEventListener('pageshow', () => $$('a[data-vt] img').forEach(m => { m.style.viewTransitionName = ''; }));
})();
