#!/usr/bin/env python3
"""
Renderiza o relatório de funil em HTML (auto-contido) a partir de um dados.json.

A parte de JUÍZO (números reais, análise dos cards, narrativa do pipeline e do
plano) é montada pelo agente dentro do dados.json. Este script faz a parte
MECÂNICA: layout, tema (cores/logo da marca), desenho dos funis em SVG e as
animações (CSS/JS puro, sem dependências).

Funis: o "funil de vendas" é desenhado VERTICAL (hero, ouro→teal com handoff); os
funis de marketing e comercial são HORIZONTAIS e encorpados. O afunilamento é
visual (gradual por posição) — a magnitude real fica nos números, garantindo um
gráfico sempre bonito mesmo com valores muito díspares (ex.: 62.039 → 1).

Uso:
    python build_report.py dados.json -o relatorio.html
    python build_report.py dados.json -o relatorio.html --no-anim

Esquema do dados.json: ver ../references/estrutura-dados.md
"""
import argparse
import html
import json
import re


def num(v):
    if isinstance(v, (int, float)):
        return float(v)
    if not v:
        return 0.0
    m = re.search(r"\d[\d.]*", str(v))
    if not m:
        return 0.0
    digits = re.sub(r"[^\d]", "", m.group(0))
    return float(digits) if digits else 0.0


def esc(s):
    return html.escape(str(s if s is not None else ""))


def is_date(raw):
    return bool(re.search(r"[/–]", raw)) or bool(re.search(r"\d-\d", raw))


def count_span(raw, animate, cls=""):
    raw = str(raw if raw is not None else "")
    c = (cls + " js-count").strip()
    if animate and re.search(r"\d", raw) and not is_date(raw):
        return f'<span class="{c}" data-raw="{esc(raw)}">{esc(raw)}</span>'
    return (f'<span class="{esc(cls)}">{esc(raw)}</span>' if cls else esc(raw))


def _poly(points, fill, grad_id, animate, idx):
    cls = ' class="fpoly"' if animate else ""
    delay = f' style="animation-delay:{idx*0.1:.2f}s"' if animate else ""
    return (f'<polygon points="{points}" fill="{fill}" '
            f'filter="url(#sh_{grad_id})"{cls}{delay}/>')


def _grad(gid, colors):
    return (f'<linearGradient id="{gid}" x1="0" y1="0" x2="1" y2="0">'
            f'<stop offset="0" stop-color="{colors[0]}"/>'
            f'<stop offset="1" stop-color="{colors[1]}"/></linearGradient>')


def _defs(grad_id, mkt_colors, com_colors):
    gm, gc = f"{grad_id}_m", f"{grad_id}_c"
    return (f'<defs>{_grad(gm, mkt_colors)}{_grad(gc, com_colors)}'
            f'<filter id="sh_{grad_id}" x="-8%" y="-14%" width="116%" height="140%">'
            f'<feDropShadow dx="0" dy="3" stdDeviation="6" flood-color="#000" '
            f'flood-opacity="0.30"/></filter></defs>'), gm, gc


def hfunnel_svg(etapas, grad_id, mkt_colors, com_colors, animate, w=800, h=216):
    """Funil horizontal encorpado: trapézios altos com taper visual por posição."""
    n = len(etapas)
    if n == 0:
        return ""
    defs, gm, gc = _defs(grad_id, mkt_colors, com_colors)
    maxH, cy = 150, 112
    left, right, gap = 20, w - 20, 5
    seg = (right - left) / n

    def frac(i):
        return 1.0 - 0.32 * (i / (n - 1)) if n > 1 else 1.0

    polys, texts = [], []
    for i, e in enumerate(etapas):
        x0, x1 = left + i * seg, left + (i + 1) * seg - gap
        t0, t1 = maxH * frac(i), maxH * frac(min(i + 1, n - 1))
        pts = (f"{x0:.0f},{cy-t0/2:.0f} {x1:.0f},{cy-t1/2:.0f} "
               f"{x1:.0f},{cy+t1/2:.0f} {x0:.0f},{cy+t0/2:.0f}")
        fill = f"url(#{gc})" if e.get("fase") == "com" else f"url(#{gm})"
        polys.append(_poly(pts, fill, grad_id, animate, i))
        cx = left + i * seg + seg / 2
        texts.append(f'<text x="{cx:.0f}" y="18" fill="#7e8eae" font-size="11" '
                     f'letter-spacing="1" text-anchor="middle">{esc(e.get("nome","")).upper()}</text>')
        texts.append(f'<text x="{cx:.0f}" y="{cy+8:.0f}" fill="#0c1a14" font-size="26" '
                     f'font-weight="800" text-anchor="middle">{esc(e.get("valor",""))}</text>')
        nota, tipo = e.get("nota", ""), e.get("tipo", "")
        if nota:
            col = {"win": "#4dd49c", "leak": "#f47168"}.get(tipo, "#90a0bf")
            extra = " &#9664; vaza" if tipo == "leak" else ""
            fw = ' font-weight="700"' if tipo else ""
            texts.append(f'<text x="{cx:.0f}" y="206" fill="{col}" font-size="11.5"'
                         f'{fw} text-anchor="middle">{esc(nota)}{extra}</text>')
    return (f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg">{defs}'
            f'{"".join(polys)}<g font-family="Segoe UI,Arial">{"".join(texts)}</g></svg>')


