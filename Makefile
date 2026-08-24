NAME = transcendence
COMPOSE = docker-compose
COMPOSE_FILE = docker-compose.yml
ENV_FILE = .env
COMPOSE_CMD = $(COMPOSE) -f $(COMPOSE_FILE)

GREEN = \033[0;32m
YELLOW = \033[0;33m
BLUE = \033[0;34m
RED = \033[0;31m
CYAN = \033[0;36m
BOLD = \033[1m
RESET = \033[0m

all: up

check-env:
	@if [ ! -f "$(ENV_FILE)" ]; then \
		echo "$(BOLD)$(RED)❌ [$(NAME)] Arquivo $(ENV_FILE) não encontrado.$(RESET)"; \
		echo "$(YELLOW)Execute 'make init' e ajuste os valores antes de subir o projeto.$(RESET)"; \
		exit 1; \
	fi

init:
	@if [ -f "$(ENV_FILE)" ]; then \
		echo "$(YELLOW)⚠ [$(NAME)] $(ENV_FILE) já existe; nada foi sobrescrito.$(RESET)"; \
	else \
		cp .env.example $(ENV_FILE); \
		echo "$(GREEN)✔ [$(NAME)] $(ENV_FILE) criado a partir de .env.example.$(RESET)"; \
		echo "$(YELLOW)⚠ Edite POSTGRES_PASSWORD e JWT_SECRET_KEY antes de usar em um ambiente real.$(RESET)"; \
	fi

up: check-env
	@echo "$(BOLD)$(GREEN)🚀 [$(NAME)] Subindo containers...$(RESET)"
	@$(COMPOSE_CMD) config --quiet
	@$(COMPOSE_CMD) up -d --build
	@echo "$(BOLD)$(GREEN)✅ [$(NAME)] Containers iniciados com sucesso.$(RESET)"
	@echo "$(CYAN)HTTPS: https://localhost$(RESET)"

down: check-env
	@echo "$(BOLD)$(YELLOW)🛑 [$(NAME)] Derrubando containers...$(RESET)"
	@$(COMPOSE_CMD) down --remove-orphans
	@echo "$(YELLOW)✔ [$(NAME)] Containers finalizados.$(RESET)"

start: check-env
	@echo "$(BOLD)$(GREEN)▶ [$(NAME)] Iniciando containers existentes...$(RESET)"
	@$(COMPOSE_CMD) start
	@echo "$(GREEN)✔ [$(NAME)] Containers iniciados.$(RESET)"

stop: check-env
	@echo "$(BOLD)$(YELLOW)⏸ [$(NAME)] Parando containers...$(RESET)"
	@$(COMPOSE_CMD) stop
	@echo "$(YELLOW)✔ [$(NAME)] Containers parados.$(RESET)"

restart: down up

re: restart

build: check-env
	@echo "$(BOLD)$(BLUE)🔧 [$(NAME)] Construindo imagens...$(RESET)"
	@$(COMPOSE_CMD) build
	@echo "$(BLUE)✔ [$(NAME)] Build concluído.$(RESET)"

ps: check-env
	@echo "$(BOLD)$(CYAN)📦 [$(NAME)] Status dos containers:$(RESET)"
	@$(COMPOSE_CMD) ps

status: ps

logs: check-env
	@echo "$(BOLD)$(CYAN)📜 [$(NAME)] Exibindo logs...$(RESET)"
	@$(COMPOSE_CMD) logs -f

logs-backend: check-env
	@$(COMPOSE_CMD) logs -f backend

logs-frontend: check-env
	@$(COMPOSE_CMD) logs -f frontend

logs-proxy: check-env
	@$(COMPOSE_CMD) logs -f proxy

logs-db: check-env
	@$(COMPOSE_CMD) logs -f db

config: check-env
	@echo "$(BOLD)$(BLUE)🔍 [$(NAME)] Validando $(COMPOSE_FILE)...$(RESET)"
	@$(COMPOSE_CMD) config --quiet
	@echo "$(GREEN)✔ [$(NAME)] Compose válido.$(RESET)"

clean: check-env
	@echo "$(BOLD)$(RED)🧹 [$(NAME)] Removendo containers, redes e volumes do projeto...$(RESET)"
	@$(COMPOSE_CMD) down -v --remove-orphans
	@echo "$(RED)✔ [$(NAME)] Limpeza concluída.$(RESET)"

fclean: check-env
	@echo "$(BOLD)$(RED)🔥 [$(NAME)] Removendo containers, volumes e imagens locais do projeto...$(RESET)"
	@$(COMPOSE_CMD) down -v --rmi local --remove-orphans
	@echo "$(RED)✔ [$(NAME)] Limpeza pesada concluída.$(RESET)"

reset: fclean up

shell-backend: check-env
	@$(COMPOSE_CMD) exec backend sh

shell-db: check-env
	@$(COMPOSE_CMD) exec db sh

help:
	@echo "$(BOLD)$(CYAN)\n📘 Comandos disponíveis:\n$(RESET)"
	@echo "$(GREEN)  make init$(RESET)          → cria .env a partir de .env.example"
	@echo "$(GREEN)  make up$(RESET)            → sobe o projeto com build"
	@echo "$(YELLOW)  make down$(RESET)          → derruba os containers preservando volumes"
	@echo "$(GREEN)  make start$(RESET)         → inicia containers já criados"
	@echo "$(YELLOW)  make stop$(RESET)          → para os containers sem removê-los"
	@echo "$(BLUE)  make build$(RESET)         → reconstrói as imagens"
	@echo "$(CYAN)  make ps$(RESET)            → mostra o status dos containers"
	@echo "$(CYAN)  make logs$(RESET)          → acompanha logs de todos os serviços"
	@echo "$(CYAN)  make logs-backend$(RESET)  → acompanha apenas o backend"
	@echo "$(CYAN)  make logs-frontend$(RESET) → acompanha apenas o frontend"
	@echo "$(CYAN)  make logs-proxy$(RESET)    → acompanha apenas o Nginx/proxy"
	@echo "$(CYAN)  make logs-db$(RESET)       → acompanha apenas o PostgreSQL"
	@echo "$(BLUE)  make config$(RESET)        → valida o docker-compose.yml"
	@echo "$(RED)  make clean$(RESET)         → remove containers + volumes do projeto"
	@echo "$(RED)  make fclean$(RESET)        → remove também imagens locais do projeto"
	@echo "$(BOLD)$(RED)  make reset$(RESET)         → limpa tudo do projeto e sobe novamente"
	@echo "$(CYAN)  make shell-backend$(RESET) → abre shell no backend"
	@echo "$(CYAN)  make shell-db$(RESET)      → abre shell no PostgreSQL"
	@echo "$(CYAN)  make help$(RESET)          → mostra esta ajuda\n"

.PHONY: all check-env init up down start stop restart re build ps status logs \
	logs-backend logs-frontend logs-proxy logs-db config clean fclean reset \
	shell-backend shell-db help
