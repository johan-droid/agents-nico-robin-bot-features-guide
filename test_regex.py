#!/usr/bin/env python3
"""
Simple regex pattern test without external dependencies
"""

import re

def test_patterns():
    """Test regex patterns work correctly"""
    print("Testing regex patterns...")
    
    # Doxxing patterns
    phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    address_pattern = r'\b\d+\s+[A-Za-z]+\s+(Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln|Boulevard|Blvd|Court|Ct|Way|Place|Pl)\b'
    
    # Spam patterns
    url_pattern = r'https?://[^\s]+'
    www_pattern = r'www\.[^\s]+'
    promo_pattern = r'\b(buy|sell|discount|offer|deal|free|win|prize|click|visit|check out|limited time)\b'
    price_pattern = r'\b\$\d+\.?\d*\b'
    
    # Self-harm patterns
    self_harm_pattern1 = r'\b(kill|die|suicide|end my life|hurt myself|self.harm|cutting|overdose)\b'
    self_harm_pattern2 = r'\b(want to die|don.t want to live|better off dead)\b'
    
    # Test cases
    test_cases = [
        ("Call me at 555-123-4567", phone_pattern, True),
        ("Email me at test@example.com", email_pattern, True),
        ("I live at 123 Main Street", address_pattern, True),
        ("Visit https://example.com now", url_pattern, True),
        ("Check out www.example.com today", www_pattern, True),
        ("Buy our amazing products now!", promo_pattern, True),
        ("Only $9.99 for limited time!", price_pattern, True),
        ("I want to kill myself", self_harm_pattern1, True),
        ("I don't want to live anymore", self_harm_pattern2, True),
        ("Hello everyone how are you", phone_pattern, False),
    ]
    
    passed = 0
    total = len(test_cases)
    
    for text, pattern, should_match in test_cases:
        match = bool(re.search(pattern, text, re.IGNORECASE))
        if match == should_match:
            print(f"✓ '{text}' - {'matched' if match else 'no match'} (expected {'match' if should_match else 'no match'})")
            passed += 1
        else:
            print(f"✗ '{text}' - {'matched' if match else 'no match'} (expected {'match' if should_match else 'no match'})")
    
    print(f"\nResults: {passed}/{total} tests passed")
    return passed == total

if __name__ == "__main__":
    success = test_patterns()
    if success:
        print("🎉 All regex patterns work correctly!")
    else:
        print("❌ Some regex patterns failed.")
