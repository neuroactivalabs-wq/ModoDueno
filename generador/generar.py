# -*- coding: utf-8 -*-
"""Genera calendario.md, calendario.csv, guiones-reels.md y las imágenes de la campaña.
Uso:  python3 generar.py <carpeta_salida> [--sin-imagenes]
Para cambiar el nombre del producto: edita NOMBRE en datos.py y vuelve a ejecutar."""
import sys, os, csv, json, subprocess, datetime, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from datos import NOMBRE, HASH, FASES, DIAS, REELS

OUT = sys.argv[1]
IMGS = '--sin-imagenes' not in sys.argv
N = lambda s: s.replace('{NOMBRE}', NOMBRE)
MESES = {12: 'dic', 1: 'ene'}
MESES_L = {12: 'diciembre', 1: 'enero'}

def carpeta(i, f):
    return 'dia-%02d' % (i + 1)

def fecha_larga(f, dia):
    d = datetime.date.fromisoformat(f)
    return '%s %d de %s%s' % (dia, d.day, MESES_L[d.month], ' de 2027' if d.year == 2027 else '')

def imgs_de(post, folder):
    if post[0] == 'unica':
        return ['post.png']
    n = len(post[1])
    return ['post-%dde%d.png' % (k + 1, n) for k in range(n)]

# ---------------- calendario.md ----------------
md = ['# Calendario diario · %s' % NOMBRE, '',
      '%d días numerados · 1 reel + 1 post al día + historias. Empieza el día 1 cuando quieras, pero cuadra el calendario para que el **día 35 caiga en lunes** (es el día 1 del reto).' % len(DIAS), '',
      '**Horarios sugeridos (hora de Panamá):** post a las 12:30 p. m. y reel a las 7:00 p. m. (6 p. m. CDMX, 7 p. m. Bogotá y Lima, 9 p. m. Buenos Aires y Santiago).', '',
      '**Imágenes:** cada día tiene su carpeta en `imagenes/` (por ejemplo `imagenes/dia-01/`): `post.png` o `post-1de6.png…` para carruseles (1080×1350) y `reel-portada.png` (1080×1920).', '',
      '**Palabras clave:** HORAS (test gratis), RETO (reto de 7 días), HECHO (tareas del reto).', '',
      '**Hashtags del mes:** `%s`' % HASH, '', '---', '']
fase_act = None
rows = []
for i, (f, dia, fase, obj, ctx, reel, pie, post, texto, hist) in enumerate(DIAS):
    if fase != fase_act:
        md += ['## ' + FASES[fase], '']; fase_act = fase
    fol = carpeta(i, f)
    r = REELS[reel]
    md += ['### Día %d' % (i + 1), '',
           '**Objetivo:** ' + N(obj), '', '**Contexto:** ' + N(ctx), '',
           '**🎬 Reel:** %s · %s → guion en `guiones-reels.md` · portada `imagenes/%s/reel-portada.png`' % (reel, N(r[0]), fol), '',
           'Pie del reel:', '', '```', N(pie), '', HASH, '```', '',
           '**🖼️ Post:** %s · `imagenes/%s/` (%s)' % ('Imagen única' if post[0] == 'unica' else 'Carrusel de %d' % len(post[1]), fol, ', '.join(imgs_de(post, fol)) if post[0] == 'unica' else 'post-1de%d.png…' % len(post[1])), '',
           'Texto del post:', '', '```', N(texto), '', HASH, '```', '',
           '**📱 Historias:** ' + N(hist), '']
    rows.append({'dia': i + 1, 'fase': FASES[fase], 'objetivo': N(obj), 'reel': reel, 'titulo_reel': N(r[0]), 'pie_reel': N(pie),
                 'tipo_post': 'Imagen única' if post[0] == 'unica' else 'Carrusel', 'imagenes': 'imagenes/%s/' % fol, 'texto_post': N(texto),
                 'hashtags': HASH, 'historias': N(hist), 'contexto': N(ctx)})
