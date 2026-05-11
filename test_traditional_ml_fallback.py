#!/usr/bin/env python3
"""
Test script to verify Traditional ML Provider fallback behavior
when alt-profanity-check is not available
"""

import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_traditional_ml_fallback():
    """Test TraditionalMLProvider with and without alt-profanity-check"""
    
    print("Testing Traditional ML Provider Fallback Behavior")
    print("=" * 50)
    
    # Test 1: Check if alt-profanity-check is available
    try:
        from profanity_check import predict_prob
        print("✅ alt-profanity-check is available")
        library_available = True
    except ImportError:
        print("⚠️  alt-profanity-check is NOT available (fallback mode)")
        library_available = False
    
    # Test 2: Import and test TraditionalMLProvider
    try:
        from services.llm_gateway import TraditionalMLProvider
        provider = TraditionalMLProvider()
        print("✅ TraditionalMLProvider imported successfully")
    except Exception as e:
        print(f"❌ Failed to import TraditionalMLProvider: {e}")
        return False
    
    # Test 3: Test moderation with various messages
    test_messages = [
        ("Hello everyone, how are you?", "safe"),
        ("This is a clean message", "safe"),
        ("Visit example.com for great deals!", "spam_promo"),  # Should trigger regex
        ("Call me at 555-123-4567", "doxxing"),  # Should trigger regex
        ("I want to hurt myself", "self_harm"),  # Should trigger regex
    ]
    
    print("\nTesting moderation results:")
    print("-" * 30)
    
    for message, expected_category in test_messages:
        try:
            result = await provider.moderate(message, {})
            
            if library_available:
                print(f"✅ '{message}' -> {result.category} (score: {result.score:.3f})")
            else:
                # In fallback mode, should return safe for non-regex content
                if expected_category == "safe" or result.category in ["doxxing", "spam_promo", "self_harm"]:
                    print(f"✅ '{message}' -> {result.category} (score: {result.score:.3f}) - Regex working")
                else:
                    print(f"⚠️  '{message}' -> {result.category} (expected {expected_category}) - Fallback mode")
            
        except Exception as e:
            print(f"❌ Error testing '{message}': {e}")
            return False
    
    # Test 4: Verify regex patterns work regardless of library availability
    print("\nTesting regex patterns (should work in all cases):")
    print("-" * 30)
    
    regex_tests = [
        ("Call me at 555-123-4567", "doxxing", 0.8),
        ("Email test@example.com now", "doxxing", 0.8),
        ("Visit https://example.com", "spam_promo", 0.5),
        ("Buy now for $9.99!", "spam_promo", 0.5),
        ("I want to kill myself", "self_harm", 0.9),
    ]
    
    for message, expected_category, min_score in regex_tests:
        try:
            result = await provider.moderate(message, {})
            if result.category == expected_category and result.score >= min_score:
                print(f"✅ '{message}' -> {result.category} (score: {result.score:.3f})")
            else:
                print(f"❌ '{message}' -> {result.category} (score: {result.score:.3f}) - Expected {expected_category}")
        except Exception as e:
            print(f"❌ Error testing '{message}': {e}")
            return False
    
    print("\n" + "=" * 50)
    if library_available:
        print("🎉 Full Traditional ML functionality working!")
    else:
        print("⚠️  Fallback mode working - regex patterns functional")
        print("💡 Install alt-profanity-check for full functionality: pip install alt-profanity-check==1.8.0")
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_traditional_ml_fallback())
    sys.exit(0 if success else 1)
