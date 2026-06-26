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


def test_stamp_value_conta_numero():
    out = br.stamp_value("226", animate=True)
    assert "js-count" in out and "226" in out


def test_stamp_value_ignora_data():
    out = br.stamp_value("28/05–24/06", animate=True)
    assert "js-count" not in out


def test_stamp_value_sem_anim():
    assert br.stamp_value("226", animate=False) == "226"


def test_funnel_svg_tem_poligonos_e_gradientes():
    etapas = [{"nome": "A", "valor": "100"}, {"nome": "B", "valor": "50"}]
    svg = br.funnel_svg(etapas, "gX", ("#111", "#222"), ("#333", "#444"), animate=True)
    assert svg.count("<polygon") == 2
    assert 'id="gX_m"' in svg and 'id="gX_c"' in svg
    assert "fpoly" in svg  # classe de animação


def test_escape_em_nome():
    etapas = [{"nome": "<script>", "valor": "1"}]
    svg = br.funnel_svg(etapas, "gY", ("#1", "#2"), ("#3", "#4"), animate=False)
    assert "<script>" not in svg
    assert "&LT;SCRIPT&GT;" in svg.upper()  # escapado e uppercased no rótulo


def test_render_exemplo_completo():
    dados = json.loads(EX.read_text(encoding="utf-8"))
    html = br.render(dados, animate=True)
    assert html.startswith("<!DOCTYPE html>")
    assert "{" not in html.split("<style>")[0]  # sem placeholders no topo
    # 9 + 4 + 6 etapas = 19 polígonos
    assert html.count("<polygon") == 19
    # 3 funis x 2 gradientes = 6
    assert html.count("<linearGradient") == 6
    assert "IntersectionObserver" in html  # JS de animação presente


def test_render_sem_anim():
    dados = json.loads(EX.read_text(encoding="utf-8"))
    html = br.render(dados, animate=False)
    assert "IntersectionObserver" not in html
    assert "fpoly" not in html


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
