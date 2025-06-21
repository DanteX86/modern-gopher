.PHONY: help test test-fast lint coverage clean recommendations install demo keybindings setup check suggestion suggetion debug debug-syntax debug-style debug-security debug-types debug-all debug-summary

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
	@echo "  suggestion      - Get smart suggestions for next steps"
	@echo ""
	@echo "Debug Commands:"
	@echo "  debug           - Comprehensive error analysis (recommended)"
	@echo "  debug-syntax    - Check Python syntax"
	@echo "  debug-style     - Check code style/linting (flake8)"
	@echo "  debug-security  - Check security issues (bandit)"
	@echo "  debug-types     - Check type annotations (mypy)"
	@echo "  debug-all       - Run all debug checks (verbose)"
	@echo "  debug-summary   - Show debugging command summary"

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

# Syntax check
debug-syntax:
	@echo "Running syntax check..."
	@python3 -m py_compile *.py

# Style check
debug-style:
	@echo "Running style and lint check (flake8)..."
	@flake8 .

# Security check
debug-security:
	@echo "Running security check (bandit)..."
	@bandit -r src/ -c .bandit

# Type check
debug-types:
	@echo "Running type check (mypy)..."
	@mypy .

# Enhanced debug target with comprehensive error checking
debug:
	@echo "=== Comprehensive Debug Analysis ==="
	@echo "Running all debugging tools to identify and report errors..."
	@echo ""
	@echo "1. Syntax Check:"
	@python3 -m py_compile *.py 2>/dev/null && echo "   ✅ No syntax errors" || echo "   ❌ Syntax errors found"
	@echo ""
	@echo "2. Style Check (flake8):"
	@flake8 --select=E9,F63,F7,F82 --show-source --statistics . 2>/dev/null && echo "   ✅ No critical style errors" || echo "   ⚠️  Style issues found (see above)"
	@echo ""
	@echo "3. Security Check (bandit):"
	@bandit -f txt src/ -c .bandit 2>/dev/null | grep -E "(High|Medium):" | wc -l | xargs -I {} echo "   Found {} security issues"
	@echo ""
	@echo "4. Test Execution:"
	@pytest --tb=no -q 2>/dev/null && echo "   ✅ All tests passing" || echo "   ❌ Test failures detected"
	@echo ""
	@echo "=== Debug Summary Complete ==="
	@echo "For detailed output, run individual commands:"
	@echo "  make debug-syntax    - Python syntax check"
	@echo "  make debug-style     - Code style analysis"
	@echo "  make debug-security  - Security vulnerability scan"
	@echo "  make debug-types     - Type checking"

# Run all debug checks (verbose)
debug-all: debug-syntax debug-style debug-security debug-types

# Summary of debugging steps
debug-summary:
	@echo "=== Debugging Summary ==="
	@echo "1. Syntax Check: make debug-syntax"
	@echo "2. Style/Lint Check: make debug-style"
	@echo "3. Security Check: make debug-security"
	@echo "4. Type Check: make debug-types"
	@echo "5. Comprehensive Debug: make debug"
	@echo "Combine All: make debug-all"

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

# Smart suggestions based on project state
suggestion:
	@echo "=== Smart Project Suggestions ==="
	@echo "Analyzing current project state..."
	@echo ""
	@# Check git status and suggest next steps
	@if git status --porcelain | grep -q .; then \
		echo "📝 Uncommitted changes detected:"; \
		git status --short; \
		echo "💡 Suggestion: Review and commit changes with 'git add . && git commit -m \"description\"'"; \
	else \
		echo "✅ Working directory is clean"; \
		echo "💡 Suggestion: Good time to start new features or run tests"; \
	fi
	@echo ""
	@# Check test status
	@echo "🧪 Test recommendations:"
	@if [ -f .pytest_cache/README.md ]; then \
		echo "   • Run 'make test-fast' for quick validation"; \
		echo "   • Run 'make test' for comprehensive testing"; \
	else \
		echo "   • Run 'make test' to establish test baseline"; \
	fi
	@echo ""
	@# Check recent activity
	@echo "📈 Recent development:"
	@git log --oneline -3 | sed 's/^/   • /'
	@echo ""
	@# Context-specific suggestions
	@echo "🎯 Context-specific suggestions:"
	@if git branch --show-current | grep -q feature; then \
		echo "   • You're on a feature branch - consider running 'make check' before merging"; \
		echo "   • Test your changes with 'make demo'"; \
		echo "   • Review keybindings with 'make keybindings'"; \
	elif git branch --show-current | grep -q main\|master; then \
		echo "   • You're on main branch - good time to start a new feature"; \
		echo "   • Run 'make check' to verify everything is working"; \
	else \
		echo "   • Current branch: $$(git branch --show-current)"; \
		echo "   • Run 'make check' to verify project health"; \
	fi
	@echo ""
	@echo "🔧 Quick actions:"
	@echo "   • make demo      - Test the browser"
	@echo "   • make check     - Run all checks"
	@echo "   • make test-fast - Quick test validation"
	@echo "   • git status     - Check repository state"

# Alias for common typo
suggetion: suggestion

