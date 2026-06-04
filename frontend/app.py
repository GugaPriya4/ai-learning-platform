import streamlit as st
import requests
import json

API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="AI Learning Platform",
    page_icon="🎓",
    layout="wide"
)

def get_curriculum():
    r = requests.get(f"{API_URL}/curriculum")
    return r.json()

def get_progress():
    r = requests.get(f"{API_URL}/progress")
    return r.json()

if "page" not in st.session_state:
    st.session_state.page = "home"
if "style" not in st.session_state:
    st.session_state.style = "simple"
if "quiz_questions" not in st.session_state:
    st.session_state.quiz_questions = []
if "quiz_answers" not in st.session_state:
    st.session_state.quiz_answers = {}
if "flashcards" not in st.session_state:
    st.session_state.flashcards = []
if "card_index" not in st.session_state:
    st.session_state.card_index = 0
if "show_back" not in st.session_state:
    st.session_state.show_back = False
if "selected_topic" not in st.session_state:
    st.session_state.selected_topic = ""

st.sidebar.title("AI Learning Platform")
st.sidebar.markdown("---")

pages = {
    "🏠 Home": "home",
    "📊 Knowledge Map": "knowledge_map",
    "📈 My Progress": "progress",
    "🎯 Learn a Topic": "learn",
    "🃏 Flashcards": "flashcards",
    "📝 Adaptive Quiz": "adaptive_quiz",
    "📋 Revision Plan": "revision"
}

for label, page_id in pages.items():
    if st.sidebar.button(label, use_container_width=True):
        st.session_state.page = page_id

st.sidebar.markdown("---")
try:
    prog = get_progress()
    st.sidebar.metric("Current Level", prog["current_level"])
    mastered = sum(1 for t in prog["mastery"].values() if t["band"] == "Mastered")
    total = len(prog["mastery"])
    st.sidebar.metric("Topics Mastered", f"{mastered}/{total}")
except:
    st.sidebar.info("Start learning to see progress")

page = st.session_state.page

if page == "home":
    st.title("Welcome to AI Learning Platform")
    st.markdown("### Your personalised Git learning journey starts here")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("**Step 1**\n\nTake the Knowledge Map quiz to assess your current level")
    with col2:
        st.info("**Step 2**\n\nLearn weak topics in your preferred style")
    with col3:
        st.info("**Step 3**\n\nTake adaptive quizzes and advance levels")
    st.markdown("---")
    st.markdown("**How this platform works:**")
    st.markdown("- Uses RAG (Retrieval Augmented Generation) to teach from curated content")
    st.markdown("- Identifies your weak topics through intelligent assessment")
    st.markdown("- Adapts explanations to your preferred learning style")
    st.markdown("- Generates personalised quizzes focusing on what you need most")

elif page == "knowledge_map":
    st.title("Knowledge Mapping Assessment")
    st.markdown("This quiz maps your current Git knowledge. Answer honestly — this is not graded.")
    curriculum = get_curriculum()
    beginner_topics = [t for l in curriculum["levels"] if l["level"] == "Beginner" for t in l["topics"]]

    if not st.session_state.quiz_questions:
        if st.button("Start Knowledge Assessment", type="primary"):
            with st.spinner("Generating your personalised assessment (this may take a moment)..."):
                questions = []
                for topic in beginner_topics:
                    if len(questions) >= 15:
                        break
                    r = requests.post(f"{API_URL}/quiz", json={
                        "topic": topic["name"],
                        "level": "Beginner",
                        "count": 2
                    })
                    if r.status_code != 200:
                        st.error(f"Backend error {r.status_code}: {r.text}")
                        break
                    data = r.json()
                    for q in data.get("questions", []):
                        q["topic_id"] = topic["id"]
                        questions.append(q)
                        if len(questions) >= 15:
                            break
                st.session_state.quiz_questions = questions
                st.rerun()
    else:
        questions = st.session_state.quiz_questions
        st.markdown(f"**{len(questions)} questions — select your answers:**")
        for i, q in enumerate(questions):
            st.markdown(f"**Q{i+1}: {q['question']}**")
            
            options = q["options"]
            if isinstance(options, dict):
                options_list = [f"{k}: {v}" for k, v in options.items()]
            elif isinstance(options, list):
                options_list = options
            else:
                options_list = []

            answer = st.radio(
                "",
                ["-- Select an answer --"] + options_list,
                key=f"q_{i}",
                label_visibility="collapsed",
                index=0
            )
            if answer and answer != "-- Select an answer --":
                st.session_state.quiz_answers[i] = answer[0]
            st.markdown("---")

        if st.button("Submit Assessment", type="primary"):
            with st.spinner("Analysing your results..."):
                topic_results = {}
                for i, q in enumerate(questions):
                    tid = q["topic_id"]
                    if tid not in topic_results:
                        topic_results[tid] = {"correct": 0, "total": 0}
                    topic_results[tid]["total"] += 1
                    if st.session_state.quiz_answers.get(i) == q["answer"]:
                        topic_results[tid]["correct"] += 1

                for tid, result in topic_results.items():
                    requests.post(f"{API_URL}/assess", json={
                        "topic_id": tid,
                        "correct": result["correct"],
                        "total": result["total"]
                    })

                st.success("Assessment complete! Go to My Progress to see your results.")
                st.session_state.quiz_questions = []
                st.session_state.quiz_answers = {}

