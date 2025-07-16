import socketio
import requests
from datetime import datetime, timedelta, timezone
from config import selected_boss

DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1394566463397953677/KzpWTVQF2ls9Azjz4JHeEik6en4Z6md_pMYzEIGiIydZw8sKIID38jhHZnLEoM70KCpp"

sio = socketio.Client()

@sio.event
def connect():
    print("WebSocket連線成功")

# 只處理 newMessage
@sio.on("newMessage")
def on_new_message(data):
    # data 可能是 list
    if isinstance(data, list):
        for msg in data:
            send_formatted_message(msg)
    elif isinstance(data, dict):
        send_formatted_message(data)

def send_formatted_message(msg):
    try:
        username = msg.get("username", "")
        text = msg.get("text", "")
        channel = msg.get("channel", "")
        timestamp = msg.get("timestamp", "")

        # 格式化時間（台灣時區）
        try:
            dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00")) + timedelta(hours=8)
            time_str = dt.strftime("%m-%d %H:%M:%S")
        except Exception:
            time_str = timestamp

        # 最終輸出格式
        result = f"【{channel}】{username}：{text}  {time_str}"
        print(result)

        payload = {
            "content": result
        }
        requests.post(DISCORD_WEBHOOK_URL, json=payload)
    except Exception as e:
        print(f"格式化訊息出錯: {e}, msg: {msg}")

@sio.event
def disconnect():
    print("WebSocket關閉")

if __name__ == "__main__":
    sio.connect('https://apiv2.pal.tw')
    input("按下Enter結束...\n")
    sio.disconnect()


