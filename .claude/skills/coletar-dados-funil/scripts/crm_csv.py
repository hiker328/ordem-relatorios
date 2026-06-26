#!/usr/bin/env python3
"""
Tabula um export CSV do CRM por estágio do funil — agnóstico de CRM.

Quase todo CRM (GHL, Kommo, RD Station, HubSpot, Pipedrive) exporta os
negócios/oportunidades em CSV com uma coluna de estágio/etapa. Este script conta
quantos há em cada estágio e (opcional) soma o valor dos deals.

Exemplos:
  # ver as colunas disponíveis
  python crm_csv.py deals.csv --columns

  # contar por estágio
  python crm_csv.py deals.csv --stage-col "Etapa"

  # contar por estágio e somar o valor
  python crm_csv.py deals.csv --stage-col "Etapa" --value-col "Valor"
"""
import argparse
import csv
import re
import sys
from collections import OrderedDict


def parse_money(s):
    if not s:
        return 0.0
    s = re.sub(r"[^\d,.-]", "", str(s)).replace(".", "").replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return 0.0


def main():
    ap = argparse.ArgumentParser(description="Tabula CSV de CRM por estágio")
    ap.add_argument("csv_path")
    ap.add_argument("--stage-col", help="nome da coluna de estágio/etapa")
    ap.add_argument("--value-col", help="nome da coluna de valor (opcional)")
    ap.add_argument("--columns", action="store_true", help="lista as colunas e sai")
    ap.add_argument("--delimiter", default=None, help="força delimitador (ex.: ';')")
    args = ap.parse_args()

    with open(args.csv_path, newline="", encoding="utf-8-sig") as f:
        sample = f.read(2048)
        f.seek(0)
        delim = args.delimiter
        if not delim:
            try:
                delim = csv.Sniffer().sniff(sample, delimiters=",;\t").delimiter
            except csv.Error:
                delim = ","
        reader = csv.DictReader(f, delimiter=delim)
        cols = reader.fieldnames or []

        if args.columns or not args.stage_col:
            print("Colunas encontradas:")
            for c in cols:
                print(f"  - {c}")
            if not args.stage_col:
                print("\nUse --stage-col \"<coluna>\" para tabular por estágio.")
            return

        if args.stage_col not in cols:
            sys.exit(f"Coluna '{args.stage_col}' não existe. Veja --columns.")

        counts, values, total = OrderedDict(), OrderedDict(), 0
        for row in reader:
            stage = (row.get(args.stage_col) or "(vazio)").strip()
            counts[stage] = counts.get(stage, 0) + 1
            total += 1
            if args.value_col:
                values[stage] = values.get(stage, 0.0) + parse_money(row.get(args.value_col))

    print(f"Total de registros: {total}\n")
    print(f"{'Estágio':<32} {'Qtd':>6}" + ("   Valor" if args.value_col else ""))
    print("-" * (40 + (12 if args.value_col else 0)))
    for stage, qt in sorted(counts.items(), key=lambda x: -x[1]):
        line = f"{stage[:32]:<32} {qt:>6}"
        if args.value_col:
            line += f"   R$ {values.get(stage,0):,.2f}"
        print(line)


if __name__ == "__main__":
    main()
