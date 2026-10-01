
import base64
import textwrap
from pathlib import Path

import chromadb
import requests
import streamlit as st


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

OLLAMA_URL = "http://localhost:11434"
CHAT_MODEL = "qwen3.5:4b"
EMBED_MODEL = "nomic-embed-text"

CHROMA_PATH = BASE_DIR / "data" / "chroma_db"
COLLECTION_NAME = "university_documents"

ASSETS_DIR = BASE_DIR / "assets"

BG_IMAGE = ASSETS_DIR / "pokemon_bg.jpg"
PIKACHU_IMAGE = ASSETS_DIR / "pikachu.jpg"
PSYDUCK_IMAGE = ASSETS_DIR / "psyduck.jpg"
JIRACHI_IMAGE = ASSETS_DIR / "jirachi.jpg"


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="ChatBot | ABES Campus AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# HELPERS
# ============================================================

def render_html(html):
    st.html(textwrap.dedent(html))


def image_data_uri(path):
    if not path.exists():
        return ""

    mime = "image/jpeg"
    encoded = base64.b64encode(path.read_bytes()).decode("utf-8")
    return f"data:{mime};base64,{encoded}"


bg_uri = image_data_uri(BG_IMAGE)
pikachu_uri = image_data_uri(PIKACHU_IMAGE)
psyduck_uri = image_data_uri(PSYDUCK_IMAGE)
jirachi_uri = image_data_uri(JIRACHI_IMAGE)


# ============================================================
# CUSTOM CSS
# ============================================================

background_css = (
    f"""
    background-image:
        linear-gradient(
            90deg,
            rgba(5, 7, 20, 0.82),
            rgba(7, 9, 25, 0.55)
        ),
        linear-gradient(
            180deg,
            rgba(7, 9, 20, 0.20),
            rgba(7, 9, 20, 0.78)
        ),
        url("{bg_uri}");
    """
    if bg_uri
    else """
    background:
        radial-gradient(
            circle at 20% 20%,
            rgba(100,70,255,0.18),
            transparent 35%
        ),
        #070914;
    """
)

