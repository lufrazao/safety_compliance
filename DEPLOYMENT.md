# Deploy no Railway

Guia passo a passo para colocar o Sistema de Conformidade ANAC online.

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

1. Clique no serviço da **aplicação** (não no PostgreSQL)
2. Vá em **"Variables"** → **"+ New Variable"** → **"Add Reference"**
3. Selecione o serviço **PostgreSQL** e a variável **`DATABASE_URL`**
4. Isso injeta automaticamente a URL de conexão na aplicação

Alternativa: se não houver "Add Reference", copie manualmente o valor de `DATABASE_URL` do PostgreSQL e crie a variável no serviço da aplicação.

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

## Passo 6: Popular dados iniciais (primeira vez)

Após o primeiro deploy, carregue as normas RBAC-153 e RBAC-154:

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
- Normal quando o site da ANAC está indisponível
- O sistema usa cache ou cadastro local como fallback
