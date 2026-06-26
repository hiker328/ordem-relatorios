#!/usr/bin/env python3
"""
Renderiza o relatório de funil em HTML (auto-contido) a partir de um dados.json.

A parte de JUÍZO (números reais, análise dos cards, narrativa do pipeline e do
plano) é montada pelo agente dentro do dados.json. Este script só faz a parte
MECÂNICA: layout, tema (cores/logo da marca), desenho dos funis em SVG com
geometria proporcional aos valores e as animações (CSS/JS puro, sem dependências).

Uso:
    python build_report.py dados.json -o relatorio.html
    python build_report.py dados.json -o relatorio.html --no-anim   # sem animação

Esquema do dados.json: ver ../references/estrutura-dados.md
"""
import argparse
import html
import json
import re


def num(v):
    """Extrai o primeiro número de 'R$ 62.039', '5 · 3', '1 contrato' -> float."""
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


def stamp_value(v, animate):
    """Valor do stamp; com count-up quando é numérico (não data/intervalo)."""
    raw = str(v if v is not None else "")
    # não anima datas/intervalos (28/05–24/06) — só números/moeda/percentual
    is_date = re.search(r"[/–]", raw) or "-" in re.sub(r"^\s*-", "", raw)
    if animate and re.search(r"\d", raw) and not is_date:
        return f'<span class="js-count" data-raw="{esc(raw)}">{esc(raw)}</span>'
    return esc(raw)


def funnel_svg(etapas, grad_id, mkt_colors, com_colors, animate, width=800, height=210):
    """Funil horizontal: trapézios com espessura proporcional ao valor da etapa.

    Define dois gradientes LOCAIS a este <svg> (marketing e comercial) para evitar
    referência cruzada entre SVGs. Cada etapa usa o gradiente comercial se
    fase=='com', senão o de marketing.
    """
    n = len(etapas)
    if n == 0:
        return ""
    gm, gc = f"{grad_id}_m", f"{grad_id}_c"
    vals = [num(e.get("valor")) for e in etapas]
    vmax = max(vals) or 1
    body_top, body_bot = 40, 150
    body_h = body_bot - body_top
    cy = (body_top + body_bot) / 2
    min_t = 14
    left, right = 20, width - 20
    seg_w = (right - left) / n

    def thick(v):
        return max(min_t, body_h * (v / vmax))

    polys, texts = [], []
    for i, e in enumerate(etapas):
        x0 = left + i * seg_w
        x1 = left + (i + 1) * seg_w - 4
        t0 = thick(vals[i])
        t1 = thick(vals[i + 1]) if i + 1 < n else t0 * 0.82
        pts = (f"{x0:.0f},{cy - t0/2:.0f} {x1:.0f},{cy - t1/2:.0f} "
               f"{x1:.0f},{cy + t1/2:.0f} {x0:.0f},{cy + t0/2:.0f}")
        fill = f"url(#{gc})" if e.get("fase") == "com" else f"url(#{gm})"
        cls = ' class="fpoly"' if animate else ""
        delay = f' style="animation-delay:{i*0.12:.2f}s"' if animate else ""
        polys.append(f'<polygon points="{pts}" fill="{fill}" '
                     f'filter="url(#sh_{grad_id})"{cls}{delay}/>')

        cx = left + i * seg_w + seg_w / 2
        nome = esc(e.get("nome", "")).upper()
        valor = esc(e.get("valor", ""))
        nota = e.get("nota", "")
        tipo = e.get("tipo", "")
        texts.append(f'<text x="{cx:.0f}" y="25" fill="#7e8eae" font-size="11" '
                     f'letter-spacing="1" text-anchor="middle">{nome}</text>')
        texts.append(f'<text x="{cx:.0f}" y="{cy+8:.0f}" fill="#0c1322" '
                     f'font-size="23" font-weight="800" text-anchor="middle">{valor}</text>')
        if nota:
            col = {"win": "#4dd49c", "leak": "#f47168"}.get(tipo, "#90a0bf")
            extra = " &#9664; vaza" if tipo == "leak" else ""
            fw = ' font-weight="700"' if tipo else ""
            texts.append(f'<text x="{cx:.0f}" y="190" fill="{col}" font-size="11.5"'
                         f'{fw} text-anchor="middle">{esc(nota)}{extra}</text>')

    def grad(gid, colors):
        return (f'<linearGradient id="{gid}" x1="0" y1="0" x2="1" y2="0">'
                f'<stop offset="0" stop-color="{colors[0]}"/>'
                f'<stop offset="1" stop-color="{colors[1]}"/></linearGradient>')

    return (f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">'
            f'<defs>{grad(gm, mkt_colors)}{grad(gc, com_colors)}'
            f'<filter id="sh_{grad_id}" x="-8%" y="-12%" width="116%" height="134%">'
            f'<feDropShadow dx="0" dy="3" stdDeviation="5" flood-color="#000" '
            f'flood-opacity="0.25"/></filter></defs>'
            f'{"".join(polys)}<g font-family="Segoe UI,Arial">{"".join(texts)}</g></svg>')


