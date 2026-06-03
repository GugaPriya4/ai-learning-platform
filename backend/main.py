import os
import json
from google import genai
from google.genai import types
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from rag import retrieve_context
from prompts import get_learning_prompt, get_quiz_prompt, get_flashcard_prompt, get_revision_prompt
from scoring import update_mastery, get_all_mastery, get_weak_topics, build_adaptive_quiz_topics, check_level_gate, advance_level, load_progress
load_dotenv()
print(os.getenv("GEMINI_API_KEY")[:10])

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

app = FastAPI(title="AI Learning Platform")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

def load_curriculum():
    import os
    path = os.path.join(os.path.dirname(__file__), "..", "curriculum.json")
    with open(path, "r") as f:
        return json.load(f)

class LearnRequest(BaseModel):
    topic: str
    style: str

class QuizRequest(BaseModel):
    topic: str
    level: str
    count: int = 10

class FlashcardRequest(BaseModel):
    topic: str

class AssessRequest(BaseModel):
    topic_id: str
    correct: int
    total: int

@app.get("/")
def root():
    return {"message": "AI Learning Platform API is running"}

@app.get("/curriculum")
def get_curriculum():
    return load_curriculum()

@app.get("/progress")
def get_progress():
    curriculum = load_curriculum()
    progress = load_progress()
    current_level = progress.get("current_level", "Beginner")
    mastery = get_all_mastery(curriculum, current_level)
    weak = get_weak_topics(curriculum, current_level)
    can_advance = check_level_gate(curriculum, current_level)
    return {
        "current_level": current_level,
        "mastery": mastery,
        "weak_topics": weak,
        "can_advance": can_advance
    }

@app.post("/learn")
def learn(request: LearnRequest):
    context = retrieve_context(request.topic)
    prompt = get_learning_prompt(
        request.topic,
        context,
        request.style
    )

    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt
        )

        explanation = response.text

    except Exception as e:

        explanation = f"""
Topic: {request.topic}

Gemini API is currently unavailable or quota has been exhausted.

Retrieved Learning Content:

{context[:1500]}

Error:
{str(e)}
"""

    return {
        "topic": request.topic,
        "style": request.style,
        "explanation": explanation
    }

@app.post("/quiz")
def generate_quiz(request: QuizRequest):

    context = retrieve_context(request.topic)

    prompt = get_quiz_prompt(
        request.topic,
        context,
        request.level,
        request.count
    )

    try:

        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt
        )

        text = response.text.strip()

        if text.startswith("```"):
            text = text.split("```")[1]

            if text.startswith("json"):
                text = text[4:]

        questions = json.loads(text.strip())

    except Exception:

        questions = [
            {
                "question": f"What is {request.topic}?",
                "options": [
                    "A concept in Git",
                    "A database",
                    "An operating system",
                    "A programming language"
                ],
                "answer": "A concept in Git"
            }
        ]

    return {
        "topic": request.topic,
        "level": request.level,
        "questions": questions
    }

@app.post("/flashcards")
def generate_flashcards(request: FlashcardRequest):

    context = retrieve_context(request.topic)

    prompt = get_flashcard_prompt(
        request.topic,
        context
    )

    try:

        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt
        )

        text = response.text.strip()

        if text.startswith("```"):
            text = text.split("```")[1]

            if text.startswith("json"):
                text = text[4:]

        cards = json.loads(text.strip())

    except Exception:

        cards = [
            {
                "front": request.topic,
                "back": context[:300]
            }
        ]

    return {
        "topic": request.topic,
        "flashcards": cards
    }

@app.post("/assess")
def assess(request: AssessRequest):
    score = update_mastery(request.topic_id, request.correct, request.total)
    band = "Mastered" if score >= 80 else "Needs Revision" if score >= 60 else "Weak"
    return {
        "topic_id": request.topic_id,
        "score": score,
        "band": band
    }

@app.post("/advance")
def try_advance():
    curriculum = load_curriculum()
    progress = load_progress()
    current_level = progress.get("current_level", "Beginner")
    can_advance = check_level_gate(curriculum, current_level)
    if can_advance:
        new_level = advance_level(curriculum)
        return {"advanced": True, "new_level": new_level}
    else:
        weak = get_weak_topics(curriculum, current_level)
        return {"advanced": False, "weak_topics": weak}

@app.get("/adaptive-quiz-topics")
def adaptive_quiz_topics():
    curriculum = load_curriculum()
    progress = load_progress()
    current_level = progress.get("current_level", "Beginner")
    topics = build_adaptive_quiz_topics(curriculum, current_level)
    return {"topics": topics}

@app.get("/revision-plan")
def revision_plan():

    curriculum = load_curriculum()
    progress = load_progress()

    current_level = progress.get(
        "current_level",
        "Beginner"
    )

    weak = get_weak_topics(
        curriculum,
        current_level
    )

    if not weak:
        return {
            "plan": "Great job! No weak topics found. You are ready to advance."
        }

    weak_names = [t["name"] for t in weak]

    prompt = get_revision_prompt(
        weak_names
    )

    try:

        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt
        )

        plan = response.text

    except Exception:

        plan = f"""
Revision Plan

Focus on these topics:

{', '.join(weak_names)}

1. Review concepts
2. Study examples
3. Complete flashcards
4. Retake quiz
"""

    return {
        "plan": plan
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)
