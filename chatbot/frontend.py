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
/* ===== Google Fonts: Inter Display + Geist / JetBrains Mono ===== */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&display=swap');

/* ===== NexaCore & Shadcn 21st.dev SaaS Palette ===== */
:root, [data-theme="dark"] {
    --bg-primary: #070709;
    --bg-secondary: #0c0c11;
    --bg-card: rgba(14, 14, 20, 0.75);
    --bg-glass: rgba(255, 255, 255, 0.03);
    --bg-glass-hover: rgba(255, 255, 255, 0.07);
    --border-subtle: rgba(255, 255, 255, 0.08);
    --border-active: rgba(139, 92, 246, 0.45);
    --text-primary: #f8fafc;
    --text-secondary: #94a3b8;
    --text-muted: #64748b;
    --sidebar-bg: rgba(10, 10, 15, 0.92);
    --user-msg-bg: linear-gradient(135deg, rgba(124, 58, 237, 0.22), rgba(217, 70, 239, 0.12));
    --user-msg-border: rgba(168, 85, 247, 0.35);
    --chat-input-bg: rgba(12, 12, 18, 0.92);
    --ambient-opacity: 0.12;
    --accent-purple: #8b5cf6;
    --accent-magenta: #d946ef;
    --accent-cyan: #06b6d4;
    --accent-emerald: #10b981;
    --gradient-hero: linear-gradient(135deg, #a855f7 0%, #ec4899 50%, #06b6d4 100%);
    --gradient-beam: linear-gradient(180deg, transparent 0%, rgba(139, 92, 246, 0.15) 60%, rgba(217, 70, 239, 0.25) 100%);
    --shadow-glow: 0 0 30px rgba(168, 85, 247, 0.2);
    --shadow-card: 0 8px 32px rgba(0, 0, 0, 0.5);
    --radius-sm: 8px;
    --radius-md: 12px;
    --radius-lg: 16px;
    --radius-xl: 22px;
    --radius-full: 9999px;
    --transition: all 0.22s cubic-bezier(0.16, 1, 0.3, 1);
}

/* Light Mode (Clean Slate & Precision Purple) */
[data-theme="light"] {
    --bg-primary: #f8fafc;
    --bg-secondary: #ffffff;
    --bg-card: rgba(255, 255, 255, 0.92);
    --bg-glass: rgba(0, 0, 0, 0.02);
    --bg-glass-hover: rgba(0, 0, 0, 0.05);
    --border-subtle: rgba(0, 0, 0, 0.08);
    --border-active: rgba(139, 92, 246, 0.5);
    --text-primary: #0f172a;
    --text-secondary: #475569;
    --text-muted: #94a3b8;
    --sidebar-bg: rgba(255, 255, 255, 0.95);
    --user-msg-bg: linear-gradient(135deg, rgba(139, 92, 246, 0.12), rgba(6, 182, 212, 0.08));
    --user-msg-border: rgba(139, 92, 246, 0.3);
    --chat-input-bg: rgba(255, 255, 255, 0.98);
    --ambient-opacity: 0.04;
    --shadow-glow: 0 0 20px rgba(139, 92, 246, 0.1);
    --shadow-card: 0 4px 20px rgba(0, 0, 0, 0.06);
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

/* NexaCore Style: High-Tech Radiant Fan-Beam & Grid Background */
[data-testid="stAppViewContainer"]::before {
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: 
        /* Subtle Grid Pattern */
        linear-gradient(to right, rgba(255, 255, 255, 0.015) 1px, transparent 1px),
        linear-gradient(to bottom, rgba(255, 255, 255, 0.015) 1px, transparent 1px),
        /* Top Ambient Purple Glow */
        radial-gradient(circle at 50% -10%, rgba(139, 92, 246, var(--ambient-opacity)) 0%, transparent 60%),
        /* Bottom Radiant NexaCore Fan Light Beam */
        radial-gradient(ellipse at 50% 110%, rgba(217, 70, 239, 0.22) 0%, rgba(124, 58, 237, 0.15) 35%, transparent 70%),
        /* Corner Cyan Accent */
        radial-gradient(circle at 90% 90%, rgba(6, 182, 212, 0.08) 0%, transparent 50%);
    background-size: 40px 40px, 40px 40px, 100% 100%, 100% 100%, 100% 100%;
    z-index: -1;
    pointer-events: none;
}

/* ===== Custom Minimal Scrollbar ===== */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb {
    background: rgba(139, 92, 246, 0.3);
    border-radius: 999px;
}
::-webkit-scrollbar-thumb:hover {
    background: rgba(139, 92, 246, 0.55);
}

/* ===== Sidebar — High-Tech Glass ===== */
[data-testid="stSidebar"] {
    background: var(--sidebar-bg) !important;
    backdrop-filter: blur(24px) saturate(1.2) !important;
    -webkit-backdrop-filter: blur(24px) saturate(1.2) !important;
    border-right: 1px solid var(--border-subtle) !important;
}

[data-testid="stSidebar"] > div:first-child {
    background: transparent !important;
    padding-top: 1.5rem !important;
}

/* ===== Sidebar Brand Header ===== */
[data-testid="stSidebar"] h1 {
    font-family: 'Inter', sans-serif !important;
    font-weight: 800 !important;
    font-size: 1.6rem !important;
    letter-spacing: -0.03em;
    color: var(--text-primary) !important;
}

/* ===== Sidebar Section Labels ===== */
[data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] h5 {
    font-family: 'Inter', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.72rem !important;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--text-muted) !important;
    margin-top: 0.6rem !important;
    margin-bottom: 0.4rem !important;
}

/* ===== Sidebar Dividers ===== */
[data-testid="stSidebar"] hr {
    border-color: var(--border-subtle) !important;
    margin: 0.85rem 0 !important;
}

/* ===== Sidebar Buttons (Conversation Cards) ===== */
[data-testid="stSidebar"] .stButton > button {
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.84rem !important;
    background: var(--bg-glass) !important;
    color: var(--text-secondary) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: var(--radius-md) !important;
    padding: 0.6rem 0.9rem !important;
    transition: var(--transition) !important;
    text-align: left !important;
}

[data-testid="stSidebar"] .stButton > button:hover {
    background: var(--bg-glass-hover) !important;
    border-color: var(--border-active) !important;
    color: var(--text-primary) !important;
    box-shadow: 0 0 20px rgba(139, 92, 246, 0.2) !important;
    transform: translateY(-1px);
}

/* ===== New Chat Button — Gradient Pulse ===== */
[data-testid="stSidebar"] .stButton > button[kind="secondary"]:first-of-type,
.new-chat-btn > button,
button[key="new_chat_btn"] {
    background: linear-gradient(135deg, #8b5cf6, #d946ef) !important;
    color: white !important;
    font-weight: 600 !important;
    border: none !important;
    box-shadow: 0 4px 20px rgba(139, 92, 246, 0.35) !important;
    letter-spacing: -0.01em;
}

[data-testid="stSidebar"] .stButton > button[kind="secondary"]:first-of-type:hover,
button[key="new_chat_btn"]:hover {
    box-shadow: 0 6px 28px rgba(217, 70, 239, 0.5) !important;
    transform: translateY(-2px) !important;
}

/* ===== File Uploader ===== */
[data-testid="stSidebar"] [data-testid="stFileUploader"] {
    background: var(--bg-glass) !important;
    border: 1px dashed rgba(139, 92, 246, 0.3) !important;
    border-radius: var(--radius-md) !important;
    padding: 0.5rem !important;
}

[data-testid="stSidebar"] [data-testid="stFileUploader"]:hover {
    border-color: var(--accent-purple) !important;
    background: rgba(139, 92, 246, 0.06) !important;
}

/* ===== Slider ===== */
[data-testid="stSidebar"] .stSlider > div > div > div {
    background: linear-gradient(90deg, #8b5cf6, #d946ef) !important;
}

[data-testid="stSidebar"] .stSlider [data-testid="stThumbValue"] {
    color: var(--accent-purple) !important;
    font-weight: 600 !important;
}

/* ===== Main Content Area ===== */
.main .block-container {
    max-width: 860px !important;
    padding-top: 1.5rem !important;
    padding-bottom: 6rem !important;
}

/* ===== Chat Messages ===== */
[data-testid="stChatMessage"] {
    background: transparent !important;
    border: none !important;
    padding: 0.85rem 0 !important;
    animation: nexaSlideIn 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes nexaSlideIn {
    from { opacity: 0; transform: translateY(12px); }
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
    padding: 0.95rem 1.2rem !important;
    max-width: 82%;
    box-shadow: 0 4px 20px rgba(139, 92, 246, 0.12);
}

/* AI Message Card (NexaCore High-Contrast Card) */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) > div:last-child {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: 4px var(--radius-lg) var(--radius-lg) var(--radius-lg) !important;
    padding: 1.1rem 1.3rem !important;
    backdrop-filter: blur(16px);
    max-width: 88%;
    box-shadow: var(--shadow-card);
}

/* Chat Avatars */
[data-testid="chatAvatarIcon-user"] {
    background: linear-gradient(135deg, #8b5cf6, #d946ef) !important;
    border-radius: var(--radius-full) !important;
}

[data-testid="chatAvatarIcon-assistant"] {
    background: linear-gradient(135deg, #181824, #271a38) !important;
    border: 1px solid rgba(139, 92, 246, 0.4) !important;
    border-radius: var(--radius-full) !important;
    box-shadow: 0 0 16px rgba(139, 92, 246, 0.3);
}

/* ===== Floating Centered Prompt Input Bar (NexaCore Style) ===== */
[data-testid="stChatInput"] {
    background: transparent !important;
    border: none !important;
}

[data-testid="stChatInput"] > div {
    background: var(--chat-input-bg) !important;
    backdrop-filter: blur(24px) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: var(--radius-xl) !important;
    box-shadow: 0 -10px 40px rgba(0, 0, 0, 0.5), 0 0 0 1px rgba(255, 255, 255, 0.05) !important;
    transition: var(--transition) !important;
    padding: 0.2rem 0.4rem !important;
}

[data-testid="stChatInput"] > div:focus-within {
    border-color: var(--accent-purple) !important;
    box-shadow: 0 -10px 45px rgba(0, 0, 0, 0.6), 0 0 25px rgba(139, 92, 246, 0.25) !important;
}

[data-testid="stChatInput"] textarea {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.94rem !important;
    color: var(--text-primary) !important;
    line-height: 1.5 !important;
}

[data-testid="stChatInput"] textarea::placeholder {
    color: var(--text-muted) !important;
}

/* Send Button */
[data-testid="stChatInput"] button {
    background: linear-gradient(135deg, #8b5cf6, #d946ef) !important;
    color: white !important;
    border: none !important;
    border-radius: var(--radius-full) !important;
    transition: var(--transition) !important;
}

[data-testid="stChatInput"] button:hover {
    box-shadow: 0 0 20px rgba(217, 70, 239, 0.5) !important;
    transform: scale(1.06);
}

/* ===== Code Blocks ===== */
code {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.85rem !important;
}

pre {
    background: rgba(8, 8, 12, 0.9) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: var(--radius-md) !important;
    padding: 1.1rem !important;
}

p code, li code {
    background: rgba(139, 92, 246, 0.15) !important;
    color: #c084fc !important;
    padding: 0.15rem 0.45rem !important;
    border-radius: 5px !important;
    font-size: 0.82rem !important;
}

/* ===== Typography ===== */
[data-testid="stChatMessage"] p {
    font-size: 0.93rem !important;
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
    font-size: 0.93rem !important;
    line-height: 1.7 !important;
    margin-bottom: 0.35rem !important;
}

/* ===== Memory Pill Tags (Nexa Purple/Cyan Glow) ===== */
.memory-pill {
    display: inline-block;
    background: linear-gradient(135deg, rgba(139, 92, 246, 0.16), rgba(6, 182, 212, 0.1));
    border: 1px solid rgba(139, 92, 246, 0.3);
    color: #c4b5fd;
    font-family: 'Inter', sans-serif;
    font-size: 0.73rem;
    font-weight: 600;
    padding: 0.32rem 0.75rem;
    border-radius: var(--radius-full);
    margin: 0.15rem 0.2rem;
    transition: var(--transition);
}

.memory-pill:hover {
    background: linear-gradient(135deg, rgba(139, 92, 246, 0.28), rgba(217, 70, 239, 0.18));
    border-color: rgba(168, 85, 247, 0.6);
    box-shadow: 0 0 14px rgba(139, 92, 246, 0.25);
    transform: translateY(-1px);
}

/* ===== Tool Status Pill ===== */
.tool-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    background: rgba(6, 182, 212, 0.12);
    border: 1px solid rgba(6, 182, 212, 0.3);
    color: #67e8f9;
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
    background: var(--accent-purple);
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
    padding: 0.3rem 0;
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

/* ===== Clean Print Styles ===== */
@media print {
    [data-testid="stSidebar"], 
    header, 
    [data-testid="stChatInput"],
    .welcome-container,
    .stButton {
        display: none !important;
    }
    
    html, body, .stApp, [data-testid="stAppViewContainer"] {
        background: #ffffff !important;
        color: #000000 !important;
    }
    
    [data-testid="stAppViewContainer"]::before {
        display: none !important;
    }
    
    .main .block-container {
        max-width: 100% !important;
        padding: 0 !important;
    }
    
    [data-testid="stChatMessage"] > div:last-child {
        background: transparent !important;
        border: 1px solid #e2e8f0 !important;
        color: #000000 !important;
        box-shadow: none !important;
        page-break-inside: avoid;
    }
    
    [data-testid="stChatMessage"] p,
    [data-testid="stChatMessage"] li {
        color: #000000 !important;
    }
}

/* ===== NexaCore Animated Hero Section ===== */
.welcome-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 58vh;
    text-align: center;
    animation: nexaSlideIn 0.6s cubic-bezier(0.16, 1, 0.3, 1);
    position: relative;
    padding: 2.5rem 0 1.5rem 0;
}

/* Glowing Chip Badge (NexaCore 21st.dev style) */
.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    background: rgba(139, 92, 246, 0.12);
    border: 1px solid rgba(168, 85, 247, 0.4);
    padding: 0.4rem 1rem;
    border-radius: 9999px;
    font-family: 'Inter', sans-serif;
    font-size: 0.74rem;
    font-weight: 700;
    color: #e879f9;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    margin-bottom: 1.2rem;
    box-shadow: 0 0 25px rgba(168, 85, 247, 0.25), inset 0 0 15px rgba(139, 92, 246, 0.15);
    backdrop-filter: blur(14px);
    animation: nexaBadgePulse 3.5s ease-in-out infinite alternate;
}

@keyframes nexaBadgePulse {
    0% { border-color: rgba(139, 92, 246, 0.4); box-shadow: 0 0 20px rgba(139, 92, 246, 0.2); }
    100% { border-color: rgba(6, 182, 212, 0.6); box-shadow: 0 0 30px rgba(6, 182, 212, 0.35); }
}

.hero-badge-dot {
    width: 6px;
    height: 6px;
    background: #06b6d4;
    border-radius: 50%;
    box-shadow: 0 0 8px #06b6d4;
    animation: pulse 1.6s infinite;
}

/* Bold Geometric Headline with Metallic/Chrome Gradient */
.welcome-title {
    font-family: 'Inter', sans-serif;
    font-weight: 900;
    font-size: 3.5rem;
    letter-spacing: -0.04em;
    line-height: 1.08;
    margin-bottom: 0.9rem;
    background: linear-gradient(
        135deg,
        #ffffff 0%,
        #f1f5f9 30%,
        #cbd5e1 55%,
        #a855f7 85%,
        #06b6d4 100%
    );
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.welcome-subtitle {
    font-family: 'Inter', sans-serif;
    font-weight: 400;
    font-size: 1.05rem;
    color: var(--text-muted);
    max-width: 540px;
    line-height: 1.65;
    margin-bottom: 2.2rem;
}

/* NexaCore Bento Grid Feature Cards with Status Chips */
.cap-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 16px;
    max-width: 660px;
    width: 100%;
}

.cap-card {
    background: rgba(14, 14, 20, 0.7);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: var(--radius-lg);
    padding: 1.3rem 1.4rem;
    text-align: left;
    transition: var(--transition);
    position: relative;
    overflow: hidden;
}

.cap-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    border-radius: var(--radius-lg);
    padding: 1px;
    background: linear-gradient(135deg, transparent 30%, rgba(139, 92, 246, 0.6), rgba(6, 182, 212, 0.5));
    -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
    -webkit-mask-composite: xor;
    mask-composite: exclude;
    opacity: 0;
    transition: opacity 0.3s ease;
}

.cap-card:hover {
    background: rgba(20, 20, 30, 0.85);
    transform: translateY(-3px);
    box-shadow: 0 14px 35px rgba(0, 0, 0, 0.45), 0 0 25px rgba(139, 92, 246, 0.2);
}

.cap-card:hover::before {
    opacity: 1;
}

.cap-header-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 0.75rem;
}

.cap-icon-box {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 38px;
    height: 38px;
    border-radius: 10px;
    background: linear-gradient(135deg, rgba(139, 92, 246, 0.2), rgba(217, 70, 239, 0.1));
    border: 1px solid rgba(139, 92, 246, 0.35);
    font-size: 1.15rem;
    box-shadow: 0 0 14px rgba(139, 92, 246, 0.18);
}

.cap-status-pill {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    font-weight: 600;
    padding: 0.2rem 0.55rem;
    border-radius: 9999px;
    background: rgba(16, 185, 129, 0.12);
    border: 1px solid rgba(16, 185, 129, 0.3);
    color: #34d399;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}

.cap-title {
    font-family: 'Inter', sans-serif;
    font-weight: 700;
    font-size: 0.95rem;
    color: var(--text-primary);
    margin-bottom: 0.3rem;
    letter-spacing: -0.02em;
}

.cap-desc {
    font-family: 'Inter', sans-serif;
    font-weight: 400;
    font-size: 0.8rem;
    color: var(--text-muted);
    line-height: 1.5;
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
    # Brand Header (NexaCore 21st.dev Style)
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.5rem; padding: 0.2rem 0;">
        <span style="font-size: 1.8rem; filter: drop-shadow(0 0 14px rgba(168, 85, 247, 0.6));">⚡</span>
        <div>
            <div style="font-family: 'Inter', sans-serif; font-weight: 800; font-size: 1.45rem;
                background: linear-gradient(135deg, #ffffff 0%, #c084fc 60%, #06b6d4 100%);
                -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                letter-spacing: -0.03em; line-height: 1.1;">NeuralChat</div>
            <div class="status-badge">
                <span class="status-dot"></span>
                <span>NexaCore 4.0 · Live</span>
            </div>
        </div>
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

# Welcome Screen (when no messages)
if not st.session_state['message_history']:
    st.markdown("""
    <div class="welcome-container">
        <div class="hero-badge">
            <span class="hero-badge-dot"></span>
            <span>✦ NEXUS AI 4.0 · DEEP REASONING</span>
        </div>
        <div class="welcome-title">Engineer and Scale with Clarity</div>
        <div class="welcome-subtitle">
            Autonomous multi-tool intelligence with persistent vector memory, semantic document synthesis, and real-time execution.
        </div>
        <div class="cap-grid">
            <div class="cap-card">
                <div class="cap-header-row">
                    <div class="cap-icon-box">🧠</div>
                    <span class="cap-status-pill">ACTIVE</span>
                </div>
                <div class="cap-title">Contextual Memory</div>
                <div class="cap-desc">Auto-learns your tech stack and personal preferences with FAISS vector deduplication</div>
            </div>
            <div class="cap-card">
                <div class="cap-header-row">
                    <div class="cap-icon-box">📄</div>
                    <span class="cap-status-pill">RAG READY</span>
                </div>
                <div class="cap-title">Deep Document Synthesis</div>
                <div class="cap-desc">Drop research PDFs and codebase manuals for instantaneous semantic Q&A</div>
            </div>
            <div class="cap-card">
                <div class="cap-header-row">
                    <div class="cap-icon-box">⚡</div>
                    <span class="cap-status-pill">TURBO</span>
                </div>
                <div class="cap-title">Advanced Reasoning & Code</div>
                <div class="cap-desc">Architectural planning, algorithmic refactoring, and multi-step debugging</div>
            </div>
            <div class="cap-card">
                <div class="cap-header-row">
                    <div class="cap-icon-box">🌐</div>
                    <span class="cap-status-pill">LIVE FEED</span>
                </div>
                <div class="cap-title">Live Web & Financial Tools</div>
                <div class="cap-desc">Real-time web search and live market data integration</div>
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