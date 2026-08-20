import streamlit as st
from backend import (
    chatbot, llm, base_llm, get_all_threads, save_chat_title, delete_chat,
    process_pdf_for_thread, load_faiss_for_thread, retrieve_from_documents,
    _CURRENT_THREAD_ID, get_all_user_memories, delete_user_memory,
    clear_all_user_memories
)
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
import uuid
import os
import tempfile
import backend
import json
from pathlib import Path

# ======================= Page Config =======================
st.set_page_config(
    page_title="NeuralChat AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ======================= 21st.dev Inspired CSS =======================
st.markdown("""
<style>
/* ===== Google Fonts: Inter Display + JetBrains Mono ===== */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&display=swap');

/* ===== Lovable.dev Vibrant Mesh Theme Tokens ===== */
:root, [data-theme="dark"] {
    --bg-primary: #0a0a0c;
    --bg-secondary: #121216;
    --bg-card: rgba(18, 18, 24, 0.85);
    --bg-glass: rgba(255, 255, 255, 0.04);
    --bg-glass-hover: rgba(255, 255, 255, 0.08);
    --border-subtle: rgba(255, 255, 255, 0.08);
    --border-active: rgba(236, 72, 153, 0.5);
    --text-primary: #ffffff;
    --text-secondary: #94a3b8;
    --text-muted: #64748b;
    --sidebar-bg: #0d0d11;
    --user-msg-bg: linear-gradient(135deg, rgba(236, 72, 153, 0.25), rgba(99, 102, 241, 0.25));
    --user-msg-border: rgba(236, 72, 153, 0.4);
    --chat-input-bg: #18181f;
    --accent-pink: #ec4899;
    --accent-purple: #8b5cf6;
    --accent-blue: #3b82f6;
    --accent-cyan: #06b6d4;
    --accent-coral: #ff6b6b;
    --gradient-hero: linear-gradient(135deg, #ff6b6b 0%, #ec4899 35%, #8b5cf6 70%, #3b82f6 100%);
    --gradient-lovable: linear-gradient(135deg, #f43f5e 0%, #ec4899 40%, #8b5cf6 80%, #3b82f6 100%);
    --shadow-glow: 0 0 35px rgba(236, 72, 153, 0.3);
    --shadow-card: 0 10px 40px rgba(0, 0, 0, 0.6);
    --radius-sm: 8px;
    --radius-md: 12px;
    --radius-lg: 18px;
    --radius-xl: 26px;
    --radius-full: 9999px;
    --transition: all 0.22s cubic-bezier(0.16, 1, 0.3, 1);
}

/* Light Mode (Clean Slate & Lovable Pastel Glow) */
[data-theme="light"] {
    --bg-primary: #fafafa;
    --bg-secondary: #ffffff;
    --bg-card: rgba(255, 255, 255, 0.95);
    --bg-glass: rgba(0, 0, 0, 0.02);
    --bg-glass-hover: rgba(0, 0, 0, 0.05);
    --border-subtle: rgba(0, 0, 0, 0.08);
    --border-active: rgba(236, 72, 153, 0.5);
    --text-primary: #0f172a;
    --text-secondary: #475569;
    --text-muted: #94a3b8;
    --sidebar-bg: #f4f4f7;
    --user-msg-bg: linear-gradient(135deg, rgba(236, 72, 153, 0.12), rgba(99, 102, 241, 0.1));
    --user-msg-border: rgba(236, 72, 153, 0.3);
    --chat-input-bg: #ffffff;
    --shadow-glow: 0 0 25px rgba(236, 72, 153, 0.15);
    --shadow-card: 0 4px 25px rgba(0, 0, 0, 0.06);
}

/* ===== Global Resets ===== */
html, body, .stApp, [data-testid="stAppViewContainer"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    background-color: var(--bg-primary) !important;
    color: var(--text-primary) !important;
    letter-spacing: -0.015em;
}

.stApp {
    background: var(--bg-primary) !important;
}

/* ===== Lovable Vibrant Multicolored Mesh Aurora Background ===== */
[data-testid="stAppViewContainer"]::before {
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: 
        /* Top Left Coral/Sunset Glow */
        radial-gradient(circle at 10% 15%, rgba(255, 107, 107, 0.35) 0%, transparent 45%),
        /* Top Right Electric Blue Glow */
        radial-gradient(circle at 90% 18%, rgba(59, 130, 246, 0.4) 0%, transparent 50%),
        /* Center Vivid Pink/Magenta Core */
        radial-gradient(ellipse at 50% 45%, rgba(236, 72, 153, 0.38) 0%, transparent 60%),
        /* Mid-Left Purple */
        radial-gradient(circle at 15% 65%, rgba(139, 92, 246, 0.35) 0%, transparent 50%),
        /* Bottom Cyan Accent */
        radial-gradient(circle at 80% 85%, rgba(6, 182, 212, 0.25) 0%, transparent 45%);
    filter: blur(40px);
    z-index: -1;
    pointer-events: none;
    animation: lovableShift 18s ease-in-out infinite alternate;
}

@keyframes lovableShift {
    0% { transform: scale(1) rotate(0deg); opacity: 0.95; }
    50% { transform: scale(1.04) rotate(1.5deg); opacity: 1; }
    100% { transform: scale(0.98) rotate(-1.5deg); opacity: 0.9; }
}

/* ===== Custom Minimal Scrollbar ===== */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb {
    background: rgba(236, 72, 153, 0.3);
    border-radius: 999px;
}
::-webkit-scrollbar-thumb:hover {
    background: rgba(236, 72, 153, 0.6);
}

/* ===== Sidebar — Lovable Minimalist Dark ===== */
[data-testid="stSidebar"] {
    background: var(--sidebar-bg) !important;
    border-right: 1px solid var(--border-subtle) !important;
}

[data-testid="stSidebar"] > div:first-child {
    background: transparent !important;
    padding-top: 1rem !important;
}

/* Sidebar Profile / Workspace Card */
.sidebar-workspace-pill {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-md);
    padding: 0.55rem 0.75rem;
    margin-bottom: 1rem;
    font-size: 0.86rem;
    font-weight: 600;
    color: var(--text-primary);
}

.workspace-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 22px;
    height: 22px;
    background: linear-gradient(135deg, #f43f5e, #ec4899);
    border-radius: 6px;
    font-size: 0.75rem;
    font-weight: 700;
    color: white;
    margin-right: 0.5rem;
}

/* ===== Sidebar Section Labels ===== */
[data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] h5 {
    font-family: 'Inter', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.72rem !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--text-muted) !important;
    margin-top: 0.8rem !important;
    margin-bottom: 0.4rem !important;
}

/* ===== Sidebar Dividers ===== */
[data-testid="stSidebar"] hr {
    border-color: var(--border-subtle) !important;
    margin: 0.75rem 0 !important;
}

/* ===== Sidebar Buttons (Conversation Cards) ===== */
[data-testid="stSidebar"] .stButton > button {
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.84rem !important;
    background: transparent !important;
    color: var(--text-secondary) !important;
    border: 1px solid transparent !important;
    border-radius: var(--radius-md) !important;
    padding: 0.55rem 0.85rem !important;
    transition: var(--transition) !important;
    text-align: left !important;
}

[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(255, 255, 255, 0.06) !important;
    border-color: var(--border-subtle) !important;
    color: var(--text-primary) !important;
    transform: translateX(2px);
}

/* ===== New Chat Button — Lovable Gradient Button ===== */
[data-testid="stSidebar"] .stButton > button[kind="secondary"]:first-of-type,
.new-chat-btn > button,
button[key="new_chat_btn"] {
    background: linear-gradient(135deg, #ff6b6b, #ec4899, #8b5cf6) !important;
    color: white !important;
    font-weight: 600 !important;
    border: none !important;
    border-radius: var(--radius-md) !important;
    box-shadow: 0 4px 18px rgba(236, 72, 153, 0.4) !important;
    letter-spacing: -0.01em;
}

[data-testid="stSidebar"] .stButton > button[kind="secondary"]:first-of-type:hover,
button[key="new_chat_btn"]:hover {
    box-shadow: 0 6px 25px rgba(236, 72, 153, 0.6) !important;
    transform: translateY(-2px) !important;
}

/* ===== Upgrade to Pro Pill (Lovable Sidebar Bottom Card) ===== */
.pro-card {
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-md);
    padding: 0.8rem 0.9rem;
    margin-top: 1rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.pro-card-title {
    font-size: 0.82rem;
    font-weight: 700;
    color: var(--text-primary);
}

.pro-card-subtitle {
    font-size: 0.72rem;
    color: var(--text-muted);
}

.pro-icon-badge {
    width: 28px;
    height: 28px;
    border-radius: 8px;
    background: linear-gradient(135deg, #8b5cf6, #ec4899);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.85rem;
    color: white;
}

/* ===== File Uploader ===== */
[data-testid="stSidebar"] [data-testid="stFileUploader"] {
    background: var(--bg-glass) !important;
    border: 1px dashed rgba(236, 72, 153, 0.3) !important;
    border-radius: var(--radius-md) !important;
    padding: 0.5rem !important;
}

[data-testid="stSidebar"] [data-testid="stFileUploader"]:hover {
    border-color: var(--accent-pink) !important;
    background: rgba(236, 72, 153, 0.06) !important;
}

/* ===== Slider ===== */
[data-testid="stSidebar"] .stSlider > div > div > div {
    background: var(--gradient-lovable) !important;
}

[data-testid="stSidebar"] .stSlider [data-testid="stThumbValue"] {
    color: var(--accent-pink) !important;
    font-weight: 600 !important;
}

/* ===== Main Content Area ===== */
.main .block-container {
    max-width: 900px !important;
    padding-top: 2rem !important;
    padding-bottom: 6rem !important;
}

/* ===== Chat Messages ===== */
[data-testid="stChatMessage"] {
    background: transparent !important;
    border: none !important;
    padding: 0.85rem 0 !important;
    animation: lovableSlideIn 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes lovableSlideIn {
    from { opacity: 0; transform: translateY(14px); }
    to { opacity: 1; transform: translateY(0); }
}

/* User Message Card */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    justify-content: flex-end;
}

[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) > div:last-child {
    background: var(--user-msg-bg) !important;
    border: 1px solid var(--user-msg-border) !important;
    border-radius: var(--radius-lg) var(--radius-lg) 4px var(--radius-lg) !important;
    padding: 0.95rem 1.25rem !important;
    max-width: 82%;
    box-shadow: 0 4px 20px rgba(236, 72, 153, 0.15);
}

/* AI Message Card */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) > div:last-child {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: 4px var(--radius-lg) var(--radius-lg) var(--radius-lg) !important;
    padding: 1.15rem 1.35rem !important;
    backdrop-filter: blur(18px);
    max-width: 88%;
    box-shadow: var(--shadow-card);
}

/* Chat Avatars */
[data-testid="chatAvatarIcon-user"] {
    background: linear-gradient(135deg, #f43f5e, #ec4899) !important;
    border-radius: var(--radius-full) !important;
}

[data-testid="chatAvatarIcon-assistant"] {
    background: linear-gradient(135deg, #8b5cf6, #3b82f6) !important;
    border-radius: var(--radius-full) !important;
    box-shadow: 0 0 16px rgba(139, 92, 246, 0.4);
}

/* ===== Lovable Chat Input Capsule ===== */
[data-testid="stChatInput"] {
    background: transparent !important;
    border: none !important;
}

[data-testid="stChatInput"] > div {
    background: var(--chat-input-bg) !important;
    backdrop-filter: blur(24px) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: var(--radius-xl) !important;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.6), 0 0 0 1px rgba(255, 255, 255, 0.05) !important;
    transition: var(--transition) !important;
    padding: 0.35rem 0.6rem !important;
}

[data-testid="stChatInput"] > div:focus-within {
    border-color: var(--accent-pink) !important;
    box-shadow: 0 8px 40px rgba(0, 0, 0, 0.7), 0 0 25px rgba(236, 72, 153, 0.3) !important;
}

[data-testid="stChatInput"] textarea {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.95rem !important;
    color: var(--text-primary) !important;
    line-height: 1.5 !important;
}

[data-testid="stChatInput"] textarea::placeholder {
    color: var(--text-muted) !important;
}

/* Send Button */
[data-testid="stChatInput"] button {
    background: linear-gradient(135deg, #f43f5e, #ec4899) !important;
    color: white !important;
    border: none !important;
    border-radius: var(--radius-full) !important;
    transition: var(--transition) !important;
}

[data-testid="stChatInput"] button:hover {
    box-shadow: 0 0 20px rgba(236, 72, 153, 0.6) !important;
    transform: scale(1.06);
}

/* ===== Typography ===== */
[data-testid="stChatMessage"] p {
    font-size: 0.94rem !important;
    line-height: 1.7 !important;
    color: var(--text-primary) !important;
}

[data-testid="stChatMessage"] h1, 
[data-testid="stChatMessage"] h2, 
[data-testid="stChatMessage"] h3 {
    font-family: 'Inter', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: -0.03em;
    color: var(--text-primary) !important;
}

[data-testid="stChatMessage"] li {
    font-size: 0.94rem !important;
    line-height: 1.7 !important;
    margin-bottom: 0.35rem !important;
}

/* ===== Memory Pill Tags ===== */
.memory-pill {
    display: inline-block;
    background: linear-gradient(135deg, rgba(236, 72, 153, 0.18), rgba(139, 92, 246, 0.15));
    border: 1px solid rgba(236, 72, 153, 0.35);
    color: #f472b6;
    font-family: 'Inter', sans-serif;
    font-size: 0.73rem;
    font-weight: 600;
    padding: 0.32rem 0.75rem;
    border-radius: var(--radius-full);
    margin: 0.15rem 0.2rem;
    transition: var(--transition);
}

.memory-pill:hover {
    background: linear-gradient(135deg, rgba(236, 72, 153, 0.3), rgba(139, 92, 246, 0.25));
    border-color: rgba(236, 72, 153, 0.6);
    box-shadow: 0 0 14px rgba(236, 72, 153, 0.3);
    transform: translateY(-1px);
}

/* ===== Tool Status Pill ===== */
.tool-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    background: rgba(59, 130, 246, 0.15);
    border: 1px solid rgba(59, 130, 246, 0.35);
    color: #93c5fd;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    font-weight: 500;
    padding: 0.22rem 0.6rem;
    border-radius: var(--radius-full);
    margin-right: 0.35rem;
    margin-bottom: 0.4rem;
}

/* ===== Typing indicator ===== */
.typing-indicator {
    display: inline-flex;
    gap: 5px;
    padding: 0.6rem 0;
}

.typing-dot {
    width: 6px;
    height: 6px;
    background: var(--accent-pink);
    border-radius: 50%;
    animation: typingBounce 1.4s infinite ease-in-out;
}

.typing-dot:nth-child(2) { animation-delay: 0.2s; }
.typing-dot:nth-child(3) { animation-delay: 0.4s; }

@keyframes typingBounce {
    0%, 80%, 100% { transform: scale(0.6); opacity: 0.3; }
    40% { transform: scale(1); opacity: 1; }
}

/* ===== Status Badge (sidebar) ===== */
.status-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.45rem;
    font-family: 'Inter', sans-serif;
    font-size: 0.72rem;
    color: var(--text-muted);
    padding: 0.2rem 0;
}

.status-dot {
    width: 6px;
    height: 6px;
    background: #10b981;
    border-radius: 50%;
    box-shadow: 0 0 8px rgba(16, 185, 129, 0.6);
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.4; }
}

/* ===== Streamlit Header / Menu Styling ===== */
header {
    background: transparent !important;
    backdrop-filter: blur(10px) !important;
}

[data-testid="stHeader"] {
    background: transparent !important;
}

footer { visibility: hidden; }

/* ===== Lovable Hero Section ===== */
.lovable-hero-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 48vh;
    text-align: center;
    padding: 2.5rem 0 1rem 0;
    position: relative;
}

/* Top Connected Tools Pill (Lovable Style) */
.tools-connect-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.6rem;
    background: rgba(18, 18, 24, 0.85);
    border: 1px solid rgba(255, 255, 255, 0.12);
    padding: 0.35rem 0.95rem;
    border-radius: 9999px;
    font-size: 0.82rem;
    font-weight: 500;
    color: #e2e8f0;
    margin-bottom: 1.4rem;
    backdrop-filter: blur(16px);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    cursor: default;
    transition: var(--transition);
}

.tools-connect-pill:hover {
    border-color: rgba(236, 72, 153, 0.4);
    box-shadow: 0 0 20px rgba(236, 72, 153, 0.2);
}

.tool-mini-icons {
    display: flex;
    align-items: center;
    gap: -4px;
}

.tool-mini-icon {
    width: 20px;
    height: 20px;
    border-radius: 50%;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 0.68rem;
    border: 1.5px solid #18181f;
}

/* Main Lovable Headline: "Let's build something, Vraj" */
.lovable-title {
    font-family: 'Inter', sans-serif;
    font-weight: 800;
    font-size: 3.2rem;
    letter-spacing: -0.04em;
    color: #ffffff;
    margin-bottom: 1.6rem;
    line-height: 1.1;
}

/* Lovable Mock Action Capsule Bar */
.lovable-input-capsule {
    background: #181820;
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 18px;
    padding: 1.2rem 1.4rem;
    max-width: 620px;
    width: 100%;
    margin-bottom: 2.5rem;
    text-align: left;
    box-shadow: 0 10px 35px rgba(0, 0, 0, 0.4);
}

.lovable-input-placeholder {
    color: #64748b;
    font-size: 0.94rem;
    margin-bottom: 1.2rem;
}

.lovable-input-actions {
    display: flex;
    align-items: center;
    justify-content: space-between;
    color: #94a3b8;
    font-size: 0.85rem;
}

/* Bottom Projects / Capabilities Card (Lovable Style) */
.lovable-bottom-section {
    background: #111116;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 20px 20px 0 0;
    padding: 1.5rem 1.8rem;
    max-width: 860px;
    width: 100%;
    box-shadow: 0 -10px 40px rgba(0, 0, 0, 0.5);
}

.lovable-filter-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 1.2rem;
}

.lovable-filters {
    display: flex;
    align-items: center;
    gap: 0.6rem;
}

.lovable-filter-btn {
    padding: 0.35rem 0.85rem;
    border-radius: 9999px;
    font-size: 0.8rem;
    font-weight: 500;
    color: #94a3b8;
    background: transparent;
    border: 1px solid transparent;
}

.lovable-filter-btn.active {
    background: rgba(255, 255, 255, 0.1);
    color: #ffffff;
    font-weight: 600;
}

.lovable-cards-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 14px;
}

.lovable-feature-card {
    background: rgba(24, 24, 32, 0.7);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 14px;
    padding: 1.1rem 1.25rem;
    text-align: left;
    transition: var(--transition);
}

.lovable-feature-card:hover {
    border-color: rgba(236, 72, 153, 0.4);
    background: rgba(30, 30, 42, 0.9);
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.4);
}

.lovable-card-tag {
    font-size: 0.68rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: #ec4899;
    margin-bottom: 0.3rem;
}

.lovable-card-title {
    font-size: 0.92rem;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 0.25rem;
}

.lovable-card-desc {
    font-size: 0.78rem;
    color: #94a3b8;
    line-height: 1.45;
}
    40% { transform: scale(1); opacity: 1; }
}

/* ===== Status Badge (sidebar) ===== */
.status-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    font-family: 'Inter', sans-serif;
    font-size: 0.7rem;
    color: var(--text-muted);
    padding: 0.3rem 0;
}

.status-dot {
    width: 6px;
    height: 6px;
    background: #22c55e;
    border-radius: 50%;
    box-shadow: 0 0 6px rgba(34, 197, 94, 0.5);
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}
</style>
""", unsafe_allow_html=True)


# ======================= Utility Functions =======================

def get_or_create_user_id():
    """
    Get a persistent user ID that survives page refreshes.
    Stored in a hidden file in the app directory.
    """
    user_id_file = Path(".streamlit/.user_id")

    # Create directory if it doesn't exist
    user_id_file.parent.mkdir(exist_ok=True)

    # Load existing user_id if it exists
    if user_id_file.exists():
        try:
            with open(user_id_file, 'r') as f:
                user_id = f.read().strip()
                if user_id:
                    print(f"[INFO] Loaded persistent user_id: {user_id}")
                    return user_id
        except Exception as e:
            print(f"[WARN] Error loading user_id: {e}")

    # Create new user_id
    user_id = str(uuid.uuid4())
    try:
        with open(user_id_file, 'w') as f:
            f.write(user_id)
        print(f"[INFO] Created new persistent user_id: {user_id}")
    except Exception as e:
        print(f"[WARN] Error saving user_id: {e}")

    return user_id

def generate_thread_id():
    thread_id = uuid.uuid4()
    return thread_id

def reset_chat():
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    add_thread(st.session_state['thread_id'])
    st.session_state['message_history'] = []

def add_thread(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'][thread_id] = 'chat title'

def load_conversation(thread_id):
    state = chatbot.get_state(config={'configurable': {'thread_id': thread_id}})
    messages = state.values.get('messages', [])
    # Filter out ToolMessages - keep only HumanMessage and AIMessage
    filtered_messages = [msg for msg in messages if not isinstance(msg, ToolMessage)]
    return filtered_messages

def chat_title(thread_id, query):
    try:
        title = base_llm.invoke(f'Generate a concise title (max 5 words) for this conversation: {query}')

        # Handle different response formats
        if isinstance(title.content, str):
            title_text = title.content
        elif isinstance(title.content, list) and len(title.content) > 0:
            first = title.content[0]
            title_text = first.get('text', '') if isinstance(first, dict) else str(first)
        else:
            title_text = query[:25] + ('...' if len(query) > 25 else '')
    except Exception as e:
        print(f"[WARN] Error generating title: {e}")
        title_text = query[:25] + ('...' if len(query) > 25 else '')

    # Trim to keep sidebar clean
    title_text = title_text.strip().strip('"').strip("'")[:40]

    # save to the session state
    st.session_state['chat_threads'][thread_id] = title_text

    # save to the database
    try:
        save_chat_title(thread_id, title_text)
    except Exception as e:
        print(f"[WARN] Error saving title to db: {e}")

def render_tool_badges(tools_used):
    """Render beautiful tool pills"""
    if tools_used:
        tool_html = ""
        tool_icons = {
            "search_internet": "🌐",
            "calculator": "🧮",
            "get_stock_price": "📈",
            "retrieve_from_documents": "📄"
        }
        for t in tools_used:
            icon = tool_icons.get(t, "⚡")
            tool_html += f'<span class="tool-pill">{icon} {t}</span>'
        st.markdown(tool_html, unsafe_allow_html=True)

@st.dialog("Delete Chat")
def confirm_delete_dialog(thread_id):
    title_to_delete = st.session_state['chat_threads'].get(thread_id, 'Chat')
    st.warning(f"Are you sure you want to delete '{title_to_delete}'? This action cannot be undone.")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("✓ Delete", key="confirm_delete_btn", use_container_width=True):
            if delete_chat(thread_id):
                st.session_state['chat_threads'].pop(thread_id, None)

                # If we deleted the current chat, switch to most recent existing chat
                if st.session_state['thread_id'] == thread_id:
                    remaining_chats = list(st.session_state['chat_threads'].keys())
                    if remaining_chats:
                        st.session_state['thread_id'] = remaining_chats[-1]
                        messages = load_conversation(remaining_chats[-1])
                        temp_messages = []
                        for msg in messages:
                            if isinstance(msg, HumanMessage):
                                role='user'
                                content = msg.content
                            else:
                                role='assistant'
                                content = msg.content
                                if isinstance(content, list) and len(content) > 0:
                                    content = content[0].get('text', '')
                            if content and (isinstance(content, str) and content.strip() or isinstance(content, list) and len(content) > 0):
                                temp_messages.append({'role': role, 'content': content})
                        st.session_state['message_history'] = temp_messages
                    else:
                        reset_chat()
                st.rerun()

    with col2:
        if st.button("✕ Cancel", key="cancel_delete_btn", use_container_width=True):
            st.rerun()


# ======================= Session Setup =======================

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

# Create or load persistent user ID from file (survives page refresh!)
if 'user_id' not in st.session_state:
    st.session_state['user_id'] = get_or_create_user_id()
    print(f"[INFO] Session user_id set to: {st.session_state['user_id']}")

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()

if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = get_all_threads()
    print(f"Chat threads loaded: {st.session_state['chat_threads']}")

add_thread(st.session_state['thread_id'])


# ======================= Sidebar UI =======================

with st.sidebar:
    # Brand Header (Lovable.dev Workspace Style)
    st.markdown("""
    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.8rem; padding: 0.2rem 0;">
        <div style="display: flex; align-items: center; gap: 0.6rem;">
            <span style="font-size: 1.6rem; filter: drop-shadow(0 0 12px rgba(236, 72, 153, 0.6));">🔥</span>
            <div style="font-family: 'Inter', sans-serif; font-weight: 800; font-size: 1.35rem; color: #ffffff; letter-spacing: -0.03em;">NeuralChat</div>
        </div>
        <div class="status-badge">
            <span class="status-dot"></span>
        </div>
    </div>
    <div class="sidebar-workspace-pill">
        <div style="display: flex; align-items: center;">
            <span class="workspace-badge">V</span>
            <span>Vraj's Workspace</span>
        </div>
        <span style="color: #64748b; font-size: 0.75rem;">▾</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("")

    # New Chat Button
    if st.button('✦  New Conversation', key='new_chat_btn', use_container_width=True):
        reset_chat()

    st.divider()

    # Document Upload
    st.markdown("##### 📎 Documents")

    uploaded_file = st.file_uploader(
        "Drop a PDF here",
        type="pdf",
        key=f"pdf_upload_{st.session_state['thread_id']}",
        label_visibility="collapsed"
    )

    if uploaded_file:
        with st.status("Processing PDF...", expanded=True) as status:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                tmp_file.write(uploaded_file.getbuffer())
                tmp_path = tmp_file.name

            result = process_pdf_for_thread(
                tmp_path,
                st.session_state['thread_id'],
                uploaded_file.name
            )

            if result['status'] == 'success':
                status.update(label="✅ PDF processed!", state="complete")
                st.success(f"✅ {result['message']}")
            else:
                status.update(label="❌ Error", state="error")
                st.error(f"❌ {result['message']}")

            os.remove(tmp_path)

    st.divider()

    # Chat Settings
    st.markdown("##### ⚙️ Settings")

    keep_recent = st.slider(
        "Context window",
        min_value=5,
        max_value=50,
        value=12,
        step=1,
        help="Recent messages kept in full. Older messages are summarized."
    )
    from backend import set_keep_recent
    set_keep_recent(keep_recent)

    st.divider()

    # Memory Profile
    st.markdown("##### 🧠 Memory")

    if 'user_id' in st.session_state:
        user_memories = get_all_user_memories(st.session_state['user_id'])

        if user_memories:
            # Render as pill tags
            pills_html = ""
            for mem in user_memories:
                pills_html += f'<span class="memory-pill" title="Stored: {mem["created_at"]}">{mem["content"]}</span>'
            st.markdown(pills_html, unsafe_allow_html=True)

            st.caption(f"📊 {len(user_memories)} memories stored")

            # Individual delete buttons
            with st.expander("Manage Memories", expanded=False):
                for mem in user_memories:
                    col_mem, col_del = st.columns([5, 1])
                    with col_mem:
                        st.markdown(f"<span style='font-size: 0.78rem; color: #a1a1aa;'>• {mem['content']}</span>", unsafe_allow_html=True)
                    with col_del:
                        if st.button("×", key=f"del_mem_{mem['id']}", help="Delete"):
                            delete_user_memory(mem['id'], st.session_state['user_id'])
                            st.rerun()

                if st.button("🗑️ Clear All", use_container_width=True, key="clear_all_mem"):
                    clear_all_user_memories(st.session_state['user_id'])
                    st.rerun()
        else:
            st.markdown("""
            <div style="text-align: center; padding: 1rem 0; color: #71717a; font-size: 0.8rem;">
                <div style="font-size: 1.5rem; margin-bottom: 0.3rem; opacity: 0.5;">💭</div>
                No memories yet.<br>Start chatting and I'll learn about you!
            </div>
            """, unsafe_allow_html=True)

    st.divider()

    # Conversation History
    st.markdown("##### 💬 Conversations")

    if st.session_state['chat_threads']:
        for thread_id, title in reversed(st.session_state['chat_threads'].items()):
            is_active = thread_id == st.session_state['thread_id']
            col1, col2 = st.columns([5, 1])

            with col1:
                # Truncate long titles
                display_title = str(title)[:35] + ("..." if len(str(title)) > 35 else "")
                if st.button(
                    f"{'▸ ' if is_active else '  '}{display_title}",
                    key=str(thread_id),
                    use_container_width=True
                ):
                    st.session_state['thread_id'] = thread_id
                    messages = load_conversation(thread_id)

                    temp_messages = []
                    for msg in messages:
                        if isinstance(msg, HumanMessage):
                            role = 'user'
                            content = msg.content
                        else:
                            role = 'assistant'
                            content = msg.content
                            if isinstance(content, list) and len(content) > 0:
                                content = content[0].get('text', '')

                        if content and (isinstance(content, str) and content.strip() or isinstance(content, list) and len(content) > 0):
                            temp_messages.append({'role': role, 'content': content})

                    st.session_state['message_history'] = temp_messages

            with col2:
                if st.button("×", key=f"delete_{thread_id}", help="Delete chat"):
                    confirm_delete_dialog(thread_id)
    else:
        st.markdown("""
        <div style="text-align: center; padding: 0.75rem 0; color: #71717a; font-size: 0.78rem;">
            No conversations yet
        </div>
        """, unsafe_allow_html=True)


# ======================= Main Chat Area =======================

# Welcome Screen (when no messages) - Exact Lovable.dev UI
if not st.session_state['message_history']:
    st.markdown("""
    <div class="lovable-hero-container">
        <div class="tools-connect-pill">
            <div class="tool-mini-icons">
                <span class="tool-mini-icon" style="background: #ef4444; color: white;">M</span>
                <span class="tool-mini-icon" style="background: #3b82f6; color: white;">🌐</span>
                <span class="tool-mini-icon" style="background: #10b981; color: white;">📄</span>
                <span class="tool-mini-icon" style="background: #eab308; color: black;">⚡</span>
            </div>
            <span>Connect all your tools →</span>
        </div>
        
        <div class="lovable-title">Let's build something, Vraj</div>
        
        <div class="lovable-input-capsule">
            <div class="lovable-input-placeholder">Ask NeuralChat to create, analyze, or synthesize anything below...</div>
            <div class="lovable-input-actions">
                <span style="font-size: 1.1rem; cursor: pointer;">＋</span>
                <div style="display: flex; align-items: center; gap: 1rem;">
                    <span style="display: inline-flex; align-items: center; gap: 0.25rem; font-weight: 600; color: #f8fafc;">
                        Build <span style="font-size: 0.65rem;">▾</span>
                    </span>
                    <span style="font-size: 1rem; cursor: pointer;">🎙️</span>
                </div>
            </div>
        </div>

        <div class="lovable-bottom-section">
            <div class="lovable-filter-row">
                <div class="lovable-filters">
                    <span style="color: #64748b; font-size: 0.85rem; margin-right: 0.2rem;">🔍 Search</span>
                    <button class="lovable-filter-btn active">My Capabilities</button>
                    <button class="lovable-filter-btn">Recent Memory</button>
                    <button class="lovable-filter-btn">Templates</button>
                </div>
                <span style="color: #94a3b8; font-size: 0.78rem; font-weight: 500; cursor: pointer;">Browse all →</span>
            </div>
            
            <div class="lovable-cards-grid">
                <div class="lovable-feature-card">
                    <div class="lovable-card-tag">Memory Core</div>
                    <div class="lovable-card-title">Persistent Semantic Recall</div>
                    <div class="lovable-card-desc">Remembers your custom preferences, codebases, and technical details across sessions.</div>
                </div>
                <div class="lovable-feature-card">
                    <div class="lovable-card-tag">RAG Engine</div>
                    <div class="lovable-card-title">Document Intelligence</div>
                    <div class="lovable-card-desc">Upload PDFs to the sidebar for fast semantic search and deep content synthesis.</div>
                </div>
                <div class="lovable-feature-card">
                    <div class="lovable-card-tag">Multi-Agent Tools</div>
                    <div class="lovable-card-title">Live Web & Stock Analytics</div>
                    <div class="lovable-card-desc">Real-time financial tickers, search engine indexing, and Python calculations.</div>
                </div>
                <div class="lovable-feature-card">
                    <div class="lovable-card-tag">Engineering Depth</div>
                    <div class="lovable-card-title">Full-Stack Synthesis</div>
                    <div class="lovable-card-desc">Architect scalable systems, refactor complex algorithms, and debug in real time.</div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Render conversation history
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        # Show tool badges above assistant responses
        if message['role'] == 'assistant' and message.get('tools_used'):
            render_tool_badges(message['tools_used'])
        st.markdown(message['content'])

# Chat Input
user_input = st.chat_input('Ask me anything...')

if user_input:
    # Add message to history
    st.session_state['message_history'].append({'role': 'user', 'content': user_input})
    with st.chat_message('user'):
        st.markdown(user_input)

    CONFIG = {'configurable': {'thread_id': st.session_state['thread_id']}}
    should_rerun = False

    # Generate title for first message
    if len(st.session_state['message_history']) == 1:
        chat_title(st.session_state['thread_id'], user_input)
        should_rerun = True

    # Stream response
    with st.chat_message("assistant"):
        status_placeholder = st.empty()
        message_placeholder = st.empty()

        def stream_with_tool_tracking():
            # Set both thread_id and user_id
            backend._CURRENT_THREAD_ID = st.session_state['thread_id']
            backend._CURRENT_USER_ID = st.session_state['user_id']

            current_message = ""
            tools_used = []

            # Show typing indicator
            status_placeholder.markdown("""
            <div class="typing-indicator">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
            """, unsafe_allow_html=True)

            try:
                for event in chatbot.stream(
                    {"messages": [HumanMessage(content=user_input)]},
                    config=CONFIG,
                    stream_mode="values"
                ):
                    if 'messages' in event:
                        messages = event['messages']
                        if messages and hasattr(messages[-1], 'tool_calls'):
                            tool_calls = messages[-1].tool_calls
                            if tool_calls:
                                for tool_call in tool_calls:
                                    tool_name = tool_call.get('name', 'Unknown Tool')
                                    if tool_name not in tools_used:
                                        tools_used.append(tool_name)
                                    tool_icons = {
                                        "search_internet": "🌐",
                                        "calculator": "🧮",
                                        "get_stock_price": "📈",
                                        "retrieve_from_documents": "📄"
                                    }
                                    icon = tool_icons.get(tool_name, "⚡")
                                    status_placeholder.markdown(
                                        f'<span class="tool-pill" style="font-size: 0.75rem;">{icon} Using {tool_name}...</span>',
                                        unsafe_allow_html=True
                                    )

                        if messages and isinstance(messages[-1], AIMessage):
                            content = messages[-1].content
                            if isinstance(content, str) and content.strip():
                                current_message = content
                                status_placeholder.empty()
                                message_placeholder.markdown(current_message)
                            elif isinstance(content, list) and len(content) > 0:
                                text = ""
                                for part in content:
                                    if isinstance(part, dict):
                                        text += part.get('text', '')
                                    else:
                                        text += str(part)
                                if text.strip():
                                    current_message = text
                                    status_placeholder.empty()
                                    message_placeholder.markdown(current_message)
            except Exception as stream_err:
                print(f"[ERROR] Stream error: {stream_err}")
                status_placeholder.empty()
                if "429" in str(stream_err) or "RESOURCE_EXHAUSTED" in str(stream_err):
                    current_message = "⚠️ **Rate limit reached**. Google Gemini Free Tier limits requests per minute. Please wait 20-30 seconds and try again."
                else:
                    current_message = f"⚠️ **Something went wrong:** `{str(stream_err)}`"
                message_placeholder.markdown(current_message)

            # Show persistent tool badges
            status_placeholder.empty()
            if tools_used:
                render_tool_badges(tools_used)

            return current_message, tools_used

        ai_message, tools_used = stream_with_tool_tracking()

    st.session_state['message_history'].append({
        'role': 'assistant',
        'content': ai_message,
        'tools_used': tools_used if tools_used else None
    })
    # Always rerun so new memories and titles update in the sidebar immediately
    st.rerun()