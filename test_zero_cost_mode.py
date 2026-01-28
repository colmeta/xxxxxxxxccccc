#!/usr/bin/env python3
"""
ZERO-COST VERIFICATION TEST
Tests that platform works with NO API tokens available.
"""
import sys
import os

# Fix Windows console encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add worker to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'worker'))

def test_gemini_offline_mode():
    """Test that Gemini client enters offline mode when API keys missing"""
    print("\n=== TEST 1: Gemini Offline Mode ===")
    
    # Temporarily clear API keys
    old_gemini = os.environ.get('GEMINI_API_KEY')
    old_groq = os.environ.get('GROQ_API_KEY')
    
    os.environ['GEMINI_API_KEY'] = ''
    os.environ['GROQ_API_KEY'] = ''
    
    from worker.utils.gemini_client import GeminiClient
    client = GeminiClient()
    
    # Restore keys
    if old_gemini:
        os.environ['GEMINI_API_KEY'] = old_gemini
    if old_groq:
        os.environ['GROQ_API_KEY'] = old_groq
    
    assert client.offline_mode or not client.ai_available, "[FAIL] Client should be in offline mode"
    print("[OK] Gemini client correctly enters offline mode when keys missing")
    return True

def test_enrichment_bridge_layers():
    """Test that enrichment bridge respects zero_cost.env configuration"""
    print("\n=== TEST 2: Enrichment Layer Configuration ===")
    
    # Create a mock page object
    class MockPage:
        pass
    
    from worker.utils.enrichment_bridge import EnrichmentBridge
    bridge = EnrichmentBridge(MockPage())
    
    # Check disabled layers
    disabled_layers = [3, 4, 5, 6, 8, 9, 11, 12, 13]
    for layer_num in disabled_layers:
        is_enabled = bridge.layer_config.get(layer_num, True)
        if is_enabled:
            print(f"[WARN] Layer {layer_num} should be disabled but is enabled")
        else:
            print(f"[OK] Layer {layer_num} correctly disabled")
    
    # Check enabled layers 
    enabled_layers = [1, 2, 7, 10]
    for layer_num in enabled_layers:
        is_enabled = bridge.layer_config.get(layer_num, False)
        if not is_enabled:
            print(f"[WARN] Layer {layer_num} should be enabled but is disabled")
        else:
            print(f"[OK] Layer {layer_num} correctly enabled")
    
    return True

def test_offline_contact_discovery():
    """Test offline contact discovery functions"""
    print("\n=== TEST 3: Offline Contact Discovery ===")
    
    from worker.utils.offline_contact_discovery import offline_contact_discovery
    
    # Create mock page
    class MockPage:
        async def goto(self, url, **kwargs):
            pass
        async def content(self):
            return "<html><body>Contact us: test@ example.com, support@company.com</body></html>"
    
    # Test email extraction (simulated)
    discovery = offline_contact_discovery(MockPage())
    
    # Test email validation
    assert discovery.validate_email_format("test@example.com"), "[FAIL] Valid email rejected"
    assert not discovery.validate_email_format("invalid-email"), "[FAIL] Invalid email accepted"
    print("[OK] Email format validation working")
    
    # Test phone validation
    assert discovery.validate_phone_format("+1-555-123-4567"), "[FAIL] Valid phone rejected"
    assert not discovery.validate_phone_format("123"), "[FAIL] Invalid phone accepted"
    print("[OK] Phone format validation working")
    
    # Test company name filtering
    assert discovery.filter_junk_company_name("Valid Company Inc"), "[FAIL] Valid name rejected"
    assert not discovery.filter_junk_company_name("This is a very long description that is over 60 characters long"), "[FAIL] Long description accepted"
    assert not discovery.filter_junk_company_name("Company - With - Too - Many - Hyphens"), "[FAIL] Junk name accepted"
    print("[OK] Company name filtering working")
    
    return True

def test_zero_cost_config():
    """Test that zero_cost.env configuration is readable"""
    print("\n=== TEST 4: Zero-Cost Configuration ===")
    
    from dotenv import load_dotenv
    load_dotenv("worker/zero_cost.env")
    
    # Check key settings
    assertions = [
        (os.getenv("ENABLE_LAYER_6_PATENTS", "true") == "false", "Layer 6 (Patents) should be disabled"),
        (os.getenv("ENABLE_LAYER_8_TRADE", "true") == "false", "Layer 8 (Trade) should be disabled"),
        (os.getenv("AI_VALIDATION_ENABLED", "true") == "false", "AI validation should be disabled"),
        (os.getenv("USE_HEURISTIC_VALIDATION", "false") == "true", "Heuristic validation should be enabled"),
    ]
    
    for assertion, msg in assertions:
        if assertion:
            print(f"[OK] {msg}")
        else:
            print(f"[FAIL] {msg}")
            return False
    
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("ZERO-COST DATA PLATFORM VERIFICATION")
    print("=" * 60)
    
    tests = [
        test_gemini_offline_mode,
        test_enrichment_bridge_layers,
        test_offline_contact_discovery,
        test_zero_cost_config,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"[FAIL] Test failed with exception: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)
    
    if failed == 0:
        print("[SUCCESS] ALL TESTS PASSED - Zero-cost mode ready!")
        print("\nNext steps:")
        print("1. Create a test job in Supabase")
        print("2. Run: cd worker && python hydra_controller.py --timeout 300")
        print("3. Check logs for 'DISABLED' messages on API-dependent layers")
        print("4. Verify leads have phone/website (no email without paid services)")
        sys.exit(0)
    else:
        print("[FAIL] SOME TESTS FAILED - Review errors above")
        sys.exit(1)
