import os
import google.generativeai as genai

API_KEY = os.environ.get("GEMINI_API_KEY")

if not API_KEY:
    print("GEMINI_API_KEY environment variable not set in this terminal session!")
else:
    genai.configure(api_key=API_KEY)
    print("Models available for your key that support generateContent:\n")
    for m in genai.list_models():
        if "generateContent" in m.supported_generation_methods:
            print(m.name)