def vfunnel_svg(etapas, grad_id, mkt_colors, com_colors, animate, w=820):
    """Funil de vendas VERTICAL (hero): bandas afuniladas, ouro→teal, com handoff."""
    n = len(etapas)
    if n == 0:
        return ""
    defs, gm, gc = _defs(grad_id, mkt_colors, com_colors)
    cx = 388
    wmax, wmin = 470, 84
    bandH, gap, handoff_gap = 40, 7, 34
    top = 22
    # detecta índice do 1º estágio comercial p/ inserir o handoff
    first_com = next((i for i, e in enumerate(etapas) if e.get("fase") == "com"), None)

    def width_at(i):
        return wmin + (wmax - wmin) * (1 - i / (n - 1)) if n > 1 else wmax

    # y de topo de cada banda
    ys, y = [], top
    for i in range(n):
        if first_com is not None and i == first_com:
            y += handoff_gap
        ys.append(y)
        y += bandH + gap
    total_h = y + 6
    handoff_y = ys[first_com] - handoff_gap / 2 - gap / 2 if first_com else None

    polys, texts = [], []
    for i, e in enumerate(etapas):
        w0, w1 = width_at(i), width_at(min(i + 1, n - 1))
        y0, y1 = ys[i], ys[i] + bandH
        pts = (f"{cx-w0/2:.0f},{y0:.0f} {cx+w0/2:.0f},{y0:.0f} "
               f"{cx+w1/2:.0f},{y1:.0f} {cx-w1/2:.0f},{y1:.0f}")
        fill = f"url(#{gc})" if e.get("fase") == "com" else f"url(#{gm})"
        polys.append(_poly(pts, fill, grad_id, animate, i))
        yc = y0 + bandH / 2
        # rótulo à esquerda
        texts.append(f'<text x="{cx-wmax/2-18:.0f}" y="{yc+4:.0f}" fill="#aebbd6" '
                     f'font-size="13" font-weight="600" text-anchor="end">'
                     f'{esc(e.get("nome",""))}</text>')
        # valor + nota à direita
        texts.append(f'<text x="{cx+wmax/2+22:.0f}" y="{yc:.0f}" fill="#fff" '
                     f'font-size="21" font-weight="700" text-anchor="start">'
                     f'{esc(e.get("valor",""))}</text>')
        nota, tipo = e.get("nota", ""), e.get("tipo", "")
        if nota:
            col = {"win": "#4dd49c", "leak": "#f47168"}.get(tipo, "#90a0bf")
            extra = " &#9664; vaza" if tipo == "leak" else ""
            texts.append(f'<text x="{cx+wmax/2+22:.0f}" y="{yc+17:.0f}" fill="{col}" '
                         f'font-size="11.5" text-anchor="start">{esc(nota)}{extra}</text>')
    hand = ""
    if handoff_y:
        hand = (f'<line x1="60" y1="{handoff_y:.0f}" x2="760" y2="{handoff_y:.0f}" '
                f'stroke="rgba(255,255,255,.14)" stroke-dasharray="2 5"/>'
                f'<text x="{cx:.0f}" y="{handoff_y-6:.0f}" text-anchor="middle" '
                f'fill="#7184a6" font-size="10" letter-spacing="2">'
                f'HANDOFF &#183; MARKETING &#8594; COMERCIAL</text>')
    return (f'<svg viewBox="0 0 {w} {total_h:.0f}" xmlns="http://www.w3.org/2000/svg">'
            f'{defs}{"".join(polys)}{hand}'
            f'<g font-family="Segoe UI,Arial">{"".join(texts)}</g></svg>')


