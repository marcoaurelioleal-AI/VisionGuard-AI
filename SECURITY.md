# Segurança do VisionGuard API

Este documento descreve as proteções de segurança atuais do VisionGuard API, as limitações conhecidas do MVP e recomendações para uma versão de produção.

## Proteções Atuais

### Limite de tamanho de upload

A API limita o tamanho máximo do arquivo enviado para reduzir risco de abuso, consumo excessivo de memória e uploads acidentais muito grandes.

Configuração atual:

```python
MAX_UPLOAD_SIZE_MB = 10
```

Quando o arquivo excede esse limite, a API retorna `413 Payload Too Large`.

### Limite de resolução e pixels da imagem

Além do tamanho em MB, a API valida as dimensões da imagem depois do decode com OpenCV.

Configurações atuais:

```python
MAX_IMAGE_WIDTH = 4096
MAX_IMAGE_HEIGHT = 4096
MAX_IMAGE_PIXELS = 16_000_000
```

Essa proteção reduz risco de imagens muito grandes causarem alto uso de CPU/memória durante a execução do OpenCV ou YOLO.

### Rate limiting nas rotas pesadas

As rotas que recebem upload e executam OpenCV/YOLO possuem rate limiting em memória por cliente e por rota.

Configuração atual:

```python
RATE_LIMIT_MAX_REQUESTS = 60
RATE_LIMIT_WINDOW_SECONDS = 60
```

Rotas protegidas:

- `POST /detect/faces`
- `POST /detect/faces/annotated`
- `POST /detect/objects`
- `POST /detect/objects/annotated`
- `POST /detect/all`
- `POST /detect/all/annotated`
- `POST /analyze/image`

Quando o limite é excedido, a API retorna `429 Too Many Requests` com o header `Retry-After`.

### Validação de extensão, content-type e decode da imagem

Uploads são validados antes do processamento:

- Extensões aceitas: `.jpg`, `.jpeg`, `.png`.
- Content-types aceitos: `image/jpeg`, `image/png`.
- O conteúdo do arquivo precisa ser decodificado com sucesso pelo OpenCV.
- Arquivos vazios são rejeitados.

Essa validação reduz risco de envio de arquivos incompatíveis ou inválidos para os serviços de visão computacional.

### Nomes seguros para imagens de saída

As imagens anotadas salvas em `outputs/` usam:

- limpeza simples do nome original;
- extensão validada;
- sufixo único com UUID.

Exemplo de saída:

```text
outputs/minha_imagem_a1b2c3d4.jpg
```

Isso reduz risco de sobrescrever arquivos anteriores e evita depender diretamente do nome enviado pelo usuário.

### Queries parametrizadas no SQLite

As operações atuais de escrita e leitura do histórico usam queries parametrizadas com placeholders `?`.

Exemplos:

- `INSERT INTO analysis_records (...) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`
- `LIMIT ?`

Isso reduz risco de SQL injection nos pontos atuais em que dados do usuário são persistidos ou usados em consultas.

## Limitações Atuais do MVP

O VisionGuard API ainda é um MVP e possui limitações importantes:

- Não há autenticação.
- Não há autorização por usuário/perfil.
- O rate limiter é em memória e funciona melhor em execução local ou em um único processo.
- O rate limiter em memória não compartilha estado entre múltiplos workers, containers ou servidores.
- Não há política CORS restritiva configurada para produção.
- Não há limpeza automática dos arquivos antigos em `outputs/`.
- Não há logs estruturados de segurança/auditoria.
- Não há antivírus/sandbox para arquivos enviados.
- O projeto não deve ser usado para decisões sensíveis sem revisão humana.

## Recomendações Futuras Para Produção

Antes de expor o VisionGuard API publicamente, recomenda-se:

- Adicionar autenticação, por exemplo API key, OAuth2 ou login com provedor externo.
- Adicionar autorização para separar usuários, limites e permissões.
- Migrar o rate limiting para Redis, API Gateway, Nginx, Cloudflare ou outro mecanismo compartilhado.
- Configurar CORS de forma restritiva, permitindo apenas domínios confiáveis.
- Adicionar logs estruturados com correlação de requisições, IP, rota, status code e tempo de resposta.
- Adicionar limpeza periódica de arquivos antigos em `outputs/`.
- Definir política de retenção para imagens e registros no SQLite.
- Considerar armazenamento externo seguro para outputs, como S3 ou equivalente.
- Adicionar monitoramento de erros e métricas de uso.
- Definir limites diferentes por rota, usuário ou plano de uso.
- Validar headers de proxy, como `X-Forwarded-For`, somente quando a aplicação estiver atrás de proxy confiável.
- Executar a aplicação com HTTPS em produção.

## Resumo

O MVP já possui proteções importantes contra uploads inválidos, imagens grandes, abuso básico de endpoints pesados e sobrescrita de arquivos. Ainda assim, autenticação, rate limiting distribuído, CORS restritivo, logs estruturados e limpeza automática de outputs são passos importantes antes de uma publicação em produção.
