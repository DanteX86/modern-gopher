# GitHub Labels Configuration

## Issue Type Labels

| Label | Color | Description |
|-------|-------|-------------|
| `bug` | #d73a49 | Something isn't working |
| `enhancement` | #a2eeef | New feature or request |
| `documentation` | #0075ca | Improvements or additions to documentation |
| `question` | #d876e3 | Further information is requested |
| `help wanted` | #008672 | Extra attention is needed |
| `good first issue` | #7057ff | Good for newcomers |

## Priority Labels

| Label | Color | Description |
|-------|-------|-------------|
| `priority: critical` | #b60205 | Critical issue requiring immediate attention |
| `priority: high` | #d93f0b | High priority issue |
| `priority: medium` | #fbca04 | Medium priority issue |
| `priority: low` | #0e8a16 | Low priority issue |

## Component Labels

| Label | Color | Description |
|-------|-------|-------------|
| `component: core` | #1d76db | Core protocol and client functionality |
| `component: browser` | #0052cc | Terminal browser interface |
| `component: cli` | #5319e7 | Command-line interface |
| `component: config` | #f9d0c4 | Configuration system |
| `component: plugins` | #e4e669 | Plugin system and plugins |
| `component: tests` | #c2e0c6 | Testing and test infrastructure |
| `component: ci/cd` | #bfd4f2 | Continuous integration and deployment |

## Status Labels

| Label | Color | Description |
|-------|-------|-------------|
| `status: blocked` | #e11d21 | Blocked by dependencies or other issues |
| `status: in progress` | #fbca04 | Currently being worked on |
| `status: needs review` | #f7e101 | Waiting for code review |
| `status: needs testing` | #fef2c0 | Needs testing before merge |
| `status: ready` | #0e8a16 | Ready for development |

## Platform Labels

| Label | Color | Description |
|-------|-------|-------------|
| `platform: macOS` | #ededed | Specific to macOS |
| `platform: linux` | #f7931e | Specific to Linux |
| `platform: windows` | #00a8ff | Specific to Windows |
| `platform: cross-platform` | #5cb85c | Affects multiple platforms |

## Size Labels (for effort estimation)

| Label | Color | Description |
|-------|-------|-------------|
| `size: XS` | #e6ffed | Extra small - quick fix |
| `size: S` | #c2e0c6 | Small - few hours of work |
| `size: M` | #fef2c0 | Medium - 1-2 days of work |
| `size: L` | #f7c6c7 | Large - 3-5 days of work |
| `size: XL` | #ffeaa7 | Extra large - 1+ weeks of work |

## Special Labels

| Label | Color | Description |
|-------|-------|-------------|
| `breaking change` | #d73a49 | Introduces breaking changes |
| `security` | #ee0701 | Security-related issue |
| `performance` | #84b6eb | Performance improvement |
| `refactor` | #0366d6 | Code refactoring |
| `duplicate` | #cfd3d7 | This issue or pull request already exists |
| `wontfix` | #ffffff | This will not be worked on |
| `invalid` | #e4e669 | This doesn't seem right |

## Creating Labels in GitHub

```bash
# Install GitHub CLI if needed
# brew install gh

# Authenticate
gh auth login

# Create labels (run from repository root)
gh label create "priority: critical" --color b60205 --description "Critical issue requiring immediate attention"
gh label create "priority: high" --color d93f0b --description "High priority issue"
gh label create "priority: medium" --color fbca04 --description "Medium priority issue"
gh label create "priority: low" --color 0e8a16 --description "Low priority issue"

gh label create "component: core" --color 1d76db --description "Core protocol and client functionality"
gh label create "component: browser" --color 0052cc --description "Terminal browser interface"
gh label create "component: cli" --color 5319e7 --description "Command-line interface"
gh label create "component: config" --color f9d0c4 --description "Configuration system"
gh label create "component: plugins" --color e4e669 --description "Plugin system and plugins"
gh label create "component: tests" --color c2e0c6 --description "Testing and test infrastructure"
gh label create "component: ci/cd" --color bfd4f2 --description "Continuous integration and deployment"

gh label create "status: blocked" --color e11d21 --description "Blocked by dependencies or other issues"
gh label create "status: in progress" --color fbca04 --description "Currently being worked on"
gh label create "status: needs review" --color f7e101 --description "Waiting for code review"
gh label create "status: needs testing" --color fef2c0 --description "Needs testing before merge"
gh label create "status: ready" --color 0e8a16 --description "Ready for development"

gh label create "platform: macOS" --color ededed --description "Specific to macOS"
gh label create "platform: linux" --color f7931e --description "Specific to Linux"
gh label create "platform: windows" --color 00a8ff --description "Specific to Windows"
gh label create "platform: cross-platform" --color 5cb85c --description "Affects multiple platforms"

gh label create "size: XS" --color e6ffed --description "Extra small - quick fix"
gh label create "size: S" --color c2e0c6 --description "Small - few hours of work"
gh label create "size: M" --color fef2c0 --description "Medium - 1-2 days of work"
gh label create "size: L" --color f7c6c7 --description "Large - 3-5 days of work"
gh label create "size: XL" --color ffeaa7 --description "Extra large - 1+ weeks of work"

gh label create "breaking change" --color d73a49 --description "Introduces breaking changes"
gh label create "security" --color ee0701 --description "Security-related issue"
gh label create "performance" --color 84b6eb --description "Performance improvement"
gh label create "refactor" --color 0366d6 --description "Code refactoring"
```

