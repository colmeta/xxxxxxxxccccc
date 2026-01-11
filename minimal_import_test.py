import sys
print("Starting import test...")
try:
    from google import genai
    print("Import Success!")
    print(f"GenAI Version: {getattr(genai, '__version__', 'unknown')}")
except Exception as e:
    print(f"Import Failed: {e}")
print("End of test.")