def render_cards(cards):
    if not cards:
        return ""
    out = []
    for c in cards:
        lab = {"risk": "risk", "force": "force", "note": "note"}.get(c.get("tipo", "note"), "note")
        out.append(f'<div class="card"><div class="lab {lab}">{esc(c.get("label",""))}</div>'
                   f'<h4>{esc(c.get("titulo",""))}</h4><p>{c.get("texto","")}</p></div>')
    return '<div class="grid2">' + "".join(out) + "</div>"


def render_pipeline(pipe):
    if not pipe:
        return ""
    dots = {"hot": "var(--green)", "warm": "var(--amber)", "cold": "var(--red)"}
    rows = "".join(
        f'<div class="pi"><div class="pd" style="background:{dots.get(d.get("status","warm"),"var(--amber)")}"></div>'
        f'<div><span class="pnm">{esc(d.get("nome",""))}</span>'
        f'<span class="pst st-{d.get("status","warm")}">{esc(d.get("status_label",""))}</span>'
        f'<div class="pdesc">{esc(d.get("desc",""))}</div></div></div>' for d in pipe)
    return (f'<div class="card span" style="margin-top:14px;"><div class="lab" '
            f'style="color:var(--teal2)">Pipeline ativo &#183; {len(pipe)} negócios</div>'
            f'<div class="pipe">{rows}</div></div>')


def render_funil(f, m, animate):
    fid = f.get("id", "x")
    eyebrow_cls = {"vendas": "e-geral", "marketing": "e-mkt", "comercial": "e-com"}.get(fid, "e-geral")
    mkt = (m["_mkt_a"], m["_mkt_b"])
    com = (m["_com_a"], m["_com_b"])
    mkt_colors = com if fid == "comercial" else mkt
    etapas = f.get("etapas", [])
    if fid == "vendas":
        svg = vfunnel_svg(etapas, "g_" + fid, mkt, com, animate)
    else:
        svg = hfunnel_svg(etapas, "g_" + fid, mkt_colors, com, animate)
    frase = f.get("frase")
    frase_html = ""
    if frase:
        frase_html = (f'<div class="card span" style="margin-top:26px;"><div class="lab note">'
                      f'{esc(frase.get("rotulo","A leitura de uma frase"))}</div>'
                      f'<h4>{esc(frase.get("titulo",""))}</h4><p>{frase.get("texto","")}</p></div>')
    return (f'<section><div class="eyebrow {eyebrow_cls}"><span class="pill">'
            f'{esc(f.get("pill",""))}</span> {esc(f.get("eyebrow",""))}</div>'
            f'<h2>{esc(f.get("titulo",""))}</h2><p class="sub">{f.get("sub","")}</p>'
            f'<div class="hfun">{svg}</div>{frase_html}'
            f'{render_cards(f.get("cards", []))}{render_pipeline(f.get("pipeline", []))}</section>')


def render_resultado(res, animate):
    """Seção de KPIs em R$ (receita, ROAS, CAC, ticket) com delta vs período anterior e meta."""
    if not res or not res.get("kpis"):
        return ""
    cards = []
    for k in res["kpis"]:
        delta, bom = k.get("delta"), k.get("bom")
        d_html = ""
        if delta:
            dcls = "up" if bom else ("down" if bom is False else "")
            arrow = "&#9650; " if bom else ("&#9660; " if bom is False else "")
            d_html = f'<div class="kd {dcls}">{arrow}{esc(delta)}</div>'
        meta = f'<div class="km">{esc(k.get("meta"))}</div>' if k.get("meta") else ""
        cards.append(f'<div class="kpi"><div class="kl">{esc(k.get("label",""))}</div>'
                     f'<div class="kv">{count_span(k.get("valor",""), animate)}</div>'
                     f'{d_html}{meta}</div>')
    return (f'<section><div class="eyebrow e-geral"><span class="pill">Resultado</span> '
            f'em R$</div><h2>{esc(res.get("titulo","O retorno em dinheiro"))}</h2>'
            f'<p class="sub">{res.get("sub","")}</p>'
            f'<div class="kpis">{"".join(cards)}</div></section>')


