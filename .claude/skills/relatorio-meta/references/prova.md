# Prova — Relatório Executivo Meta Ads

> Exemplo com dados FICTÍCIOS. Mostra o tipo de relatório que a solução gera pro cliente.

## Input de exemplo (colado)
```
Cliente: clínica de estética, vende consultas (meta combinada: CPA até R$ 60 por agendamento)
Período: 01 a 30 de junho
Período anterior: 01 a 31 de maio
Relatório:
- Junho: investimento R$ 4.200 | agendamentos 84 | CPA R$ 50 | CTR 1,4% | alcance 61.000
- Maio: investimento R$ 4.000 | agendamentos 62 | CPA R$ 64 | CTR 1,1% | alcance 58.000
```

## Output esperado (trecho)
```
1. RESUMO EXECUTIVO
Em junho foram investidos R$ 4.200 em anúncios, que geraram 84 novos agendamentos —
22 a mais que em maio (62). Cada agendamento custou em média R$ 50, abaixo da meta
combinada de R$ 60. Foi o melhor mês até aqui em volume e em custo por agendamento.

2. PRINCIPAIS MÉTRICAS
Indicador            | Junho   | O que significa                              | vs. maio
Investimento         | R$ 4.200| valor aplicado em anúncios no mês            | +R$ 200
Agendamentos         | 84      | novos agendamentos vindos dos anúncios       | +22
Custo por agendamento| R$ 50   | quanto custou, em média, cada agendamento    | -R$ 14 (melhorou)
Alcance              | 61.000  | pessoas diferentes que viram os anúncios     | +3.000
Engajamento (CTR 1,4%)| 1,4%   | de cada 100 que viram, ~1 a 2 clicaram       | subiu

3. DESTAQUES E ALERTAS
DESTAQUES:
- 84 agendamentos no mês, 35% a mais que maio.
- Custo por agendamento caiu de R$ 64 pra R$ 50, abaixo da meta de R$ 60.
ALERTAS:
- O investimento subiu pouco (R$ 200); o ganho veio de eficiência, não de mais verba —
  pra crescer mais, vai precisar de mais orçamento.

4. INSIGHTS
- Os anúncios estão mais eficientes: gastando quase o mesmo, trouxeram mais agendamentos.
- O custo por agendamento abaixo da meta abre espaço seguro pra investir mais no próximo mês.

5. PRÓXIMAS AÇÕES
1. Aumentar o orçamento gradualmente — o custo por agendamento está abaixo da meta, então
   dá pra buscar mais volume sem estourar o combinado.
2. Acompanhar o custo por agendamento de perto ao subir a verba, pra manter dentro da meta.
```

## Por que funciona
O relatório sai dos próprios números colados (não há achismo): volume, custo por resultado e a comparação com maio vêm direto do que foi exportado. O jargão vira frase de dono de negócio, e a comparação só aparece porque o período anterior foi colado — sem isso, a solução não compararia.
