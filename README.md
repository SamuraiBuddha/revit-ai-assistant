# Revit AI Assistant

A multi-agent AI system for Autodesk Revit that combines local LLMs with cloud orchestration for privacy-conscious architectural automation.

## 🚀 Features

- **11 Specialized Agents**: Each handling specific Revit domains
- **Privacy-First**: All project data processed locally (except orchestration)
- **Smart Orchestration**: Claude 3 Opus coordinates complex multi-step tasks
- **Standards Compliance**: RAG-powered ASHRAE/BICSI/ASME checking
- **Native Revit UI**: Custom ribbon interface for seamless integration
- **High Performance**: Optimized for architectural workflows

## 🤖 Agent Architecture

| Agent | Purpose | Recommended Model | VRAM |
|-------|---------|-------------------|------|
| **Orchestrator** | Task coordination | Claude 3 Opus (Cloud) | N/A |
| **API Expert** | Revit API code generation | CodeLlama 13B | ~10GB |
| **Dynamo Agent** | Visual programming scripts | StarCoder2 15B | ~12GB |
| **Temporal Chief** | Phase management | Llama 3.1 8B | ~6GB |
| **Visibility Graphics** | View troubleshooting | Mistral 7B | ~5GB |
| **Export Manager** | File format handling | CodeLlama 7B | ~5GB |
| **Import Manager** | Data ingestion | CodeLlama 7B | ~5GB |
| **Family Builder** | System families | DeepSeek Coder 6.7B | ~5GB |
| **Component Modeler** | .RFA creation | Llama 3.1 8B | ~6GB |
| **Coordinate Manager** | Survey/project coords | Phi-3 14B | ~10GB |
| **Standards Agent** | Code compliance | Mixtral 8x7B MoE | ~24GB |

## 🛠️ Technology Stack

- **Framework**: PydanticAI (type-safe agent framework)
- **Local LLMs**: LM Studio, Ollama, or vLLM
- **Vector DB**: ChromaDB for standards RAG
- **Languages**: Python (agents) + C# (Revit add-in)
- **Protocol**: MCP for agent communication

## 📋 Prerequisites

- Autodesk Revit 2021+
- Python 3.9+
- NVIDIA GPU with 24GB+ VRAM (RTX 4090 recommended)
- 64GB+ System RAM
- LM Studio or Ollama installed

## 🚀 Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/SamuraiBuddha/revit-ai-assistant.git
   cd revit-ai-assistant
   ```

2. **Install Python dependencies**
   ```bash
   pip install -e .
   ```

3. **Download and configure local models**
   ```bash
   python scripts/install_models.py
   ```

4. **Build standards RAG database**
   ```bash
   python scripts/index_standards.py
   ```

5. **Build and install Revit add-in**
   ```bash
   python scripts/build_addin.py
   python scripts/deploy.py
   ```

## 📁 Project Structure

```
revit-ai-assistant/
├── src/
│   ├── agents/           # PydanticAI agent implementations
│   ├── models/           # Local LLM configurations
│   ├── knowledge/        # Standards RAG and API docs
│   ├── RevitAIAssistant/ # C# Revit add-in
│   └── server/           # MCP protocol server
├── scripts/              # Setup and deployment
├── config/               # Configuration files
└── examples/             # Usage examples
```

## 💡 Usage Examples

### Simple API Query
```python
# Ask the API Expert
result = await api_expert.run(
    "How do I get all doors on the current level?",
    deps=revit_context
)
print(result.code_snippet)  # Complete C# code with error handling
```

### Multi-Agent Coordination
```python
# Orchestrator handles complex tasks
result = await orchestrator.run(
    "Prepare Level 3 for MEP coordination meeting",
    deps=revit_context
)
# Automatically delegates to multiple agents
```

### Standards Compliance Check
```python
# Check ASHRAE compliance
result = await standards_agent.run(
    "Verify HVAC ductwork sizing meets ASHRAE 90.1",
    deps=revit_context
)
```

## 🔐 Privacy & Security

- **Local Processing**: All Revit project data stays on your machine
- **No Cloud Storage**: Models run locally, no external API calls (except orchestrator)
- **Audit Logging**: All agent actions logged locally
- **Configurable**: Choose which agents to enable

## 🤝 Contributing

Contributions welcome! Please read our [Contributing Guide](CONTRIBUTING.md) first.

## 📄 License

MIT License - see [LICENSE](LICENSE) file.

## 🙏 Acknowledgments

- Built on [PydanticAI](https://github.com/pydantic/pydantic-ai) by the Pydantic team
- Inspired by the need for privacy-conscious architectural automation
- Special thanks to the open source LLM community

---

**Note**: This is an active development project. For production use, thoroughly test with your specific workflows.