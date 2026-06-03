# AI-Powered Personalised Learning Platform

An intelligent learning platform that uses RAG (Retrieval Augmented Generation) to deliver personalised Git education.

## AI Concepts Demonstrated
- Retrieval Augmented Generation (RAG)
- Vector Embeddings with sentence-transformers
- Semantic Search using ChromaDB
- Personalised LLM responses via Gemini API
- Adaptive Assessment and Mastery Tracking
- Prompt Engineering for different learning styles

## Tech Stack
- FastAPI — REST backend
- Streamlit — Interactive frontend
- ChromaDB — Vector database
- LlamaIndex — RAG framework
- Sentence Transformers (all-MiniLM-L6-v2) — Embeddings
- Gemini 1.5 Flash — LLM for content generation

## Architecture
Three layer architecture:
1. Curriculum Layer — JSON manages topics, levels, prerequisites
2. Knowledge Layer — RAG pipeline retrieves relevant content
3. Intelligence Layer — Gemini generates personalised explanations

## How to Run
1. Clone the repo
2. Create virtual environment and install dependencies
3. Add GEMINI_API_KEY to .env
4. Run ingestion: python backend/ingest.py
5. Start backend: uvicorn backend/main:app --reload
6. Start frontend: streamlit run frontend/app.py

## Features
- Knowledge mapping quiz
- Topic mastery tracking (Mastered / Needs Revision / Weak)
- 4 learning styles (Examples / Simple / Detailed / Definition)
- Flashcard generation
- Adaptive quiz (80% weak topics + 20% next level)
- Level progression with 85% gate
- Personalised revision plans