import time
import random
import cv2
import numpy as np
import pyautogui
from pynput.keyboard import Key, Controller

# 初始化鍵盤控制器
keyboard = Controller()

# ----------------------------
# 第一部分：執行預設動作序列
# ----------------------------
def press_key(key, min_hold=0.08, max_hold=0.09):
    hold_time = random.uniform(min_hold, max_hold)
    keyboard.press(key)
    time.sleep(hold_time)
    keyboard.release(key)
    time.sleep(random.uniform(0.03, 0.04))  # 模擬按鍵間隙

def do_action():
    # 按住下方向鍵，持續隨機時間，再按 x
    print("🎮 執行動作：按住 ↓，再按一下 x")
    keyboard.press(Key.down)
    time.sleep(random.uniform(0.5, 0.7))
    press_key('x')
    keyboard.release(Key.down)


def run_actions(max_count=2):
    """
    執行設定次數的隨機動作，每次間隔固定秒數，含 10% 機率偷懶。
    """
    action_count = 0
    try:
        while action_count < max_count:
            print(f"⌛ 等待 1.00 秒...")
            time.sleep(1)
            if random.random() < 0.1:
                print("😴 偷懶一輪...")
                continue
            do_action()
            action_count += 1
            print(f"✅ 動作已執行 {action_count} 次")
        print(f"🏁 已執行 {max_count} 次，動作結束。")
    except KeyboardInterrupt:
        print("🛑 動作中斷，結束動作序列。")

# ----------------------------
# 第二部分：持續按住 → 並偵測 BOSS
# ----------------------------
def detect_boss_multi(templates: list, region: tuple) -> dict:
    """
    截圖並比對多個 BOSS 模板，回傳相似度字典。
    """
    shot = pyautogui.screenshot(region=region)
    gray = cv2.cvtColor(np.array(shot), cv2.COLOR_RGB2GRAY)
    results = {}
    for tpl in templates:
        tmpl = cv2.imread(tpl, cv2.IMREAD_GRAYSCALE)
        if tmpl is None:
            print(f"❌ 無法讀取模板: {tpl}")
            results[tpl] = 0.0
            continue
        res = cv2.matchTemplate(gray, tmpl, cv2.TM_CCOEFF_NORMED)
        results[tpl] = float(res.max())
    return results


def hold_right_and_detect(templates, threshold=0.6, region=(8, 624, 1911, 146), interval=0.5):
    """
    按住 → 並持續偵測多圖；達標或中斷後放開並結束。
    """
    print("▶️ 按住 → 開始偵測…")
    keyboard.press(Key.right)
    try:
        cycle = 1
        while True:
            sims = detect_boss_multi(templates, region)
            ts = time.strftime("%Y-%m-%d %H:%M:%S")
            found = False
            for tpl, sim in sims.items():
                status = '🎯' if sim >= threshold else '❌'
                print(f"[{ts}] {status} {tpl} 相似度: {sim:.3f} (第 {cycle} 次)")
                if sim >= threshold:
                    found = True
            if found:
                print("🎉 偵測成功，放開 → 並結束偵測。")
                break
            cycle += 1
            time.sleep(interval)
    except KeyboardInterrupt:
        print("🛑 中斷偵測，放開 → 鍵。")
    finally:
        keyboard.release(Key.right)
        print("⏹ 已放開 →，程式結束。")

# ----------------------------
# 主程式入口：先執行動作，再執行偵測
# ----------------------------
if __name__ == "__main__":
    # 第一階段：執行動作序列
    run_actions(max_count=2)
    # 第二階段：按住右鍵並偵測 BOSS
    TEMPLATES = ["6.png", "7.png"]
    THRESHOLD = 0.6
    REGION = (8, 624, 1911, 146)
    INTERVAL = 0.5
    hold_right_and_detect(TEMPLATES, THRESHOLD, REGION, INTERVAL)
