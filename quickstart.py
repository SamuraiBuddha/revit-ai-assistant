#!/usr/bin/env python
"""Quick start script for Revit AI Assistant"""

import asyncio
import os
from pathlib import Path
from src.utils import AgentRegistry
from src.schemas import RevitContext

print("""
╔═══════════════════════════════════════════════════════╗
║          Revit AI Assistant - Quick Start             ║
║                                                       ║
║  Multi-agent system for Autodesk Revit               ║
║  Using local LLMs for privacy-focused automation     ║
╚═══════════════════════════════════════════════════════╝
""")

async def check_setup():
    """Check if everything is set up correctly"""
    issues = []
    
    # Check for .env file
    if not Path(".env").exists():
        issues.append("⚠️  .env file not found - create it with ANTHROPIC_API_KEY")
    
    # Check for config
    if not Path("config/default_config.yaml").exists():
        issues.append("⚠️  Configuration file missing")
    
    # Check for LM Studio/Ollama
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            try:
                await client.get("http://localhost:1234/health", timeout=2.0)
                print("✅ LM Studio detected on port 1234")
            except:
                try:
                    await client.get("http://localhost:11434/api/tags", timeout=2.0)
                    print("✅ Ollama detected on port 11434")
                except:
                    issues.append("⚠️  No local LLM server detected (LM Studio/Ollama)")
    except:
        pass
    
    if issues:
        print("\n🔧 Setup Issues Found:")
        for issue in issues:
            print(f"   {issue}")
        print("\nRun: python scripts/install_models.py")
        return False
    
    return True

async def interactive_demo():
    """Run an interactive demo"""
    print("\n🚀 Starting Interactive Demo\n")
    
    # Initialize registry
    print("Loading agents...")
    registry = AgentRegistry()
    await registry.initialize_agents()
    
    agents = registry.list_agents()
    print(f"\n✅ Loaded {len(agents)} agents: {', '.join(agents)}")
    
    # Create mock context
    context = RevitContext(
        project_path="demo_project.rvt",
        project_name="Demo Project",
        active_view_id="view_123",
        active_phase_id=None,
        selected_element_ids=[],
        user_preferences={},
        standards_db=None,
        api_docs_index=None,
        revit_api=None
    )
    
    print("\n📋 Available Agents:")
    print("1. API Expert - Generate Revit API code")
    print("2. Dynamo Agent - Create visual programming scripts")
    print("3. Standards Agent - Check compliance with ASHRAE/BICSI/ASME")
    print("4. Orchestrator - Coordinate complex multi-agent tasks")
    
    while True:
        print("\n" + "="*50)
        agent_num = input("\nSelect agent (1-4) or 'q' to quit: ").strip()
        
        if agent_num.lower() == 'q':
            break
            
        agent_map = {
            '1': 'api_expert',
            '2': 'dynamo_agent',
            '3': 'standards_agent',
            '4': 'orchestrator'
        }
        
        agent_name = agent_map.get(agent_num)
        if not agent_name:
            print("Invalid selection")
            continue
            
        agent = registry.get_agent(agent_name)
        if not agent:
            print(f"{agent_name} not available")
            continue
            
        query = input(f"\nEnter your query for {agent_name}: ").strip()
        if not query:
            continue
            
        print(f"\n🤔 Processing with {agent_name}...")
        
        try:
            result = await agent.process(query, context)
            
            print(f"\n✅ Result from {agent_name}:")
            print("-" * 40)
            
            # Display result based on type
            if hasattr(result, 'code_snippet'):
                print(f"Code:\n{result.code_snippet}")
            elif hasattr(result, 'tasks'):
                print(f"Orchestration Plan:")
                for task in result.tasks:
                    print(f"  - {task.agent_name}: {task.task_description}")
            elif hasattr(result, 'nodes'):
                print(f"Dynamo Script: {result.script_name}")
                print(f"Nodes: {len(result.nodes)}")
            elif hasattr(result, 'compliant'):
                print(f"Compliance: {'✅ PASS' if result.compliant else '❌ FAIL'}")
                print(f"Summary: {result.summary}")
            else:
                print(result)
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    await registry.shutdown()
    print("\n👋 Thanks for trying Revit AI Assistant!")

async def main():
    """Main entry point"""
    
    # Check setup
    print("🔍 Checking setup...")
    if not await check_setup():
        print("\n❌ Please complete setup before running the demo")
        return
    
    print("\n✅ Setup looks good!")
    
    # Run demo
    await interactive_demo()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
