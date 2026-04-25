import streamlit as st
import os
import sys

# บังคับให้ Console รองรับภาษาไทย (แก้ Error: charmap codec can't encode)
if sys.stdout and hasattr(sys.stdout, 'reconfigure') and sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr and hasattr(sys.stderr, 'reconfigure') and sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8')

import logging
import uuid
import time
from dotenv import load_dotenv

# -------------------- Setup --------------------
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -------------------- Streamlit Config --------------------
st.set_page_config(
    page_title="RegCom Assistant",
    page_icon="📘",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# -------------------- Custom CSS --------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* ===== Global ===== */
    .stApp {
        background: linear-gradient(160deg, #f5f9fc 0%, #f9fbfe 30%, #ffffff 60%, #fafcff 100%);
        font-family: 'Inter', sans-serif;
    }

    /* ===== Hide default Streamlit elements ===== */
    #MainMenu, footer, header { visibility: hidden; }
    .stDeployButton { display: none; }

    /* ===== Header Banner ===== */
    .header-banner {
        background: linear-gradient(135deg, #b8d8f0 0%, #d4e8f7 50%, #c5e0f3 100%);
        border-radius: 20px;
        padding: 2rem 2.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 6px 24px rgba(160, 200, 230, 0.2);
        position: relative;
        overflow: hidden;
    }
    .header-banner::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -30%;
        width: 300px;
        height: 300px;
        background: rgba(255,255,255,0.2);
        border-radius: 50%;
    }
    .header-banner::after {
        content: '';
        position: absolute;
        bottom: -40%;
        left: -20%;
        width: 250px;
        height: 250px;
        background: rgba(255,255,255,0.15);
        border-radius: 50%;
    }
    .header-banner h1 {
        color: #3a6b8c;
        font-size: 1.8rem;
        font-weight: 700;
        margin: 0;
        position: relative;
        z-index: 1;
    }
    .header-banner p {
        color: #5a8aaa;
        font-size: 0.95rem;
        margin: 0.5rem 0 0 0;
        font-weight: 400;
        position: relative;
        z-index: 1;
    }

    /* ===== Chat Container ===== */
    .chat-area {
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(200, 220, 240, 0.5);
        border-radius: 20px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        min-height: 400px;
        max-height: 55vh;
        overflow-y: auto;
        box-shadow: 0 4px 20px rgba(160, 200, 230, 0.08);
    }

    /* ===== Message Bubbles ===== */
    .msg-row {
        display: flex;
        margin-bottom: 1rem;
        animation: fadeSlideIn 0.4s ease;
    }
    .msg-row.user { justify-content: flex-end; }
    .msg-row.bot { justify-content: flex-start; }

    @keyframes fadeSlideIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .msg-avatar {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.35rem;     /* ขยายขนาด icon ให้ใหญ่ขึ้น */
        flex-shrink: 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    .msg-avatar.user-av {
        background: linear-gradient(135deg, #a8d4f0, #bfe0f5);
        color: #4a7fa0;
        margin-left: 10px;
        order: 2;
    }
    .msg-avatar.bot-av {
        background: linear-gradient(135deg, #c4b5e0, #d1c4e9);
        color: #6a5c8a;
        margin-right: 10px;
        font-size: 26px; /* ให้เกือบเต็มวง */
    }

    .msg-bubble {
        max-width: 75%;
        padding: 1rem 1.25rem;
        border-radius: 18px;
        font-size: 0.92rem;
        line-height: 1.7;
        position: relative;
        word-wrap: break-word;
    }
    .msg-bubble.user-bubble {
        background: linear-gradient(135deg, #a8d4f0 0%, #bce0f7 100%);
        color: #2c5570;
        border-bottom-right-radius: 6px;
        box-shadow: 0 3px 12px rgba(160, 200, 230, 0.2);
    }
    .msg-bubble.bot-bubble {
        background: #ffffff;
        color: #3d4f5f;
        border: 1px solid rgba(190, 215, 235, 0.4);
        border-bottom-left-radius: 6px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.03);
    }

    .msg-time {
        font-size: 0.7rem;
        color: rgba(0, 0, 0, 0.85);
        margin-top: 6px;
        text-align: right;
    }
    .msg-row.bot .msg-time { text-align: left; }

    /* ===== Typing Indicator ===== */
    .typing-indicator {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 0.8rem 1.2rem;
        background: #ffffff;
        border: 1px solid rgba(190, 215, 235, 0.4);
        border-radius: 18px;
        border-bottom-left-radius: 6px;
        max-width: 100px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.03);
    }
    .typing-dot {
        width: 7px;
        height: 7px;
        background: #a8d4f0;
        border-radius: 50%;
        animation: bounce 1.4s infinite ease-in-out;
    }
    .typing-dot:nth-child(2) { animation-delay: 0.16s; }
    .typing-dot:nth-child(3) { animation-delay: 0.32s; }

    @keyframes bounce {
        0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
        40% { transform: scale(1); opacity: 1; }
    }

    /* ===== Input Area ===== */
    .stChatInput {
        border-radius: 16px !important;
    }
    .stChatInput > div {
        border-radius: 16px !important;
        border: 1.5px solid rgba(180, 210, 235, 0.4) !important;
        background: rgba(255, 255, 255, 0.95) !important;
        backdrop-filter: blur(10px) !important;
        box-shadow: 0 2px 12px rgba(160, 200, 230, 0.06) !important;
        transition: all 0.3s ease !important;
    }
    .stChatInput > div:focus-within {
        border-color: #a8d4f0 !important;
        box-shadow: 0 3px 18px rgba(168, 212, 240, 0.15) !important;
    }
    .stChatInput textarea {
        font-family: 'Inter', sans-serif !important;
        font-size: 0.98rem !important;
        color: #ffffff !important;
        font-weight: 500 !important;
    }
    .stChatInput button {
        background: linear-gradient(135deg, #a8d4f0, #bce0f7) !important;
        border: none !important;
        border-radius: 12px !important;
        transition: all 0.3s ease !important;
    }
    .stChatInput button:hover {
        transform: scale(1.05) !important;
        box-shadow: 0 3px 12px rgba(168, 212, 240, 0.3) !important;
    }
    .stChatInput button svg {
        color: #4a7fa0 !important;
    }

    /* ===== Sidebar ===== */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f7fafd 0%, #ffffff 100%) !important;
        border-right: 1px solid rgba(190, 215, 235, 0.2);
    }
    section[data-testid="stSidebar"] .stButton > button {
        background: linear-gradient(135deg, #a8d4f0, #bce0f7) !important;
        color: #3a6b8c !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        padding: 0.6rem 1rem !important;
        transition: all 0.3s ease !important;
    }
    section[data-testid="stSidebar"] .stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 14px rgba(168, 212, 240, 0.3) !important;
    }

    /* ===== Stats Cards ===== */
    .stat-card {
        background: rgba(255,255,255,0.9);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(190, 215, 235, 0.25);
        border-radius: 14px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.8rem;
        box-shadow: 0 1px 8px rgba(0,0,0,0.02);
    }
    .stat-card .stat-label {
        font-size: 0.75rem;
        color: #97a8b5;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 600;
    }
    .stat-card .stat-value {
        font-size: 1.1rem;
        font-weight: 700;
        color: #3d4f5f;
        margin-top: 4px;
    }

    /* ===== Scrollbar ===== */
    .chat-area::-webkit-scrollbar { width: 5px; }
    .chat-area::-webkit-scrollbar-track { background: transparent; }
    .chat-area::-webkit-scrollbar-thumb {
        background: #c5ddef;
        border-radius: 10px;
    }
    .chat-area::-webkit-scrollbar-thumb:hover {
        background: #a8d4f0;
    }

    /* ===== Welcome message ===== */
    .welcome-msg {
        text-align: center;
        padding: 3rem 2rem;
        color: #97a8b5;
    }
    .welcome-msg .welcome-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
        display: block;
    }
    .welcome-msg h3 {
        color: #5a7a8f;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    .welcome-msg p {
        color: #9db0bc;
        font-size: 0.9rem;
    }

    /* ===== Quick action chips ===== */
    .quick-chips {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        justify-content: center;
        margin-top: 1rem;
    }
    .chip {
        background: rgba(168, 212, 240, 0.1);
        border: 1px solid rgba(168, 212, 240, 0.3);
        border-radius: 20px;
        padding: 0.4rem 1rem;
        font-size: 0.8rem;
        color: #6a9ab8;
        cursor: default;
        transition: all 0.3s ease;
    }
    .chip:hover {
        background: rgba(168, 212, 240, 0.18);
        box-shadow: 0 2px 8px rgba(168, 212, 240, 0.12);
    }
</style>
""", unsafe_allow_html=True)


# -------------------- Session State --------------------
# 1. เช็คว่ามี session_id ใน URL หรือไม่
if "session_id" not in st.session_state:
    if "session_id" in st.query_params:
        # ยึดค่าแชทเดิมจาก URL
        st.session_state.session_id = st.query_params["session_id"]
    else:
        # ถ้าไม่มี(เข้าครั้งแรก) ให้สุ่มใหม่ แล้วใส่กลับเข้าไปใน URL
        new_session = str(uuid.uuid4())
        st.session_state.session_id = new_session
        st.query_params["session_id"] = new_session

# บังคับให้อัปเดต URL ตามค่า session_state เสมอ
st.query_params["session_id"] = st.session_state.session_id

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "is_thinking" not in st.session_state:
    st.session_state.is_thinking = False



# -------------------- Agent Import --------------------
# Import create_agent จาก rag-comp.py (ใช้ importlib เพราะชื่อไฟล์มี hyphen)
@st.cache_resource
def load_rag_module():
    """โหลดโมดูล rag-comp.py"""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "rag_comp",
        os.path.join(os.path.dirname(__file__), "rag-comp.py")
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


try:
    rag_module = load_rag_module()
    # สร้าง agent พร้อม session_id เพื่อจำประวัติสนทนา
    agent = rag_module.create_agent(session_id=st.session_state.session_id)
    agent_loaded = True
    
    # -------------------- Load History from AWS --------------------
    # ถ้าในหน้าจอยังไม่มีประวัติแชท (เช่น เพิ่งกด Refresh) ให้ลองไปดึงประวัติเก่าของ Session นี้มาจาก AWS
    if not st.session_state.chat_history:
        try:
            import boto3
            import json
            from datetime import datetime
            
            client = boto3.client(
                'bedrock-agentcore',
                region_name=os.getenv("AWS_DEFAULT_REGION", "ap-southeast-2"),
                aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
            )
            
            # ต้องใส่ actorId ด้วย ไม่งั้นจะติด Error: Missing required parameter "actorId"
            resp = client.list_events(
                memoryId=rag_module.MEMORY_ID, 
                sessionId=st.session_state.session_id,
                actorId="regcom-assistant"
            )
            
            events = resp.get('events', [])
            loaded_history = []
            
            # API ข้อมูลมักจะมาแบบใหม่สุดอยู่บนสุด เราจึง reverse ให้ข้อความเก่าขึ้นก่อน
            for event in reversed(events):
                payloads = event.get('payload', [])
                for p in payloads:
                    # เอาเฉพาะข้อมูลแชท (มองข้าม blob metadata ต่างๆ)
                    if 'conversational' in p:
                        raw_text = p['conversational'].get('content', {}).get('text', '')
                        if raw_text:
                            try:
                                msg_data = json.loads(raw_text)
                                msg = msg_data.get("message", {})
                                msg_role = msg.get("role", "")
                                text_content = msg.get("content", [{}])[0].get("text", "")
                                
                                if text_content:
                                    role = "user" if msg_role.lower() == "user" else "assistant"
                                    # จำลองเวลาเป็นปัจจุบันไปก่อน เพื่อความง่ายต่อการแสดงผล
                                    time_str = datetime.now().strftime("%H:%M")
                                    loaded_history.append({
                                        "role": role,
                                        "content": text_content,
                                        "timestamp": time_str
                                    })
                            except json.JSONDecodeError:
                                pass # ข้ามถ้าข้อความไม่ใช่รูปแบบ JSON ที่ถูกต้อง

            if loaded_history:
                st.session_state.chat_history = loaded_history
        except Exception as aws_err:
            logger.warning(f"Could not load chat history from AWS: {aws_err}")

except Exception as e:
    logger.error(f"Failed to load agent: {e}")
    agent_loaded = False
    agent_error = str(e)


# -------------------- Helper Functions --------------------
def get_time_str():
    """คืนค่าเวลาปัจจุบันเป็น string"""
    from datetime import datetime
    return datetime.now().strftime("%H:%M")


def render_message(role, content, timestamp):
    """สร้าง HTML สำหรับ message bubble"""
    import html
    import re
    
    # ลบ Tag <thinking> ออกไปให้หมด ทั้งตอนเจอเต็มๆ และตอนกำลังค่อยๆ Stream โผล่มา
    content_cleaned = re.sub(r'<thinking>.*?(?:</thinking>|$)', '', content, flags=re.DOTALL).strip()
    
    # ป้องกัน Tag ประหลาดอื่นๆ ทำ UI พัง
    escaped_content = html.escape(content_cleaned)
    
    if role == "user":
        return f"""<div class="msg-row user">
<div class="msg-bubble user-bubble">
{escaped_content}
<div class="msg-time">{timestamp}</div>
</div>
<div class="msg-avatar user-av">👤</div>
</div>"""
    else:
        # แปลง newlines เป็น <br> สำหรับ bot response
        formatted = escaped_content.replace("\n", "<br>")
        return f"""<div class="msg-row bot">
<div class="msg-avatar bot-av">🤖</div>
<div class="msg-bubble bot-bubble">
{formatted}
<div class="msg-time">{timestamp}</div>
</div>
</div>"""


def render_typing_indicator():
    """สร้าง HTML สำหรับ typing indicator"""
    return """<div class="msg-row bot">
<div class="msg-avatar bot-av">🤖</div>
<div class="typing-indicator">
<div class="typing-dot"></div>
<div class="typing-dot"></div>
<div class="typing-dot"></div>
</div>
</div>"""


# -------------------- Header --------------------
st.markdown("""
<div class="header-banner">
    <h1>📘 RegCom Assistant</h1>
    <p>ผู้ช่วยตอบคำถามเกี่ยวกับกฎระเบียบและข้อบังคับ — Powered by Amazon Bedrock</p>
</div>
""", unsafe_allow_html=True)

# -------------------- Sidebar --------------------
with st.sidebar:
    st.markdown("### ⚙️ ตั้งค่า")

    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-label">Session ID</div>
        <div class="stat-value">{st.session_state.session_id[:8]}...</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-label">จำนวนข้อความ</div>
        <div class="stat-value">{len(st.session_state.chat_history)}</div>
    </div>
    """, unsafe_allow_html=True)

    status_text = "🟢 พร้อมใช้งาน" if agent_loaded else "🔴 ไม่สามารถโหลด Agent ได้"
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-label">สถานะระบบ</div>
        <div class="stat-value">{status_text}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    if st.button("🔄 เริ่มสนทนาใหม่", use_container_width=True):
        new_session = str(uuid.uuid4())
        st.session_state.session_id = new_session
        st.query_params["session_id"] = new_session
        st.session_state.chat_history = []
        st.rerun()

    if st.button("🗑️ ล้างประวัติ", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()


# -------------------- Chat Area --------------------
chat_container = st.empty()

def update_chat_ui():
    chat_html = ""
    if not st.session_state.chat_history:
        chat_html = """
        <div class="welcome-msg">
            <span class="welcome-icon">💬</span>
            <h3>สวัสดีครับ! ยินดีต้อนรับ</h3>
            <p>ลองถามคำถามเกี่ยวกับกฎระเบียบหรือข้อบังคับได้เลยครับ</p>
            <div class="quick-chips">
                <span class="chip">📋 ระเบียบการลา</span>
                <span class="chip">📝 ข้อบังคับพนักงาน</span>
                <span class="chip">⚖️ กฎหมายแรงงาน</span>
                <span class="chip">🏢 ระเบียบสำนักงาน</span>
            </div>
        </div>
        """
    else:
        for msg in st.session_state.chat_history:
            if msg["role"] == "typing":
                chat_html += render_typing_indicator()
            else:
                chat_html += render_message(msg["role"], msg["content"], msg["timestamp"])
                
    chat_container.markdown(f'<div class="chat-area" id="chat-area">{chat_html}</div>', unsafe_allow_html=True)

update_chat_ui()

# Auto-scroll to bottom
st.markdown("""
<script>
    const chatArea = document.getElementById('chat-area');
    if (chatArea) { chatArea.scrollTop = chatArea.scrollHeight; }
</script>
""", unsafe_allow_html=True)


# -------------------- Input --------------------
user_input = st.chat_input("พิมพ์คำถามของคุณที่นี่...", key="chat_input")

if user_input:
    # เพิ่มข้อความผู้ใช้
    st.session_state.chat_history.append({
        "role": "user",
        "content": user_input,
        "timestamp": get_time_str(),
    })
    
    # เรนเดอร์ข้อความผู้ใช้ก่อน
    update_chat_ui()

    # เรียก Agent
    if agent_loaded:
        import asyncio
        async def stream_bot_response():
            bot_index = len(st.session_state.chat_history)
            
            # เตรียมช่องว่างสำหรับข้อความ Bot
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": "",
                "timestamp": get_time_str(),
            })
            
            try:
                # วิ่ง Loop แบบ Streaming ทยอยส่งตัวอักษร
                async for chunk in agent.stream_async(user_input):
                    if 'delta' in chunk and 'text' in chunk['delta']:
                        st.session_state.chat_history[bot_index]["content"] += chunk['delta']['text']
                        update_chat_ui()
            except Exception as e:
                logger.error(f"Agent error: {e}")
                st.session_state.chat_history[bot_index]["content"] += f"\\n\\n❌ เกิดข้อผิดพลาด: {str(e)}"
                update_chat_ui()
                
        # สั่งรัน Async Loop
        asyncio.run(stream_bot_response())
    else:
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": f"⚠️ ไม่สามารถโหลด Agent ได้: {agent_error}",
            "timestamp": get_time_str(),
        })
        update_chat_ui()

    # รีเฟรชหน้าเพื่อให้สถานะ UI ลงตัวตามการอัพเดทสุดท้าย
    st.rerun()


# -------------------- Footer --------------------
st.markdown("""
<div style="text-align: center; padding: 1rem 0 0.5rem 0; color: #c0c8d0; font-size: 0.75rem;">
    RegCom Assistant v1.0 • Powered by Strands + Amazon Bedrock Knowledge Base
</div>
""", unsafe_allow_html=True)
