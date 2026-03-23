# /start — Iniciar TibiaWiki MCP Server

Skill para verificar requisitos, iniciar o crawler e deixar o servidor MCP online.

## Instruções

Ao executar este skill, siga **exatamente** estes passos:

### Passo 1 — Verificar requisitos

Execute os seguintes comandos e valide cada um:

```bash
# 1. Docker instalado
docker --version

# 2. Docker Compose instalado (v2)
docker compose version

# 3. Docker daemon rodando
docker info > /dev/null 2>&1

# 4. Porta 8000 livre (MCP)
! lsof -i :8000 > /dev/null 2>&1

# 5. Porta 5432 livre (PostgreSQL)
! lsof -i :5432 > /dev/null 2>&1
```

Se algum requisito falhar:
- **Docker não instalado**: Informe o usuário para instalar Docker — `https://docs.docker.com/get-docker/`
- **Docker Compose não encontrado**: Informe que Docker Compose V2 é necessário
- **Docker daemon parado**: Informe para iniciar o Docker (`sudo systemctl start docker` ou abrir Docker Desktop)
- **Porta 8000 ocupada**: Informe qual processo ocupa a porta e sugira liberá-la
- **Porta 5432 ocupada**: Informe qual processo ocupa a porta e sugira liberá-la

Se todos os requisitos passarem, prossiga para o passo 2.

### Passo 2 — Criar diretório de dados persistentes

```bash
mkdir -p ./data/postgres
```

Isso garante que o PostgreSQL terá armazenamento persistente na máquina hospedeira em `./data/postgres/`.

### Passo 3 — Iniciar os serviços

```bash
docker compose up --build -d
```

Isso irá:
1. Subir o PostgreSQL (com dados persistentes em `./data/postgres/`)
2. Executar o crawler/importer (`src/main.py`) — baixa e processa todas as páginas do TibiaWiki
3. Após o importer terminar, subir o servidor MCP na porta 8000

### Passo 4 — Acompanhar progresso

Monitore os logs para verificar o andamento:

```bash
# Ver logs do importer em tempo real (limitar output)
docker compose logs -f importer 2>&1 | head -50
```

Aguarde até que o serviço `importer` termine (exit code 0) e o serviço `mcp` esteja healthy:

```bash
# Verificar status dos serviços
docker compose ps
```

### Passo 5 — Confirmar MCP online

Verifique se o MCP está respondendo:

```bash
curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/sse
```

### Passo 6 — Output final

Exiba para o usuário a seguinte mensagem de sucesso:

```
✅ TibiaWiki MCP Server está online!

🔗 MCP URL: http://localhost:8000/sse

Para conectar ao Claude Desktop, adicione ao seu arquivo de configuração MCP:

{
  "mcpServers": {
    "tibiawiki": {
      "url": "http://localhost:8000/sse"
    }
  }
}

📂 Dados do PostgreSQL persistidos em: ./data/postgres/
📋 Para ver os logs: docker compose logs -f
🛑 Para parar: docker compose down
```

### Troubleshooting

- Se o importer falhar, verifique os logs: `docker compose logs importer`
- Se o MCP não subir, verifique: `docker compose logs mcp`
- Para reiniciar tudo: `docker compose down && docker compose up --build -d`
- Os dados do banco são persistentes — reiniciar não perde dados
