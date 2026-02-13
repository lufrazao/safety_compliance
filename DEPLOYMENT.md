# Deploy no Railway

Guia passo a passo para colocar o Sistema de Conformidade ANAC online.

---

## ⚠️ IMPORTANTE: Dados persistentes

**Se os aeroportos cadastrados somem a cada novo deploy**, a variável `DATABASE_URL` não está configurada. Sem ela, o sistema usa SQLite no container, e os dados são perdidos a cada push.

**Solução:** Siga os Passos 2 e 3 abaixo para adicionar PostgreSQL e vincular `DATABASE_URL` ao serviço da aplicação. Depois disso, os dados permanecem entre deploys.

---

## Pré-requisitos

- Conta no [Railway](https://railway.app)
- Repositório no GitHub (já configurado)

---

## Passo 1: Criar projeto no Railway

1. Acesse [railway.app](https://railway.app) e faça login
2. Clique em **"New Project"**
3. Selecione **"Deploy from GitHub repo"**
4. Conecte sua conta GitHub (se ainda não conectou)
5. Escolha o repositório `safety_compliance`
6. Railway detectará automaticamente o projeto

---

## Passo 2: Adicionar PostgreSQL

1. No dashboard do projeto, clique em **"+ New"**
2. Selecione **"Database"** → **"PostgreSQL"**
3. Aguarde o provisionamento (alguns segundos)
4. Clique no banco PostgreSQL e vá em **"Variables"**
5. Copie a variável `DATABASE_URL` (ou `DATABASE_PUBLIC_URL`)

---

## Passo 3: Vincular o banco à aplicação

**Onde configurar:** no serviço da **aplicação** (o que roda o código), não no serviço do PostgreSQL.

1. Clique no serviço da **aplicação** (não no PostgreSQL)
2. Vá em **"Variables"** → **"+ New Variable"** → **"Add Reference"**
3. Na janela que abrir:
   - **Nome da variável:** `DATABASE_URL` (digite exatamente isso)
   - **Serviço:** selecione o serviço **PostgreSQL** do seu projeto
   - **Variável:** selecione **`DATABASE_URL`** (a variável que o PostgreSQL já expõe)
4. Salve. O Railway injeta automaticamente a URL de conexão na aplicação.

Alternativa: se não houver "Add Reference", copie manualmente o valor de `DATABASE_URL` do PostgreSQL (em Variables do serviço PostgreSQL) e crie a variável `DATABASE_URL` no serviço da aplicação.

---

## Passo 4: Configurar o comando de start

Railway usa o `Procfile` automaticamente. O comando é:

```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

O `$PORT` é definido pelo Railway. Não é necessário alterar nada.

---

## Passo 5: Deploy

1. Faça push das alterações para o GitHub (se ainda não fez)
2. Railway fará o deploy automaticamente a cada push na branch `main`
3. Aguarde o build e o deploy (2–5 minutos)
4. Clique em **"Settings"** → **"Generate Domain"** para obter a URL pública (ex: `safety-compliance-production.up.railway.app`)

---

## Passo 6: Popular dados iniciais (obrigatório)

**Sem o seed, a verificação de conformidade mostrará 0 normas.** Após o primeiro deploy, carregue as normas RBAC-153 e RBAC-154:

**Opção recomendada – Endpoint de seed**

Após o deploy, chame uma vez (substitua pela sua URL):

```bash
curl -X POST https://SUA-URL.up.railway.app/api/seed
```

Ou no navegador, abra a aba de rede (F12 → Network), vá em qualquer página e execute no console:

```javascript
fetch('/api/seed', { method: 'POST' }).then(r => r.json()).then(console.log)
```

**Opção alternativa – Railway CLI**

```bash
railway login
railway link
railway run python -m app.seed_data
```

---

## Passo 7: Verificar

1. Acesse a URL gerada (ex: `https://safety-compliance-production.up.railway.app`)
2. Cadastre um aeroporto de teste
3. Execute "Verificar Conformidade"

---

## Variáveis de ambiente (opcional)

| Variável       | Descrição                    | Padrão        |
|----------------|------------------------------|---------------|
| `DATABASE_URL` | URL do PostgreSQL            | (obrigatório no Railway) |
| `PORT`         | Porta (Railway define)       | Automático    |

---

## Troubleshooting

**Aeroportos cadastrados somem a cada deploy**
- A variável `DATABASE_URL` não está definida no serviço da aplicação
- O sistema está usando SQLite (arquivo no container = efêmero)
- **Solução:** Passos 2 e 3 – adicione PostgreSQL e vincule `DATABASE_URL` à aplicação
- Após vincular, os dados passam a persistir no PostgreSQL

**Erro de conexão com o banco**
- Confirme que `DATABASE_URL` está definida e aponta para o PostgreSQL
- Verifique se o formato é `postgresql://` (o app converte `postgres://` automaticamente)

**Build falha**
- Confira se `requirements.txt` está na raiz
- Verifique os logs em **"Deployments"** → **"View Logs"**

**Página em branco**
- Abra o console do navegador (F12)
- Verifique se as requisições para `/api/*` retornam 200

**ANAC lookup retorna 503**
- Execute `POST /api/seed` para popular anac_airports (27 aeroportos) e airports (7 de exemplo)
- O sistema busca primeiro na base interna (anac_airports + airports); só chama a ANAC externa se não encontrar
