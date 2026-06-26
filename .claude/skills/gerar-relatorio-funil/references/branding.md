# Branding do relatório (logo + cores)

O relatório pode usar a identidade visual da empresa do usuário. **Tudo é opcional**
— sem isso, o relatório sai com tema genérico (navy + ouro/teal).

## O que pedir ao usuário (opcional)
1. **Logo** — arquivo (PNG/SVG) ou URL. Vai no topo do relatório.
2. **Cor primária** (marketing) e **cor secundária** (comercial), em HEX.
   - Se ele só souber "azul e laranja", peça o HEX ou pegue do logo/site.
3. Se não tiver nada → **não use logo** e siga com as cores genéricas (padrão).

## Como aplica no `dados.json`
```jsonc
"marca": {
  "nome": "Agência X",
  "logo": "logo.png",            // ou URL; null = sem logo
  "cor_primaria": "#FF7A00",     // vira o "ouro"/marketing
  "cor_secundaria": "#0F62FE",   // vira o "teal"/comercial
  "cor_fundo": "#0B1020"         // opcional; padrão navy #02112F
}
```

## Dicas de boa aparência
- O fundo é escuro; use cores **vivas** para primária/secundária (elas aparecem em
  cima do navy). Cores muito escuras somem.
- Primária ≠ secundária (são os dois lados do funil: marketing x comercial).
- Se o logo for escuro, ele pode sumir no fundo — prefira versão clara/branca do
  logo, ou deixe sem logo.
- Para casar com a marca sem quebrar o contraste, mantenha `cor_fundo` escuro.

## Logo local x compartilhar
Se o logo for um arquivo local, o `src` no HTML aponta para o caminho. Para o
relatório ficar **100% portátil** (um arquivo só, enviável por e-mail), você pode
pedir para embutir o logo como data URI — opcional; por padrão usamos o caminho/URL.