elif page == "progress":
    st.title("My Learning Progress")
    try:
        prog = get_progress()
        st.markdown(f"### Current Level: {prog['current_level']}")
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        mastered = [t for t in prog["mastery"].values() if t["band"] == "Mastered"]
        revision = [t for t in prog["mastery"].values() if t["band"] == "Needs Revision"]
        weak = [t for t in prog["mastery"].values() if t["band"] == "Weak"]
        col1.metric("Mastered", len(mastered), delta="ready")
        col2.metric("Needs Revision", len(revision), delta="review")
        col3.metric("Weak", len(weak), delta="focus here")
        st.markdown("---")
        st.markdown("### Topic Breakdown")
        for tid, data in prog["mastery"].items():
            col_a, col_b, col_c = st.columns([3, 1, 1])
            col_a.write(data["name"])
            col_b.write(f"{data['score']}%")
            if data["band"] == "Mastered":
                col_c.success("Mastered")
            elif data["band"] == "Needs Revision":
                col_c.warning("Needs Revision")
            else:
                col_c.error("Weak")

        st.markdown("---")
        if prog["can_advance"]:
            st.success("You are ready to advance to the next level!")
            if st.button("Advance to Next Level", type="primary"):
                r = requests.post(f"{API_URL}/advance")
                data = r.json()
                if data["advanced"]:
                    st.balloons()
                    st.success(f"Congratulations! You advanced to {data['new_level']}!")
                    st.rerun()
        else:
            st.info("Score 85% average across all topics to advance to the next level.")
    except Exception as e:
        st.error(f"Error loading progress: {e}")

elif page == "learn":
    st.title("Learn a Topic")
    curriculum = get_curriculum()
    prog = get_progress()
    current_level = prog.get("current_level", "Beginner")

    all_topics = []
    for lvl in curriculum["levels"]:
        if lvl["level"] == current_level:
            all_topics = [(t["id"], t["name"]) for t in lvl["topics"]]

    st.markdown("### Choose your learning style")
    col1, col2, col3, col4 = st.columns(4)
    if col1.button("Examples", use_container_width=True):
        st.session_state.style = "examples"
    if col2.button("Simple", use_container_width=True):
        st.session_state.style = "simple"
    if col3.button("Detailed", use_container_width=True):
        st.session_state.style = "detailed"
    if col4.button("Definition", use_container_width=True):
        st.session_state.style = "definition"

    st.info(f"Current style: **{st.session_state.style}**")
    st.markdown("---")

    topic_names = [t[1] for t in all_topics]
    selected_name = st.selectbox("Select a topic to learn:", topic_names)
    selected_id = next((t[0] for t in all_topics if t[1] == selected_name), "")

    if st.button("Teach Me", type="primary"):
        with st.spinner(f"Retrieving content and generating personalised explanation..."):
            r = requests.post(f"{API_URL}/learn", json={
                "topic": selected_name,
                "style": st.session_state.style
            })
            data = r.json()
            st.markdown("### Your Personalised Explanation")
            st.markdown(data["explanation"])
            st.markdown("---")
            if st.button("Get Flashcards for this topic"):
                st.session_state.selected_topic = selected_name
                st.session_state.page = "flashcards"
                st.rerun()

