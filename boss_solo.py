import pyautogui
import time
import random
import cv2
import numpy as np
import os
import requests
import pytesseract
import re
import subprocess
from datetime import datetime
from PIL import Image
from config import (
    selected_boss,
    CHANNEL_REGION,
    TIMEOUT_CONFIG,
    HP_REGION    
)

# timeout 設定
ocr_timeout = TIMEOUT_CONFIG["ocr_timeout"]
wait_image_timeout = TIMEOUT_CONFIG["wait_image_timeout"]
between_steps = TIMEOUT_CONFIG["between_steps"]
after_notify_delay = TIMEOUT_CONFIG["after_notify_delay"]

# debug 圖片儲存
DEBUG_FOLDER = "ocr_debug"
os.makedirs(DEBUG_FOLDER, exist_ok=True)

print("\n📋 正在執行 BOSS 偵測配置：")
print(f"🔹 名稱：{selected_boss['name']}")
print(f"🔹 圖片路徑：{selected_boss['image_path']}")
print(f"🔹 偵測區域：{selected_boss['region']}")
print(f"🔹 相似度門檻：{selected_boss['threshold']}")
print(f"🔹 Webhook：{selected_boss['discord_webhook']}")
print(f"🔹 訊息模板：{selected_boss['message_template']}\n")

def human_click(x, y):
    pyautogui.moveTo(
        x + random.randint(-2, 2),
        y + random.randint(-2, 2),
        duration=random.uniform(0.1, 0.3)
    )
    pyautogui.click()
    time.sleep(random.uniform(0.5, 1.2))

def wait_for_image(template_path, timeout=wait_image_timeout, threshold=0.85):
    template = cv2.imread(template_path, cv2.IMREAD_COLOR)
    if template is None:
        print(f"❌ 圖片讀取失敗：{template_path}")
        return False

    start = time.time()
    while time.time() - start < timeout:
        screenshot = pyautogui.screenshot()
        screen = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
        if (result >= threshold).any():
            print("✅ 偵測到登入畫面")
            return True
        print("⌛ 等待登入畫面載入...")
        time.sleep(3)

    print("⚠️ 超時未偵測到登入畫面")
    return False

def detect_boss():
    print(f"🕵️‍♂️ 掃描 BOSS 提示中...（threshold={selected_boss['threshold']}, max_checks={selected_boss['max_checks']} 次）")
    template = cv2.imread(selected_boss['image_path'], cv2.IMREAD_GRAYSCALE)
    if template is None:
        print(f"❌ BOSS 圖片讀取失敗：{selected_boss['image_path']}")
        return False

    highest_val = 0
    for i in range(1, selected_boss['max_checks'] + 1):
        screenshot = pyautogui.screenshot(region=selected_boss['region'])
        screen = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)
        result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
        max_val = result.max()

        if max_val >= selected_boss['threshold']:
            print(f"🎯 第 {i} 次：發現 BOSS 提示！（相似度：{max_val:.3f}）")
            return True
        else:
            highest_val = max(highest_val, max_val)
            print(f"❌ 第 {i} 次：相似度不足（最高至今：{highest_val:.3f}）")
        time.sleep(0.5)

    print("❌ 所有偵測次數內未發現 BOSS")
    return False

def get_boss_hp_percentage(timeout=10):
    start_time = time.time()
    while time.time() - start_time < timeout:
        screenshot = pyautogui.screenshot(region=HP_REGION)
        gray = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)
        _, thresh = cv2.threshold(gray, 160, 255, cv2.THRESH_BINARY)

        text = pytesseract.image_to_string(thresh, lang='eng', config='--psm 7').strip()
        print("🧾 OCR 擷取文字：", text)

        match = re.search(r'(\d{1,3})\s*%', text)
        if match:
            percent = int(match.group(1))
            print(f"✅ 偵測到血量百分比：{percent}%")
            return percent
        else:
            print("❌ 未偵測到 % 數，重試中...")

        time.sleep(0.5)

    print("⚠️ 超時仍未偵測到血量 % 數（可能沒人打）")
    return None

