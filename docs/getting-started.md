# Getting Started with Revit AI Assistant

## Prerequisites

### Hardware Requirements
- **GPU**: NVIDIA RTX 3060 (12GB) minimum, RTX 4090 (24GB) recommended
- **RAM**: 32GB minimum, 64GB recommended
- **Storage**: 100GB free space for models

### Software Requirements
- Autodesk Revit 2021 or later
- Python 3.9 or later
- CUDA-capable GPU drivers
- Git

### AI Infrastructure
Choose one of the following:
- **LM Studio** (Easiest) - [Download](https://lmstudio.ai/)
- **Ollama** - [Download](https://ollama.ai/)
- **vLLM** (Fastest) - For production use

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/SamuraiBuddha/revit-ai-assistant.git
cd revit-ai-assistant
```

### 2. Create Python Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -e .
```

### 4. Set Up Local Models

#### Using LM Studio:
1. Open LM Studio
2. Search and download these models:
   - `TheBloke/Llama-3.1-8B-Instruct-GGUF` (Q5_K_M)
   - `TheBloke/CodeLlama-13B-Instruct-GGUF` (Q4_K_M)
   - `TheBloke/Mixtral-8x7B-Instruct-v0.1-GGUF` (Q4_K_M)
3. Start the local server (default port: 1234)

#### Using Ollama:
```bash
# Pull required models
ollama pull llama3.1:8b
ollama pull codellama:13b
ollama pull mixtral:8x7b
ollama pull mistral:7b

# Start Ollama
ollama serve
```

### 5. Configure API Keys
Create a `.env` file:
```bash
# For orchestrator (Claude)
ANTHROPIC_API_KEY=your_api_key_here
```

### 6. Build Standards Database
```bash
# Add your standards PDFs to src/knowledge/data/standards/
# Then run:
python scripts/index_standards.py
```

### 7. Install Revit Add-in
```bash
python scripts/build_addin.py
python scripts/deploy.py
```

## First Run

1. Start your local LLM server (LM Studio/Ollama)
2. Open Revit
3. Look for the "AI Assistant" tab in the ribbon
4. Click "AI Orchestrator" to open the main interface

## Testing the Installation

Run the basic examples:
```bash
# Test API Expert
python examples/basic_api_query.py

# Test multi-agent coordination
python examples/multi_agent_coordination.py
```

## Troubleshooting

### Models not loading
- Check if LM Studio/Ollama is running
- Verify model names in `config/default_config.yaml`
- Check available VRAM

### Revit add-in not showing
- Check Revit add-in manager
- Verify installation path
- Check `RevitAIAssistant.addin` file

### Out of memory errors
- Use smaller quantization (Q4_K_M instead of Q5_K_M)
- Run fewer agents simultaneously
- Adjust `gpu_layers` in model config

## Next Steps

- Read [Agent Architecture](agent-architecture.md)
- Configure your [Local LLM Setup](local-llm-setup.md)
- Explore [API Reference](api-reference.md)