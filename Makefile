.PHONY: help test lint coverage clean recommendations install demo

# Default target
help:
	@echo "Available targets:"
	@echo "  test          - Run all tests"
	@echo "  lint          - Run code linting"
	@echo "  coverage      - Show test coverage"
	@echo "  demo          - Run browser demo"
	@echo "  install       - Install dependencies"
	@echo "  clean         - Clean build artifacts"
	@echo "  recommendations - Show development recommendations"

# Install dependencies
install:
	pip install -r requirements.txt

# Run tests
test:
	python run_tests.py

# Run linting
lint:
	pylint *.py

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

# Show development recommendations
recommendations:
	@echo "=== Development Recommendations ==="
	@echo "1. Run tests: make test"
	@echo "2. Check code quality: make lint"
	@echo "3. Review test coverage: make coverage"
	@echo "4. Try the demo: make demo"
	@echo "5. Check git status: git status"
	@echo "6. Review recent changes: git log --oneline -10"
	@echo "7. Update dependencies if needed: make install"
	@echo "8. Review implementation docs in *.md files"
	@echo "9. Clean up build artifacts: make clean"
	@echo "10. Consider running specific feature demos:"
	@echo "    - python demo_search_functionality.py"
	@echo "    - python demo_url_input.py"

