# MCP to Agents Migration Skill

## Skill Definition

**Name:** mcp-to-agents-migration
**Version:** 1.0.0
**Type:** Agent Development
**Complexity:** Intermediate

## Description

Systematically migrates MCP Server tools from incubation to production @function_tool decorators with proper validation and error handling.

## Migration Pattern

### Before (MCP):
```python
from mcp.server import Server

server = Server("customer-success-fte")

@server.tool("search_knowledge_base")
async def search_kb(query: str) -> str:
    results = simple_search(query)
    return str(results)
```

### After (OpenAI Agents SDK):
```python
from agents import function_tool
from pydantic import BaseModel

class KnowledgeSearchInput(BaseModel):
    query: str
    max_results: int = 5

@function_tool
async def search_knowledge_base(input: KnowledgeSearchInput) -> str:
    """Search product documentation.
    
    Args:
        input: Search parameters
        
    Returns:
        Formatted results
    """
    try:
        results = await production_search(input.query, input.max_results)
        return format_results(results)
    except Exception as e:
        logger.error(f"Search failed: {e}")
        return "Search temporarily unavailable."
```

## Migration Checklist

- [ ] Create Pydantic input model
- [ ] Add @function_tool decorator
- [ ] Implement try/except error handling
- [ ] Replace simple logic with production implementation
- [ ] Add structured logging
- [ ] Write transition tests
- [ ] Document tool usage in docstring

## Related Skills

- **agent-incubation** - Source MCP tools
- **agent-specialization** - Target production agent
