# No Emoji In Code Skill

## Quick Reference

**Name:** no-emoji-code
**Purpose:** Prevent emojis in all source code files (Python, TypeScript, SQL, YAML, etc.)
**Why:** Emoji characters in source files cause encoding errors on some systems and terminals

## When to Apply
- All Python source files (.py)
- All TypeScript/JavaScript files (.ts, .tsx, .js, .jsx)
- All SQL files (.sql)
- All YAML/Docker/Kubernetes files
- All configuration files

## Key Rule
NEVER use emoji characters in:
- String literals inside code
- Comments
- Log messages
- Variable names
- Class/function names

Emojis are ONLY acceptable in:
- Markdown documentation files (.md) when explicitly requested
- User-facing web UI text content rendered from separate data files

## See Also
SKILL.md for full details and linting setup.
