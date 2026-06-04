def get_learning_prompt(topic: str, context: str, style: str) -> str:
    style_instructions = {
        "examples": """Teach using ONLY real-world analogies and practical examples.
Structure your response like this:
1. One sentence what it is
2. Real world analogy (relate to everyday life)
3. Practical Git example with actual commands
4. When would you use this in a real project
Do NOT copy the source text. Rewrite everything in example-driven format.""",

        "simple": """Teach like explaining to a complete beginner with zero technical knowledge.
Structure your response like this:
1. What is it? (one simple sentence, no jargon)
2. Why does it matter? (in plain english)
3. How do you use it? (step by step, very simple)
Use short sentences. Avoid technical terms. If you must use a term, explain it immediately.""",

        "detailed": """Give a thorough technical explanation covering all aspects.
Structure your response like this:
1. Formal definition
2. How it works internally
3. All important commands with explanations
4. Common use cases
5. Best practices and pitfalls to avoid
Be comprehensive but organized.""",

        "definition": """Teach using clear definitions and precise terminology.
Structure your response like this:
1. Formal definition (precise, complete)
2. Break down each part of the definition
3. Key terminology related to this topic
4. Distinction from similar concepts
Be precise and dictionary-like in your explanations."""
    }

    instruction = style_instructions.get(style, style_instructions["simple"])

    return f"""You are an expert Git tutor. Your job is to TEACH, not to copy content.

The learner wants to understand: {topic}
Their preferred learning style: {style}

Teaching instructions:
{instruction}

Use the information below as your knowledge source, but DO NOT copy it directly.
Transform it into a personalised explanation that matches the teaching style above.

Knowledge source:
{context}

Now write your personalised explanation of {topic} in the {style} style.
Keep it under 250 words. Make it engaging and clear."""

def get_quiz_prompt(topic: str, context: str, level: str, count: int = 10) -> str:
    return f"""You are a Git quiz generator. Generate {count} MCQ questions about "{topic}".

CRITICAL RULES - VIOLATIONS WILL BREAK THE SYSTEM:
1. Every question MUST have 4 COMPLETELY DIFFERENT options from each other
2. NO question can share the same 4 options as another question
3. The correct answer MUST be different for each question - mix A, B, C, D answers
4. Questions must test DIFFERENT things - commands, concepts, syntax, use cases, differences

Here are example question STYLES you must vary between:
- "Which command is used to...?" 
- "What happens when you run...?"
- "What is the difference between X and Y?"
- "In which situation would you use...?"
- "What does this command do: git ...?"

Knowledge to base questions on:
{context}

Return ONLY this exact JSON format, nothing else:
[
  {{
    "question": "Which Git command creates a snapshot of staged changes?",
    "options": {{"A": "git push", "B": "git commit", "C": "git clone", "D": "git fetch"}},
    "answer": "B",
    "explanation": "git commit saves a snapshot of staged changes to the repository history"
  }},
  {{
    "question": "What does git status show?",
    "options": {{"A": "Commit history", "B": "Remote branches", "C": "Staged and unstaged changes", "D": "Repository size"}},
    "answer": "C",
    "explanation": "git status shows which files are staged, unstaged, and untracked"
  }}
]

Now generate {count} questions about {topic} following the same pattern. Make each question unique."""


def get_flashcard_prompt(topic: str, context: str) -> str:
    return f"""You are a flashcard generator for Git learning.
Create exactly 5 flashcards for the topic: {topic}

Use this content as your knowledge source:
{context}

RULES:
- Each flashcard must cover a DIFFERENT aspect of {topic}
- Front: a specific question or concept prompt
- Back: a clear, concise answer (2-3 sentences max)
- Make cards progressively harder (basic → intermediate → advanced)
- Do NOT just copy sentences from the source

Return ONLY valid JSON array, no markdown, no extra text:
[
  {{
    "front": "specific question or concept",
    "back": "clear concise answer"
  }},
  {{
    "front": "second different concept",
    "back": "answer"
  }},
  {{
    "front": "third concept",
    "back": "answer"
  }},
  {{
    "front": "fourth concept",
    "back": "answer"
  }},
  {{
    "front": "fifth harder concept",
    "back": "answer"
  }}
]"""


def get_revision_prompt(weak_topics: list) -> str:
    topics_str = ", ".join(weak_topics)
    return f"""You are a learning coach creating a focused revision plan.
The learner is weak in these Git topics: {topics_str}

Create a practical 3-day revision plan.

Day 1: Focus on understanding concepts
Day 2: Focus on hands-on practice with commands  
Day 3: Focus on applying in real scenarios

For each day list exactly what to do for each weak topic.
Be specific and actionable. Keep total plan under 300 words."""