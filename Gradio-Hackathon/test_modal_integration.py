#!/usr/bin/env python3
"""
Test Modal Integration - Minimal Credit Burn
Test the 14-strand hair braid before deploying to HuggingFace
"""

import os
import sys
from typing import Dict, Any

# Add the path to our modal client
sys.path.append('/Users/cooper/Desktop/AI_ML/hackathon/UADO')

def test_modal_import():
    """Test if we can import our Modal client"""
    print("🧪 Testing Modal client import...")
    try:
        from modal_llm_client import ModalLLMClient, SimpleAgent, create_meta_workflow_creator
        print("✅ Modal client imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Modal client import failed: {e}")
        return False

def test_modal_basic(modal_token: str):
    """Test basic Modal functionality with minimal credit burn"""
    print("🔥 Testing basic Modal functionality (minimal credit burn)...")
    
    try:
        from modal_llm_client import ModalLLMClient
        
        # Initialize client
        client = ModalLLMClient(modal_token)
        
        if not client.deployed:
            print("❌ Modal app not deployed")
            return False
        
        # Test with minimal prompt to burn minimal credits
        test_prompt = "Say hello in 5 words or less."
        result = client.run_inference(test_prompt, "claude-3-5-sonnet-20241022")
        
        print(f"💸 Credits burned! Result: {result}")
        return True
        
    except Exception as e:
        print(f"❌ Modal test failed: {e}")
        return False

def test_simple_agent(modal_token: str):
    """Test SimpleAgent with minimal credit burn"""
    print("🤖 Testing SimpleAgent (more credit burn)...")
    
    try:
        from modal_llm_client import ModalLLMClient, SimpleAgent
        
        client = ModalLLMClient(modal_token)
        agent = SimpleAgent(client)
        
        # Minimal test task
        test_task = "List 3 benefits of AI in one sentence each."
        
        print("💸 Testing direct execution...")
        direct_result = agent.execute_direct(test_task)
        print(f"Direct result: {direct_result}")
        
        print("💸 Testing MCO execution...")
        mco_context = {
            "goal": "Create concise, structured output",
            "success_criteria": ["Clear structure", "Factual accuracy"],
            "progressive_revelation": True
        }
        mco_result = agent.execute_with_mco(test_task, mco_context)
        print(f"MCO result: {mco_result}")
        
        return direct_result.get('success', False) and mco_result.get('success', False)
        
    except Exception as e:
        print(f"❌ SimpleAgent test failed: {e}")
        return False

def test_meta_workflow():
    """Test meta workflow creator (no credits burned)"""
    print("🎭 Testing meta workflow creator...")
    
    try:
        from modal_llm_client import create_meta_workflow_creator
        
        workflow_files = create_meta_workflow_creator()
        
        required_files = ['mco.core', 'mco.sc', 'mco.features', 'mco.styles']
        for file_name in required_files:
            if file_name not in workflow_files:
                print(f"❌ Missing {file_name}")
                return False
            if len(workflow_files[file_name]) < 100:  # Basic length check
                print(f"❌ {file_name} seems too short")
                return False
        
        print("✅ Meta workflow creator working")
        return True
        
    except Exception as e:
        print(f"❌ Meta workflow test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing the 14-strand hair braid monstrosity...")
    print("=" * 50)
    
    # Test 1: Import
    if not test_modal_import():
        print("💀 Import test failed - can't proceed")
        return
    
    # Test 2: Meta workflow (no credits)
    if not test_meta_workflow():
        print("💀 Meta workflow test failed")
        return
    
    # Check for Modal token in environment (try both MODAL_TOKEN and MODAL_KEY)
    modal_token = os.getenv('MODAL_TOKEN') or os.getenv('MODAL_KEY')
    if not modal_token:
        print("⏭️  No MODAL_TOKEN env var - skipping credit tests")
        print("✅ Basic tests passed - ready for HuggingFace deployment")
        return
    
    # Test 3: Basic Modal (minimal credits)
    print("\n💸 ABOUT TO BURN MINIMAL CREDITS...")
    if not test_modal_basic(modal_token):
        print("💀 Basic Modal test failed")
        return
    
    # Test 4: SimpleAgent (more credits)
    print("\n💸💸 ABOUT TO BURN MORE CREDITS...")
    if not test_simple_agent(modal_token):
        print("💀 SimpleAgent test failed")
        return
    
    print("\n🎉 ALL TESTS PASSED!")
    print("🚀 The 14-strand monstrosity is ready for HuggingFace!")
    print("🔥 Time to deploy and pray to Jesus it works in production!")

if __name__ == "__main__":
    main()