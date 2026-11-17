# Projeto 4 — Cadastro de Pets para Adoção

Projeto escolar baseado na estrutura do exemplo do professor: **Flask + MySQL + Leaflet + OpenStreetMap**. Inclui cadastro/login, perfis, CRUD de pets, filtros, mapa, pedidos, favoritos, fotos por URL HTTPS e tabelas de triagem.

## 1. Preparar o MySQL no DBeaver

1. Instale e inicie o **MySQL Server 8.0.16+**. O DBeaver é um cliente, não substitui o servidor.
2. Abra o DBeaver, crie uma conexão MySQL (`localhost`, porta `3306`, usuário e senha do seu MySQL).
3. Abra **Editor SQL → Novo script** e execute todo o arquivo `sql/banco.sql`.
4. Confira com `USE ong_adocao_pets; SHOW TABLES;`.
5. **Atenção:** `CREATE TABLE IF NOT EXISTS` não altera tabelas antigas. Em caso de banco anterior, faça backup e confira a estrutura antes de usar este script.

## 2. Abrir no VS Code (Windows)

No terminal da pasta `projeto4_adocao_pets`:

```powershell
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edite o `.env` e troque `SUA_SENHA` pela senha do MySQL; defina `SECRET_KEY` aleatória. Se sua senha contiver `@`, `#`, `:` ou `/`, codifique os caracteres especiais para uso em URL ou use uma senha de desenvolvimento sem esses caracteres. **Não compartilhe nem publique o `.env`.**

```powershell
python app.py
```

Abra http://127.0.0.1:5000. API Swagger: http://127.0.0.1:5000/apidocs/ . Teste de conexão: http://127.0.0.1:5000/health .

## 3. Testar o fluxo

1. Na aba **Minha conta**, crie uma conta **responsável** e faça login.
2. Vá em **Explorar pets**, clique no mapa para selecionar coordenadas aproximadas.
3. Abra **Cadastrar pet**, preencha o formulário e salve.
4. Saia e crie uma conta **adotante** com outro e-mail.
5. Encontre o pet, favorite e envie um pedido de adoção.
6. Entre novamente como responsável e vá à aba **Pedidos** para aceitar ou recusar.
7. O pet adotado sai da busca padrão; os demais pedidos pendentes são recusados em uma transação.

## Estrutura

- `app.py`: rotas Flask, autenticação e MySQL.
- `templates/index.html`: interface HTML.
- `static/style.css`: estilos.
- `static/app.js`: frontend e chamadas à API.
- `static/leaflet/`: arquivos Leaflet do exemplo do professor.
- `sql/banco.sql`: seis tabelas e relacionamentos.
- `.env.example`: exemplo de configuração sem credenciais reais.

## Observações para a avaliação

- A tabela `triagem_adotantes` existe, mas o formulário de triagem ainda não está integrado à interface.
- Fotos: há API para cadastrar **URL HTTPS** de fotos; upload de arquivos e galeria visual ainda não foram implementados.
- A rota de favoritos está pronta. A interface oferece adicionar/remover favoritos.
- A API é exposta no Swagger, mas os detalhes de parâmetros e respostas ainda precisam ser documentados.
- A autenticação utiliza sessão Flask. Para publicação com autenticação por cookie, configure HTTPS, `COOKIE_SECURE=true`, chave secreta forte e proteção CSRF para rotas de escrita.
- Não publique o projeto em produção sem revisar segurança, proteção CSRF, limites de requisição, política de privacidade e autorização.
- A aplicação não cria contas administradoras publicamente (por segurança). A administração completa não possui painel próprio nesta versão.
- A hospedagem Render + Aiven exige configurar `DATABASE_URL`, TLS/CA e variáveis de ambiente no serviço. Não envie certificados ou segredos ao Git.
