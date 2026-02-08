# No Emoji In Code Skill

## Skill Definition

**Name:** no-emoji-code
**Version:** 1.0.0
**Type:** Code Quality
**Complexity:** Simple

## Problem

Emoji characters in source code cause issues:
- `SyntaxError` on systems with ASCII-only terminals
- Encoding errors when files are read by tools expecting pure UTF-8 without BOM
- CI/CD pipeline failures on some Linux environments
- Confusing diffs in version control

## Rule

**NEVER place emoji characters in any source code file.**

This applies to:
- Python (`.py`) — string literals, comments, log messages, print statements
- TypeScript/JavaScript (`.ts`, `.tsx`, `.js`, `.jsx`) — same
- SQL (`.sql`) — comments, string literals
- YAML/Docker/Kubernetes files
- Shell scripts
- Configuration files (`.toml`, `.ini`, `.cfg`, `.json`)

## Allowed Alternatives

Instead of emojis in code, use:

### Python logging
```python
# WRONG
logger.info("Agent initialized - OK")

# RIGHT
logger.info("Agent initialized: ready")
logger.info("[OK] Agent initialized")
```

### Python print statements
```python
# WRONG
print("Starting services...")

# RIGHT
print("[STARTING] Services initializing...")
print("Starting services...")
```

### String messages
```python
# WRONG
return "Agent initialized successfully!"

# RIGHT
return "Agent initialized successfully"
```

### TypeScript/React UI
```tsx
// WRONG - emoji in code
const label = "Support";

// RIGHT - use text or reference a constant
const label = "CloudFlow Support";

// For UI icons, use SVG components or icon libraries, NOT emoji literals
// import { CloudIcon } from './icons'
```

## Linting Setup

Add to `.pre-commit-config.yaml`:
```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    hooks:
      - id: check-byte-order-marker
  - repo: local
    hooks:
      - id: no-emoji
        name: No emoji in source files
        entry: python -c "
import sys, re
pattern = re.compile(
    '['
    '\U0001F600-\U0001F64F'
    '\U0001F300-\U0001F5FF'
    '\U0001F680-\U0001F6FF'
    '\U0001F1E0-\U0001F1FF'
    '\U00002600-\U000026FF'
    '\U00002700-\U000027BF'
    '\U0001F900-\U0001F9FF'
    '\U0001FA00-\U0001FA6F'
    '\U0001FA70-\U0001FAFF'
    ']+')
for f in sys.argv[1:]:
    with open(f, encoding='utf-8', errors='ignore') as fh:
        for i, line in enumerate(fh, 1):
            if pattern.search(line):
                print(f'{f}:{i}: emoji found')
                sys.exit(1)
"
        language: python
        types: [python, ts, tsx, javascript, sql, yaml]
```

## Code Review Checklist

When reviewing or writing code:
- [ ] No emoji in string literals
- [ ] No emoji in comments
- [ ] No emoji in log/print statements
- [ ] No emoji in variable/function names
- [ ] Log prefixes use `[OK]`, `[ERROR]`, `[WARN]`, `[INFO]` instead of emoji

## Application to This Project

Files with emoji that need fixing (if any):
- Check with: `grep -r "[^\x00-\x7F]" src/ --include="*.py"`
- Auto-fix: replace emoji with text equivalents