def render_cards(cards):
    if not cards:
        return ""
    out = []
    for c in cards:
        lab_cls = {"risk": "risk", "force": "force", "note": "note"}.get(
            c.get("tipo", "note"), "note")
        out.append(f'<div class="card"><div class="lab {lab_cls}">'
                   f'{esc(c.get("label",""))}</div><h4>{esc(c.get("titulo",""))}</h4>'
                   f'<p>{c.get("texto","")}</p></div>')
    return '<div class="grid2">' + "".join(out) + "</div>"


def render_pipeline(pipe):
    if not pipe:
        return ""
    dots = {"hot": "var(--green)", "warm": "var(--amber)", "cold": "var(--red)"}
    rows = []
    for d in pipe:
        st = d.get("status", "warm")
        rows.append(f'<div class="pi"><div class="pd" style="background:'
                    f'{dots.get(st,"var(--amber)")}"></div><div>'
                    f'<span class="pnm">{esc(d.get("nome",""))}</span>'
                    f'<span class="pst st-{st}">{esc(d.get("status_label",""))}</span>'
                    f'<div class="pdesc">{esc(d.get("desc",""))}</div></div></div>')
    return (f'<div class="card span" style="margin-top:14px;">'
            f'<div class="lab" style="color:var(--teal2)">Pipeline ativo · '
            f'{len(pipe)} negócios</div><div class="pipe">{"".join(rows)}</div></div>')


def render_funil(f, m, animate):
    fid = f.get("id", "x")
    eyebrow_cls = {"vendas": "e-geral", "marketing": "e-mkt",
                   "comercial": "e-com"}.get(fid, "e-geral")
    mkt = (m["_mkt_a"], m["_mkt_b"])
    com = (m["_com_a"], m["_com_b"])
    # funil comercial inteiro na cor comercial; demais usam mkt (e com p/ fase 'com')
    mkt_colors = com if fid == "comercial" else mkt
    svg = funnel_svg(f.get("etapas", []), "g_" + fid, mkt_colors, com, animate)
    frase = f.get("frase")
    frase_html = ""
    if frase:
        frase_html = (f'<div class="card span" style="margin-top:26px;">'
                      f'<div class="lab note">{esc(frase.get("rotulo","A leitura de uma frase"))}'
                      f'</div><h4>{esc(frase.get("titulo",""))}</h4>'
                      f'<p>{frase.get("texto","")}</p></div>')
    return (f'<section><div class="eyebrow {eyebrow_cls}">'
            f'<span class="pill">{esc(f.get("pill",""))}</span> '
            f'{esc(f.get("eyebrow",""))}</div><h2>{esc(f.get("titulo",""))}</h2>'
            f'<p class="sub">{f.get("sub","")}</p>'
            f'<div class="hfun">{svg}</div>{frase_html}'
            f'{render_cards(f.get("cards", []))}'
            f'{render_pipeline(f.get("pipeline", []))}</section>')


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
                  f'style="height:34px;margin-bottom:14px;display:block"/>' if logo else "")
    titulo = esc(cab.get("titulo", ""))
    if cab.get("titulo_em"):
        titulo = titulo.replace(esc(cab["titulo_em"]), f'<em>{esc(cab["titulo_em"])}</em>')

    stamps = ""
    for s in cab.get("stamps", []):
        small = (f' <small>{esc(s.get("small"))}</small>' if s.get("small") else "")
        stamps += (f'<div><div class="k">{esc(s.get("k",""))}</div>'
                   f'<div class="v">{stamp_value(s.get("v",""), animate)}{small}</div></div>')

    funis = "".join(render_funil(f, m, animate) for f in dados.get("funis", []))

    conc = dados.get("conclusao", {})
    conc_html = ""
    if conc:
        paras = "".join(f"<p>{p}</p>" for p in conc.get("paragrafos", []))
        tags = "".join(
            f'<p><span class="tag {"c" if t.get("cor")=="c" else ""}">'
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
            f'<div class="pz">{esc(it.get("prazo",""))}</div></div>'
            for it in plano["itens"])
        plano_html = (f'<section style="border-bottom:none;">'
                      f'<div class="eyebrow e-geral"><span class="pill">Plano</span> '
                      f'próximos passos</div><h2>'
                      f'{esc(plano.get("titulo","O que destrava cada funil"))}</h2>'
                      f'<div class="plan">{rows}</div></section>')

    anim_css = ANIM_CSS if animate else ""
    anim_js = ANIM_JS if animate else ""
    reveal = ' class="reveal"' if animate else ""

    return TEMPLATE.format(
        lang="pt-BR",
        title=esc(cab.get("titulo_aba", cab.get("titulo", "Relatório de Funil"))),
        bg=fundo, gold=primaria, teal=secundaria, anim_css=anim_css,
        brand_html=brand_html, brand_line=esc(cab.get("brand_line", "")),
        titulo=titulo, lede=cab.get("lede", ""), stamps=stamps,
        funis=funis, conclusao=conc_html, plano=plano_html,
        rodape=dados.get("rodape", ""), reveal=reveal, anim_js=anim_js)


