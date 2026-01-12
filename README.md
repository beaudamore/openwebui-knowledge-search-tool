# OpenWebUI Knowledge Search Tool

Generic, reusable knowledge base search tool for OpenWebUI designed to be copied and configured for different models or purposes with isolated KB access.

**Version:** 2.0.0  
**Author:** Beau D'Amore ([www.damore.ai](https://www.damore.ai))

## Features

- **Multi-Instance Design**: Copy the tool multiple times and configure each independently
- **KB Isolation**: Each tool instance accesses only its designated knowledge bases
- **Multi-KB Support**: Search across multiple knowledge bases simultaneously
- **Hybrid Search**: Combine semantic and keyword search for better results
- **Reranking**: Optional relevance-based reranking of search results
- **Relevance Filtering**: Filter results by minimum relevance threshold
- **Automatic KB Discovery**: List available knowledge bases for configuration
- **Debug Mode**: Detailed search insights and diagnostics

## Installation

### Setup in OpenWebUI

1. Upload `tool/generic_multi_knowledge_search_tool_v2.py` to OpenWebUI
2. **Copy and rename** for each model/purpose:
   - Example: `father_elias_search_tool.py`
   - Example: `hr_knowledge_search_tool.py`
   - Example: `legal_research_tool.py`
3. Edit the tool title in the file header to match
4. Configure the `default_knowledge_base` valve with comma-separated KB names
5. Assign to your specific model

## Usage

### Configuration Examples

#### Example 1: Specialized Theology Model
```
Tool Name: Father Elias Search
default_knowledge_base: "Eastern Orthodox Theology,Church Fathers,Byzantine Spirituality"
Assigned to: Father Elias Model
```

#### Example 2: HR Department Model
```
Tool Name: HR Knowledge Search
default_knowledge_base: "Employee Handbook,HR Policies,Benefits Guide"
Assigned to: HR Assistant Model
```

#### Example 3: Legal Research Model
```
Tool Name: Legal Research Tool
default_knowledge_base: "Contract Templates,Legal Precedents,Compliance Guidelines"
Assigned to: Legal Assistant Model
```

### Key Settings (Valves)

| Setting | Description | Default |
|---------|-------------|---------|
| `default_knowledge_base` | Comma-separated KB names | Empty |
| `max_results` | Max results per KB search | 5 |
| `reranker_results` | Number after reranking (0=disabled) | 0 |
| `relevance_threshold` | Min relevance score (0.0-1.0) | 0.0 |
| `enable_hybrid_search` | Combine semantic + keyword search | False |
| `enable_debug_output` | Show debug info in responses | True |

## Benefits

✅ **Isolation**: Each model only accesses its designated knowledge bases  
✅ **Flexibility**: Different models can have different search settings  
✅ **Scalability**: Add new specialized models easily  
✅ **Clarity**: Tool name indicates purpose  
✅ **Multi-KB Support**: One tool can search multiple related KBs  

## Model Integration

Once configured, the model simply calls:
```python
search_knowledge(query="Your search query here")
```

The tool automatically searches only the configured knowledge bases for that instance.

## Documentation

- [Complete Usage Guide](docs/USAGE_GUIDE.md)
- [Global RAG Template](docs/GLOBAL_RAG_TEMPLATE.txt)

## Notes

- Knowledge base names must **exactly match** what's in OpenWebUI
- Use `list_knowledge_bases()` function to see available KB names
- Each tool instance is independent—changing one doesn't affect others
- Hybrid search requires global OpenWebUI setting to be enabled

## License

MIT License - See individual repository for details

## Author

**Beau D'Amore**  
[www.damore.ai](https://www.damore.ai)