elif page == "flashcards":
    st.title("Flashcards")
    curriculum = get_curriculum()
    all_topics = []
    for lvl in curriculum["levels"]:
        for t in lvl["topics"]:
            all_topics.append((t["id"], t["name"]))

    topic_names = [t[1] for t in all_topics]
    default_idx = 0
    if st.session_state.selected_topic in topic_names:
        default_idx = topic_names.index(st.session_state.selected_topic)

    selected_name = st.selectbox("Select topic for flashcards:", topic_names, index=default_idx)

    if st.button("Generate Flashcards", type="primary"):
        with st.spinner("Generating flashcards from retrieved content..."):
            r = requests.post(f"{API_URL}/flashcards", json={"topic": selected_name})
            data = r.json()
            st.session_state.flashcards = data["flashcards"]
            st.session_state.card_index = 0
            st.session_state.show_back = False
            st.rerun()

    if st.session_state.flashcards:
        cards = st.session_state.flashcards
        idx = st.session_state.card_index
        card = cards[idx]

        st.markdown(f"**Card {idx + 1} of {len(cards)}**")
        st.progress((idx + 1) / len(cards))

        with st.container():
            st.markdown("### Front")
            st.info(card["front"])
            if st.session_state.show_back:
                st.markdown("### Back")
                st.success(card["back"])
                col1, col2, col3 = st.columns(3)
                if col1.button("Previous") and idx > 0:
                    st.session_state.card_index -= 1
                    st.session_state.show_back = False
                    st.rerun()
                if col3.button("Next") and idx < len(cards) - 1:
                    st.session_state.card_index += 1
                    st.session_state.show_back = False
                    st.rerun()
            else:
                if st.button("Reveal Answer", type="primary"):
                    st.session_state.show_back = True
                    st.rerun()

elif page == "adaptive_quiz":
    st.title("Adaptive Quiz")
    st.markdown("This quiz focuses 80% on your weak topics and 20% on next level preview.")

    if not st.session_state.quiz_questions:
        r = requests.get(f"{API_URL}/adaptive-quiz-topics")
        topics_data = r.json()
        topics = topics_data.get("topics", [])

        if not topics:
            st.info("Complete the knowledge assessment first to get your adaptive quiz.")
        else:
            st.markdown("**Your quiz will cover:**")
            for t in topics:
                st.write(f"- {t['name']}")

            if st.button("Generate Adaptive Quiz", type="primary"):
                with st.spinner("Generating your personalised quiz..."):
                    questions = []
                    for topic in topics[:4]:
                        r = requests.post(f"{API_URL}/quiz", json={
                            "topic": topic["name"],
                            "level": "Beginner"
                        })
                        data = r.json()
                        if data["questions"]:
                            q = data["questions"][0]
                            q["topic_id"] = topic["id"]
                            questions.append(q)
                    st.session_state.quiz_questions = questions
                    st.rerun()
    else:
        questions = st.session_state.quiz_questions
        st.markdown(f"**{len(questions)} questions:**")

        for i, q in enumerate(questions):
            st.markdown(f"**Q{i+1}: {q['question']}**")
            options = [f"{k}: {v}" for k, v in q["options"].items()]
            answer = st.radio("", options, key=f"aq_{i}", label_visibility="collapsed")
            if answer:
                st.session_state.quiz_answers[i] = answer[0]
            st.markdown("---")

        if st.button("Submit Quiz", type="primary"):
            correct_count = sum(
                1 for i, q in enumerate(questions)
                if st.session_state.quiz_answers.get(i) == q["answer"]
            )
            total = len(questions)
            score = round((correct_count / total) * 100)
            st.markdown(f"### Your Score: {correct_count}/{total} ({score}%)")

            for i, q in enumerate(questions):
                user_ans = st.session_state.quiz_answers.get(i, "")
                if user_ans == q["answer"]:
                    st.success(f"Q{i+1}: Correct")
                else:
                    st.error(f"Q{i+1}: Wrong — correct answer is {q['answer']}: {q['options'][q['answer']]}")
                    st.info(f"Explanation: {q['explanation']}")

            topic_results = {}
            for i, q in enumerate(questions):
                tid = q["topic_id"]
                if tid not in topic_results:
                    topic_results[tid] = {"correct": 0, "total": 0}
                topic_results[tid]["total"] += 1
                if st.session_state.quiz_answers.get(i) == q["answer"]:
                    topic_results[tid]["correct"] += 1

            for tid, result in topic_results.items():
                requests.post(f"{API_URL}/assess", json={
                    "topic_id": tid,
                    "correct": result["correct"],
                    "total": result["total"]
                })

            st.session_state.quiz_questions = []
            st.session_state.quiz_answers = {}

elif page == "revision":
    st.title("Revision Plan")
    st.markdown("Get a personalised revision plan based on your weak topics.")
    if st.button("Generate My Revision Plan", type="primary"):
        with st.spinner("Creating your personalised revision plan..."):
            r = requests.get(f"{API_URL}/revision-plan")
            data = r.json()
            st.markdown("### Your Personalised Revision Plan")
            st.markdown(data["plan"])