import streamlit as st
import requests
import chromadb
from pathlib import Path
import textwrap


# ============================================================
# CONFIGURATION
# ============================================================

OLLAMA_URL = "http://localhost:11434"

EMBEDDING_MODEL = "nomic-embed-text:latest"
CHAT_MODEL = "qwen3.5:4b"

# app.py is inside:
# ChatBot/backend/app.py
#
# parent.parent = ChatBot/
BASE_DIR = Path(__file__).resolve().parent.parent

# ChromaDB:
# ChatBot/data/chroma_db/
CHROMA_PATH = BASE_DIR / "data" / "chroma_db"


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="ChatBot — Digital Campus AI",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# HTML HELPER
# ============================================================
# This fixes the issue where Streamlit was displaying
# HTML code as plain text.

def render_html(html):
    st.html(textwrap.dedent(html))

# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
<style>

/* ==========================================================
   GLOBAL
   ========================================================== */

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

header {
    visibility: hidden;
}

.stApp {
    background:
        radial-gradient(
            circle at 50% 15%,
            rgba(91, 33, 182, 0.14),
            transparent 32%
        ),
        radial-gradient(
            circle at 85% 85%,
            rgba(8, 145, 178, 0.08),
            transparent 30%
        ),
        #05050b;

    color: #f5f3ff;
}

.block-container {
    padding-top: 1rem !important;
    padding-bottom: 1rem !important;
    max-width: 1500px !important;
}


/* ==========================================================
   TOP BRAND
   ========================================================== */

.brand-wrapper {
    display: flex;
    align-items: center;
    justify-content: space-between;

    padding: 10px 22px 14px 22px;

    border-bottom: 1px solid rgba(255,255,255,0.08);

    background: rgba(5,5,11,0.65);

    backdrop-filter: blur(20px);

    margin-bottom: 15px;
}

.brand-left {
    display: flex;
    align-items: center;
    gap: 12px;
}

.brand-icon {
    width: 42px;
    height: 42px;

    display: flex;
    align-items: center;
    justify-content: center;

    border-radius: 13px;

    background:
        linear-gradient(
            135deg,
            rgba(139,92,246,0.35),
            rgba(34,211,238,0.12)
        );

    border: 1px solid rgba(167,139,250,0.28);

    box-shadow:
        0 0 28px rgba(139,92,246,0.20);

    color: #a78bfa;

    font-size: 22px;
}

.brand-name {
    font-size: 17px;
    font-weight: 700;
    letter-spacing: 0.5px;
}

.brand-subtitle {
    font-size: 8px;
    color: #a78bfa;
    letter-spacing: 2px;
    font-weight: 600;
}

.system-online {
    display: flex;
    align-items: center;
    gap: 8px;

    color: #66647a;

    font-size: 9px;
    letter-spacing: 1.7px;
}

.online-dot {
    width: 7px;
    height: 7px;

    border-radius: 50%;

    background: #34d399;

    box-shadow:
        0 0 12px #34d399;
}


/* ==========================================================
   SIDEBAR
   ========================================================== */

section[data-testid="stSidebar"] {
    background:
        rgba(9,9,20,0.90);

    border-right:
        1px solid rgba(255,255,255,0.08);
}

section[data-testid="stSidebar"] > div {
    padding-top: 1rem;
}

section[data-testid="stSidebar"] button {
    border-radius: 12px !important;

    border:
        1px solid rgba(255,255,255,0.08) !important;

    background:
        rgba(255,255,255,0.025) !important;

    color: #a7a4b8 !important;

    transition: 0.25s !important;
}

section[data-testid="stSidebar"] button:hover {
    border-color:
        rgba(139,92,246,0.35) !important;

    background:
        rgba(139,92,246,0.10) !important;

    color: white !important;
}


/* ==========================================================
   SIDEBAR CARD
   ========================================================== */

.sidebar-card {
    padding: 15px;

    border-radius: 15px;

    margin-top: 20px;

    background:
        linear-gradient(
            135deg,
            rgba(139,92,246,0.10),
            rgba(34,211,238,0.04)
        );

    border:
        1px solid rgba(255,255,255,0.08);
}

