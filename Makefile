.PHONY: help test test-fast lint coverage clean recommendations install demo keybindings setup check

# Default target
help:
	@echo "Available targets:"
	@echo "  test          - Run all tests"
	@echo "  test-fast     - Run tests excluding slow ones"
	@echo "  lint          - Run code linting"
	@echo "  coverage      - Show test coverage"
	@echo "  demo          - Run browser demo"
	@echo "  install       - Install dependencies"
	@echo "  setup         - Full development setup"
	@echo "  clean         - Clean build artifacts"
	@echo "  keybindings   - Manage keybindings"
	@echo "  check         - Run comprehensive checks"
	@echo "  recommendations - Show development recommendations"

# Install dependencies
install:
	pip install -r requirements.txt

# Run tests
test:
	python -m pytest tests/ -v

# Run fast tests (excluding slow integration tests)
test-fast:
	python -m pytest tests/ -v --ignore=tests/test_integration.py --ignore=tests/test_cli.py

# Run linting
lint:
	@echo "Running linting checks..."
	@if command -v flake8 >/dev/null 2>&1; then \
		flake8 src/ tests/ --max-line-length=100 --exclude=__pycache__; \
	else \
		echo "flake8 not found, skipping lint check"; \
	fi

# Show test coverage
coverage:
	python show_test_coverage.py

# Run browser demo
demo:
	./demo_browser.py

# Clean build artifacts
clean:
	rm -rf __pycache__/
	rm -rf .pytest_cache/
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -f .coverage

# Full development setup
setup:
	@echo "Setting up development environment..."
	pip install -r requirements.txt
	@echo "Running initial tests..."
	python -m pytest tests/test_keybindings.py -v
	@echo "Setup complete! Run 'make help' to see available commands."

# Manage keybindings
keybindings:
	@echo "=== Keybinding Management ==="
	@echo "Available keybinding commands:"
	@echo "  List all keybindings: python -m modern_gopher.cli keybindings list"
	@echo "  Reset to defaults:   python -m modern_gopher.cli keybindings reset"
	@echo "  Edit config file:    $$EDITOR ~/.config/modern-gopher/keybindings.json"
	@echo ""
	@echo "Current keybindings:"
	@python -m modern_gopher.cli keybindings list

# Comprehensive checks
check:
	@echo "Running comprehensive checks..."
	@echo "1. Running fast tests..."
	@make test-fast
	@echo "2. Running linting..."
	@make lint
	@echo "3. Checking keybinding system..."
	@python -c "from modern_gopher.keybindings import KeyBindingManager; m=KeyBindingManager(); print(f'✅ Keybindings loaded: {len(m.bindings)} bindings')"
	@echo "4. Checking configuration..."
	@python -c "from modern_gopher.config import get_config; c=get_config(); print('✅ Configuration loaded successfully')"
	@echo "All checks passed! ✅"

# Show development recommendations
recommendations:
	@echo "=== Development Recommendations ==="
	@echo "1. Run comprehensive checks: make check"
	@echo "2. Run all tests: make test"
	@echo "3. Run fast tests only: make test-fast"
	@echo "4. Check code quality: make lint"
	@echo "5. Review test coverage: make coverage"
	@echo "6. Try the browser demo: make demo"
	@echo "7. Manage keybindings: make keybindings"
	@echo "8. Check git status: git status"
	@echo "9. Review recent changes: git log --oneline -10"
	@echo "10. Clean up artifacts: make clean"
	@echo "11. Full dev setup: make setup"
	@echo "12. Review docs: docs/KEYBINDINGS.md docs/README.md"

