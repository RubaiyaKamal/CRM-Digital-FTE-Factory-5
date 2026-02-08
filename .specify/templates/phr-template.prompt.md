---
id: {{ID}}
title: "{{TITLE}}"
stage: {{STAGE}}
date: {{DATE_ISO}}
surface: agent
model: {{MODEL}}
feature: {{FEATURE}}
branch: {{BRANCH}}
user: {{USER}}
command: {{COMMAND}}
labels: {{LABELS_YAML}}
links:
  spec: {{SPEC_LINK}}
  ticket: {{TICKET_LINK}}
  adr: {{ADR_LINK}}
  pr: {{PR_LINK}}
files_changed: {{FILES_YAML}}
tests: {{TESTS_YAML}}
---

# Prompt History Record: {{TITLE}}

## Context

**Stage:** {{STAGE}}
**Feature:** {{FEATURE}}
**Date:** {{DATE_ISO}}
**Surface:** agent (Claude Code)

## User Input

```
{{PROMPT_TEXT}}
```

## Assistant Response

{{RESPONSE_TEXT}}

## Outcome

{{OUTCOME}}

## Follow-up Actions

{{FOLLOW_UP}}

## Evaluation

- **Clarity:** {{CLARITY_SCORE}}/5
- **Completeness:** {{COMPLETENESS_SCORE}}/5
- **Alignment:** {{ALIGNMENT_SCORE}}/5

## Notes

{{NOTES}}