.sidebar-card-title {
    color: white;

    font-size: 11px;

    font-weight: 600;

    margin-bottom: 4px;
}

.sidebar-card-text {
    color: #66647a;

    font-size: 9px;

    line-height: 1.5;
}

.sidebar-footer {
    text-align: center;

    margin-top: 20px;

    color: #444252;

    font-size: 7px;

    letter-spacing: 1.3px;
}


/* ==========================================================
   WORKSPACE
   ========================================================== */

.workspace {
    padding: 5px 30px 0 30px;
}

.workspace-label {
    color: #a78bfa;

    font-size: 8px;

    letter-spacing: 2px;

    font-weight: 700;
}

.workspace-title {
    font-size: 25px;

    font-weight: 500;

    margin-top: 5px;

    color: rgba(255,255,255,0.92);
}

.workspace-badge {
    display: inline-block;

    margin-top: 8px;

    padding: 5px 11px;

    border-radius: 20px;

    border: 1px solid rgba(255,255,255,0.08);

    background:
        rgba(255,255,255,0.025);

    color: #a7a4b8;

    font-size: 8px;

    letter-spacing: 1px;
}

.workspace-badge span {
    color: #34d399;

    margin-right: 4px;
}


/* ==========================================================
   AI CORE
   ========================================================== */

.ai-core {
    height: 220px;

    display: flex;

    align-items: center;

    justify-content: center;

    position: relative;

    overflow: hidden;
}

.core-glow {
    position: absolute;

    width: 170px;
    height: 170px;

    border-radius: 50%;

    background:
        radial-gradient(
            circle,
            rgba(139,92,246,0.25),
            rgba(34,211,238,0.07),
            transparent 70%
        );

    filter: blur(12px);

    animation: glow 4s ease-in-out infinite;
}

.core {
    width: 115px;
    height: 115px;

    border-radius: 50%;

    position: relative;

    display: flex;

    align-items: center;

    justify-content: center;

    background:
        radial-gradient(
            circle,
            rgba(34,211,238,0.18),
            rgba(139,92,246,0.12) 45%,
            rgba(5,5,11,0.2) 70%
        );

    border:
        1px solid rgba(167,139,250,0.45);

    box-shadow:
        0 0 35px rgba(139,92,246,0.28),
        inset 0 0 30px rgba(34,211,238,0.10);

    animation:
        coreFloat 4s ease-in-out infinite;

    z-index: 3;
}

.core::before {
    content: "";

    position: absolute;

    inset: -20px;

    border-radius: 50%;

    border:
        1px solid rgba(139,92,246,0.25);

    animation:
        orbit 8s linear infinite;
}

.core::after {
    content: "";

    position: absolute;

    inset: -38px;

    border-radius: 50%;

    border:
        1px solid rgba(34,211,238,0.13);

    animation:
        orbit 12s linear infinite reverse;
}

.core-symbol {
    font-size: 35px;

    color: #a78bfa;

    text-shadow:
        0 0 20px rgba(167,139,250,0.8);
}

.core-status {
    position: absolute;

    bottom: 8px;

    color: #66647a;

    font-size: 7px;

    letter-spacing: 2px;
}

.core-status-dot {
    display: inline-block;

    width: 5px;
    height: 5px;

    border-radius: 50%;

    background: #22d3ee;

    box-shadow:
        0 0 10px #22d3ee;

    margin-right: 6px;
}


/* ==========================================================
   QUICK ACTIONS
   ========================================================== */

.quick-title {
    text-align: center;

    color: #66647a;

    font-size: 8px;

    letter-spacing: 1.5px;

    margin-bottom: 8px;
}

.quick-card {
    padding: 12px 10px;

    text-align: center;

    border-radius: 13px;

    background:
        rgba(255,255,255,0.025);

    border:
        1px solid rgba(255,255,255,0.08);

    color: #a7a4b8;

    font-size: 9px;

    transition: 0.25s;
}

.quick-icon {
    display: block;

    color: #a78bfa;

    font-size: 17px;

    margin-bottom: 3px;
}


