# Instruções para Criar Repositório no GitHub

## Passo 1: Criar o Repositório no GitHub

1. Acesse https://github.com e faça login
2. Clique no botão **"+"** no canto superior direito
3. Selecione **"New repository"**
4. Preencha os dados:
   - **Repository name**: `safety_compliance` (ou outro nome de sua preferência)
   - **Description**: `Sistema de Gestão de Conformidade ANAC para Aeroportos Brasileiros`
   - **Visibility**: Escolha **Public** ou **Private**
   - **NÃO marque** "Add a README file" (já temos um)
   - **NÃO marque** "Add .gitignore" (já temos um)
   - **NÃO marque** "Choose a license" (pode adicionar depois se quiser)
5. Clique em **"Create repository"**

## Passo 2: Conectar o Repositório Local ao GitHub

Após criar o repositório no GitHub, você verá uma página com instruções. Execute os seguintes comandos no terminal:

```bash
cd /Users/Luciana/safety_compliance

# Adicionar o remote do GitHub (substitua SEU_USUARIO pelo seu username do GitHub)
git remote add origin https://github.com/SEU_USUARIO/safety_compliance.git

# Ou se preferir usar SSH:
# git remote add origin git@github.com:SEU_USUARIO/safety_compliance.git

# Verificar se foi adicionado corretamente
git remote -v

# Fazer o push do código
git push -u origin main
```

## Passo 3: Verificar

1. Acesse o repositório no GitHub
2. Verifique se todos os arquivos foram enviados corretamente
3. O README.md deve aparecer na página principal do repositório

## Comandos Úteis para o Futuro

### Adicionar e commitar mudanças:
```bash
git add .
git commit -m "Descrição das mudanças"
git push
```

### Ver status:
```bash
git status
```

### Ver histórico:
```bash
git log --oneline
```

### Criar uma nova branch:
```bash
git checkout -b nome-da-branch
git push -u origin nome-da-branch
```

## Nota sobre Arquivos Sensíveis

Os seguintes arquivos estão no `.gitignore` e **NÃO** serão enviados:
- `compliance.db` (banco de dados)
- Arquivos `.pdf` (documentos)
- Arquivos `.xlsx` (planilhas)
- Arquivos em `__pycache__/`
- Arquivos `.env` (variáveis de ambiente)

Se precisar adicionar algum desses arquivos, remova-os do `.gitignore` antes de fazer commit.
