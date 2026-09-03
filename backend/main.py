from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List

from analyzer import analyze_code, generate_hint, complexity_rank
from ai_helper import get_ai_explanation
from database import init_db, save_analysis, get_history, create_user, verify_user, get_stats

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()


class AnalyzeRequest(BaseModel):
    problem: str
    code: str
    language: str
    user_id: Optional[int] = None


class AuthRequest(BaseModel):
    username: str
    password: str


@app.post("/signup")
def signup(request: AuthRequest):
    if len(request.username.strip()) < 3:
        return {"success": False, "message": "Username must be at least 3 characters."}
    if len(request.password) < 4:
        return {"success": False, "message": "Password must be at least 4 characters."}

    user_id = create_user(request.username.strip(), request.password)
    if user_id is None:
        return {"success": False, "message": "That username is already taken."}

    return {"success": True, "user_id": user_id, "username": request.username.strip()}


@app.post("/login")
def login(request: AuthRequest):
    user_id = verify_user(request.username.strip(), request.password)
    if user_id is None:
        return {"success": False, "message": "Incorrect username or password."}

    return {"success": True, "user_id": user_id, "username": request.username.strip()}


class SolutionInput(BaseModel):
    label: str
    code: str
    language: str


class CompareRequest(BaseModel):
    problem: str
    solutions: List[SolutionInput]


@app.post("/compare")
def compare(request: CompareRequest):
    results = []
    for sol in request.solutions:
        static_result = analyze_code(request.problem, sol.code, sol.language)
        results.append({
            "label": sol.label,
            "language": sol.language,
            "approach": static_result["approach"],
            "pattern": static_result["pattern"],
            "time_complexity": static_result["time_complexity"],
            "space_complexity": static_result["space_complexity"],
            "rank": complexity_rank(static_result["time_complexity"]),
        })

    best_rank = min(r["rank"] for r in results)
    best_labels = [r["label"] for r in results if r["rank"] == best_rank]

    return {
        "results": results,
        "best_labels": best_labels,  # more than one if tied
    }


@app.post("/analyze")
def analyze(request: AnalyzeRequest):
    static_result = analyze_code(request.problem, request.code, request.language)
    final_result = get_ai_explanation(
        request.problem, request.code, request.language, static_result
    )

    save_analysis(request.problem, request.code, request.language, final_result, user_id=request.user_id)

    return final_result


@app.post("/hint")
def hint(request: AnalyzeRequest):
    static_result = analyze_code(request.problem, request.code, request.language)
    hint_data = generate_hint(static_result["pattern"])
    return {
        "hint": hint_data["message"],
        "is_optimal": hint_data["is_optimal"],
        "pattern": static_result["pattern"],
    }


@app.get("/history")
def history(user_id: Optional[int] = None, pattern: Optional[str] = None):
    return get_history(user_id=user_id, pattern=pattern)


@app.get("/stats")
def stats(user_id: Optional[int] = None):
    return get_stats(user_id=user_id)



