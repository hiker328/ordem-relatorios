#!/usr/bin/env python3
"""
Puxa métricas de mídia do Meta (Business Manager) via Graph API Insights.

Devolve JSON cru que o agente usa para montar o funil de marketing do relatório.
NÃO monta o relatório — só coleta. Credenciais: ver ../references/credenciais.md.

Métricas-chave do topo: impressões, cliques, CTR, gasto (spend), leads (actions),
+ breakdowns de posicionamento e região, e desempenho por anúncio (fadiga/criativo).

Exemplos:
  # visão geral da conta (últimos 30 dias)
  python meta_fetch.py --account act_123 --token TOKEN

  # por anúncio (achar o criativo que carrega tudo / fadiga)
  python meta_fetch.py --account act_123 --token TOKEN --level ad

  # quebra por posicionamento (Instagram x Facebook) e por região
  python meta_fetch.py --account act_123 --token TOKEN --breakdown publisher_platform
  python meta_fetch.py --account act_123 --token TOKEN --breakdown region

  # período custom
  python meta_fetch.py --account act_123 --token TOKEN --since 2026-05-28 --until 2026-06-24
"""
import argparse
import json
import sys

try:
    import requests
except ImportError:
    sys.exit("Faltou a lib 'requests'. Rode: pip install requests")

API = "https://graph.facebook.com"


def fetch(account, token, version, level, breakdown, date_preset, since, until):
    acct = account if account.startswith("act_") else f"act_{account}"
    fields = ("impressions,clicks,ctr,cpc,cpm,spend,reach,frequency,"
              "actions,cost_per_action_type")
    if level == "ad":
        fields = "ad_name,adset_name,campaign_name," + fields
    params = {
        "access_token": token,
        "fields": fields,
        "level": level,
        "limit": 200,
    }
    if breakdown:
        params["breakdowns"] = breakdown
    if since and until:
        params["time_range"] = json.dumps({"since": since, "until": until})
    else:
        params["date_preset"] = date_preset

    url = f"{API}/{version}/{acct}/insights"
    rows = []
    while url:
        r = requests.get(url, params=params, timeout=90)
        params = None  # paginação já carrega tudo na URL "next"
        data = r.json()
        if "error" in data:
            sys.exit(f"Erro Meta: {data['error'].get('message')}")
        rows.extend(data.get("data", []))
        url = data.get("paging", {}).get("next")
    return rows


def leads_from_actions(row):
    """Soma ações de lead (lead, lead_grouped, on-form leads)."""
    total = 0
    for a in row.get("actions", []) or []:
        t = a.get("action_type", "")
        if "lead" in t:
            try:
                total += int(float(a.get("value", 0)))
            except (TypeError, ValueError):
                pass
    return total


def summarize(rows):
    """Resumo simples para conferência rápida (o agente usa o JSON cru também)."""
    agg = {"impressions": 0, "clicks": 0, "spend": 0.0, "leads": 0}
    for r in rows:
        agg["impressions"] += int(float(r.get("impressions", 0) or 0))
        agg["clicks"] += int(float(r.get("clicks", 0) or 0))
        agg["spend"] += float(r.get("spend", 0) or 0)
        agg["leads"] += leads_from_actions(r)
    if agg["impressions"]:
        agg["ctr"] = round(agg["clicks"] / agg["impressions"] * 100, 2)
    if agg["leads"]:
        agg["cpl"] = round(agg["spend"] / agg["leads"], 2)
    return agg


def main():
    ap = argparse.ArgumentParser(description="Coleta insights do Meta (Graph API)")
    ap.add_argument("--account", required=True, help="ad account id (act_123 ou 123)")
    ap.add_argument("--token", required=True, help="access token (ads_read)")
    ap.add_argument("--version", default="v19.0")
    ap.add_argument("--level", default="account", choices=["account", "campaign", "adset", "ad"])
    ap.add_argument("--breakdown", default=None,
                    help="ex.: publisher_platform | region | age,gender")
    ap.add_argument("--date-preset", default="last_30d")
    ap.add_argument("--since", default=None, help="YYYY-MM-DD")
    ap.add_argument("--until", default=None, help="YYYY-MM-DD")
    ap.add_argument("--out", default=None, help="arquivo de saída (.json)")
    args = ap.parse_args()

    rows = fetch(args.account, args.token, args.version, args.level,
                 args.breakdown, args.date_preset, args.since, args.until)
    result = {"level": args.level, "breakdown": args.breakdown,
              "resumo": summarize(rows), "linhas": rows}
    out = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(out)
        print(f"OK -> {args.out} ({len(rows)} linhas) · resumo: {result['resumo']}")
    else:
        print(out)


if __name__ == "__main__":
    main()
