def get_learning_prompt(topic: str, context: str, style: str) -> str:
    style_instructions = {
        "examples": "Use real-world analogies and practical code examples. Every concept must have a hands-on example.",
        "simple": "Use very simple language. Short sentences. Avoid jargon. Explain like the learner is a complete beginner.",
        "detailed": "Give a thorough, in-depth explanation covering all aspects, edge cases, and best practices.",
        "definition": "Start with a clear formal definition, then explain each part of the definition carefully."
    }
    instruction = style_instructions.get(style, style_instructions["simple"])
    return f"""You are an expert Git tutor teaching a software engineering trainee.
Use ONLY the content provided below as your source of truth.
Do not use outside knowledge.

Teaching style: {instruction}

Content to teach from:
{context}

Now teach the topic: {topic}

Keep your response clear, structured and under 300 words."""


def get_quiz_prompt(topic: str, context: str, level: str) -> str:
    return f"""You are a quiz generator for a Git learning platform.
Generate exactly 10 multiple choice questions about: {topic}
Level: {level}
Use ONLY this content as your source:
{context}

Return ONLY a valid JSON array with exactly this structure, no extra text:
[
  {{
    "question": "question text here",
    "options": {{"A": "option1", "B": "option2", "C": "option3", "D": "option4"}},
    "answer": "A",
    "explanation": "why this is correct"
  }}
]"""


def get_flashcard_prompt(topic: str, context: str) -> str:
    return f"""You are a flashcard generator for a Git learning platform.
Create exactly 5 flashcards for the topic: {topic}
Use ONLY this content as your source:
{context}

Return ONLY a valid JSON array with exactly this structure, no extra text:
[
  {{
    "front": "question or concept",
    "back": "answer or explanation"
  }}
]"""


def get_revision_prompt(weak_topics: list) -> str:
    topics_str = ", ".join(weak_topics)
    return f"""You are a learning coach creating a revision plan.
The learner is weak in these Git topics: {topics_str}

Create a focused 3-day revision plan covering only these weak topics.
Be specific about what to practice each day.
Keep it practical and actionable.
Format it clearly with Day 1, Day 2, Day 3 sections."""