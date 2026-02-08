# Agent Specialization Reference

## Overview
Transforms incubation prototypes into production-grade Custom Agents using OpenAI Agents SDK with proper error handling, typing, observability, and deployment readiness.

## Key Capabilities
- Converting MCP tools to @function_tool decorators
- Adding Pydantic input validation
- Implementing structured error handling
- Production prompt engineering
- Agent testing with real scenarios
- Performance optimization

## Prerequisites
- Completed incubation phase with working prototype
- OpenAI Agents SDK installed
- Discovery log and specification documents
- Test suite from incubation

## Related Files
- `src/agent/customer_success_agent.py` - Production agent
- `src/agent/tools.py` - All @function_tool definitions
- `src/agent/prompts.py` - System prompts
- `tests/test_agent.py` - Agent tests

## Constitutional Alignment
- **Principle 2: Agent Maturity Model** - Required specialization phase
- **Principle 9: Test-Driven Reliability** - Production tests required
- **Principle 6: Production-Grade Observability** - Metrics built-in
