#!/usr/bin/env python
"""Download and setup local models for Revit AI Assistant"""

import os
import sys
import yaml
import subprocess
from pathlib import Path
import argparse

def load_config():
    """Load model configuration"""
    config_path = Path("config/model_endpoints.yaml")
    if not config_path.exists():
        print(f"Error: {config_path} not found")
        sys.exit(1)
        
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def setup_ollama_models(config):
    """Pull models using Ollama"""
    print("\n=== Setting up Ollama models ===")
    models = config.get('ollama', {}).get('models', [])
    
    for model in models:
        print(f"\nPulling {model}...")
        try:
            subprocess.run(['ollama', 'pull', model], check=True)
            print(f"✓ Successfully pulled {model}")
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to pull {model}: {e}")
        except FileNotFoundError:
            print("✗ Ollama not found. Please install from https://ollama.ai/")
            return

def check_lm_studio():
    """Check if LM Studio is available"""
    print("\n=== LM Studio Setup ===")
    print("Please ensure LM Studio is installed and running.")
    print("\nRecommended models to download in LM Studio:")
    
    config = load_config()
    lm_models = config.get('lm_studio', {}).get('models', [])
    
    for model in lm_models:
        print(f"  - {model['file']} ({model['name']})")
    
    print("\nDownload these from the LM Studio model browser.")
    print("Default endpoint: http://localhost:1234")

def setup_directories():
    """Create necessary directories"""
    print("\n=== Creating directories ===")
    
    dirs = [
        "logs",
        "chroma_db",
        "models",
        "src/knowledge/data/standards/ASHRAE",
        "src/knowledge/data/standards/BICSI", 
        "src/knowledge/data/standards/ASME",
        "src/knowledge/data/api_docs"
    ]
    
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"✓ Created {dir_path}")

def download_embeddings_model():
    """Download sentence transformers model"""
    print("\n=== Downloading embeddings model ===")
    try:
        from sentence_transformers import SentenceTransformer
        print("Downloading all-MiniLM-L6-v2...")
        model = SentenceTransformer('all-MiniLM-L6-v2')
        print("✓ Embeddings model ready")
    except ImportError:
        print("✗ sentence-transformers not installed")
        print("  Run: pip install sentence-transformers")

def main():
    parser = argparse.ArgumentParser(description="Setup models for Revit AI Assistant")
    parser.add_argument('--ollama', action='store_true', help='Setup Ollama models')
    parser.add_argument('--lm-studio', action='store_true', help='Show LM Studio setup')
    parser.add_argument('--all', action='store_true', help='Run all setup steps')
    
    args = parser.parse_args()
    
    if not any(vars(args).values()):
        args.all = True
    
    print("Revit AI Assistant - Model Setup")
    print("=" * 50)
    
    # Always create directories
    setup_directories()
    
    # Load configuration
    config = load_config()
    
    if args.all or args.ollama:
        setup_ollama_models(config)
    
    if args.all or args.lm_studio:
        check_lm_studio()
    
    if args.all:
        download_embeddings_model()
    
    print("\n=== Setup Summary ===")
    print("1. Directories created")
    print("2. Model configuration loaded")
    print("3. Next steps:")
    print("   - Add standards PDFs to src/knowledge/data/standards/")
    print("   - Run: python scripts/index_standards.py")
    print("   - Configure .env with ANTHROPIC_API_KEY")
    print("\nReady to start the assistant!")

if __name__ == "__main__":
    main()