open(os.path.join(OUT, 'calendario.md'), 'w').write('\n'.join(md))
with open(os.path.join(OUT, 'calendario.csv'), 'w', newline='', encoding='utf-8-sig') as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()), quoting=csv.QUOTE_ALL); w.writeheader(); w.writerows(rows)

# ---------------- guiones-reels.md ----------------
usos = {}
for i, d in enumerate(DIAS):
    usos.setdefault(d[5], []).append('día %d' % (i + 1))
g = ['# Guiones de reels · %s' % NOMBRE, '', '%d guiones (el R35 es una serie para los días 1 a 6 del reto).' % len(REELS), '',
     '**Reglas para todos los reels**', '',
     '- Los 3 primeros segundos deciden todo: empieza ya hablando, sin saludo ni logo.',
     '- Graba en vertical 9:16, con luz de ventana de frente y el móvil a la altura de los ojos.',
     '- Subtítulos siempre: mucha gente ve sin sonido.',
     '- Pon la portada del día (`reel-portada.png`) como portada del reel.',
     '- Palabras clave: **HORAS** (test), **RETO** (reto de 7 días), **HECHO** (tareas del reto). Si usas ManyChat, configura la respuesta automática con el enlace.',
     '- Sube el mismo video a TikTok, YouTube Shorts y Facebook Reels.',
     '- Usa solo datos y testimonios reales. Donde el guion dice [datos reales], cámbialo antes de grabar.', '', '---', '']
for code, (t, dur, fmt, gancho, esc, consejo) in REELS.items():
    g += ['## %s · %s' % (code, N(t)), '', '**Duración:** %s · **Formato:** %s · **Se publica:** %s' % (dur, fmt, '; '.join(usos.get(code, ['—']))), '',
          '**Gancho (0–3 s):** ' + N(gancho), '', '| Tiempo | Plano / acción | Voz | Texto en pantalla |', '|---|---|---|---|']
    g += ['| %s | %s | %s | %s |' % (a, N(b), N(c), N(d)) for a, b, c, d in esc]
    g += [''] + (['**Consejo:** ' + N(consejo), ''] if consejo else []) + ['---', '']
open(os.path.join(OUT, 'guiones-reels.md'), 'w').write('\n'.join(g))

# ---------------- imágenes ----------------
if not IMGS:
    sys.exit(0)
