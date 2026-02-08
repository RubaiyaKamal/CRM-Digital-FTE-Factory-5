# Agent Incubation Reference

## Overview
This skill guides the incubation phase of agent development using Claude Code - the exploration and prototyping stage where requirements are discovered and the agent's capabilities are defined.

## Key Capabilities
- Problem space exploration
- Edge case discovery
- MCP server development
- Agent skill definition
- Prompt engineering and testing
- Discovery log documentation

## Prerequisites
- Claude Code CLI installed
- Sample customer data for testing
- Product documentation for knowledge base
- Clear business problem statement

## Related Files
- `specs/discovery-log.md` - Incubation findings
- `specs/<feature>/spec.md` - Crystallized specification
- `prototype/` - Incubation code (not production)
- `mcp_server.py` - MCP tool definitions

## Key Principles
- Iterate rapidly, don't over-engineer
- Document every edge case discovered
- Test with real-world scenarios
- Capture working prompts for production
- Focus on discovering requirements, not perfection

## Constitutional Alignment
- **Principle 2: Agent Maturity Model** - Required incubation phase
- **Principle 10: Spec-Driven Development** - Discovery log required
- **Principle 9: Test-Driven Reliability** - Edge cases become tests