# 預處理 OCR 圖像
def preprocess_for_ocr(image):
    gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
    _, thresh = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY)
    kernel = np.ones((1, 1), np.uint8)
    processed = cv2.dilate(thresh, kernel, iterations=1)
    return processed

# 新 OCR 偵測頻道邏輯（強化）
def get_channel_id_from_screen(timeout=ocr_timeout):
    start = time.time()
    while time.time() - start < timeout:
        screenshot = pyautogui.screenshot(region=CHANNEL_REGION)
        processed = preprocess_for_ocr(screenshot)

        text = pytesseract.image_to_string(
            processed,
            lang='eng',
            config='--psm 7 -c tessedit_char_whitelist=0123456789'
        ).strip()

        print(f"🧾 OCR 擷取文字：{text}")
        match = re.search(r"\d{1,4}", text)
        if match:
            channel = match.group()
            if 1 <= int(channel) <= 5000:
                print(f"✅ 偵測到頻道：{channel}")
                return channel
            else:
                print(f"⚠️ 偵測到不合理頻道號：{channel}")
        else:
            print("❌ 未偵測成功，重試中...")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        Image.fromarray(processed).save(os.path.join(DEBUG_FOLDER, f"fail_{timestamp}.png"))
        time.sleep(0.5)

    print("⚠️ 頻道擷取超時，回傳預設值")
    return "未知頻道"

def play_alert():
    if os.path.exists("alert.mp3"):
        subprocess.Popen(["afplay", "alert.mp3"])
    else:
        subprocess.Popen(["say", "王王王王出現了！"])

def send_discord_alert(message):
    payload = {"content": message}
    try:
        response = requests.post(selected_boss['discord_webhook'], json=payload)
        if response.status_code in [200, 204]:
            print("✅ Discord 通知發送成功")
        else:
            print(f"⚠️ 發送失敗，狀態碼：{response.status_code}")
            print("伺服器回應：", response.text)
    except Exception as e:
        print(f"❌ 發送 Discord 通知時發生錯誤：{e}")

def channel():
    print("🔄 查看頻道")
    human_click(1714, 1050)
    human_click(1704, 962)
    time.sleep(3)
    print("✅ 查看完成")

def change_channel():
    print("🔄 開始換頻")
    human_click(1714, 250)
    human_click(1714, 1050)
    human_click(1704, 962)
    human_click(1290, 241)
    human_click(872, 612)
    print("✅ 換頻完成")

def enter_game():
    print("🎮 進入遊戲流程")
    time.sleep(5)
    human_click(1297, 574)
    time.sleep(5)
    human_click(1311, 406)
    print("✅ 進入遊戲完成")

def run_cycle():
    while True:
        change_channel()

        if wait_for_image("enter_ready.png"):
            enter_game()
        else:
            print("❌ 跳過進入遊戲")

        time.sleep(between_steps)

        if detect_boss():
            print("🔔 發現 BOSS，播放提示")
            play_alert()
            print("📌 準備進行頻道偵測與通知...")
            channel()
            channel_id = get_channel_id_from_screen()
            print(f"📌 頻道偵測完成：{channel_id}")
            human_click(1348, 243)
            print("📌 點擊結束按鈕完成")

            # 新增血量偵測
            hp = get_boss_hp_percentage()
            if hp is not None:
                message = f"{selected_boss['message_template'].format(channel_id=channel_id)}（剩餘血量：約 {hp}%）"
            else:
                message = f"{selected_boss['message_template'].format(channel_id=channel_id)}(目前還沒人打)"


            send_discord_alert(message)
            print("📌 Discord 通知發送完成")
            print("✅ 已通知，繼續換頻...\n")
            time.sleep(after_notify_delay)
            # send_discord_alert("偵測到殭屍姑姑 擠我頻道")
            break  # 偵測到 BOSS 後結束循環，準備換頻
        else:
            print("❌ 未偵測到 BOSS，準備換下一頻...\n")
            time.sleep(between_steps)

# 執行主流程
run_cycle()