def render_tabela(t):
    """Tabela genérica (atribuição lead→venda, desempenho por closer etc.)."""
    if not t or not t.get("linhas"):
        return ""
    cls = {"vendas": "e-geral", "marketing": "e-mkt", "comercial": "e-com"}.get(t.get("cor"), "e-geral")
    head = "".join(f"<th>{esc(c)}</th>" for c in t.get("colunas", []))
    body = "".join("<tr>" + "".join(f"<td>{esc(c)}</td>" for c in linha) + "</tr>"
                   for linha in t["linhas"])
    pill = f'<span class="pill">{esc(t.get("pill","Tabela"))}</span> ' if t.get("pill") else ""
    sub = f'<p class="sub">{t.get("sub","")}</p>' if t.get("sub") else ""
    return (f'<section><div class="eyebrow {cls}">{pill}{esc(t.get("eyebrow",""))}</div>'
            f'<h2>{esc(t.get("titulo",""))}</h2>{sub}'
            f'<table class="tbl"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></section>')


def render(dados, animate=True):
    m = dados.get("marca", {})
    primaria = m.get("cor_primaria", "#F4B321")
    secundaria = m.get("cor_secundaria", "#3ec8cf")
    fundo = m.get("cor_fundo", "#02112F")
    m["_mkt_a"] = m.get("cor_marketing_a", primaria)
    m["_mkt_b"] = m.get("cor_marketing_b", "#ffd87a")
    m["_com_a"] = m.get("cor_comercial_a", secundaria)
    m["_com_b"] = m.get("cor_comercial_b", "#7fe3e8")

    cab = dados.get("cabecalho", {})
    logo = m.get("logo")
    brand_html = (f'<img src="{esc(logo)}" alt="{esc(m.get("nome",""))}" '
                  f'style="height:36px;margin-bottom:16px;display:block"/>' if logo else "")
    titulo = esc(cab.get("titulo", ""))
    if cab.get("titulo_em"):
        titulo = titulo.replace(esc(cab["titulo_em"]), f'<em>{esc(cab["titulo_em"])}</em>')

    stamps = ""
    for s in cab.get("stamps", []):
        small = f' <small>{esc(s.get("small"))}</small>' if s.get("small") else ""
        delta = ""
        if s.get("delta"):
            dcls = "up" if s.get("bom") else ("down" if s.get("bom") is False else "")
            arrow = "&#9650;" if s.get("bom") else ("&#9660;" if s.get("bom") is False else "")
            delta = f'<div class="sdelta {dcls}">{arrow} {esc(s.get("delta"))}</div>'
        stamps += (f'<div><div class="k">{esc(s.get("k",""))}</div><div class="v">'
                   f'{count_span(s.get("v",""), animate)}{small}</div>{delta}</div>')

    funis = "".join(render_funil(f, m, animate) for f in dados.get("funis", []))
    resultado = render_resultado(dados.get("resultado"), animate)
    tabelas = "".join(render_tabela(t) for t in dados.get("tabelas", []))

    conc = dados.get("conclusao", {})
    conc_html = ""
    if conc:
        paras = "".join(f"<p>{p}</p>" for p in conc.get("paragrafos", []))
        tags = "".join(f'<p><span class="tag {"c" if t.get("cor")=="c" else ""}">'
                       f'{esc(t.get("label",""))}:</span> {t.get("texto","")}</p>'
                       for t in conc.get("tags", []))
        conc_html = (f'<div class="close"><div class="ct">'
                     f'{esc(conc.get("titulo","A conclusão"))}</div>{paras}{tags}</div>')

    plano = dados.get("plano", {})
    plano_html = ""
    if plano.get("itens"):
        rows = "".join(
            f'<div class="pl"><div class="sd {"c" if it.get("setor")=="c" else "m"}">'
            f'{"Comercial" if it.get("setor")=="c" else "Marketing"}</div>'
            f'<div class="ax"><b>{esc(it.get("acao",""))}</b>'
            f'<small>{esc(it.get("detalhe",""))}</small></div>'
            f'<div class="pz">{esc(it.get("prazo",""))}</div></div>' for it in plano["itens"])
        plano_html = (f'<section style="border-bottom:none;"><div class="eyebrow e-geral">'
                      f'<span class="pill">Plano</span> próximos passos</div><h2>'
                      f'{esc(plano.get("titulo","O que destrava cada funil"))}</h2>'
                      f'<div class="plan">{rows}</div></section>')

    return TEMPLATE.format(
        lang="pt-BR",
        title=esc(cab.get("titulo_aba", cab.get("titulo", "Relatório de Funil"))),
        bg=fundo, gold=primaria, teal=secundaria,
        anim_css=(ANIM_CSS if animate else ""), anim_js=(ANIM_JS if animate else ""),
        brand_html=brand_html, brand_line=esc(cab.get("brand_line", "")),
        titulo=titulo, lede=cab.get("lede", ""), stamps=stamps, funis=funis,
        resultado=resultado, tabelas=tabelas, conclusao=conc_html, plano=plano_html,
        rodape=dados.get("rodape", ""))


