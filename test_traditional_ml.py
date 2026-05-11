#!/usr/bin/env python3
"""
Test script for Traditional ML Provider
This script tests the TraditionalMLProvider implementation
"""

import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.llm_gateway import TraditionalMLProvider, ModerationResult


async def test_traditional_ml_provider():
    """Test the TraditionalMLProvider with various message types"""
    
    provider = TraditionalMLProvider()
    
    test_cases = [
        ("Hello everyone, how are you today?", "safe"),
        ("You are a stupid idiot", "harassment"),
        ("I hate all people of that race", "hate_speech"),
        ("Call me at 555-123-4567 for more info", "doxxing"),
        ("Visit www.example.com to buy our amazing products! Only $9.99!", "spam_promo"),
        ("I want to kill myself", "self_harm"),
        ("This is a normal message with nothing bad", "safe"),
    ]
    
    print("Testing Traditional ML Provider...")
    print("=" * 50)
    
    for message, expected_category in test_cases:
        try:
            result = await provider.moderate(message, {})
            print(f"Message: {message}")
            print(f"Expected: {expected_category}")
            print(f"Result: {result.category} (score: {result.score:.3f}, action: {result.action})")
            print(f"Rationale: {result.rationale}")
            print("-" * 30)
        except Exception as e:
            print(f"Error testing '{message}': {e}")
            print("-" * 30)
    
    print("Test completed!")


if __name__ == "__main__":
    asyncio.run(test_traditional_ml_provider())
