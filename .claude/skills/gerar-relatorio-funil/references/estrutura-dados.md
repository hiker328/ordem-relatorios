# Esquema do dados.json

O `build_report.py` lê um `dados.json` e renderiza o HTML. O agente monta esse JSON
com os números reais (de `coletar-dados-funil`) e a **análise** (cards, pipeline,
conclusão, plano). Veja um exemplo completo em `examples/dados-exemplo.json`.

## Estrutura

```jsonc
{
  "marca": {
    "nome": "Agência X",
    "logo": null,                  // caminho/URL do logo, ou null (sem logo)
    "cor_primaria": "#F4B321",     // cor do marketing/ouro (vars CSS)
    "cor_secundaria": "#3ec8cf",   // cor do comercial/teal
    "cor_fundo": "#02112F",        // navy de fundo
    "cor_marketing_a": "#e8a512",  // (opcional) parada inicial do gradiente mkt
    "cor_marketing_b": "#ffd87a",  // (opcional) parada final
    "cor_comercial_a": "#1f939b",  // (opcional)
    "cor_comercial_b": "#66dce3"   // (opcional)
  },
  "cabecalho": {
    "titulo_aba": "...",           // <title> da aba
    "brand_line": "AGÊNCIA · CLIENTE",
    "titulo": "Os três funis, e onde cada um vaza.",
    "titulo_em": "vaza",           // palavra destacada em dourado no título
    "lede": "texto de abertura (aceita <b>)",
    "stamps": [                    // métricas do topo (até ~5)
      {"k":"Período","v":"28/05–24/06"},
      {"k":"Leads","v":"226","delta":"+18% vs mês ant.","bom":true},
      {"k":"MQL","v":"51","small":"23%","delta":"+34% vs mês ant.","bom":true}
      // "small" = nota ao lado; "delta" = comparação vs período anterior;
      // "bom": true (verde ▲) | false (vermelho ▼) | ausente (neutro)
    ]
  },
  "funis": [
    {
      "id":"vendas",               // "vendas" | "marketing" | "comercial"
      "pill":"Funil 1","eyebrow":"Visão geral",
      "titulo":"...","sub":"... (aceita <b>)",
      "etapas":[
        {"nome":"Leads","valor":"226","nota":"34,8% do clique","tipo":"win","fase":"mkt"},
        {"nome":"MQL","valor":"51","nota":"22,6%","tipo":"leak","fase":"mkt"}
        // tipo: "win" (verde) | "leak" (vermelho, marca vazamento) | ausente (neutro)
        // fase: "mkt" (cor primária) | "com" (cor secundária) — usado no funil "vendas"
      ],
      "frase":{"rotulo":"A leitura de uma frase","titulo":"...","texto":"... (aceita <b>,<span class=n>)"}
    },
    { "id":"marketing", ..., "etapas":[...], "cards":[ ... ] },
    { "id":"comercial", ..., "etapas":[...], "cards":[ ... ], "pipeline":[ ... ] }
  ],
  "conclusao": {
    "titulo":"A conclusão",
    "paragrafos":["... (aceita HTML)"],
    "tags":[ {"label":"Marketing","cor":"m","texto":"..."},
             {"label":"Comercial","cor":"c","texto":"..."} ]
  },
  "plano": {
    "titulo":"O que destrava cada funil",
    "itens":[ {"setor":"c","acao":"...","detalhe":"...","prazo":"Imediato"} ]
    // setor: "m" (marketing) | "c" (comercial)
  },
  "rodape": "fontes dos dados, período, observações"
}
```

## cards (dentro de funis)
```jsonc
{"tipo":"risk","label":"Risco · crítico","titulo":"...","texto":"... (aceita HTML)"}
// tipo: "risk" (vermelho) | "force" (verde) | "note" (âmbar)
```

## pipeline (dentro do funil comercial)
```jsonc
{"nome":"Cliente","status":"hot","status_label":"contrato na rua","desc":"..."}
// status: "hot" (verde) | "warm" (âmbar) | "cold" (vermelho)
```

## resultado (opcional) — o retorno em R$ (ROI/ROAS/CAC/ticket)
Seção de KPIs em dinheiro, logo após os funis. Mostra que volume virou caixa.
```jsonc
"resultado": {
  "titulo":"O retorno em dinheiro", "sub":"...",
  "kpis":[
    {"label":"Receita fechada","valor":"R$ 9.600","delta":"1 contrato","bom":true},
    {"label":"ROAS","valor":"4,3x","delta":"+0,8x vs mês ant.","bom":true,"meta":"meta: 4,0x"},
    {"label":"CAC","valor":"R$ 2.247","delta":"cai com os em rota","bom":true}
    // "bom": true (verde ▲) | false (vermelho ▼) | ausente; "meta" e "delta" opcionais
  ]
}
```

## tabelas (opcional) — atribuição e por-closer
Tabelas genéricas após o resultado. Use para **atribuição lead→venda** (cruzando
Meta+CRM) e **desempenho por closer** (liga à suíte ordem-skills; cite o ciclo de
venda no `sub`).
```jsonc
"tabelas":[
  {"cor":"marketing","pill":"Atribuição","eyebrow":"De onde veio o que fechou",
   "titulo":"Lead → venda (closed-loop)","sub":"...",
   "colunas":["Campanha","Leads","MQL","Contrato"],
   "linhas":[["Faturamento +100k","78","32","1"], ["Aberta","126","17","0"]]},
  {"cor":"comercial","pill":"Por closer","eyebrow":"...","titulo":"Quem converte melhor",
   "colunas":["Closer","MQL","Agendou","Fechou","Taxa"],
   "linhas":[["Marina","27","8","1","30%"]]}
]
// cor: "marketing" | "comercial" | "vendas" (cor do eyebrow). Conteúdo é escapado.
```

## Regras importantes
- **`valor`** pode ter texto ("R$ 2.247", "5 · 3"); o gerador extrai o número para
  dimensionar o funil e mostra o texto como está.
- O **funil "vendas"** usa `fase` em cada etapa para colorir mkt (dourado) vs
  comercial (teal), com o handoff implícito na troca de cor.
- Campos de texto aceitam HTML inline (`<b>`, `<span class="n">…</span>`). O resto é
  escapado automaticamente — não injete HTML em `nome`, `valor`, `label`, etc.
- Marque **um** vazamento principal por funil com `"tipo":"leak"`.
