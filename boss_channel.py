import pyautogui
import time
import random
import cv2
import numpy as np
import os
import requests
import pytesseract
import re

# 模擬點擊（人為延遲與微偏移）
def human_click(x, y):
    pyautogui.moveTo(
        x + random.randint(-2, 2),
        y + random.randint(-2, 2),
        duration=random.uniform(0.1, 0.3)
    )
    pyautogui.click()
    time.sleep(random.uniform(0.5, 1.2))

# 等待畫面載入完成（偵測進入遊戲按鈕）
def wait_for_image(template_path, timeout=20, threshold=0.85):
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

def detect_boss(template_path="0.png", threshold=0.6, max_checks=7):
    print(f"🕵️‍♂️ 掃描 BOSS 提示中...（threshold={threshold}, max_checks={max_checks} 次）")

    # 用灰階載入圖像，可提升準確度
    template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
    if template is None:
        print(f"❌ BOSS 圖片讀取失敗：{template_path}")
        return False

    highest_val = 0
    for i in range(1, max_checks + 1):
        # region = (717, 300, 469, 33)  # 只偵測王提示區域 雪毛
        region = (570, 290, 794, 47)  # 只偵測王提示區域 # 姑姑鐘 可能可以通用要多試試
        # region = (692, 301, 522, 27) 

        screenshot = pyautogui.screenshot(region=region)
        screen = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)

        result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
        max_val = result.max()

        if max_val >= threshold:
            print(f"🎯 第 {i} 次：發現 BOSS 提示！（相似度：{max_val:.3f}）")
            return True
        else:
            highest_val = max(highest_val, max_val)
            print(f"❌ 第 {i} 次：相似度不足（最高至今：{highest_val:.3f}）")

        time.sleep(0.5)

    print("❌ 所有偵測次數內未發現 BOSS")
    return False

# # 擷取頻道編號（OCR）
# def get_channel_id_from_screen():
#     region = (585, 278, 105, 22)  # 精準區域（頻道顯示區）
#     screenshot = pyautogui.screenshot(region=region)
#     screenshot = screenshot.convert("L")  # 灰階化
#     text = pytesseract.image_to_string(screenshot, lang='eng', config='--psm 7')
#     print(f"🧾 OCR 擷取文字：{text.strip()}")

#     match = re.search(r"\d{3,5}", text)
#     if match:
#         return match.group()
#     return "未知頻道"

def get_channel_id_from_screen(timeout=15):
    region = (585, 278, 105, 22)
    start = time.time()

    while time.time() - start < timeout:
        screenshot = pyautogui.screenshot(region=region)
        screenshot = screenshot.convert("L")
        text = pytesseract.image_to_string(screenshot, lang='eng', config='--psm 7')
        print(f"🧾 OCR 擷取文字：{text.strip()}")

        match = re.search(r"\d{3,5}", text)
        if match:
            return match.group()
        time.sleep(0.5)

    print("⚠️ 頻道擷取超時，回傳預設值")
    return "未知頻道"


# # 播放提示音
# def play_alert():
#     if os.path.exists("alert.mp3"):
#         os.system("afplay alert.mp3")
#     else:
#         os.system('say "王王王王出現了！"')

# 傳送 Discord
def send_discord_alert(message):
    webhook_url = "https://discord.com/api/webhooks/1386644016560476160/fqvm7j01D0YKfnxkDh17YlGZpLHshNkSSKzNKVMr-GFXFGkYr2BFRjLeTOnU_8m2QXci"
    payload = {
        "content": message
    }

    try:
        response = requests.post(webhook_url, json=payload)
        if response.status_code in [200, 204]:
            print("✅ Discord 通知發送成功")
        else:
            print(f"⚠️ 發送失敗，狀態碼：{response.status_code}")
            print("伺服器回應：", response.text)
    except Exception as e:
        print(f"❌ 發送 Discord 通知時發生錯誤：{e}")

# 查看換頻
def channel():
    print("🔄 查看頻道")
    human_click(1714, 1050)
    human_click(1704, 962)
    time.sleep(3)
    print("✅ 查看完成")


# 換頻流程
def change_channel():
    print("🔄 開始換頻")
    human_click(1714, 250)
    human_click(1714, 1050)
    human_click(1704, 962)
    human_click(1290, 241)
    human_click(872, 612)
    print("✅ 換頻完成")

# 進入遊戲流程
def enter_game():
    print("🎮 進入遊戲流程")
    time.sleep(5)
    human_click(1297, 574)
    time.sleep(5)
    human_click(1311, 406)
    print("✅ 進入遊戲完成")

# 主循環流程
def run_cycle():
    while True:
        change_channel()

        if wait_for_image("enter_ready.png", timeout=30):
            enter_game()
        else:
            print("❌ 跳過進入遊戲")

        time.sleep(2)

        if detect_boss("2.png", threshold=0.3, max_checks=6):
            # print("🔔 發現 BOSS，播放提示")
            # play_alert()

            # channel()
            # channel_id = get_channel_id_from_screen()
            # human_click(1348, 243)
            # send_discord_alert(f"⚠️ 雪毛怪人BOSS 出現了！頻道：{channel_id}，請立刻上線！")
        

            print("📌 準備進行頻道偵測與通知...")
            channel()
            channel_id = get_channel_id_from_screen()
            print(f"📌 頻道偵測完成：{channel_id}")
            human_click(1348, 243)
            print("📌 點擊結束按鈕完成")
            send_discord_alert(f"⚠️ 姑姑鐘BOSS 出現了！頻道：{channel_id}，請立刻上線！")
            print("📌 Discord 通知發送完成")


            print("✅ 已通知，繼續換頻...\n")
            time.sleep(3)
            continue  # ✅ 不結束，繼續下一輪
        
        else:
            print("❌ 未偵測到 BOSS，準備換下一頻...\n")
            time.sleep(2)

# 執行
run_cycle()
