import os
import time
import google.generativeai as genai

print("Step 1: Checking API key...")
API_KEY = os.environ.get("GEMINI_API_KEY")

if not API_KEY:
    print("❌ GEMINI_API_KEY not found in this terminal session.")
    print("Run this first, in THIS terminal:")
    print('   $env:GEMINI_API_KEY="your_key_here"')
    exit()

print(f"✅ Key found (starts with: {API_KEY[:6]}...)")

print("\nStep 2: Configuring Gemini...")
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-3.6-flash")
print("✅ Configured.")

print("\nStep 3: Sending a simple test prompt (should take a few seconds)...")
start = time.time()

try:
    response = model.generate_content("Say 'hello world' and nothing else.")
    elapsed = time.time() - start
    print(f"✅ SUCCESS in {elapsed:.1f} seconds!")
    print("\nResponse from AI:")
    print(response.text)
except Exception as e:
    elapsed = time.time() - start
    print(f"❌ FAILED after {elapsed:.1f} seconds")
    print(f"Error: {e}")