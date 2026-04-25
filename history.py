import os
import boto3
from dotenv import load_dotenv

# โหลดคีย์ AWS
load_dotenv()

MEMORY_ID = "reg_and_comp_memory-qjIiNIFM9j" # รหัสตู้ลิ้นชักใหญ่ของเรา

def check_memory():
    # สร้าง Client สำหรับเชื่อมต่อกับ AWS
    client = boto3.client(
        'bedrock-agentcore',  # ใช้ชื่อ Data Plane Service ของ AgentCore
        region_name=os.getenv("AWS_DEFAULT_REGION", "ap-southeast-2"),
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
    )
    
    print(f"🔍 ส่องข้อมูล Memory: {MEMORY_ID}")
    
    try:
        # ดึง Events หรือประวัติที่อยู่ในแฟ้มนี้
        # หมายเหตุ: คุณต้องระบุ session_id ที่ต้องการดู
        # เช่น ถ้าอยากดูของ Session ไหน ให้เอา Session ID มาใส่แทน "session_id_ที่ต้องการส่อง"
        target_session = "543b6434-4dd1-4ccd-b815-2edb71f1f480"
        
        # ดึง Events หรือประวัติที่อยู่ในแฟ้มนี้
        response = client.list_events(
            memoryId=MEMORY_ID,
            sessionId=target_session,
            actorId="regcom-assistant"
        )
        
        # เก็บข้อความทั้งหมดไว้ในตัวแปร List
        chat_log = []
        
        # วนลูปอ่านประวัติ
        for event in response.get('events', []):
            print(f"DEBUG Event: {str(event)}")
            role = event.get('actorId')
            # ตรวจสอบโครงสร้าง Content
            content = event.get('content', {})
            text = content.get('text', 'No text')
            
            # บางทีอาจจะอยู่ที่อื่น?
            if text == 'No text' and 'message' in content:
                text = content.get('message', {}).get('content', [{}])[0].get('text', 'No text (deeply nested)')

            line = f"[{role}]: {text}"
            print(line)
            chat_log.append(line)
        
        # สร้างโฟลเดอร์ logs ถ้ายังไม่มี
        os.makedirs("logs", exist_ok=True)
        filename = f"logs/chat_history_{target_session}.txt"
        
        # เขียนไฟล์ลง Local
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"--- ประวัติการสนทนา Session: {target_session} ---\n\n")
            f.write("\n".join(chat_log))
            
        print(f"\n✅ บันทึกประวัติเสร็จสิ้น! สามารถเปิดดูได้ที่ไฟล์: {filename}")
            
    except Exception as e:
        print(f"ไม่สามารถอ่านได้ (หรือยังไม่มีข้อมูลประวัติ): {e}")

if __name__ == "__main__":
    check_memory()