/* ==========================================================
   CHAT MESSAGES
   ========================================================== */

div[data-testid="stChatMessage"] {
    background:
        rgba(255,255,255,0.025) !important;

    border:
        1px solid rgba(255,255,255,0.07) !important;

    border-radius: 17px !important;

    margin-bottom: 12px !important;

    padding: 5px !important;
}

div[data-testid="stChatMessage"] p {
    color: #dedbea;

    font-size: 13px;

    line-height: 1.7;
}


/* ==========================================================
   CHAT INPUT
   ========================================================== */

div[data-testid="stChatInput"] {
    border:
        1px solid rgba(167,139,250,0.18) !important;

    border-radius: 18px !important;

    background:
        rgba(13,13,26,0.90) !important;

    box-shadow:
        0 20px 60px rgba(0,0,0,0.30) !important;
}

div[data-testid="stChatInput"]:focus-within {
    border-color:
        rgba(139,92,246,0.45) !important;

    box-shadow:
        0 0 0 3px rgba(139,92,246,0.05),
        0 20px 70px rgba(91,33,182,0.15) !important;
}


/* ==========================================================
   SOURCE
   ========================================================== */

.source-box {
    margin-top: 8px;

    padding: 9px 13px;

    border-radius: 10px;

    background:
        rgba(139,92,246,0.055);

    border:
        1px solid rgba(139,92,246,0.12);

    color: #8b88a0;

    font-size: 9px;
}


/* ==========================================================
   ANIMATIONS
   ========================================================== */

@keyframes glow {
    0%,100% {
        transform: scale(0.9);
        opacity: 0.6;
    }

    50% {
        transform: scale(1.1);
        opacity: 1;
    }
}

@keyframes coreFloat {
    0%,100% {
        transform: translateY(0);
    }

    50% {
        transform: translateY(-7px);
    }
}

@keyframes orbit {
    from {
        transform: rotate(0deg);
    }

    to {
        transform: rotate(360deg);
    }
}


/* ==========================================================
   MOBILE
   ========================================================== */

@media (max-width: 700px) {

    .brand-wrapper {
        padding-left: 10px;
        padding-right: 10px;
    }

    .system-online {
        display: none;
    }

    .workspace {
        padding-left: 10px;
        padding-right: 10px;
    }

    .workspace-title {
        font-size: 20px;
    }

    .ai-core {
        height: 190px;
    }

    .core {
        width: 90px;
        height: 90px;
    }

    .core-symbol {
        font-size: 27px;
    }
}

</style>
""",
    unsafe_allow_html=True
)


# ============================================================
# OLLAMA STATUS
# ============================================================

def check_ollama():

    try:

        response = requests.get(
            f"{OLLAMA_URL}/api/tags",
            timeout=5
        )

        return response.status_code == 200

    except Exception:

        return False


# ============================================================
# CHROMA
# ============================================================

@st.cache_resource
def load_collection():

    client = chromadb.PersistentClient(
        path=str(CHROMA_PATH)
    )

    collection = client.get_collection(
        name="university_documents"
    )

    return collection


# ============================================================
# EMBEDDING
# ============================================================

def get_embedding(text):

    response = requests.post(
        f"{OLLAMA_URL}/api/embeddings",
        json={
            "model": EMBEDDING_MODEL,
            "prompt": text
        },
        timeout=120
    )

    response.raise_for_status()

    return response.json()["embedding"]


# ============================================================
# RAG RETRIEVAL
# ============================================================

def retrieve_documents(question, top_k=3):

    collection = load_collection()

    query_embedding = get_embedding(question)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    documents = results.get(
        "documents",
        [[]]
    )[0]

    metadatas = results.get(
        "metadatas",
        [[]]
    )[0]

    return documents, metadatas


# ============================================================
# QWEN ANSWER
# ============================================================

def generate_answer(question, documents):

    if not documents:

        return (
            "I couldn't find this information in the "
            "available university documents."
        )

    context = "\n\n".join(
        [
            f"DOCUMENT SECTION {i + 1}:\n{doc}"
            for i, doc in enumerate(documents)
        ]
    )

    prompt = f"""
