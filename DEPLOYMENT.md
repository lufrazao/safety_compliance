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
   - **Nome da variável:** `DATABASE_PUBLIC_URL` (recomendado) ou `DATABASE_URL`
   - **Serviço:** selecione o serviço **PostgreSQL** do seu projeto
   - **Variável:** selecione **`DATABASE_PUBLIC_URL`** (preferido) ou **`DATABASE_URL`**
4. Salve. O Railway injeta automaticamente a URL de conexão na aplicação.

**Por que DATABASE_PUBLIC_URL?** O `DATABASE_URL` do PostgreSQL usa o host `postgres.railway.internal`, que só resolve dentro da rede privada do Railway. Se o app e o banco estiverem em projetos/ambientes diferentes, ou houver falha na rede interna, use `DATABASE_PUBLIC_URL`, que usa o host público e funciona em qualquer cenário.

Alternativa: se não houver "Add Reference", copie manualmente o valor de `DATABASE_PUBLIC_URL` (ou `DATABASE_URL`) do PostgreSQL e crie a variável no serviço da aplicação.

---

## Passo 4: Senha de acesso (opcional)

Para proteger a plataforma com senha:

1. No serviço da aplicação → **Variables** → **+ New Variable**
2. **Nome:** `APP_PASSWORD`
3. **Valor:** sua senha de acesso
4. Salve. Ao acessar a plataforma, será exibida uma tela de login com **apenas o campo de senha** (sem usuário).

Se `APP_PASSWORD` não estiver definida, o acesso permanece livre.

---

## Passo 5: Configurar o comando de start

Railway usa o `Procfile` automaticamente. O comando é:

```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

O `$PORT` é definido pelo Railway. Não é necessário alterar nada.

---

## Passo 6: Deploy

1. Faça push das alterações para o GitHub (se ainda não fez)
2. Railway fará o deploy automaticamente a cada push na branch `main`
3. Aguarde o build e o deploy (2–5 minutos)
4. Clique em **"Settings"** → **"Generate Domain"** para obter a URL pública (ex: `safety-compliance-production.up.railway.app`)

---

## Passo 7: Popular dados iniciais (obrigatório)

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

## Passo 8: Verificar

1. Acesse a URL gerada (ex: `https://safety-compliance-production.up.railway.app`)
2. Cadastre um aeroporto de teste
3. Execute "Verificar Conformidade"

---

## Variáveis de ambiente (opcional)

| Variável               | Descrição                    | Padrão        |
|------------------------|------------------------------|---------------|
| `APP_PASSWORD`         | Senha de acesso à plataforma (HTTP Basic). Se definida, exige login. Usuário: qualquer (ex: admin) | Sem senha (acesso livre) |
| `DATABASE_PUBLIC_URL`  | URL pública do PostgreSQL (recomendado) | (obrigatório no Railway) |
| `DATABASE_URL`         | URL do PostgreSQL (host interno) | Alternativa |
| `PORT`                 | Porta (Railway define)       | Automático    |

---

## Troubleshooting

**Aeroportos cadastrados somem a cada deploy**
- A variável `DATABASE_URL` não está definida no serviço da aplicação
- O sistema está usando SQLite (arquivo no container = efêmero)
- **Solução:** Passos 2 e 3 – adicione PostgreSQL e vincule `DATABASE_URL` à aplicação
- Após vincular, os dados passam a persistir no PostgreSQL

**Erro "could not translate host name postgres.railway.internal"**
- O host interno do Railway só resolve dentro da rede privada do mesmo projeto
- **Solução:** Use `DATABASE_PUBLIC_URL` em vez de `DATABASE_URL`. No serviço da app → Variables → Add Reference → PostgreSQL → variável **`DATABASE_PUBLIC_URL`**
- O app já prioriza `DATABASE_PUBLIC_URL` quando disponível

**Outros erros de conexão com o banco**
- Confirme que `DATABASE_URL` ou `DATABASE_PUBLIC_URL` está definida e aponta para o PostgreSQL
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
