import streamlit as st
import requests

st.set_page_config(
    page_title="AI Chatbot",
    page_icon="🤖",
    layout="centered"
)

if "theme" not in st.session_state:
    st.session_state.theme = "Light"

if "messages" not in st.session_state:
    st.session_state.messages = []

def apply_theme(theme):
    if theme == "Dark":
        st.markdown("""
            <style>
            .stApp {
                background-color: #1e1e1e !important;
                color: #ffffff !important;
            }
            .stChatMessage {
                background-color: #2d2d2d !important;
                border-radius: 10px;
                padding: 10px;
            }
            .stChatMessage p, .stChatMessage div {
                color: #ffffff !important;
            }
            section[data-testid="stSidebar"] {
                background-color: #252526 !important;
                color: #ffffff !important;
            }
            section[data-testid="stSidebar"] p,
            section[data-testid="stSidebar"] label,
            section[data-testid="stSidebar"] span {
                color: #ffffff !important;
            }
            .stChatInputContainer {
                background-color: #2d2d2d !important;
            }
            .stChatInputContainer textarea {
                color: #ffffff !important;
                background-color: #3a3a3a !important;
            }
            .typing-animation {
                color: #aaaaaa !important;
                font-style: italic;
            }
            </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <style>
            .stApp {
                background-color: #f0f2f6 !important;
                color: #000000 !important;
            }
            .stChatMessage {
                background-color: #ffffff !important;
                border-radius: 10px;
                padding: 10px;
                border: 1px solid #e0e0e0;
            }
            .stChatMessage p, .stChatMessage div {
                color: #000000 !important;
            }
            section[data-testid="stSidebar"] {
                background-color: #e8eaf0 !important;
                color: #000000 !important;
            }
            section[data-testid="stSidebar"] p,
            section[data-testid="stSidebar"] label,
            section[data-testid="stSidebar"] span {
                color: #000000 !important;
            }
            .stChatInputContainer {
                background-color: #ffffff !important;
                border-top: 1px solid #e0e0e0;
            }
            .stChatInputContainer textarea {
                color: #000000 !important;
                background-color: #ffffff !important;
            }
            .typing-animation {
                color: #666666 !important;
                font-style: italic;
            }
            </style>
        """, unsafe_allow_html=True)

apply_theme(st.session_state.theme)

# ─── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.title("⚙️ Settings")
    st.divider()

    st.subheader("🎨 Theme")
    theme_choice = st.radio("Select Theme", ["Light", "Dark"],
                             index=0 if st.session_state.theme == "Light" else 1)
    if theme_choice != st.session_state.theme:
        st.session_state.theme = theme_choice
        st.rerun()

    st.divider()

    st.subheader("📜 Chat History")
    if st.session_state.messages:
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(f"💬 {msg['content'][:30]}...")
    else:
        st.info("No chat history yet.")

    st.divider()

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.success("Chat cleared!")
        st.rerun()

# ─── Main Chat UI ──────────────────────────────────────────────
st.title("🤖 AI Chatbot")
st.caption("Powered by Ollama + FastAPI")
st.divider()

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ─── Chat Input ────────────────────────────────────────────────
user_input = st.chat_input("Type your message here...")

if user_input:
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })
    with st.chat_message("user"):
        st.write(user_input)

    # ✅ Typing animation + streaming
    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.markdown(
            "<div class='typing-animation'>🤖 Typing...</div>",
            unsafe_allow_html=True
        )

        try:
            history = [
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages[:-1]
            ]

            # ✅ Stream response word by word
            full_reply = ""
            with requests.post(
                "http://127.0.0.1:8000/chat",
                json={"message": user_input, "history": history},
                stream=True,
                timeout=120
            ) as response:
                for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
                    if chunk:
                        full_reply += chunk
                        # ✅ Update placeholder with each token
                        placeholder.markdown(full_reply)

        except Exception as e:
            full_reply = f"❌ Cannot connect to backend: {str(e)}"
            placeholder.markdown(full_reply)

    st.session_state.messages.append({
        "role": "assistant",
        "content": full_reply
    })