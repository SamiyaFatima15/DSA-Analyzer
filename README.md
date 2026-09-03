# 🧠 DSA Code Analyzer

An AI-assisted platform to analyze your DSA (Data Structures & Algorithms) solutions — approach, time complexity, space complexity, pattern, and optimization hints — without needing LeetCode Premium.

## 💡 Why this project exists

LeetCode's own complexity/approach analysis is a premium feature, and even then it only allows one analysis per day. This tool lets you analyze **as many of your own solutions as you want, for free**, using a combination of rule-based static analysis and (optional) AI-generated explanations.

## ✨ Features

- **Multi-language support** — C++, Java, and Python
- **24 detectable DSA patterns** (see full list below)
- **Time & Space Complexity analysis** — rule-based static analysis (loop nesting, recursion, data structure usage)
- **AI-generated explanations** — human-friendly approach/optimization/explanation text (via Google Gemini API), with automatic fallback to rule-based text if the AI is unavailable
- **Hint Mode** — get a nudge toward the right approach without seeing the full solution. Clearly distinguishes between "here's a hint" and "✅ your code is already optimal" so there's no confusion about whether more optimization is possible
- **Compare Solutions** — paste 2-3 different solutions to the same problem and instantly see which one is actually the most efficient, side by side
- **User accounts** — sign up / log in, so your history and stats are your own
- **Analysis history** — every analysis is saved and browsable
- **Dashboard** (side panel) — total solved count, pattern breakdown (click any pattern to see the related problems), language breakdown, 7-day activity trend, and "weak areas" you haven't practiced yet

## 🎯 Patterns Detected

| Category | Patterns |
|---|---|
| Arrays & Searching | Hashing, Two Pointer, Sliding Window, Binary Search, Sorting, Brute Force, Single Pass |
| Recursion-based | Recursion, Backtracking, Divide and Conquer |
| Dynamic Programming | Dynamic Programming (1D & 2D detection) |
| Graphs | Graph BFS, Graph DFS, Topological Sort, Union-Find (Disjoint Set) |
| Data Structures | Heap / Priority Queue, Trie, Monotonic Stack, Segment Tree / Fenwick Tree |
| Arrays (advanced) | Prefix Sum, Kadane's Algorithm, Matrix Traversal, Interval Merging |
| Linked Lists | Fast & Slow Pointers |
| Low-level | Bit Manipulation |

**Note:** *Greedy* is intentionally not auto-detected — unlike the patterns above, it has no reliable code "shape" or syntactic signature (it's a strategy, not a structure), so keyword-based detection would produce too many false positives to be trustworthy.

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML, CSS, vanilla JavaScript |
| Backend | Python, FastAPI |
| Code Analysis | Custom rule-based static analyzer (regex + loop-nesting/indentation tracking) |
| AI | Google Gemini API (free tier) |
| Database | SQLite |
| Auth | Username/password with PBKDF2 password hashing |

## 📁 Project Structure

```
DSA Analyzer/
├── .vscode/
│   └── settings.json        # Live Server config (ignores backend folder)
├── backend/
│   ├── main.py               # FastAPI app & routes
│   ├── analyzer.py           # Rule-based static analysis logic (24 patterns)
│   ├── ai_helper.py          # Gemini AI integration (with fallback)
│   ├── database.py           # SQLite setup, users, history, stats
│   ├── dsa_analyzer.db       # SQLite database (auto-created on first run)
│   └── requirements.txt
└── frontend/
    └── index.html            # Full UI (structure + styling + logic)
```

## 🚀 Setup & Installation

### Prerequisites
- Python 3.10+ installed
- VS Code with the **Live Server** extension

### Backend Setup

1. Open a terminal in the `backend` folder
2. Install dependencies:
   ```
   python -m pip install fastapi uvicorn google-generativeai
   ```
3. **(Optional, for AI explanations)** Get a free API key from [Google AI Studio](https://aistudio.google.com/apikey), then set it in your terminal session:
   ```
   $env:GEMINI_API_KEY="your_key_here"     # PowerShell
   ```
   *Note: this must be set before starting the server, every time you open a new terminal — unless set permanently via Windows Environment Variables (System Properties → Environment Variables → New User Variable).*
4. Start the server:
   ```
   python -m uvicorn main:app --reload
   ```
   The backend runs at `http://127.0.0.1:8000`

### Frontend Setup

1. Open `frontend/index.html` in VS Code
2. Right-click → **"Open with Live Server"**
3. The app opens in your browser, already wired to call the backend at `127.0.0.1:8000`

## 📖 Usage

1. **Sign up / Log in** (top-right corner)
2. Paste your problem statement and code, select the language
3. Click **"run analysis"** for approach, pattern, time/space complexity, and optimization suggestions
4. Click **"give me a hint"** if stuck — shows a nudge, or a clear "already optimal" message if there's nothing left to improve
5. Use **"Compare Solutions"** to paste 2-3 approaches for the same problem and see which is fastest
6. Check **"📜 history"** to see all past analyses
7. Check **"📊 dashboard"** (opens as a side panel) for overall stats, activity trend, pattern breakdown, and weak areas

## ⚠️ Known Limitations

- **Static analysis is heuristic-based, not a true parser.** It reads code as text patterns (loop keywords, variable naming conventions like `left`/`right` for two-pointer detection, etc.), so unusual code formatting or naming can occasionally cause misclassification.
- **Greedy algorithms are not auto-detected**, for the reason explained above.
- **AI explanations depend on a free-tier API** with rate limits (a handful of requests per minute). If the limit is hit, the app automatically falls back to the rule-based explanation — it never crashes, but the wording will be more generic in that case.
- **No code execution** — this tool only performs static analysis; it does not compile or run submitted code.

## 🔮 Possible Future Enhancements

- Reliable Greedy detection via structural analysis rather than keywords
- AST-based analysis for more accurate Python complexity detection
- Code quality scoring
- Deployment to a public host (Render/Railway) so it's accessible beyond localhost

## 🙏 Credits

Built as a learning project to understand full-stack development (FastAPI + SQLite + vanilla JS) and AI API integration.