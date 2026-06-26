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
      {"k":"Investido","v":"R$ 2.247"},
      {"k":"Leads","v":"226"},
      {"k":"MQL","v":"51","small":"23%"}   // "small" = nota ao lado
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

## Regras importantes
- **`valor`** pode ter texto ("R$ 2.247", "5 · 3"); o gerador extrai o número para
  dimensionar o funil e mostra o texto como está.
- O **funil "vendas"** usa `fase` em cada etapa para colorir mkt (dourado) vs
  comercial (teal), com o handoff implícito na troca de cor.
- Campos de texto aceitam HTML inline (`<b>`, `<span class="n">…</span>`). O resto é
  escapado automaticamente — não injete HTML em `nome`, `valor`, `label`, etc.
- Marque **um** vazamento principal por funil com `"tipo":"leak"`.
