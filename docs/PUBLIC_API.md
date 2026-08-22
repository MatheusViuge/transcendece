# Public API v1

A Public API do Instituto Consuelo expõe um contrato versionado para integração externa sem reutilizar o JWT da aplicação web.

## Base URL

No deployment Docker local:

```text
https://localhost/api/v1/public
```

O prefixo `v1` é parte do contrato. Mudanças incompatíveis devem ser publicadas em uma nova versão (`v2`, etc.), mantendo `v1` estável enquanto ela for suportada.

## Autenticação

Todos os endpoints da Public API exigem:

```http
X-API-Key: <secret>
```

API keys são gerenciadas por um usuário autenticado com JWT nos endpoints internos `/api/api-keys`. O secret completo é devolvido **somente** na criação ou rotação. O banco armazena apenas hash SHA-256, prefixo identificável e metadados.

### Criar uma API key

```bash
curl -k -X POST https://localhost/api/api-keys \
  -H "Authorization: Bearer <JWT>" \
  -H "Content-Type: application/json" \
  -d '{"name":"integration","scopes":["courses:read","courses:write"]}'
```

`courses:write` só pode ser emitido para instrutores. Uma key read-only usa apenas `courses:read`.

### Listar / revogar / rotacionar

```bash
curl -k https://localhost/api/api-keys -H "Authorization: Bearer <JWT>"
curl -k -X DELETE https://localhost/api/api-keys/<KEY_ID> -H "Authorization: Bearer <JWT>"
curl -k -X POST https://localhost/api/api-keys/<KEY_ID>/rotate -H "Authorization: Bearer <JWT>"
```

Uma key revogada deixa de autenticar imediatamente. Usuários só podem administrar suas próprias keys.

## Rate limiting

O limite padrão é **20 requests por 60 segundos por API key**. O estado do limiter fica no PostgreSQL e é atualizado com lock da linha da key, portanto workers diferentes compartilham o mesmo contador.

Respostas autenticadas incluem `X-RateLimit-Limit`, `X-RateLimit-Remaining` e `X-RateLimit-Reset`. Ao exceder o limite, a API retorna `429 Too Many Requests` e `Retry-After`.

## Endpoints

### GET `/courses`

Lista cursos com `page` (>=1) e `page_size` (1..100).

```bash
curl -k "https://localhost/api/v1/public/courses?page=1&page_size=20" -H "X-API-Key: <API_KEY>"
```

### GET `/courses/{id}`

```bash
curl -k https://localhost/api/v1/public/courses/1 -H "X-API-Key: <API_KEY>"
```

### POST `/courses`

Requer `courses:write` e key de instrutor. O instrutor é derivado do owner da key, nunca de input do cliente.

```bash
curl -k -X POST https://localhost/api/v1/public/courses \
  -H "X-API-Key: <API_KEY>" -H "Content-Type: application/json" \
  -d '{"title":"Integração via API","description":"Curso externo.","price":99.90,"workload_hours":12,"category_id":1,"level_id":1}'
```

### PUT `/courses/{id}`

Requer `courses:write`; o instrutor só altera cursos próprios.

```bash
curl -k -X PUT https://localhost/api/v1/public/courses/31 \
  -H "X-API-Key: <API_KEY>" -H "Content-Type: application/json" \
  -d '{"title":"Integração via API — atualizado","price":119.90}'
```

### DELETE `/courses/{id}`

Requer `courses:write` e ownership. Retorna `204 No Content`.

```bash
curl -k -X DELETE https://localhost/api/v1/public/courses/31 -H "X-API-Key: <API_KEY>"
```

## Erros

- `401` — API key ausente, inválida ou revogada
- `403` — scope insuficiente / escrita não permitida
- `404` — recurso não encontrado ou não pertencente ao instrutor na escrita
- `422` — parâmetros/body inválidos
- `429` — rate limit excedido

A resposta de autenticação não revela hash nem detalhes que ajudem a enumerar secrets.

## OpenAPI

Swagger: `https://localhost/api/docs`

O esquema `X-API-Key` aparece no OpenAPI através de `APIKeyHeader`. Os schemas públicos são separados dos schemas internos para preservar o contrato v1.
