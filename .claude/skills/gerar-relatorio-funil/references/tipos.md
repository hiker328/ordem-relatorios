# Tipos de relatório

O **mesmo `dados.json`** gera formatos diferentes — basta escolher o `tipo`. Assim
os relatórios não saem todos iguais: você adapta ao objetivo e ao interlocutor.

Defina via `--tipo` na linha de comando **ou** com o campo `"tipo"` no `dados.json`.
Padrão: `completo`.

| Tipo | Para quê | Inclui |
|------|----------|--------|
| **completo** | Diagnóstico cheio (padrão) | 3 funis + R$ + tabelas + conclusão + plano |
| **executivo** | 1 página para o dono/decisor | funil de vendas + R$ + conclusão + plano |
| **midia** | Reunião com o gestor de tráfego | funil de marketing + cards + atribuição + plano de mídia |
| **comercial** | Reunião com o time de vendas | funil comercial + pipeline/por-closer + plano comercial |
| **performance** | Foco em ROI/retorno | KPIs em R$ + funil de vendas + atribuição |
| **semanal** | Acompanhamento rápido | KPIs (com deltas) + funil de vendas + plano |

```bash
python scripts/build_report.py dados.json --tipo executivo -o relatorio.html
python scripts/build_report.py dados.json --tipo midia     -o midia.html
```

## Como funciona
Cada tipo seleciona e ordena as seções a partir do mesmo `dados.json`:
- **midia** mostra só as tabelas e itens de plano de **marketing** (`cor:"marketing"`,
  `setor:"m"`); **comercial** filtra para os de **comercial**.
- Tipos enxutos (executivo/semanal) escondem os funis 2 e 3 e tabelas, mantendo a
  narrativa essencial.

## Dica
Monte o `dados.json` **uma vez** (completo) e gere vários tipos dele: um `completo`
para o arquivo, um `executivo` para o dono, um `midia` para a reunião de tráfego.
Combine com a marca (cores/logo) para cada cliente ter sua identidade.
