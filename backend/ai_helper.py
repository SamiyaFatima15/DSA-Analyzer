import os
import concurrent.futures
import google.generativeai as genai

# Set your API key as an environment variable for safety instead of
# hardcoding it here. See instructions below the code for how to set it.
API_KEY = os.environ.get("GEMINI_API_KEY")

if API_KEY:
    genai.configure(api_key=API_KEY)

model = genai.GenerativeModel("gemini-3.6-flash")  # Google's currently-recommended model for new users (as of testing)


def get_ai_explanation(problem: str, code: str, language: str, static_result: dict) -> dict:
    """
    Takes the RULE-BASED static analysis (already computed by analyzer.py)
    and asks the AI to turn it into a clear, human-friendly explanation.

    Important: the AI is NOT asked to independently decide time/space
    complexity — it's given our static analysis as ground truth and asked
    to explain and refine the WORDING, not the numbers. This keeps the
    complexity values trustworthy (rule-based) while making the
    explanation feel natural (AI-based).
    """

    if not API_KEY:
        print("⚠️ GEMINI_API_KEY not set in this terminal session — using static result only.")
        return static_result

    prompt = f"""You are a DSA (Data Structures & Algorithms) tutor helping a student
understand their own code. Below is a problem, the student's code, and a
static analysis that was already computed by a rule-based tool.

Problem:
{problem}

Language: {language}

Code:
{code}

Static analysis (treat time_complexity and space_complexity as CORRECT —
do not change these values, only explain them):
- Approach: {static_result['approach']}
- Pattern: {static_result['pattern']}
- Time Complexity: {static_result['time_complexity']}
- Space Complexity: {static_result['space_complexity']}

Respond in strict JSON with exactly these keys, no extra text, no markdown:
{{
  "approach": "1-2 sentence human-friendly description of the approach",
  "optimization": "1-2 sentence optimization suggestion, or say it's already optimal",
  "explanation": "2-3 sentence beginner-friendly explanation of WHY the time and space complexity are what they are, referencing the actual code"
}}
"""

    try:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(model.generate_content, prompt)
            response = future.result(timeout=25)  # increased from 15s — free-tier can be slow under load

        text = response.text.strip()

        # Strip accidental markdown code fences if the model adds them
        if text.startswith("```"):
            text = text.strip("`")
            if text.lower().startswith("json"):
                text = text[4:].strip()

        import json
        ai_data = json.loads(text)

        # Merge: keep the RULE-BASED complexity values, replace only the
        # explanatory text fields with the AI's improved wording.
        return {
            "approach": ai_data.get("approach", static_result["approach"]),
            "pattern": static_result["pattern"],
            "time_complexity": static_result["time_complexity"],
            "space_complexity": static_result["space_complexity"],
            "optimization": ai_data.get("optimization", static_result["optimization"]),
            "explanation": ai_data.get("explanation", static_result["explanation"]),
            "code_quality": static_result.get("code_quality"),
            "edge_cases": static_result.get("edge_cases"),
        }

    except Exception as e:
        # If the AI call fails for any reason (bad key, network, rate
        # limit, malformed JSON), silently fall back to the static result
        # so the app never breaks because of the AI layer.
        print(f"AI explanation failed ({type(e).__name__}), falling back to static result: {e}")
        return static_result