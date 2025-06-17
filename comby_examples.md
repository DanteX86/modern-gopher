# Comby Examples and Reference

Comby is a powerful tool for structural code search and replace across multiple programming languages.

## Basic Usage

```bash
# Basic syntax
comby 'MATCH_TEMPLATE' 'REWRITE_TEMPLATE' [FILES]

# Show matches only
comby 'pattern' '' file.py -match-only

# Show diff without applying changes
comby 'old_name' 'new_name' file.py -diff

# Apply changes in place
comby 'old_name' 'new_name' file.py -in-place

# Work on all files in directory
comby 'pattern' 'replacement' -directory .
```

## Pattern Matching with Holes

Comby uses `:[hole]` syntax to match code structures:

```bash
# Match any function call
comby 'function_name(:[args])' 'new_function_name(:[args])' *.py

# Match any assignment
comby ':[var] = :[value]' ':[var] = validate(:[value])' *.py

# Match if statements
comby 'if :[condition]: :[body]' 'if :[condition]:\n    log("condition met")\n:[body]' *.py
```

## Common Examples

### 1. Rename functions across files
```bash
comby 'old_function(:[args])' 'new_function(:[args])' -directory . -extensions .py
```

### 2. Add logging to function calls
```bash
comby 'api_call(:[args])' 'log("calling api"); api_call(:[args])' *.py
```

### 3. Update import statements
```bash
comby 'from old_module import :[items]' 'from new_module import :[items]' *.py
```

### 4. Refactor class methods
```bash
comby 'def :[method](self, :[args]): :[body]' 'def :[method](self, :[args]):\n    self._validate()\n:[body]' *.py
```

### 5. Update configuration patterns
```bash
comby 'config[":[key]"]' 'get_config(":[key]")' *.py
```

## Language-Specific Matchers

```bash
# Force Python matcher
comby 'pattern' 'replacement' file.txt -matcher .py

# JavaScript
comby 'console.log(:[msg])' 'logger.info(:[msg])' *.js

# Go
comby 'fmt.Println(:[args])' 'log.Printf(:[args])' *.go

# C/C++
comby 'printf(:[args])' 'fprintf(stderr, :[args])' *.c
```

## Useful Flags

- `-match-only` or `-o`: Only show matches, don't rewrite
- `-diff`: Show diff without applying changes
- `-in-place`: Apply changes directly to files
- `-count`: Show count of matches per file
- `-extensions .py,.js` or `-e .py,.js`: Specify file extensions
- `-exclude node_modules,build`: Exclude directories
- `-jobs 8`: Set number of parallel jobs
- `-review` or `-r`: Interactive review mode

## Advanced Patterns

### Multiple hole matching
```bash
# Match try-catch blocks
comby 'try: :[try_body] except :[exception]: :[except_body]' \
      'try:\n:[try_body]\nexcept :[exception] as e:\n    log_error(e)\n:[except_body]' *.py
```

### Conditional matching with rules
```bash
# Only match functions with specific names
comby -rule 'where :[name] == "deprecated_func"' \
      'def :[name](:[args]): :[body]' \
      'def new_func(:[args]): :[body]' *.py
```

### JSON/YAML transformations
```bash
# Update JSON configuration
comby '"old_key": :[value]' '"new_key": :[value]' config.json

# YAML transformations
comby 'old_setting: :[value]' 'new_setting: :[value]' *.yml
```

## Tips and Best Practices

1. **Test first**: Always use `-match-only` or `-diff` before applying changes
2. **Use version control**: Commit your code before running comby transformations
3. **Start specific**: Begin with specific patterns and gradually generalize
4. **Review changes**: Use `-review` for interactive approval of changes
5. **Backup important files**: Large refactoring should be done with backups

## Integration with Version Control

```bash
# Create a branch for refactoring
git checkout -b refactor-function-names

# Apply comby transformation
comby 'old_pattern' 'new_pattern' -directory . -extensions .py -in-place

# Review changes
git diff

# Commit if satisfied
git add -A && git commit -m "Refactor: rename functions using comby"
```

## Supported Languages

Comby supports many languages including:
- Python, JavaScript, TypeScript
- Go, Rust, C, C++
- Java, Scala, Kotlin
- HTML, CSS, JSON, YAML
- And many more...

Check supported languages: `comby -list`

