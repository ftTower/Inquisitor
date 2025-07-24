PYTHON_VENV_CREATE = python3

VENV_DIR = venv

PYTHON = $(VENV_DIR)/bin/python

PIP = $(VENV_DIR)/bin/pip

SCRIPT = ./core/main.py

# --- Targets ---

.PHONY: all run clean clear setup venv install-deps

all: run

clear: ## Clears the terminal screen
	@clear

re : clean run

run: setup clear
	@echo "Running $(SCRIPT)..."
	@# Ensure the script is run with the virtual environment's Python
	$(PYTHON) $(SCRIPT) "10.0.2.12" "08:00:27:13:0b:43" "10.0.2.10" "08:00:27:c1:37:be"
	@echo "Script finished."

clean: ## Removes __pycache__ directories and .pyc files, and the virtual environment
	@echo "Cleaning up build artifacts..."
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	@echo "Cleaning up virtual environment..."
	rm -rf $(VENV_DIR)
	@echo "Cleanup complete."

setup: venv install-deps ## Ensures the virtual environment is ready and dependencies are installed

venv: ## Creates the virtual environment if it doesn't exist
	@sudo apt update && sudo apt install python3-venv python3-dev libpcap-dev -y
	@echo "Checking for virtual environment..."
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "Creating virtual environment at $(VENV_DIR)..."; \
		$(PYTHON_VENV_CREATE) -m venv $(VENV_DIR); \
		echo "Virtual environment created."; \
	else \
		echo "Virtual environment already exists."; \
	fi

install-deps: $(VENV_DIR) ## Installs Python dependencies into the virtual environment
	@echo "Installing/Updating dependencies..."
	$(PIP) install getmac
	$(PIP) install wheel setuptools
	$(PIP) install pcapy-ng

	@echo "Dependencies checked/installed."

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'