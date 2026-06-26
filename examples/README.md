# Exemplos

Três amostras **fictícias** com dados e paletas diferentes, mostrando entrada e
saída do relatório de funil. Cada `dados-*.json` é a entrada do `build_report.py`;
cada `relatorio-*.html` é a saída (abra no navegador para ver animado).

| Cenário | Dados | Relatório | Paleta |
|---------|-------|-----------|--------|
| Captação de integradores (SolarOS) | `dados-exemplo.json` | `relatorio-exemplo.html` | navy + ouro/teal |
| E-commerce de moda (Lumière) | `dados-ecommerce.json` | `relatorio-ecommerce.html` | roxo + verde |
| Clínica / saúde (Vitalis) | `dados-clinica.json` | `relatorio-clinica.html` | laranja + azul |

`previews/` tem prints PNG de cada um (topo em `preview-*.png`, página inteira em
`relatorio-*.png`) e o GIF da animação (`animacao.gif`).

`tipos/` tem um exemplo de cada **tipo de relatório** (completo, executivo, midia,
comercial, performance, semanal) gerado do mesmo `dados-exemplo.json` — ver
`tipos.md` na skill `gerar-relatorio-funil`.

Regerar um relatório:
```bash
python ../.claude/skills/gerar-relatorio-funil/scripts/build_report.py \
  dados-ecommerce.json -o relatorio-ecommerce.html
```

> Todos os dados são inventados (nomes, números e empresas fictícios).
