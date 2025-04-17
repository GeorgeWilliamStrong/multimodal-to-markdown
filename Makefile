.PHONY: all setup deploy clean

# Default target runs setup and deploy
all: setup deploy

# Setup .env file
env:
	@echo "Setting up environment..."
	@if [ ! -f .env ]; then \
		echo "Creating .env file template..."; \
		echo "INSTILL_CORE_API_TOKEN=your_instill_core_api_token" > .env; \
		echo "OPENAI_API_TOKEN=your_openai_api_token" >> .env; \
		echo "Please edit .env file with your actual API tokens"; \
	else \
		echo ".env file already exists"; \
	fi

# Setup creates necessary environment and secrets
setup:
	@echo "Creating OpenAI secret in Instill Core..."
	python scripts/create_openai_secret.py

# Deploy the pipeline recipes
deploy:
	@echo "Deploying pipeline recipes..."
	python scripts/deploy_recipes.py

# Help target
help:
	@echo "Unstructured Data ETL Pipelines Makefile"
	@echo ""
	@echo "Targets:"
	@echo "  env     - Setup .env file"
	@echo "  all     - Run setup and deploy (default)"
	@echo "  setup   - Create .env file template and set up secrets"
	@echo "  deploy  - Deploy all pipeline recipes to Instill Core"
	@echo "  help    - Show this help message"