st.markdown(
    f"""
<style>

.stApp {{
    {background_css}

    background-size: cover;
    background-position: center top;
    background-attachment: fixed;

    color: #f4f7ff;
}}


/* ============================================================
   DARK OVERLAY
   ============================================================ */

.stApp::before {{
    content: "";
    position: fixed;
    inset: 0;

    background:
        radial-gradient(
            circle at 50% 20%,
            rgba(90, 60, 255, 0.12),
            transparent 35%
        ),
        rgba(4, 6, 18, 0.24);

    pointer-events: none;
    z-index: 0;
}}


.main .block-container {{
    position: relative;
    z-index: 1;

    max-width: 1450px;

    padding-top: 1.2rem;
    padding-bottom: 6rem;
}}


/* ============================================================
   STREAMLIT DEFAULTS
   ============================================================ */

#MainMenu {{
    visibility: hidden;
}}

footer {{
    visibility: hidden;
}}

header {{
    background: transparent !important;
}}


/* ============================================================
   SIDEBAR
   ============================================================ */

section[data-testid="stSidebar"] {{
    background:
        linear-gradient(
            180deg,
            rgba(5, 7, 23, 0.97),
            rgba(9, 7, 27, 0.94)
        );

    border-right:
        1px solid rgba(120, 95, 255, 0.28);

    backdrop-filter: blur(18px);
}}

section[data-testid="stSidebar"] > div {{
    padding-top: 1rem;
}}


/* ============================================================
   NORMAL BUTTONS
   ============================================================ */

.stButton > button {{
    width: 100%;

    border-radius: 12px;

    border:
        1px solid rgba(140, 110, 255, 0.25);

    background:
        rgba(10, 12, 30, 0.58);

    color: #e9ecff;

    transition: all 0.22s ease;
}}

.stButton > button:hover {{
    border-color:
        rgba(80, 220, 255, 0.72);

    background:
        rgba(60, 60, 150, 0.35);

    color: white;

    transform: translateY(-2px);

    box-shadow:
        0 0 22px rgba(70, 190, 255, 0.16);
}}


/* ============================================================
   HEADER
   ============================================================ */

.top-header {{
    padding: 13px 18px;

    border:
        1px solid rgba(130, 100, 255, 0.24);

    border-radius: 18px;

    background:
        rgba(6, 8, 25, 0.45);

    backdrop-filter: blur(18px);

    box-shadow:
        0 15px 45px rgba(0,0,0,0.18);
}}


/* ============================================================
   WELCOME / GLASS
   ============================================================ */

.glass-card {{
    border:
        1px solid rgba(130, 110, 255, 0.28);

    background:
        linear-gradient(
            135deg,
            rgba(10, 12, 35, 0.72),
            rgba(17, 20, 48, 0.48)
        );

    backdrop-filter: blur(16px);

    border-radius: 22px;

    box-shadow:
        0 20px 60px rgba(0,0,0,0.24),
        inset 0 1px 0 rgba(255,255,255,0.05);
}}


/* ============================================================
   AI CORE
   ============================================================ */

.ai-core-wrap {{
    height: 250px;

    display: flex;

    justify-content: center;

    align-items: center;

    position: relative;
}}

.ai-orbit {{
    position: absolute;

    width: 270px;
    height: 105px;

    border-radius: 50%;

    border:
        1px solid rgba(100, 200, 255, 0.42);

    transform: rotate(-18deg);

    box-shadow:
        0 0 25px rgba(80, 130, 255, 0.14);
}}

.ai-orbit-two {{
    position: absolute;

    width: 230px;
    height: 90px;

    border-radius: 50%;

    border:
        1px solid rgba(170, 90, 255, 0.42);

    transform: rotate(28deg);
}}

.ai-glow {{
    width: 145px;
    height: 145px;

    border-radius: 50%;

    display: flex;

    align-items: center;

    justify-content: center;

    background:
        radial-gradient(
            circle,
            rgba(140, 100, 255, 0.42),
            rgba(40, 30, 100, 0.35) 52%,
            transparent 72%
        );

    box-shadow:
        0 0 55px rgba(105, 75, 255, 0.45),
        0 0 110px rgba(0, 190, 255, 0.14);

    border:
        1px solid rgba(170, 130, 255, 0.32);

    position: relative;

    z-index: 2;
}}

.ai-image {{
    width: 105px;
    height: 105px;

    object-fit: cover;

    border-radius: 50%;

    border:
        2px solid rgba(180, 150, 255, 0.65);

    box-shadow:
        0 0 28px rgba(130, 100, 255, 0.55);
}}

.ai-fallback {{
    font-size: 52px;
}}


/* ============================================================
   SIDE IMAGE CARDS
   ============================================================ */

.character-card {{
    height: 190px;

    overflow: hidden;

    border-radius: 18px;

    border:
        1px solid rgba(120, 100, 255, 0.28);

    background:
        rgba(8, 10, 28, 0.55);

    position: relative;

    box-shadow:
        0 18px 45px rgba(0,0,0,0.24);
}}

.character-card img {{
    width: 100%;
    height: 100%;

    object-fit: cover;

    opacity: 0.82;
}}

.character-overlay {{
    position: absolute;

    inset: 0;

    background:
        linear-gradient(
            180deg,
            transparent 20%,
            rgba(5,7,20,0.88) 100%
        );
}}

.character-text {{
    position: absolute;

    left: 16px;
    right: 16px;
    bottom: 14px;
}}


/* ============================================================
   QUICK ACTIONS
   ============================================================ */

.quick-card {{
    min-height: 120px;

    padding: 18px 12px;

    border-radius: 18px;

    text-align: center;

    background:
        linear-gradient(
            145deg,
            rgba(20, 18, 58, 0.74),
            rgba(0, 65, 100, 0.28)
        );

    border:
        1px solid rgba(120, 100, 255, 0.30);

    backdrop-filter: blur(12px);

    box-shadow:
        0 12px 35px rgba(0,0,0,0.20);

    transition: all 0.22s ease;
}}

.quick-card:hover {{
    transform: translateY(-4px);

    border-color:
        rgba(75, 220, 255, 0.65);

    box-shadow:
        0 0 30px rgba(70, 180, 255, 0.14);
}}

.quick-icon {{
    font-size: 27px;

    filter:
        drop-shadow(
            0 0 10px
            rgba(120,100,255,0.65)
        );
}}

.quick-card-title {{
    margin-top: 8px;

    font-size: 14px;

    font-weight: 750;

    color: #f6f7ff;
}}

.quick-card-subtitle {{
    margin-top: 5px;

    font-size: 11px;

    color: #8d95b5;
}}

.quick-action-btn button {{
    margin-top: -2px;

    border-radius:
        0 0 15px 15px !important;

    border-top:
        1px solid rgba(130,110,255,0.10) !important;

    background:
        rgba(7,9,25,0.55) !important;

    font-size: 11px !important;
}}


/* ============================================================
   CHAT
   ============================================================ */

div[data-testid="stChatMessage"] {{
    background: transparent;
    border: none;

    padding-top: 7px;
    padding-bottom: 7px;
}}

div[data-testid="stChatMessage"] p {{
    color: #edf0ff;

    font-size: 14px;

    line-height: 1.65;
}}

div[data-testid="stChatMessage"]:has(
    div[data-testid="chatAvatarIcon-user"]
) {{
    background:
        linear-gradient(
            135deg,
            rgba(85,65,180,0.28),
            rgba(0,150,210,0.10)
        );

    border:
        1px solid rgba(120,100,255,0.24);

    border-radius: 18px;

    margin:
        8px 0 8px 8%;

    padding:
        12px 16px;

    backdrop-filter: blur(12px);
}}

div[data-testid="stChatMessage"]:has(
    div[data-testid="chatAvatarIcon-assistant"]
) {{
    background:
        linear-gradient(
            135deg,
            rgba(15,18,48,0.70),
            rgba(60,40,110,0.30)
        );

    border:
        1px solid rgba(100,210,255,0.16);

    border-radius: 18px;

    margin:
        8px 8% 8px 0;

    padding:
        12px 16px;

    backdrop-filter: blur(12px);
}}


/* ============================================================
   SOURCES
   ============================================================ */

.source-label {{
    margin-top: 10px;

    margin-bottom: 6px;

    font-size: 10px;

    letter-spacing: 1.5px;

    color: #7f88a8;
}}

.source-box {{
    padding: 8px 11px;

    border-radius: 9px;

    background:
        rgba(80,80,180,0.10);

    border:
        1px solid rgba(100,180,255,0.12);

    font-size: 11px;

    color: #a1a8c2;
}}


/* ============================================================
   CHAT INPUT
   ============================================================ */

div[data-testid="stChatInput"] {{
    border-color:
        rgba(100, 190, 255, 0.42);

    background:
        rgba(7, 9, 25, 0.72);

    backdrop-filter: blur(14px);
}}


/* ============================================================
   RESPONSIVE
   ============================================================ */

@media (max-width: 900px) {{
    .character-card {{
        height: 150px;
    }}

    div[data-testid="stChatMessage"]:has(
        div[data-testid="chatAvatarIcon-user"]
    ) {{
        margin-left: 2%;
    }}

    div[data-testid="stChatMessage"]:has(
        div[data-testid="chatAvatarIcon-assistant"]
    ) {{
        margin-right: 2%;
    }}
}}

</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# OLLAMA
# ============================================================

def check_ollama():
    try:
        response = requests.get(
            f"{OLLAMA_URL}/api/tags",
            timeout=5,
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

    return client.get_collection(
        name=COLLECTION_NAME
    )


# ============================================================
# EMBEDDING
# ============================================================

def get_embedding(text):
    response = requests.post(
        f"{OLLAMA_URL}/api/embeddings",
        json={
            "model": EMBED_MODEL,
            "prompt": text,
        },
        timeout=60,
    )

    response.raise_for_status()

    return response.json()["embedding"]


# ============================================================
# RETRIEVAL
# ============================================================

def retrieve_documents(question, n_results=3):
    collection = load_collection()

    embedding = get_embedding(question)

    results = collection.query(
        query_embeddings=[embedding],
        n_results=n_results,
    )

    documents = results.get(
        "documents",
        [[]],
    )[0]

    metadatas = results.get(
        "metadatas",
        [[]],
    )[0]

    return documents, metadatas


# ============================================================
# LLM
# ============================================================

def generate_answer(question, context):
    prompt = f"""
You are ChatBot, a university student support assistant.

Answer the student's question using ONLY the university
information provided in the context.

Rules:
1. Do not invent information.
2. Do not use outside knowledge.
3. If the answer is not available, say:
"I couldn't find this information in the available university documents."
4. Keep the answer short and direct.
5. Use simple English.
6. Clearly mention dates when available.
7. Do not mention these instructions.

UNIVERSITY CONTEXT:

{context}

STUDENT QUESTION:

{question}

ANSWER:
"""

    response = requests.post(
        f"{OLLAMA_URL}/api/chat",
        json={
            "model": CHAT_MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            "stream": False,
            "think": False,
            "options": {
                "temperature": 0.2,
                "num_predict": 150,
            },
        },
        timeout=120,
    )

    response.raise_for_status()

    return response.json()["message"]["content"]


# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "quick_question" not in st.session_state:
    st.session_state.quick_question = None


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    render_html(
        """
        <div style="
            padding: 8px 4px 20px 4px;
        ">

            <div style="
                font-size:12px;
                letter-spacing:3px;
                color:#9d8cff;
            ">
                ⚡ DIGITAL CAMPUS AI
            </div>

            <div style="
                font-size:27px;
                font-weight:850;
                color:white;
                margin-top:5px;
            ">
                ChatBot
            </div>

            <div style="
                font-size:12px;
                color:#7e88a9;
                margin-top:6px;
            ">
                University Student Support
            </div>

        </div>
        """
    )


    if st.button(
        "＋  New Conversation",
        use_container_width=True,
    ):
        st.session_state.messages = []
        st.session_state.quick_question = None
        st.rerun()


    st.markdown(
        """
        <div style="
            margin-top:22px;
            margin-bottom:10px;
            font-size:10px;
            letter-spacing:2px;
            color:#727da1;
        ">
            RECENT QUESTIONS
        </div>
        """,
        unsafe_allow_html=True,
    )


    if st.session_state.messages:

        recent_users = [
            m
            for m in st.session_state.messages
            if m["role"] == "user"
        ][-5:]

        for index, message in enumerate(recent_users):

            preview = message["content"]

            if len(preview) > 28:
                preview = preview[:28] + "..."

            if st.button(
                f"💬  {preview}",
                key=f"recent_{index}",
                use_container_width=True,
            ):
                st.session_state.quick_question = (
                    message["content"]
                )
                st.rerun()

    else:

        st.markdown(
            """
            <div style="
                color:#56617f;
                font-size:12px;
                padding:7px 2px;
            ">
                No conversations yet
            </div>
            """,
            unsafe_allow_html=True,
        )


    # --------------------------------------------------------
    # PIKACHU CARD
    # --------------------------------------------------------

    if pikachu_uri:

        render_html(
            f"""
            <div class="character-card"
                 style="margin-top:25px;">

                <img src="{pikachu_uri}">

                <div class="character-overlay"></div>

                <div class="character-text">

                    <div style="
                        font-size:10px;
                        letter-spacing:1.5px;
                        color:#9e8cff;
                    ">
                        CAMPUS AI
                    </div>

                    <div style="
                        font-size:16px;
                        font-weight:750;
                        margin-top:4px;
                    ">
                        ABES Student Support
                    </div>

                    <div style="
                        font-size:11px;
                        color:#a2aac5;
                        margin-top:5px;
                    ">
                        Powered by local AI
                    </div>

                    <div style="
                        font-size:10px;
                        color:#66f5bf;
                        margin-top:9px;
                    ">
                        ● SYSTEM ONLINE
                    </div>

                </div>

            </div>
            """
        )

    else:

        st.info("Add pikachu.jpg to the assets folder.")


    st.markdown(
        "<div style='height:14px'></div>",
        unsafe_allow_html=True,
    )


    if st.button(
        "Clear Conversation",
        use_container_width=True,
    ):
        st.session_state.messages = []
        st.rerun()


# ============================================================
# TOP HEADER
# ============================================================

render_html(
    """
    <div class="top-header">

        <div style="
            display:flex;
            justify-content:space-between;
            align-items:center;
        ">

            <div>

                <div style="
                    font-size:11px;
                    letter-spacing:3px;
                    color:#a18cff;
                ">
                    ⚡ CHATBOT
                </div>

                <div style="
                    font-size:13px;
                    color:#8992b0;
                    margin-top:4px;
                ">
                    DIGITAL CAMPUS INTELLIGENCE
                </div>

            </div>


            <div style="
                padding:8px 13px;
                border-radius:20px;

                border:
                    1px solid
                    rgba(80,255,190,0.24);

                background:
                    rgba(60,255,180,0.06);

                color:#6ff5bf;

                font-size:10px;
                letter-spacing:1px;
            ">
                ● AI SYSTEM ONLINE
            </div>

        </div>

    </div>
    """
)


# ============================================================
# TITLE
# ============================================================

render_html(
    """
    <div style="
        text-align:center;
        margin-top:30px;
        margin-bottom:5px;
    ">

        <div style="
            font-size:11px;
            letter-spacing:4px;
            color:#c1b8e8;
        ">
            UNIVERSITY INTELLIGENCE
        </div>

        <div style="
            font-size:38px;
            font-weight:900;
            margin-top:8px;

            background:
                linear-gradient(
                    90deg,
                    #ffffff,
                    #b49cff,
                    #63e8ff
                );

            -webkit-background-clip:text;
            -webkit-text-fill-color:transparent;

            text-shadow:
                0 0 30px rgba(120,90,255,0.18);
        ">
            How can I help you today?
        </div>

    </div>
    """
)


# ============================================================
# AI CORE + JIRACHI
# ============================================================

if jirachi_uri:

    render_html(
        f"""
        <div class="ai-core-wrap">

            <div class="ai-orbit"></div>

            <div class="ai-orbit-two"></div>

            <div class="ai-glow">

                <img
                    class="ai-image"
                    src="{jirachi_uri}"
                >

            </div>

        </div>
        """
    )

else:

    render_html(
        """
        <div class="ai-core-wrap">

            <div class="ai-glow">
                <div class="ai-fallback">
                    ✦
                </div>
            </div>

        </div>
        """
    )


# ============================================================
# WELCOME + PSYDUCK
# ============================================================

welcome_left = (
    f"""
    <img
        src="{pikachu_uri}"
        style="
            width:100%;
            height:150px;
            object-fit:cover;
            border-radius:15px;
            opacity:0.88;
        "
    >
    """
    if pikachu_uri
    else
    """
    <div style="
        height:150px;
        display:flex;
        align-items:center;
        justify-content:center;
        font-size:40px;
    ">
        ⚡
    </div>
    """
)

welcome_right = (
    f"""
    <img
        src="{psyduck_uri}"
        style="
            width:100%;
            height:150px;
            object-fit:cover;
            border-radius:15px;
            opacity:0.88;
        "
    >
    """
    if psyduck_uri
    else
    """
    <div style="
        height:150px;
        display:flex;
        align-items:center;
        justify-content:center;
        font-size:40px;
    ">
        💧
    </div>
    """
)


render_html(
    f"""
    <div class="glass-card"
         style="
            padding:16px;
            margin-bottom:28px;
         ">

        <div style="
            display:grid;
            grid-template-columns: 170px 1fr 170px;
            gap:18px;
            align-items:center;
        ">

            <div>
                {welcome_left}
            </div>


            <div style="
                padding:8px 10px;
            ">

                <div style="
                    font-size:17px;
                    font-weight:800;
                    color:#ffffff;
                ">
                    Welcome to ABES Campus AI
                </div>

                <div style="
                    font-size:13px;
                    line-height:1.7;
                    color:#9ba4c2;
                    margin-top:8px;
                ">
                    Ask questions about academic calendars,
                    examinations and other university
                    information available in the knowledge base.
                </div>

                <div style="
                    margin-top:12px;
                    font-size:10px;
                    letter-spacing:1.4px;
                    color:#6beec1;
                ">
                    ✦ RAG-POWERED UNIVERSITY ASSISTANT
                </div>

            </div>


            <div>
                {welcome_right}
            </div>

        </div>

    </div>
    """
)


# ============================================================
# QUICK ACTIONS
# ============================================================

st.markdown(
    "### ✦ QUICK ACTIONS"
)

st.markdown(
    "<div style='height:5px'></div>",
    unsafe_allow_html=True,
)


col1, col2, col3, col4 = st.columns(4)


# ============================================================
# CALENDAR
# ============================================================

with col1:

    render_html(
        """
        <div class="quick-card">

            <div class="quick-icon">📅</div>

            <div class="quick-card-title">
                Academic Calendar
            </div>

            <div class="quick-card-subtitle">
                View academic schedule
            </div>

        </div>
        """
    )

    st.markdown(
        '<div class="quick-action-btn">',
        unsafe_allow_html=True,
    )

    if st.button(
        "Ask Calendar  →",
        key="quick_calendar",
        use_container_width=True,
    ):
        st.session_state.quick_question = (
            "What information is available in the academic calendar?"
        )
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# EXAMS
# ============================================================

with col2:

    render_html(
        """
        <div class="quick-card">

            <div class="quick-icon">📝</div>

            <div class="quick-card-title">
                Exam Dates
            </div>

            <div class="quick-card-subtitle">
                Check upcoming exams
            </div>

        </div>
        """
    )

    st.markdown(
        '<div class="quick-action-btn">',
        unsafe_allow_html=True,
    )

    if st.button(
        "Ask Exams  →",
        key="quick_exam",
        use_container_width=True,
    ):
        st.session_state.quick_question = (
            "When are the upcoming exams for B.Tech 3rd semester?"
        )
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# HOSTEL
# ============================================================

with col3:

    render_html(
        """
        <div class="quick-card">

            <div class="quick-icon">🏠</div>

            <div class="quick-card-title">
                Hostel Rules
            </div>

            <div class="quick-card-subtitle">
                Ask about hostel policies
            </div>

        </div>
        """
    )

    st.markdown(
        '<div class="quick-action-btn">',
        unsafe_allow_html=True,
    )

    if st.button(
        "Ask Hostel  →",
        key="quick_hostel",
        use_container_width=True,
    ):
        st.session_state.quick_question = (
            "What are the hostel rules?"
        )
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# CAMPUS
# ============================================================

with col4:

    render_html(
        """
        <div class="quick-card">

            <div class="quick-icon">🏫</div>

            <div class="quick-card-title">
                Campus
            </div>

            <div class="quick-card-subtitle">
                Explore campus information
            </div>

        </div>
        """
    )

    st.markdown(
        '<div class="quick-action-btn">',
        unsafe_allow_html=True,
    )

    if st.button(
        "Ask Campus  →",
        key="quick_campus",
        use_container_width=True,
    ):
        st.session_state.quick_question = (
            "What university information is available in the documents?"
        )
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# CHAT HISTORY
# ============================================================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

        if (
            message["role"] == "assistant"
            and message.get("sources")
        ):

            st.markdown(
                """
                <div class="source-label">
                    SOURCES
                </div>
                """,
                unsafe_allow_html=True,
            )

            for source in message["sources"]:

                st.markdown(
                    f"""
                    <div class="source-box">
                        📄 {source}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


# ============================================================
# CHAT INPUT
# ============================================================

manual_question = st.chat_input(
    "Ask ChatBot anything about ABES..."
)


if st.session_state.quick_question:

    question = st.session_state.quick_question

    st.session_state.quick_question = None

elif manual_question:

    question = manual_question

else:

    question = None


# ============================================================
# PROCESS QUESTION
# ============================================================

if question:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question,
        }
    )

    with st.chat_message("user"):

        st.markdown(question)


    with st.chat_message("assistant"):

        with st.spinner("✦ ChatBot is thinking..."):

            try:

                if not check_ollama():

                    answer = (
                        "Ollama is not running. "
                        "Please start Ollama and try again."
                    )

                    sources = []

                else:

                    documents, metadatas = retrieve_documents(
                        question,
                        n_results=3,
                    )

                    context = (
                        "\n\n---\n\n"
                        .join(documents)
                    )

                    answer = generate_answer(
                        question,
                        context,
                    )

                    sources = []

                    for metadata in metadatas:

                        if metadata:

                            source_name = metadata.get(
                                "source",
                                "University document",
                            )

                            if source_name not in sources:

                                sources.append(
                                    source_name
                                )


                st.markdown(answer)


                if sources:

                    st.markdown(
                        """
                        <div class="source-label">
                            SOURCES
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    for source in sources:

                        st.markdown(
                            f"""
                            <div class="source-box">
                                📄 {source}
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )


            except Exception as e:

                answer = (
                    "Sorry, something went wrong while "
                    "processing your question."
                )

                sources = []

                st.error(
                    f"Technical error: {e}"
                )


    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
            "sources": sources,
        }
    )

    st.rerun()