You are an AI Student Support Assistant for ABES Engineering College.

Answer the student's question using ONLY the university document
context provided below.

Rules:
- Do not invent information.
- Do not use outside knowledge.
- Keep the answer short and direct.
- If the answer is not available, say:
  "I couldn't find this information in the available university documents."
- Do not explain your reasoning.

UNIVERSITY DOCUMENT CONTEXT:

{context}

STUDENT QUESTION:

{question}

FINAL ANSWER:
"""

    response = requests.post(
        f"{OLLAMA_URL}/api/chat",
        json={
            "model": CHAT_MODEL,

            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            "think": False,

            "stream": False,

            "options": {
                "temperature": 0.2,
                "num_predict": 150
            }
        },

        timeout=180
    )

    response.raise_for_status()

    return response.json()["message"]["content"].strip()


# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:

    st.session_state.messages = []


# ============================================================
# TOP HEADER
# ============================================================

ollama_online = check_ollama()

status_text = (
    "AI SYSTEM ONLINE"
    if ollama_online
    else "AI SYSTEM OFFLINE"
)

render_html(
    f"""
    <div class="brand-wrapper">

        <div class="brand-left">

            <div class="brand-icon">
                ✦
            </div>

            <div>

                <div class="brand-name">
                    ChatBot
                </div>

                <div class="brand-subtitle">
                    DIGITAL CAMPUS AI
                </div>

            </div>

        </div>

        <div class="system-online">

            <span class="online-dot"></span>

            {status_text}

        </div>

    </div>
    """
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        """
        <div style="
            color:#a78bfa;
            font-size:9px;
            letter-spacing:2px;
            font-weight:700;
            margin-bottom:12px;
        ">
            CAMPUS ASSISTANT
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.button(
        "＋  New Conversation",
        use_container_width=True
    ):

        st.session_state.messages = []

        st.rerun()

    st.markdown(
        """
        <div style="
            margin-top:25px;
            margin-bottom:10px;
            color:#66647a;
            font-size:8px;
            letter-spacing:1.7px;
            font-weight:600;
        ">
            CONVERSATIONS
        </div>
        """,
        unsafe_allow_html=True
    )

    # Recent questions
    if st.session_state.messages:

        user_questions = [
            message["content"]
            for message in st.session_state.messages
            if message["role"] == "user"
        ]

        for question in user_questions[-5:]:

            short_question = question[:35]

            if len(question) > 35:
                short_question += "..."

            render_html(
                f"""
                <div style="
                    padding:10px;
                    margin-bottom:5px;
                    border-radius:10px;
                    color:#a7a4b8;
                    background:rgba(255,255,255,0.025);
                    border:1px solid rgba(255,255,255,0.05);
                    font-size:9px;
                ">
                    💬 {short_question}
                </div>
                """
            )

    else:

        render_html(
            """
            <div style="
                color:#444252;
                font-size:9px;
                padding:10px;
            ">
                No conversations yet.
            </div>
            """
        )

    render_html(
        """
        <div class="sidebar-card">

            <div class="sidebar-card-title">
                ◈ ABES Campus AI
            </div>

            <div class="sidebar-card-text">
                Your intelligent student companion
            </div>

        </div>

        <div class="sidebar-footer">
            SECURE AI &nbsp; • &nbsp; RAG ENABLED
        </div>
        """
    )

    st.divider()

    if st.button(
        "🗑️ Clear Conversation",
        use_container_width=True
    ):

        st.session_state.messages = []

        st.rerun()


# ============================================================
# MAIN WORKSPACE
# ============================================================

render_html(
    """
    <div class="workspace">

        <div class="workspace-label">
            UNIVERSITY INTELLIGENCE
        </div>

        <div class="workspace-title">
            How can I help you today?
        </div>

        <div class="workspace-badge">
            <span>●</span> ABES
        </div>

    </div>
    """
)


# ============================================================
# AI CORE
# ============================================================

