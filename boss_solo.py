import pyautogui
import time
import random
import cv2
import numpy as np
import os
import requests

# DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1385589087125372999/7LB7lWc5JDGwkdwtoMlKgG8rtxRXHuyUFPCWUGmoJPe1Lou9ugAlGAL8xIm-7ZN7VYHQ"

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

def detect_boss(template_path="0.png", threshold=0.50, max_checks=7):
    print(f"🕵️‍♂️ 掃描 BOSS 提示中...（threshold={threshold}, max_checks={max_checks} 次）")

    template = cv2.imread(template_path, cv2.IMREAD_COLOR)
    if template is None:
        print(f"❌ BOSS 圖片讀取失敗：{template_path}")
        return False

    highest_val = 0
    for i in range(1, max_checks + 1):
        screenshot = pyautogui.screenshot()
        screen = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
        max_val = result.max()

        if max_val >= threshold:
            print(f"🎯 第 {i} 次：發現 BOSS 提示！（相似度：{max_val:.3f}）")
            return True
        else:
            highest_val = max(highest_val, max_val)
            print(f"❌ 第 {i} 次：相似度不足（最高至今：{highest_val:.3f}）")

        time.sleep(0.8)

    print("❌ 所有偵測次數內未發現 BOSS")
    return False



# 播放提示音（使用 macOS 內建 afplay 或語音）
def play_alert():
    if os.path.exists("alert.mp3"):
        os.system("afplay alert.mp3")
    else:
        os.system('say "王王王王出現了！"')

    # # 傳送 Discord 通知
    # try:
    #     payload = {
    #         "content": "🎯 發現 BOSS！請立刻上線！擠 櫻吹雪 頻道"
    #     }
    #     response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
    #     if response.status_code == 204:
    #         print("✅ Discord 通知已發送")
    #     else:
    #         print(f"⚠️ Discord 發送失敗：{response.status_code}")
    # except Exception as e:
    #     print(f"❌ 發送 Discord 時發生錯誤：{e}")


def send_discord_alert(message):
    webhook_url = "https://discord.com/api/webhooks/1385589087125372999/7LB7lWc5JDGwkdwtoMlKgG8rtxRXHuyUFPCWUGmoJPe1Lou9ugAlGAL8xIm-7ZN7VYHQ"
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

# 換頻流程
def change_channel():
    print("🔄 開始換頻")
    human_click(1714, 250)
    human_click(1714, 1050)  # 換頻入口
    human_click(1704, 962)   # 頻道列表
    human_click(1290, 241)   # 進入頻道
    human_click(872, 612)    # 確認換頻
    print("✅ 換頻完成")

# 進入遊戲流程
def enter_game():
    print("🎮 進入遊戲流程")
    time.sleep(5)
    human_click(1297, 574)   # 進入遊戲按鈕
    time.sleep(5)
    human_click(1311, 406)   # 確認按鈕
    print("✅ 進入遊戲完成")

# 主循環流程
def run_cycle():
    while True:
        change_channel()

        if wait_for_image("enter_ready.png", timeout=30):
            enter_game()
        else:
            print("❌ 跳過進入遊戲")

        time.sleep(2)  # 畫面穩定時間

        if detect_boss("1.png", threshold=0.3, max_checks=6):
            print("🔔 發現 BOSS，播放提示")
            play_alert()
            send_discord_alert("警告！！！BOSS 出現了！擠櫻吹雪頻道")
            break
        else:
            print("❌ 未偵測到 BOSS，準備換下一頻...\n")
            time.sleep(2)

# 執行
run_cycle()
