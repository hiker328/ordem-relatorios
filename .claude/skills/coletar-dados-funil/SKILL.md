---
name: coletar-dados-funil
description: >-
  Coleta os dados dos 3 funis (vendas, marketing, comercial) de uma agência para
  alimentar o relatório de funil. Puxa métricas de mídia do Meta/Business Manager
  via Graph API (impressões, cliques, CTR, gasto, leads, breakdowns de
  posicionamento/região/criativo) e o funil comercial do CRM (via export CSV ou
  API: MQL, agendamentos, R1, propostas, contratos, pipeline). Se o usuário não
  tiver BM e/ou CRM, coleta os números manualmente pelo chat. Use quando o usuário
  quiser reunir dados de campanha/funil, conectar Meta Ads/CRM, ou preparar os
  números para o relatório de funil.
---

# Coletar Dados do Funil

Primeira etapa do relatório: reunir e normalizar os números dos 3 funis. A coleta
é mecânica (scripts/CSV/perguntas); a leitura/análise vem depois na skill
`gerar-relatorio-funil`.

## Passo 1 — Descubra o que o usuário tem

Pergunte se ele tem acesso a: **Meta/Business Manager** (mídia) e **CRM** (comercial).
Os dois juntos é o cenário ideal (permite atribuição lead→venda). Faltando um ou os
dois, segue por entrada manual — sem problema.

| Tem | Fonte | Referência |
|-----|-------|-----------|
| Meta BM | `scripts/meta_fetch.py` | `references/meta-ads.md` |
| CRM (API ou CSV) | `scripts/crm_csv.py` (CSV universal) | `references/crm.md` |
| Nenhum / parcial | perguntar no chat | `references/manual.md` |

**Sempre que pedir credencial, ensine como obter** (`references/credenciais.md`) —
não apenas peça. Trate toda credencial como segredo.

## Passo 2 — Colete o marketing (Meta)

```bash
python scripts/meta_fetch.py --account act_123 --token "<TOKEN>" --out meta.json
python scripts/meta_fetch.py --account act_123 --token "<TOKEN>" --level ad --out meta_ads.json
python scripts/meta_fetch.py --account act_123 --token "<TOKEN>" --breakdown publisher_platform
```
Pegue: impressões, cliques, CTR, gasto, leads, CPL, e os breakdowns que revelam
problema (criativo/fadiga, Instagram x Facebook, região, semana ruim).

## Passo 3 — Colete o comercial (CRM)

Caminho universal (qualquer CRM) = export CSV:
```bash
python scripts/crm_csv.py deals.csv --columns
python scripts/crm_csv.py deals.csv --stage-col "Etapa" --value-col "Valor"
```
Mapeie os estágios para: MQL → Agendaram → R1 → Qualificadas → Proposta → Contrato.
Capture também o **pipeline ativo** (deals em aberto: nome, estágio, observação).

## Passo 4 — Complete o que faltar (manual)

Pelo que não veio de API/CSV, pergunte no chat seguindo `references/manual.md`.
**Sempre tente capturar** ticket/valor dos contratos, metas e período anterior —
isso habilita ROI/ROAS e comparação (ver `references/metricas.md`).

## Passo 5 — Entregue os números organizados

Consolide tudo (marketing + comercial + pipeline + branding, se houver) e passe
para a skill **`gerar-relatorio-funil`**, que monta o `dados.json` e renderiza o
HTML. Calcule as taxas de conversão e marque o **maior ponto de vazamento**.
