# Generic Knowledge Search Tool - Usage Guide

## Purpose
This is a **generic, reusable tool** designed to be copied multiple times and configured individually for different models or purposes in OpenWebUI.

## How It Works

### Workflow
1. **Copy** the `generic_knowledge_search_tool.py` file
2. **Rename** it to match your purpose (e.g., `father_elias_search_tool.py`, `saint_augustine_search_tool.py`, `hr_search_tool.py`)
3. **Edit the title** in the file header to match (e.g., "Father Elias Search", "Saint Augustine Search")
4. **Upload** to OpenWebUI as a new tool
5. **Configure** the tool's `default_knowledge_base` setting with a comma-separated list of KB names
6. **Assign** to your specific model

## Configuration Examples

### Example 1: Father Elias Model
```
Tool Name: Father Elias Search
default_knowledge_base: "Eastern Orthodox Theology,Church Fathers,Byzantine Spirituality"
```

### Example 2: Saint Augustine Model
```
Tool Name: Saint Augustine Search
default_knowledge_base: "Nicene Fathers,Confessions"
```

### Example 3: HR Model
```
Tool Name: HR Knowledge Search
default_knowledge_base: "Employee Handbook"
```

### Example 4: Legal Model
```
Tool Name: Legal Research Tool
default_knowledge_base: "Contract Templates,Legal Precedents,Compliance Guidelines"
```

## Key Settings Explained

| Setting | Description | Example |
|---------|-------------|---------|
| `default_knowledge_base` | Comma-separated KB names this tool can access | `"KB1,KB2,KB3"` |
| `max_results` | Max results per KB search | `5` (default) |
| `reranker_results` | Number after reranking (0=disabled) | `0` (default) |
| `relevance_threshold` | Min relevance score (0.0-1.0) | `0.0` (default) |
| `enable_hybrid_search` | Combine semantic + keyword search | `false` (default) |
| `enable_debug_output` | Show debug info in responses | `true` (default) |

## Benefits of This Approach

✅ **Isolation**: Each model only accesses its designated knowledge bases  
✅ **Flexibility**: Different models can have different search settings  
✅ **Scalability**: Add new specialized models easily  
✅ **Clarity**: Tool name indicates purpose (e.g., "Father Elias Search")  
✅ **Multi-KB Support**: One tool can search multiple related KBs  

## How Models Use It

Once configured, the model simply calls:
```
search_knowledge(query="What did Augustine say about grace?")
```

The tool automatically searches only the KBs you configured for that instance.

## Notes

- Knowledge base names must **exactly match** what's in OpenWebUI
- Use `list_knowledge_bases()` function to see available KB names
- Comma separation supports multiple KBs: `"KB One,KB Two,KB Three"`
- Each tool instance is independent—changing one doesn't affect others
