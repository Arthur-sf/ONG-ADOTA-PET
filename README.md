
# ONG ADOTA PET

## Sobre o projeto

O ONG ADOTA PET é uma plataforma web desenvolvida para facilitar a adoção responsável de animais, conectando adotantes e responsáveis por pets. O sistema permite divulgar animais disponíveis, realizar buscas personalizadas e gerenciar pedidos de adoção de forma simples e organizada.

## Links de acesso

- **Site:** https://ong-adota-pet.onrender.com
- **Documentação da API:** https://ong-adota-pet.onrender.com/apidocs/
- **Repositório GitHub:** https://github.com/Arthur-sf/ONG-ADOTA-PET

## Funcionalidades

- Cadastro e autenticação de usuários.
- Perfis de adotante e responsável.
- Cadastro, consulta, edição e exclusão de pets.
- Pesquisa de animais por filtros.
- Mapa interativo com localização aproximada dos pets.
- Envio e gerenciamento de pedidos de adoção.
- Sistema de favoritos.
- Cadastro de fotos por URL através da API.
- Interface responsiva para diferentes dispositivos.

## Tecnologias utilizadas

| Categoria | Tecnologias |
|---|---|
| Frontend | HTML, CSS e JavaScript |
| Backend | Python e Flask |
| Banco de dados | MySQL |
| Gerenciamento do banco | DBeaver |
| Mapas | Leaflet e OpenStreetMap |
| Documentação da API | Swagger e Flasgger |
| Versionamento | Git e GitHub |
| Hospedagem | Render e Aiven |

## Arquitetura do sistema

A plataforma integra frontend, backend e banco de dados por meio de uma API REST, utilizando JSON para a comunicação entre a interface e o servidor.

O banco de dados MySQL é composto por seis tabelas relacionadas, responsáveis pelo armazenamento de usuários, pets, pedidos de adoção, favoritos, fotos e dados de triagem.

## Documentação da API

A API possui 18 operações documentadas com Swagger, permitindo consultar rotas, métodos HTTP, parâmetros e códigos de resposta.

## Segurança

O sistema utiliza autenticação por sessão, proteção de senhas por hash, controle de acesso por perfil, validação de dados, variáveis de ambiente e conexão segura com o banco de dados.

## Hospedagem

A aplicação está hospedada no Render, com banco de dados no Aiven e versionamento pelo GitHub, permitindo a publicação automatizada de atualizações.

## Melhorias futuras

- Desenvolvimento de um painel administrativo.
- Integração do formulário de triagem de adotantes.
- Upload e galeria de imagens.
- Aprimoramento da segurança e proteção de dados.

---

**ONG ADOTA PET — Conectando animais a novos lares.**
