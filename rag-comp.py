import os
import uuid
import logging
import boto3
from dotenv import load_dotenv
from strands import Agent, tool

# Strands Session Manager สำหรับจำประวัติสนทนา (บันทึกลง AWS AgentCore Memory)
from bedrock_agentcore.memory.integrations.strands.session_manager import AgentCoreMemorySessionManager
from bedrock_agentcore.memory.integrations.strands.config import AgentCoreMemoryConfig

# -------------------- Setup --------------------
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MODEL_ID = "amazon.nova-pro-v1:0"
MEMORY_ID = "reg_and_comp_memory-qjIiNIFM9j"

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "ap-southeast-2")
KNOWLEDGE_BASE_ID = os.getenv("KNOWLEDGE_BASE_ID")

# สร้าง Bedrock Agent Runtime client (ใช้สำหรับ Knowledge Base)
bedrock_agent_runtime = boto3.client(
    service_name="bedrock-agent-runtime",
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
)


# -------------------- Tools --------------------


@tool
def get_data(query: str) -> str:
    """ดึงข้อมูลจาก Knowledge Base มาตอบคำถาม
    ใช้ tool นี้เมื่อต้องการค้นหาข้อมูลเกี่ยวกับกฎระเบียบ ข้อบังคับ หรือข้อมูลอื่น ๆ จากฐานความรู้

    Args:
        query: คำถามหรือคำค้นหาที่ต้องการค้นหาจากฐานความรู้
    """
    logger.info(f"*** get_data *** query: {query}")

    try:
        response = bedrock_agent_runtime.retrieve(
            knowledgeBaseId=KNOWLEDGE_BASE_ID,
            retrievalQuery={"text": query},
            retrievalConfiguration={
                "vectorSearchConfiguration": {
                    "numberOfResults": 5,  # จำนวน chunks ที่ต้องการ
                }
            },
        )

        # รวบรวมผลลัพธ์จาก Knowledge Base
        results = response.get("retrievalResults", [])

        if not results:
            return "ไม่พบข้อมูลที่เกี่ยวข้องในฐานความรู้"

        # จัดรูปแบบผลลัพธ์
        formatted_results = []
        for i, result in enumerate(results, 1):
            content = result.get("content", {}).get("text", "")
            score = result.get("score", 0)
            source = result.get("location", {}).get("s3Location", {}).get("uri", "N/A")

            formatted_results.append(
                f"--- ผลลัพธ์ที่ {i} (คะแนน: {score:.4f}) ---\n"
                f"แหล่งที่มา: {source}\n"
                f"เนื้อหา:\n{content}\n"
            )

        return "\n".join(formatted_results)

    except Exception as e:
        logger.error(f"get_data error: {e}")
        return f"เกิดข้อผิดพลาดในการค้นหาข้อมูล: {e}"


# -------------------- Session Manager --------------------
# ใช้ AgentCoreMemorySessionManager เก็บประวัติสนทนาลง AWS

DEFAULT_SESSION_ID = "default-session"


def create_agent(session_id: str = DEFAULT_SESSION_ID) -> Agent:
    """สร้าง Agent พร้อม session manager สำหรับจำประวัติสนทนา"""
    config = AgentCoreMemoryConfig(
        memory_id=MEMORY_ID,
        session_id=session_id,
        actor_id="regcom-assistant",
    )
    
    session_manager = AgentCoreMemorySessionManager(
        agentcore_memory_config=config,
        region_name=AWS_REGION,
    )

    return Agent(
        model=MODEL_ID,
        agent_id="regcom-assistant",  # จำเป็นเมื่อใช้ session_manager
        tools=[get_data],
        session_manager=session_manager,
        system_prompt=(
            "คุณเป็นผู้ช่วยตอบคำถามเกี่ยวกับกฎระเบียบและข้อบังคับ "
            "เมื่อผู้ใช้ถามคำถามเกี่ยวกับให้ใช้ tool get_data เพื่อค้นหาข้อมูลจากฐานความรู้ "
            "ถ้าผู้ใช้ถามเรื่องอื่นที่ไม่เกี่ยวกับข้อบังคับ เช่น บุคคล สถานที่ ให้ลองไปค้นในเอกสารก่อน "
            "ถ้าหาบุคคลไม่เจอขอโทษและตอบอย่างสุภาพว่า ฉันไม่มีข้อมูลเกี่ยวกับบุคคลที่คุณกล่าวถึง "
            "ถ้าหาสถานที่ไม่เจอขอโทษและตอบอย่างสุภาพว่า ฉันไม่มีข้อมูลเกี่ยวกับสถานที่ที่คุณกล่าวถึง "
            "แล้วนำข้อมูลที่ได้มาสรุปตอบเป็นภาษาไทยอย่างชัดเจน "
            "หากไม่พบข้อมูล ให้แจ้งผู้ใช้ว่าไม่พบข้อมูลที่เกี่ยวข้อง"
        ),
    )


# สร้าง agent สำหรับ import จาก chat_ui.py
agent = create_agent()


# -------------------- Main --------------------
if __name__ == "__main__":
    print("=" * 50)
    print("📘 RegCom Assistant (พร้อมจำประวัติสนทนา)")
    print("=" * 50)

    # ถาม session_id หรือใช้ default
    session_input = input("Session ID (Enter = สร้างใหม่): ").strip()
    session_id = session_input if session_input else str(uuid.uuid4())[:8]
    print(f"📌 Session: {session_id}\n")

    # สร้าง agent พร้อม session
    chat_agent = create_agent(session_id=session_id)

    while True:
        user_input = input("\nคุณ: ").strip()
        if user_input.lower() in ("exit", "quit", "q"):
            print("ลาก่อนครับ!")
            break
        if not user_input:
            continue

        response = chat_agent(user_input)
        print(f"\nBot: {response}")
        print(f"Session ID: {session_id}")