ANIM_CSS = '''
  @media (prefers-reduced-motion: no-preference){
    .fpoly{opacity:0;transform-box:fill-box;transform-origin:center;animation:fgrow .7s cubic-bezier(.2,.8,.2,1) forwards;}
    @keyframes fgrow{from{opacity:0;transform:scale(.86)}to{opacity:1;transform:scale(1)}}
    .reveal{opacity:0;transform:translateY(20px);transition:opacity .6s ease,transform .6s ease;}
    .reveal.in{opacity:1;transform:none;}
  }'''

ANIM_JS = '''
<script>
(function(){
  var rm = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  function count(el){
    var raw = el.getAttribute('data-raw')||el.textContent;
    var m = raw.match(/[\\d.]+/); if(!m){return;}
    var target = parseInt(m[0].replace(/[^\\d]/g,''),10); if(!target){return;}
    var pre = raw.slice(0,m.index), suf = raw.slice(m.index+m[0].length), steps=38, i=0;
    var t=setInterval(function(){
      i++; var cur=Math.min(target, Math.round(target*i/steps));
      el.textContent = pre + cur.toLocaleString('pt-BR') + suf;
      if(i>=steps){el.textContent = pre + target.toLocaleString('pt-BR') + suf; clearInterval(t);}
    }, 22);
  }
  var io = ('IntersectionObserver' in window) ? new IntersectionObserver(function(es){
    es.forEach(function(e){ if(e.isIntersecting){
      e.target.classList.add('in');
      e.target.querySelectorAll('.js-count').forEach(count);
      io.unobserve(e.target);
    }});
  },{threshold:.12}) : null;
  document.addEventListener('DOMContentLoaded', function(){
    if(rm || !io){ document.querySelectorAll('.js-count').forEach(count);
      document.querySelectorAll('.reveal').forEach(function(x){x.classList.add('in');}); return; }
    document.querySelectorAll('section,.close,header').forEach(function(s){
      s.classList.add('reveal'); io.observe(s);
    });
    document.querySelectorAll('header .js-count').forEach(count);
  });
})();
</script>'''


