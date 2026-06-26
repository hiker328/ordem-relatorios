#!/usr/bin/env python3
"""
Testes do gerador de relatório (build_report.py) — sem rede, só stdlib.

Rodar:
    python tests/test_build.py
    pytest tests/
"""
import importlib.util
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
BR = ROOT / ".claude" / "skills" / "gerar-relatorio-funil" / "scripts" / "build_report.py"
EX = ROOT / "examples" / "dados-exemplo.json"

spec = importlib.util.spec_from_file_location("build_report", BR)
br = importlib.util.module_from_spec(spec)
spec.loader.exec_module(br)


def test_num():
    assert br.num("62.039") == 62039
    assert br.num("R$ 2.247") == 2247
    assert br.num("5 · 3") == 5
    assert br.num("") == 0
    assert br.num(51) == 51


def test_count_span_conta_numero():
    out = br.count_span("226", animate=True)
    assert "js-count" in out and "226" in out


def test_count_span_ignora_data():
    assert "js-count" not in br.count_span("28/05–24/06", animate=True)


def test_count_span_sem_anim():
    assert br.count_span("226", animate=False) == "226"


def test_hfunnel_poligonos_e_gradientes():
    etapas = [{"nome": "A", "valor": "100"}, {"nome": "B", "valor": "50"}]
    svg = br.hfunnel_svg(etapas, "gX", ("#111", "#222"), ("#333", "#444"), animate=True)
    assert svg.count("<polygon") == 2
    assert 'id="gX_m"' in svg and 'id="gX_c"' in svg
    assert "fpoly" in svg


def test_vfunnel_handoff():
    etapas = [{"nome": "Lead", "valor": "100", "fase": "mkt"},
              {"nome": "MQL", "valor": "50", "fase": "mkt"},
              {"nome": "Venda", "valor": "5", "fase": "com"}]
    svg = br.vfunnel_svg(etapas, "gV", ("#1", "#2"), ("#3", "#4"), animate=False)
    assert svg.count("<polygon") == 3
    assert "HANDOFF" in svg  # divisor marketing -> comercial


def test_escape_em_nome():
    svg = br.hfunnel_svg([{"nome": "<script>", "valor": "1"}], "gY",
                         ("#1", "#2"), ("#3", "#4"), animate=False)
    assert "<script>" not in svg
    assert "&LT;SCRIPT&GT;" in svg.upper()


def test_render_exemplo_completo():
    dados = json.loads(EX.read_text(encoding="utf-8"))
    html = br.render(dados, animate=True)
    assert html.startswith("<!DOCTYPE html>")
    assert "{" not in html.split("<style>")[0]            # sem placeholders no topo
    assert html.count("<polygon") == 19                   # 9 + 4 + 6 etapas
    assert html.count("<linearGradient") == 6             # 3 funis x 2 gradientes
    assert "IntersectionObserver" in html
    assert "O retorno em dinheiro" in html                # seção resultado (KPIs)
    assert "closed-loop" in html                          # tabela de atribuição
    assert "Quem converte melhor" in html                 # tabela por closer
    assert 'class="kpi"' in html and 'class="tbl"' in html


def test_render_sem_anim():
    dados = json.loads(EX.read_text(encoding="utf-8"))
    html = br.render(dados, animate=False)
    assert "IntersectionObserver" not in html and "fpoly" not in html


def _run_all():
    fns = [v for k, v in globals().items() if k.startswith("test_") and callable(v)]
    falhas = 0
    for fn in fns:
        try:
            fn()
            print(f"OK  {fn.__name__}")
        except AssertionError as e:
            falhas += 1
            print(f"FAIL {fn.__name__}: {e}")
    print(f"\n{len(fns) - falhas}/{len(fns)} passaram.")
    return falhas


if __name__ == "__main__":
    import sys
    sys.exit(1 if _run_all() else 0)
