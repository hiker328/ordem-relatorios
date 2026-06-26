# Coletar o funil de marketing (Meta Graph API)

Use `scripts/meta_fetch.py`. Credenciais em `credenciais.md` (seção 1).

## O que puxar (e por quê)

| Coleta | Comando | Serve para |
|--------|---------|------------|
| Visão geral da conta | `--account act_X --token T` | Impressões, cliques, CTR, gasto, leads (topo do funil) |
| Por anúncio | `--level ad` | Achar o criativo que carrega tudo, fadiga (frequency), criativos mortos |
| Por posicionamento | `--breakdown publisher_platform` | Comparar CPL Instagram x Facebook, cortar placement ruim |
| Por região | `--breakdown region` | Achar regiões que dão lead mas não MQL |
| Por semana | rodar com `--since/--until` por semana | Ver a semana em que o CPMQL disparou |

```bash
python scripts/meta_fetch.py --account act_123 --token "<TOKEN>" --out meta.json
python scripts/meta_fetch.py --account act_123 --token "<TOKEN>" --level ad --out meta_ads.json
python scripts/meta_fetch.py --account act_123 --token "<TOKEN>" --breakdown publisher_platform
```

## Campos retornados

`impressions, clicks, ctr, cpc, cpm, spend, reach, frequency, actions,
cost_per_action_type`. **Leads** saem de `actions` (qualquer `action_type` que
contenha `lead`) — o script já soma isso em `resumo.leads` e calcula `cpl`.

## Notas

- `act_` é adicionado automaticamente se você passar só o número.
- Período: `--date-preset last_30d` (padrão) ou `--since/--until` (YYYY-MM-DD).
- Paginação é seguida automaticamente.
- **MQL não vem do Meta** — MQL é classificação comercial (vem do CRM ou manual).
  O Meta entrega até o **lead**; do lead ao MQL é leitura do funil comercial.
