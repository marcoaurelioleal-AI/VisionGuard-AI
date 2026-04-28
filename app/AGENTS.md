# AGENTS.md — VisionGuard API

## Visão geral do projeto

VisionGuard API é uma aplicação backend em Python voltada para análise, detecção e proteção visual usando Inteligência Artificial.

O projeto deve priorizar:

- Segurança
- Clareza de código
- Boas práticas de API
- Validação de entrada
- Tratamento seguro de arquivos e imagens
- Testes automatizados
- Facilidade de manutenção

## Papel do Codex neste repositório

Atue como um engenheiro de software sênior com foco em:

- Backend Python
- Segurança de APIs
- Revisão de código
- Testes automatizados
- Arquitetura simples e segura
- Explicações didáticas para um desenvolvedor em evolução

Ao modificar código, explique:

1. O problema encontrado.
2. A mudança feita.
3. O impacto esperado.
4. Como testar.

## Regras gerais de desenvolvimento

- Não faça mudanças grandes sem justificar.
- Prefira soluções simples, legíveis e seguras.
- Não remova validações existentes sem motivo claro.
- Não exponha segredos, tokens, chaves de API ou dados sensíveis.
- Não coloque credenciais diretamente no código.
- Use variáveis de ambiente para configurações sensíveis.
- Mantenha funções pequenas e com responsabilidade clara.
- Evite duplicação de lógica.
- Preserve compatibilidade com a estrutura atual do projeto.

## Segurança obrigatória

Sempre que revisar ou criar código, verifique:

- Validação de todos os dados recebidos pela API.
- Validação de uploads de arquivos e imagens.
- Limite máximo de tamanho para arquivos enviados.
- Proteção contra path traversal.
- Autenticação em endpoints sensíveis.
- Autorização correta para dados de usuários.
- Logs sem senhas, tokens ou dados sensíveis.
- Respostas de erro sem vazamento de stack trace em produção.
- CORS configurado de forma restritiva.
- Uso de ORM ou queries parametrizadas.
- Proteção contra abuso de endpoints sensíveis.

## Uploads e imagens

Ao lidar com arquivos enviados pelo usuário:

- Nunca use diretamente o nome enviado pelo usuário para salvar arquivos.
- Gere nomes seguros para arquivos.
- Valide extensão, MIME type e conteúdo real da imagem.
- Defina tamanho máximo permitido.
- Rejeite arquivos corrompidos ou inesperados.
- Não execute nenhum conteúdo enviado pelo usuário.
- Isole o diretório de uploads.
- Evite expor caminhos internos do servidor.

## Testes esperados

Sempre que possível, adicionar ou atualizar testes para:

- Casos de sucesso.
- Entradas inválidas.
- Uploads inválidos.
- Falhas de autenticação.
- Falhas de autorização.
- Limites de tamanho.
- Validação de formato.
- Tratamento de erros.

## Comandos úteis

Atualize esta seção conforme a estrutura real do projeto.

```bash
# Criar ambiente virtual
python -m venv .venv

# Ativar ambiente no Windows
.venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt

# Rodar aplicação
uvicorn app.main:app --reload

# Rodar testes
pytest