CSS = '''*{box-sizing:border-box;margin:0}body{font-family:Inter,system-ui,sans-serif}
.c{position:relative;overflow:hidden;display:flex;flex-direction:column;padding:96px 90px 84px;color:#fff}
.d{background:linear-gradient(160deg,#05060a 0%,#070826 55%,#0a0a5c 100%)}
.l{background:#f7f5f0;color:#171923}
.k{font-size:30px;font-weight:800;letter-spacing:.14em;color:#00e5ff;text-transform:uppercase}
.l .k{color:#2a1ff0}
.bar{width:120px;height:12px;background:#00e5ff;border-radius:6px;margin:0 0 40px}
h1{font-weight:900;letter-spacing:-.035em;line-height:1.02}
p.s{font-weight:500;line-height:1.35;opacity:.86}
.mid{margin:auto 0}
.ft{display:flex;justify-content:space-between;align-items:center;font-size:30px;font-weight:700}
.ft img{width:64px;height:64px;border-radius:14px;margin-right:18px}
.ft .b{display:flex;align-items:center}
.n{font-size:30px;font-weight:700;opacity:.7}
.big{font-weight:900;color:#00e5ff;letter-spacing:-.04em;line-height:1}
.l .big{color:#2a1ff0}
'''
icon = 'data:image/png;base64,' + __import__('base64').b64encode(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icon-192.png'), 'rb').read()).decode()
def foot(extra=''):
    return '<div class="ft"><div class="b"><img src="%s">%s</div><div class="n">%s</div></div>' % (icon, html.escape(NOMBRE), extra)
def fit(t, big, small, limit):
    return big if len(t) <= limit else small
jobs = []
for i, (f, dia, fase, obj, ctx, reel, pie, post, texto, hist) in enumerate(DIAS):
    fol = carpeta(i, f); os.makedirs(os.path.join(OUT, 'imagenes', fol), exist_ok=True)
    tema = 'd' if i % 2 == 0 else 'l'
    if post[0] == 'unica':
        t, s = N(post[1]), N(post[2])
        h = '<div class="c %s" style="width:1080px;height:1350px"><div class="bar"></div><div class="k">%s</div><h1 style="font-size:%dpx;margin:34px 0 40px">%s</h1><p class="s" style="font-size:44px">%s</p>%s</div>' % (
            tema, html.escape(FASES[fase].split(' · ')[1].split(' (')[0]), fit(t, 110, 88, 40), html.escape(t), html.escape(s), foot())
        jobs.append((os.path.join(OUT, 'imagenes', fol, 'post.png'), 1080, 1350, h))
    else:
        sl = post[1]; n = len(sl)
        for k, (t, b) in enumerate(sl):
            t, b = N(t), N(b)
            if k == 0:
                h = '<div class="c d" style="width:1080px;height:1350px"><div class="bar"></div><h1 style="font-size:%dpx;margin:10px 0 40px">%s</h1><p class="s" style="font-size:46px">%s</p>%s</div>' % (fit(t, 108, 90, 34), html.escape(t), html.escape(b), foot('Desliza →'))
            else:
                last = k == n - 1
                num = len(t) <= 3 or t[0].isdigit() and len(t) < 22
                if num:
                    h = '<div class="c %s" style="width:1080px;height:1350px"><div class="k">%d / %d</div><div class="big" style="font-size:%dpx;margin:60px 0 50px">%s</div><p class="s" style="font-size:52px;font-weight:600">%s</p>%s</div>' % (
                        'd' if last else 'l', k + 1, n, 220 if len(t) <= 3 else 120, html.escape(t), html.escape(b), foot())
                else:
                    h = '<div class="c %s" style="width:1080px;height:1350px"><div class="k">%d / %d</div><h1 style="font-size:%dpx;margin:60px 0 44px">%s</h1><p class="s" style="font-size:48px">%s</p>%s</div>' % (
                        'd' if last else 'l', k + 1, n, fit(t, 92, 76, 30), html.escape(t), html.escape(b), foot())
            jobs.append((os.path.join(OUT, 'imagenes', fol, 'post-%dde%d.png' % (k + 1, n)), 1080, 1350, h))
    r = REELS[reel]; gancho = N(r[3])
    h = '<div class="c d" style="width:1080px;height:1920px;padding:220px 90px 300px"><div class="k">Día %d · %s</div><div class="bar" style="margin-top:30px"></div><h1 style="font-size:%dpx;margin:20px 0">%s</h1>%s</div>' % (
        i + 1, html.escape(NOMBRE), fit(gancho, 116, 96, 42), html.escape(gancho), foot())
    jobs.append((os.path.join(OUT, 'imagenes', fol, 'reel-portada.png'), 1080, 1920, h))

def centrar(h):
    a, b = h.split('<div class="ft">', 1)
    return a.replace('">', '"><div class="mid">', 1) + '</div><div class="ft">' + b
jobs = [(a, w, hh, centrar(x)) for a, w, hh, x in jobs]
js = os.path.join(OUT, '.jobs.json'); json.dump({'css': CSS, 'jobs': jobs}, open(js, 'w'))
runner = r'''
const { chromium } = require('playwright'); const fs = require('fs');
(async () => { const d = JSON.parse(fs.readFileSync(process.argv[2])); const b = await chromium.launch(); const p = await b.newPage();
  for (const [path, w, h, body] of d.jobs) { await p.setViewportSize({ width: w, height: h });
    await p.setContent('<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@500;600;700;800;900&display=swap"><style>' + d.css + '</style></head><body>' + body + '</body></html>', { waitUntil: 'networkidle' });
    await p.screenshot({ path, clip: { x: 0, y: 0, width: w, height: h } }); }
  await b.close(); console.log('imágenes:', d.jobs.length); })();
'''
rp = os.path.join(OUT, '.render.js'); open(rp, 'w').write(runner)
subprocess.run(['node', rp, js], check=True)
os.remove(js); os.remove(rp)