TEMPLATE = '''<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
  :root{{
    --bg:{bg}; --bg2:#051831; --ink:#e9eefa; --mut:#90a0bf; --mut2:#5c6d8d;
    --gold:{gold}; --gold2:#ffd87a; --teal:{teal}; --teal2:#7fe3e8;
    --green:#4dd49c; --red:#f47168; --amber:#efad45;
    --line:rgba(255,255,255,.07); --line2:rgba(255,255,255,.12);
  }}
  *{{box-sizing:border-box;margin:0;padding:0;}}
  body{{font-family:'Segoe UI',-apple-system,Roboto,Helvetica,Arial,sans-serif;background:#000;color:var(--ink);font-size:14px;line-height:1.62;-webkit-print-color-adjust:exact;print-color-adjust:exact;}}
  .page{{max-width:860px;margin:0 auto;background:radial-gradient(120% 60% at 80% 0%,#0a2349 0%,var(--bg) 45%,var(--bg2) 100%);}}
  header{{padding:60px 60px 44px;border-bottom:1px solid var(--line);}}
  .brand{{font-size:11px;letter-spacing:5px;text-transform:uppercase;color:var(--gold);font-weight:700;display:flex;align-items:center;gap:11px;}}
  .brand::before{{content:'';width:26px;height:1px;background:var(--gold);}}
  h1{{font-size:38px;font-weight:800;letter-spacing:-1.2px;line-height:1.06;margin:20px 0 16px;}}
  h1 em{{font-style:normal;color:var(--gold2);}}
  .lede{{font-size:15px;color:#c2cee6;max-width:600px;line-height:1.7;}}
  .lede b{{color:#fff;}}
  .stamps{{display:flex;gap:0;margin-top:34px;border-top:1px solid var(--line);flex-wrap:wrap;}}
  .stamps>div{{flex:1;padding-top:18px;border-right:1px solid var(--line);min-width:120px;}}
  .stamps>div:last-child{{border:none;}}
  .stamps .k{{font-size:10px;letter-spacing:1.2px;text-transform:uppercase;color:var(--mut2);}}
  .stamps .v{{font-size:24px;font-weight:300;letter-spacing:-1px;margin-top:6px;}}
  .stamps .v small{{font-size:12px;color:var(--gold);letter-spacing:0;}}
  .stamps .sdelta{{font-size:11px;font-weight:700;margin-top:4px;color:var(--mut);}}
  .sdelta.up{{color:var(--green);}} .sdelta.down{{color:var(--red);}}
  section{{padding:52px 60px;border-bottom:1px solid var(--line);}}
  .eyebrow{{font-size:11px;letter-spacing:3px;text-transform:uppercase;font-weight:700;margin-bottom:10px;display:flex;align-items:center;gap:9px;}}
  .eyebrow .pill{{font-size:9px;letter-spacing:1px;padding:2px 9px;border-radius:20px;font-weight:800;}}
  .e-geral{{color:var(--ink);}} .e-geral .pill{{background:rgba(255,255,255,.1);color:#fff;}}
  .e-mkt{{color:var(--gold2);}} .e-mkt .pill{{background:rgba(244,179,33,.16);color:var(--gold2);}}
  .e-com{{color:var(--teal2);}} .e-com .pill{{background:rgba(62,200,207,.16);color:var(--teal2);}}
  h2{{font-size:26px;font-weight:700;letter-spacing:-.5px;margin-bottom:8px;}}
  .sub{{font-size:13.5px;color:var(--mut);max-width:600px;line-height:1.65;margin-bottom:34px;}}
  .hfun{{margin:6px 0 30px;}} .hfun svg{{width:100%;height:auto;display:block;}}
  .grid2{{display:grid;grid-template-columns:1fr 1fr;gap:14px;}}
  .card{{border:1px solid var(--line);border-radius:13px;padding:20px 22px;background:rgba(255,255,255,.016);}}
  .card.span{{grid-column:1 / -1;}}
  .card .lab{{font-size:10px;letter-spacing:1.2px;text-transform:uppercase;font-weight:800;margin-bottom:8px;}}
  .lab.risk{{color:var(--red);}} .lab.force{{color:var(--green);}} .lab.note{{color:var(--amber);}}
  .card h4{{font-size:15.5px;font-weight:700;color:#fff;margin-bottom:7px;letter-spacing:-.2px;}}
  .card p{{font-size:12.8px;color:#bcc8e0;line-height:1.62;}}
  .card p b{{color:var(--gold2);font-weight:700;}} .card p .n{{color:#fff;font-weight:700;}}
  .kpis{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;}}
  .kpi{{border:1px solid var(--line);border-radius:13px;padding:18px;background:rgba(255,255,255,.016);}}
  .kpi .kl{{font-size:10px;letter-spacing:1px;text-transform:uppercase;color:var(--mut2);font-weight:800;}}
  .kpi .kv{{font-size:29px;font-weight:300;letter-spacing:-1.5px;margin:7px 0 4px;color:#fff;}}
  .kpi .kd{{font-size:11.5px;font-weight:700;color:var(--mut);}}
  .kpi .kd.up{{color:var(--green);}} .kpi .kd.down{{color:var(--red);}}
  .kpi .km{{font-size:10.5px;color:var(--mut);margin-top:3px;}}
  .tbl{{width:100%;border-collapse:collapse;font-size:12.5px;}}
  .tbl th{{text-align:left;font-size:9.5px;letter-spacing:1px;text-transform:uppercase;color:var(--mut2);font-weight:800;padding:10px 12px;border-bottom:1px solid var(--line2);}}
  .tbl td{{padding:11px 12px;border-bottom:1px solid var(--line);color:#cdd8ee;}}
  .tbl td:first-child{{color:#fff;font-weight:600;}}
  .tbl tr:last-child td{{border-bottom:none;}}
  .pipe{{margin-top:6px;}}
  .pi{{display:flex;gap:13px;padding:13px 0;border-top:1px solid var(--line);}}
  .pi .pd{{width:8px;height:8px;border-radius:50%;margin-top:7px;flex-shrink:0;}}
  .pi .pnm{{font-weight:700;color:#fff;font-size:14px;}}
  .pi .pst{{font-size:9.5px;font-weight:800;text-transform:uppercase;letter-spacing:.4px;padding:2px 8px;border-radius:20px;margin-left:9px;}}
  .st-hot{{background:rgba(77,212,156,.14);color:var(--green);}}
  .st-warm{{background:rgba(239,173,69,.14);color:var(--amber);}}
  .st-cold{{background:rgba(244,115,107,.14);color:var(--red);}}
  .pi .pdesc{{font-size:12px;color:var(--mut);margin-top:3px;line-height:1.5;}}
  .close{{padding:48px 60px;background:linear-gradient(160deg,rgba(244,179,33,.06),transparent 70%);border-bottom:1px solid var(--line);}}
  .close .ct{{font-size:11px;letter-spacing:3px;text-transform:uppercase;color:var(--gold);font-weight:700;margin-bottom:16px;}}
  .close p{{font-size:15px;color:#cfdaef;line-height:1.72;}} .close p+p{{margin-top:13px;}}
  .close .tag{{display:inline-block;min-width:104px;color:var(--gold2);font-weight:700;}}
  .close .tag.c{{color:var(--teal2);}}
  .plan{{border:1px solid var(--line);border-radius:13px;overflow:hidden;margin-top:20px;}}
  .pl{{display:grid;grid-template-columns:124px 1fr 96px;border-top:1px solid var(--line);align-items:center;}}
  .pl:first-child{{border-top:none;}} .pl>div{{padding:16px 20px;}}
  .pl .sd{{font-size:9.5px;font-weight:800;letter-spacing:.7px;text-transform:uppercase;border-left:2px solid;padding-left:12px;}}
  .sd.m{{color:var(--gold2);border-color:var(--gold);}} .sd.c{{color:var(--teal2);border-color:var(--teal);}}
  .pl .ax b{{display:block;color:#fff;font-size:14px;line-height:1.35;}} .pl .ax small{{display:block;color:var(--mut);font-size:11.5px;margin-top:4px;line-height:1.4;}}
  .pl .pz{{font-size:11px;color:var(--mut);text-align:right;font-weight:600;}}
  footer{{padding:24px 60px 44px;font-size:10.5px;color:var(--mut2);line-height:1.7;}}
  @media print{{body{{background:var(--bg);font-size:11.5px;}}.page{{max-width:none;}}section{{break-inside:avoid;}}.reveal{{opacity:1!important;transform:none!important;}}}}
  @media(max-width:680px){{.grid2,.kpis{{grid-template-columns:1fr 1fr;}}}}{anim_css}
</style>
</head>
<body>
<div class="page">
  <header>
    {brand_html}
    <div class="brand">{brand_line}</div>
    <h1>{titulo}</h1>
    <p class="lede">{lede}</p>
    <div class="stamps">{stamps}</div>
  </header>
  {funis}
  {resultado}
  {tabelas}
  {conclusao}
  {plano}
  <footer>{rodape}</footer>
</div>
{anim_js}
</body>
</html>'''


def main():
    ap = argparse.ArgumentParser(description="Gera o relatório de funil em HTML")
    ap.add_argument("dados", help="caminho do dados.json")
    ap.add_argument("-o", "--out", default="relatorio.html")
    ap.add_argument("--no-anim", action="store_true", help="desliga animações")
    args = ap.parse_args()
    with open(args.dados, encoding="utf-8") as f:
        dados = json.load(f)
    out = render(dados, animate=not args.no_anim)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(out)
    print(f"OK -> {args.out} ({len(out)} bytes)")


if __name__ == "__main__":
    main()
