import pyautogui
import time
import random
import cv2
import numpy as np
import os

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
def wait_for_image(template_path, timeout=17, threshold=0.85):
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
        time.sleep(1)

    print("⚠️ 超時未偵測到登入畫面")
    return False

# 偵測是否出現 BOSS 提示文字（持續掃描最多 max_wait 秒）
def detect_boss(template_path="boss_alert.png", threshold=0.50, max_wait=5):
    print(f"🕵️‍♂️ 掃描 BOSS 提示中...（threshold={threshold}, max_wait={max_wait}s）")

    template = cv2.imread(template_path, cv2.IMREAD_COLOR)
    if template is None:
        print(f"❌ BOSS 圖片讀取失敗：{template_path}")
        return False

    start = time.time()
    highest_val = 0

    while time.time() - start < max_wait:
        screenshot = pyautogui.screenshot()
        screen = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
        max_val = result.max()

        if max_val >= threshold:
            print(f"🎯 發現 BOSS 提示！（相似度：{max_val:.3f}）")
            return True
        else:
            if max_val > highest_val:
                highest_val = max_val
                print(f"❌ 相似度不足（最高）：{highest_val:.3f}")
        time.sleep(0.8)

    print("❌ 時間內未偵測到 BOSS")
    return False

# 播放提示音（使用 macOS 內建 afplay 或語音）
def play_alert():
    if os.path.exists("alert.mp3"):
        os.system("afplay alert.mp3")
    else:
        os.system('say "王王王王出現了！"')

# 換頻流程
def change_channel():
    print("🔄 開始換頻")
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

        if wait_for_image("enter_ready.png", timeout=17):
            enter_game()
        else:
            print("❌ 跳過進入遊戲")

        time.sleep(2)  # 畫面穩定時間

        if detect_boss("boss_alert.png", threshold=0.5, max_wait=5):
            print("🔔 發現 BOSS，播放提示")
            play_alert()
            break
        else:
            print("❌ 未偵測到 BOSS，準備換下一頻...\n")
            time.sleep(2)

# 執行
run_cycle()
