# Workspace (template)

Layout sugerido para gerar relatórios de forma organizada. Copie esta pasta, renomeie
(ex.: `cliente-x/`) e trabalhe dentro dela.

```
cliente-x/
├── .env                 # credenciais (copie de .env.example) — NÃO comitar
├── entradas/            # exports do CRM (CSV), logo da marca
├── coletas/             # JSON do meta_fetch.py
├── dados.json           # montado pelo agente (números + análise)
└── relatorio.html       # saída final
```

Fluxo típico:
1. Coloque o logo e o CSV do CRM em `entradas/`.
2. Peça ao agente para coletar (Meta + CRM) e montar o `dados.json`.
3. Gere `relatorio.html` e envie ao cliente.

> `.env`, `entradas/`, `coletas/`, `dados.json` e `relatorio.html` já são ignorados
> pelo `.gitignore` do repo — dados de cliente e segredos não vão para o git.