ANIM_CSS = '''
  @media (prefers-reduced-motion: no-preference){
    .fpoly{opacity:0;transform-box:fill-box;transform-origin:left center;animation:fgrow .7s cubic-bezier(.2,.8,.2,1) forwards;}
    @keyframes fgrow{from{opacity:0;transform:scaleX(.15)}to{opacity:1;transform:scaleX(1)}}
    .reveal{opacity:0;transform:translateY(18px);transition:opacity .6s ease,transform .6s ease;}
    .reveal.in{opacity:1;transform:none;}
  }'''

ANIM_JS = '''
<script>
(function(){
  var rm = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  // count-up
  function count(el){
    var raw = el.getAttribute('data-raw')||el.textContent;
    var m = raw.match(/[\\d.]+/); if(!m){return;}
    var target = parseInt(m[0].replace(/[^\\d]/g,''),10); if(!target){return;}
    var pre = raw.slice(0,m.index), suf = raw.slice(m.index+m[0].length);
    var steps=38, i=0;
    var t=setInterval(function(){
      i++; var cur=Math.min(target, Math.round(target*i/steps));
      el.textContent = pre + cur.toLocaleString('pt-BR') + suf;
      if(i>=steps){el.textContent = pre + target.toLocaleString('pt-BR') + suf; clearInterval(t);}
    }, 22);
  }
  // scroll reveal
  var io = ('IntersectionObserver' in window) ? new IntersectionObserver(function(es){
    es.forEach(function(e){ if(e.isIntersecting){
      e.target.classList.add('in');
      e.target.querySelectorAll('.js-count').forEach(count);
      io.unobserve(e.target);
    }});
  },{threshold:.18}) : null;
  document.addEventListener('DOMContentLoaded', function(){
    if(rm || !io){ document.querySelectorAll('.js-count').forEach(count);
      document.querySelectorAll('.reveal').forEach(function(x){x.classList.add('in');}); return; }
    document.querySelectorAll('section,.close,header').forEach(function(s){
      s.classList.add('reveal'); io.observe(s);
    });
    // header conta logo de cara
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
  .stamps div{{flex:1;padding-top:18px;border-right:1px solid var(--line);min-width:120px;}}
  .stamps div:last-child{{border:none;}}
  .stamps .k{{font-size:10px;letter-spacing:1.2px;text-transform:uppercase;color:var(--mut2);}}
  .stamps .v{{font-size:24px;font-weight:300;letter-spacing:-1px;margin-top:6px;}}
  .stamps .v small{{font-size:12px;color:var(--gold);letter-spacing:0;}}
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
  @media(max-width:680px){{.grid2{{grid-template-columns:1fr;}}}}{anim_css}
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
