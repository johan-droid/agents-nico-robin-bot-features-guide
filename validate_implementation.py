#!/usr/bin/env python3
"""
Validation script for Traditional ML implementation
Checks that all components are properly integrated
"""

import sys
import os
import re

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_regex_patterns():
    """Test regex patterns work correctly"""
    print("Testing regex patterns...")
    
    # Doxxing patterns
    phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    
    assert re.search(phone_pattern, "Call me at 555-123-4567"), "Phone pattern failed"
    assert re.search(email_pattern, "Email me at test@example.com"), "Email pattern failed"
    
    # Spam patterns
    url_pattern = r'https?://[^\s]+'
    assert re.search(url_pattern, "Visit https://example.com now"), "URL pattern failed"
    
    # Self-harm patterns
    self_harm_pattern = r'\b(kill|die|suicide|end my life|hurt myself|self.harm|cutting|overdose)\b'
    assert re.search(self_harm_pattern, "I want to kill myself"), "Self-harm pattern failed"
    
    print("✓ All regex patterns work correctly")

def test_config_update():
    """Test that config includes traditional_ml option"""
    print("Testing configuration...")
    
    try:
        from config import settings
        assert hasattr(settings, 'llm_provider'), "llm_provider not found in settings"
        
        # Test the enum includes traditional_ml
        from typing import get_args, get_origin
        llm_provider_field = settings.__class__.__model_fields__['llm_provider']
        allowed_values = get_args(llm_provider_field.annotation)
        assert 'traditional_ml' in allowed_values, "traditional_ml not in allowed values"
        
        print("✓ Configuration updated correctly")
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False
    
    return True

def test_provider_class():
    """Test that TraditionalMLProvider class exists and has required methods"""
    print("Testing TraditionalMLProvider class...")
    
    try:
        from services.llm_gateway import TraditionalMLProvider
        
        # Check class exists
        provider = TraditionalMLProvider()
        
        # Check required methods exist
        assert hasattr(provider, 'moderate'), "moderate method not found"
        assert hasattr(provider, '_detect_doxxing'), "_detect_doxxing method not found"
        assert hasattr(provider, '_detect_spam'), "_detect_spam method not found"
        assert hasattr(provider, '_detect_self_harm'), "_detect_self_harm method not found"
        assert hasattr(provider, '_map_probability_to_category'), "_map_probability_to_category method not found"
        
        print("✓ TraditionalMLProvider class implemented correctly")
    except Exception as e:
        print(f"✗ Provider class test failed: {e}")
        return False
    
    return True

def test_build_provider():
    """Test that build_provider function includes traditional_ml option"""
    print("Testing build_provider function...")
    
    try:
        from services.llm_gateway import build_provider
        from config import Settings
        
        # Create a mock settings object with traditional_ml
        class MockSettings:
            llm_provider = "traditional_ml"
            openai_api_key = None
            openai_moderation_model = "gpt-4o-mini"
        
        mock_settings = MockSettings()
        provider = build_provider(mock_settings)
        
        # Check that it returns a TraditionalMLProvider
        from services.llm_gateway import TraditionalMLProvider
        assert isinstance(provider, TraditionalMLProvider), f"Expected TraditionalMLProvider, got {type(provider)}"
        
        print("✓ build_provider function updated correctly")
    except Exception as e:
        print(f"✗ build_provider test failed: {e}")
        return False
    
    return True

def test_requirements():
    """Test that requirements.txt includes alt-profanity-check"""
    print("Testing requirements.txt...")
    
    try:
        with open('requirements.txt', 'r') as f:
            content = f.read()
            assert 'alt-profanity-check==1.8.0' in content, "alt-profanity-check not found in requirements.txt"
        
        print("✓ requirements.txt updated correctly")
    except Exception as e:
        print(f"✗ Requirements test failed: {e}")
        return False
    
    return True

def main():
    """Run all validation tests"""
    print("Validating Traditional ML Implementation")
    print("=" * 50)
    
    tests = [
        test_regex_patterns,
        test_requirements,
        test_config_update,
        test_provider_class,
        test_build_provider,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} failed with exception: {e}")
    
    print("=" * 50)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Implementation is ready.")
        return True
    else:
        print("❌ Some tests failed. Please review the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