render_html(
    """
    <div class="ai-core">

        <div class="core-glow"></div>

        <div class="core">
            <div class="core-symbol">
                ✦
            </div>
        </div>

        <div class="core-status">
            <span class="core-status-dot"></span>
            AI CORE READY
        </div>

    </div>
    """
)


# ============================================================
# WELCOME CARD
# ============================================================

if not st.session_state.messages:

    render_html(
        """
        <div style="
            max-width:650px;
            margin:0 auto 18px auto;
            padding:15px 18px;
            display:flex;
            gap:13px;
            border:1px solid rgba(255,255,255,0.09);
            border-radius:16px;
            background:rgba(255,255,255,0.025);
        ">

            <div style="
                color:#a78bfa;
                font-size:21px;
            ">
                ✦
            </div>

            <div>

                <div style="
                    color:white;
                    font-size:12px;
                    margin-bottom:3px;
                ">
                    Welcome to ChatBot
                </div>

                <div style="
                    color:#66647a;
                    font-size:10px;
                ">
                    Ask me about academics, schedules,
                    examinations, campus information and more.
                </div>

            </div>

        </div>
        """
    )


# ============================================================
# QUICK ACTIONS
# ============================================================

render_html(
    """
    <div class="quick-title">
        QUICK ACTIONS
    </div>
    """
)

quick_col1, quick_col2, quick_col3, quick_col4 = st.columns(4)

with quick_col1:

    render_html(
        """
        <div class="quick-card">
            <span class="quick-icon">◫</span>
            Academic Calendar
        </div>
        """
    )

with quick_col2:

    render_html(
        """
        <div class="quick-card">
            <span class="quick-icon">◇</span>
            Exam Dates
        </div>
        """
    )

with quick_col3:

    render_html(
        """
        <div class="quick-card">
            <span class="quick-icon">⌂</span>
            Hostel Rules
        </div>
        """
    )

with quick_col4:

    render_html(
        """
        <div class="quick-card">
            <span class="quick-icon">◎</span>
            Campus
        </div>
        """
    )


# ============================================================
# CHAT HISTORY
# ============================================================

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )

        if message["role"] == "assistant":

            sources = message.get(
                "sources",
                []
            )

            if sources:

                render_html(
                    f"""
                    <div class="source-box">
                        📚 <b>Source:</b>
                        {", ".join(sources)}
                    </div>
                    """
                )


# ============================================================
# CHAT INPUT
# ============================================================

question = st.chat_input(
    "Ask ChatBot anything about ABES..."
)


# ============================================================
# PROCESS QUESTION
# ============================================================

if question:

    # --------------------------------------------------------
    # USER MESSAGE
    # --------------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )

    with st.chat_message("user"):

        st.markdown(question)

    # --------------------------------------------------------
    # ASSISTANT
    # --------------------------------------------------------

    with st.chat_message("assistant"):

        try:

            with st.spinner(
                "Searching university knowledge..."
            ):

                # RAG retrieval
                documents, metadatas = retrieve_documents(
                    question,
                    top_k=3
                )

                # AI answer
                answer = generate_answer(
                    question,
                    documents
                )

            # Display answer
            st.markdown(answer)

            # ------------------------------------------------
            # SOURCES
            # ------------------------------------------------

            sources = []

            for metadata in metadatas:

                if metadata:

                    source = metadata.get(
                        "source",
                        "University Document"
                    )

                    if source not in sources:

                        sources.append(source)

            if sources:

                render_html(
                    f"""
                    <div class="source-box">
                        📚 <b>Source:</b>
                        {", ".join(sources)}
                    </div>
                    """
                )

            # ------------------------------------------------
            # SAVE RESPONSE
            # ------------------------------------------------

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": answer,
                    "sources": sources
                }
            )

        except requests.exceptions.ConnectionError:

            error_message = (
                "⚠️ **Ollama is not running.**\n\n"
                "Please start Ollama and try again."
            )

            st.error(error_message)

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": error_message,
                    "sources": []
                }
            )

        except Exception as e:

            error_message = (
                "⚠️ **Something went wrong.**\n\n"
                f"`{str(e)}`"
            )

            st.error(error_message)

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": error_message,
                    "sources": []
                }
            )