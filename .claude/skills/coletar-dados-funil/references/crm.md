# Coletar o funil comercial (CRM)

Do MQL ao contrato. O dado pode vir por **API do CRM** ou, de forma universal, por
**export CSV** + `scripts/crm_csv.py`. Credenciais em `credenciais.md` (seção 2).

## Caminho universal: CSV (qualquer CRM)

1. No CRM, exporte os negócios/oportunidades para CSV (inclua a coluna de
   **etapa/estágio** e, se houver, **valor** e **origem**).
2. Tabule:
   ```bash
   python scripts/crm_csv.py deals.csv --columns
   python scripts/crm_csv.py deals.csv --stage-col "Etapa" --value-col "Valor"
   ```
3. Mapeie os estágios do CRM para as **etapas do funil** do relatório (abaixo).

## Caminho via API

Cada CRM tem endpoints próprios (GHL, Kommo, RD, HubSpot, Pipedrive). Em geral:
liste oportunidades/deals do pipeline, com `stage`, `value`, `created_at`, `source`.
Quando não houver script pronto, peça ao usuário o CSV (mais rápido e confiável que
integrar cada CRM).

## Etapas-alvo do funil comercial

Mapeie os estágios do CRM para estas etapas (ajuste à operação do cliente):

| Etapa do relatório | O que é |
|--------------------|---------|
| **MQL** | Lead qualificado de marketing (apto a abordagem comercial) |
| **Agendaram** | Marcaram a 1ª reunião (R1) |
| **R1 feitas** | Reuniões realizadas (+ no-show, se houver) |
| **Qualificadas** | Passaram no filtro pós-R1 (seguem no jogo) |
| **Proposta** | Receberam proposta |
| **Contrato** | Fecharam (venda) |

Métricas que importam aqui: **taxa de agendamento** (agendaram/MQL), **no-show**,
**taxa de proposta**, **fechamento**, e o **pipeline ativo** (deals em aberto com
estágio + observação). Definições e fórmulas em `metricas.md`.

## Atribuição (cenário ideal: BM + CRM juntos)

Quando você tem **os dois**, dá para ligar o lead do anúncio ao resultado no CRM
(qual campanha gerou o MQL/contrato). A chave de junção costuma ser **telefone,
e-mail ou o `leadgen_id`** do formulário Meta gravado no CRM. Isso fecha o ciclo
(closed-loop) e é o que torna o relatório poderoso — não só "quantos", mas "de onde
veio o que fechou".
