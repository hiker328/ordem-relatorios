# Como obter cada credencial

Guia para o usuário pegar os acessos. Trate tudo como **segredo**: não comite, não
poste em chat público, não logue em texto. Quando o usuário não tiver, **ensine**
o passo a passo (não apenas peça).

## 1. Meta — Business Manager / Graph API (funil de marketing)

Precisa de **2 coisas**: o **ID da conta de anúncios** e um **access token** com
permissão `ads_read`.

### ID da conta de anúncios (`act_...`)
1. Acesse o **Gerenciador de Negócios** (business.facebook.com).
2. Configurações do Negócio → **Contas → Contas de anúncios**.
3. Copie o **ID da conta** (um número). No script vira `act_<numero>` (ou só o
   número — o script adiciona o `act_`).

### Access token (caminho mais simples: Graph API Explorer)
1. Abra **developers.facebook.com/tools/explorer**.
2. Em "Meta App", selecione um app seu (ou crie um app de tipo "Business").
3. Em **Permissions**, adicione `ads_read` (e `read_insights`).
4. Clique **Generate Access Token** e autorize. Copie o token.
5. Esse token é de curta duração (≈1-2h) — bom para testar. Para uso recorrente,
   gere um **token de longa duração** ou um **System User token** (Configurações
   do Negócio → Usuários → Usuários do sistema → gerar token com `ads_read`).

> Token expirou / "Error validating access token" → gere outro (passo 4) ou use
> System User token (mais estável).
> Sem app criado → developers.facebook.com → "Meus apps" → Criar app → "Empresa".

## 2. CRM (funil comercial)

O dado comercial (MQL, agendamentos, R1, propostas, contratos, pipeline) vem do
**CRM do lead/cliente**. Cada CRM tem seu jeito — abaixo os caminhos. Em todos,
a alternativa universal é **exportar um CSV** dos negócios e usar `crm_csv.py`.

| CRM | Onde pegar acesso de API |
|-----|--------------------------|
| **GoHighLevel (GHL)** | Settings → Business Profile / Private Integrations → cria token (API Key). Location/Sub-account API. |
| **Kommo** | Configurações → Integrações → cria integração → `client_id`/`secret` (OAuth) ou token de longa duração. |
| **RD Station** | Integrações → Token de API / App. |
| **HubSpot** | Settings → Integrations → Private Apps → cria app → token com escopo de CRM. |
| **Pipedrive** | Settings → Personal → API → copia o **API token**. |

**Caminho universal (qualquer CRM): exportar CSV.** No CRM, exporte os
negócios/oportunidades (com a coluna de **etapa/estágio** e, se possível, **valor**)
e rode:
```bash
python crm_csv.py deals.csv --columns                       # ver colunas
python crm_csv.py deals.csv --stage-col "Etapa" --value-col "Valor"
```

## 3. Sem BM e/ou sem CRM? Sem problema.

O usuário pode **digitar os números no chat** e o agente monta o relatório do mesmo
jeito. Ver `manual.md` para a lista do que perguntar. Dá para misturar: Meta via
API + comercial manual, ou vice-versa.
