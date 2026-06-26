---
name: gerar-relatorio-funil
description: >-
  Gera um relatório visual de funil em HTML (auto-contido, tema escuro, funis em
  SVG animados, count-up de números, cards de risco/força, pipeline de deals e
  plano de ação) para agências. Lê os 3 funis (vendas, marketing, comercial),
  aplica a identidade da marca (logo + cores, opcional) e renderiza via
  build_report.py. Use quando o usuário quiser gerar/montar um relatório de funil,
  dashboard de campanha, diagnóstico de marketing+comercial, ou apresentar
  resultados de tráfego e vendas para um cliente.
---

# Gerar Relatório de Funil

Monta o relatório dos 3 funis em HTML animado. A coleta dos números é feita antes
pela skill `coletar-dados-funil` (ou manualmente). Aqui o agente faz o **juízo**
(análise dos cards, narrativa do pipeline, conclusão e plano), monta o `dados.json`
e o `build_report.py` renderiza (parte mecânica: layout, tema, funis e animação).

## Passo 1 — Garanta os dados e o branding

- Números dos 3 funis prontos (de `coletar-dados-funil` ou do chat).
- **Branding (opcional):** peça logo + cores da empresa — ver `references/branding.md`.
  Sem isso, segue com o tema genérico (navy + ouro/teal). Não bloqueie por causa disso.

## Passo 2 — Monte o `dados.json`

Siga o esquema em `references/estrutura-dados.md` (e o exemplo
`examples/dados-exemplo.json`). Sua análise entra aqui:
- **etapas** de cada funil com `valor`, `nota` e o vazamento marcado (`tipo:"leak"`).
- **cards** de risco/força/nota (o "porquê" dos números) — baseados em evidência.
- **pipeline** dos deals em aberto (nome, status, observação).
- **resultado** (opcional): KPIs em R$ — receita, ROAS, CAC, ticket — com **delta
  vs período anterior** (`bom` verde/vermelho) e **meta**. É o que mais vende a agência.
- **tabelas** (opcional): **atribuição lead→venda** (cruzar Meta+CRM) e **por closer**
  (cite o ciclo de venda; conecta à suíte `ordem-skills`).
- **stamps** do cabeçalho aceitam `delta`/`bom` para comparação vs período anterior.
- **conclusao** e **plano** (ações por setor, com prazo).
Use as fórmulas de `references/metricas.md` para as taxas e para achar o vazamento.

## Passo 3 — Renderize

```bash
python scripts/build_report.py dados.json -o relatorio.html
# sem animação (ex.: para PDF/impressão estática):
python scripts/build_report.py dados.json -o relatorio.html --no-anim
```

**Tipos de relatório** (mesmo `dados.json`, formatos diferentes — ver
`references/tipos.md`): `completo` (padrão), `executivo` (1 página p/ o dono),
`midia` (foco tráfego), `comercial` (foco vendas), `performance` (foco ROI),
`semanal` (acompanhamento). Escolha o que casa com o objetivo/interlocutor:
```bash
python scripts/build_report.py dados.json --tipo executivo -o relatorio.html
```

O HTML é **auto-contido** (CSS + SVG + JS embutidos; nenhuma dependência externa,
abre offline). Animações: funis crescem com stagger, números fazem count-up e as
seções aparecem ao rolar — tudo respeitando `prefers-reduced-motion`.

## Passo 4 — Entregue

Abra/entregue o `relatorio.html`. Para PDF, oriente "imprimir → salvar como PDF"
(o CSS já tem regras de print) ou gere com `--no-anim`.

## Princípios
- **Toda análise se apoia em número/evidência** — nada de afirmação solta.
- Cada funil aponta **um** vazamento principal e o plano ataca os vazamentos.
- Honestidade: se um dado não veio (sem BM/CRM), mostre "—", não invente.
