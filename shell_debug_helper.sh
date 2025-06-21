#!/bin/bash
# Shell Debug Helper for Modern Gopher
# Helps prevent common shell parsing errors and provides useful debugging commands

set -euo pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

echo_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

echo_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

echo_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Function to safely test commands
safe_test() {
    if [ $# -eq 0 ]; then
        echo_error "safe_test requires arguments"
        echo_info "Usage: safe_test [condition]"
        echo_info "Example: safe_test -f file.txt"
        echo_info "Example: safe_test \"\$var\" = \"value\""
        return 1
    fi
    
    # Parse arguments and stop at comments
    local test_args=()
    for arg in "$@"; do
        # Stop processing arguments if we encounter a comment
        if [[ $arg == \#* ]]; then
            break
        fi
        test_args+=("$arg")
    done
    
    # Display what we're testing (without comments)
    local display_args="${test_args[*]}"
    
    if test "${test_args[@]}"; then
        echo_success "Test passed: $display_args"
        return 0
    else
        echo_warning "Test failed: $display_args"
        return 1
    fi
}

# Function to check shell syntax
check_shell_syntax() {
    local file="$1"
    
    if [ ! -f "$file" ]; then
        echo_error "File not found: $file"
        return 1
    fi
    
    echo_info "Checking shell syntax for: $file"
    
    # Determine shell type
    local shebang=$(head -n1 "$file")
    local shell_cmd="bash"
    
    if [[ $shebang == *"zsh"* ]]; then
        shell_cmd="zsh"
    elif [[ $shebang == *"bash"* ]]; then
        shell_cmd="bash"
    elif [[ $shebang == *"sh"* ]]; then
        shell_cmd="sh"
    fi
    
    echo_info "Detected shell: $shell_cmd"
    
    if $shell_cmd -n "$file"; then
        echo_success "Syntax check passed for $file"
        return 0
    else
        echo_error "Syntax check failed for $file"
        return 1
    fi
}

# Function to provide common zsh/bash command help
show_command_help() {
    echo_info "Common Shell Commands Help"
    echo ""
    echo "Testing Commands:"
    echo "  test -f file.txt        # Check if file exists"
    echo "  test -d directory       # Check if directory exists"
    echo "  test \"\$var\" = \"value\"   # Compare strings"
    echo "  test \"\$num\" -eq 42      # Compare numbers"
    echo ""
    echo "Avoid These Common Errors:"
    echo "  ❌ test so far          # Invalid - not a proper condition"
    echo "  ✅ test -f file.txt     # Valid - checks file existence"
    echo "  ❌ [ incomplete         # Invalid - missing closing bracket"
    echo "  ✅ [ -f file.txt ]      # Valid - alternative test syntax"
    echo ""
    echo "Project Specific Commands:"
    echo "  make test               # Run project tests"
    echo "  make check              # Run all checks"
    echo "  make demo               # Demo the browser"
    echo "  ./run_browser.sh        # Run browser directly"
}

# Main function
main() {
    case "${1:-help}" in
        "test")
            shift
            safe_test "$@"
            ;;
        "check")
            if [ $# -lt 2 ]; then
                echo_error "check requires a filename"
                echo_info "Usage: $0 check script.sh"
                exit 1
            fi
            check_shell_syntax "$2"
            ;;
        "help"|"--help"|"-h")
            echo_info "Shell Debug Helper for Modern Gopher"
            echo ""
            echo "Usage: $0 [command] [arguments]"
            echo ""
            echo "Commands:"
            echo "  test [condition]    # Safely test a condition"
            echo "  check [file]        # Check shell script syntax"
            echo "  help               # Show this help and command guide"
            echo ""
            show_command_help
            ;;
        *)
            echo_error "Unknown command: $1"
            echo_info "Run '$0 help' for usage information"
            exit 1
            ;;
    esac
}

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi

