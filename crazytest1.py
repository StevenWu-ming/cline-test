import pyautogui
import time
import random
import cv2
import numpy as np
import os
import requests
import pytesseract
import re
from datetime import datetime
from PIL import Image
from pynput.keyboard import Key, Controller
import win32gui
import win32con
import win32api

# ✅ === 使用者自定參數 ===
BOSS_NAME = "瘋狂喵z客"
BOSS_IMAGE_PATH = "8.png"             # BOSS 圖片檔
BOSS_REGION = (208, 84, 1500, 74)    # 圖像偵測區域
BOSS_THRESHOLD = 0.3                 # 相似度門檻
STEALTH_ICON_PATH = "stealth_buff.png"  # ← 替換為你的隱身圖示檔名
STEALTH_REGION = (1747, 35, 27, 24)     # ← 根據實際畫面調整區域
MAX_CHECKS = 6                        # 每次最多偵測幾次
CHANNEL_REGION = (797, 136, 33, 19)   # 頻道 OCR 區域x
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1396021846188752946/f4rz4xI2hh_5Sd_4iOFcIFf5086xM7igIpEYz6CSTwXk4DKjcuw3I_r3llvwJq3f2utG"
MESSAGE_TEMPLATE = "🔔 發現 {boss_name} 出現在頻道 {channel_id}！請速前往！"

# Timeout 時間（秒）
wait_image_timeout = 60
between_steps = 2
after_notify_delay = 3
ocr_timeout = 15
# 初始化鍵盤控制器
keyboard = Controller()

# Tesseract 路徑
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# debug 圖片儲存
DEBUG_FOLDER = "ocr_debug"
os.makedirs(DEBUG_FOLDER, exist_ok=True)

# 🔍 MapleStory 視窗標題
TARGET_TITLE = "MapleStory Worlds-Artale (繁體中文版)"

def find_window(title_keyword):
    def callback(hwnd, result):
        title = win32gui.GetWindowText(hwnd)
        if title_keyword.lower() in title.lower() and win32gui.IsWindowVisible(hwnd):
            result.append(hwnd)
    hwnds = []
    win32gui.EnumWindows(callback, hwnds)
    return hwnds[0] if hwnds else None

def move_window_top_half(hwnd):
    screen_w = win32api.GetSystemMetrics(0)
    screen_h = win32api.GetSystemMetrics(1)

    x = 0
    y = 0
    width = screen_w              # ✅ 全螢幕寬
    height = screen_h // 2        # ✅ 螢幕高一半

    # 取得目前視窗位置與大小
    rect = win32gui.GetWindowRect(hwnd)
    curr_x, curr_y, curr_r, curr_b = rect
    curr_width = curr_r - curr_x
    curr_height = curr_b - curr_y

    # 如果已經在正確位置與大小就略過
    if (curr_x, curr_y, curr_width, curr_height) == (x, y, width, height):
        return False  # 表示未移動

    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    win32gui.MoveWindow(hwnd, x, y, width, height, True)
    return True  # 表示有移動

print("\n📋 正在執行 BOSS SEARCH📉")
print(f"🔹 名稱：{BOSS_NAME}")
print(f"🔹 圖片路徑：{BOSS_IMAGE_PATH}")
print(f"🔹 偵測區域：{BOSS_REGION}")
print(f"🔹 相似度門檻：{BOSS_THRESHOLD}")
print(f"🔹 Webhook：{DISCORD_WEBHOOK}")
print(f"🔹 訊息模板：{MESSAGE_TEMPLATE}\n")

def human_click(x, y, clicks=1, interval=0.1):
    pyautogui.moveTo(
        x + random.randint(-2, 2),
        y + random.randint(-2, 2),
        duration=random.uniform(0.06, 0.1)
    )
    pyautogui.click(clicks=clicks, interval=interval)
    time.sleep(random.uniform(0.3, 0.5))

# def check_and_close_reconnect(template_path="reconnect_box.png", threshold=0.85):
#     template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
#     if template is None:
#         print(f"❌ 模板讀取失敗：{template_path}")
#         return False

#     screenshot = pyautogui.screenshot()
#     screen = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)

#     result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
#     _, max_val, _, _ = cv2.minMaxLoc(result)

#     if max_val >= threshold:
#         print(f"❌ 偵測到『重新連線』視窗（相似度：{max_val:.3f}），點擊右上角 ❌")
#         human_click(1089, 238)  # 你提供的 X 座標
#         return True

#     return False 

def wait_for_image(template_path, timeout=wait_image_timeout, threshold=0.85):
    template = cv2.imread(template_path, cv2.IMREAD_COLOR)
    if template is None:
        print(f"❌ 圖片讀取失敗：{template_path}")
        return False
    start = time.time()
    while time.time() - start < timeout:
        # check_and_close_reconnect()  # ✅ 每輪檢查「重新連線」視窗

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
    print(f"🕵️‍♂️ 掃描 BOSS 提示中...（threshold={BOSS_THRESHOLD}, max_checks={MAX_CHECKS} 次）")

    template = cv2.imread(BOSS_IMAGE_PATH, cv2.IMREAD_GRAYSCALE)
    if template is None:
        print(f"❌ BOSS 圖片讀取失敗：{BOSS_IMAGE_PATH}")
        return False

    flipped_template = cv2.flip(template, 1)  # 水平翻轉

    highest_val = 0
    for i in range(1, MAX_CHECKS + 1):
        screenshot = pyautogui.screenshot(region=BOSS_REGION)
        screen = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)

        result_normal = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
        max_val_normal = result_normal.max()

        result_flipped = cv2.matchTemplate(screen, flipped_template, cv2.TM_CCOEFF_NORMED)
        max_val_flipped = result_flipped.max()

        max_val = max(max_val_normal, max_val_flipped)

        if max_val >= BOSS_THRESHOLD:
            print(f"🎯 第 {i} 次：發現 BOSS 提示！（相似度：{max_val:.3f}）")
            return True
        else:
            highest_val = max(highest_val, max_val)
            print(f"❌ 第 {i} 次：相似度不足（最高至今：{highest_val:.3f}）")

        time.sleep(0.4)

    print("❌ 所有偵測次數內未發現 BOSS")
    time.sleep(1.5)
    return False

def preprocess_for_ocr(image):
    gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
    _, thresh = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY)
    kernel = np.ones((1, 1), np.uint8)
    processed = cv2.dilate(thresh, kernel, iterations=1)
    return processed

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
        match = re.search(r"\d{1,5}", text)
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

def send_discord_alert(message):
    payload = {"content": message}
    try:
        response = requests.post(DISCORD_WEBHOOK, json=payload)
        if response.status_code in [200, 204]:
            print("✅ Discord 通知發送成功")
        else:
            print(f"⚠️ 發送失敗，狀態碼：{response.status_code}")
            print("伺服器回應：", response.text)
    except Exception as e:
        print(f"❌ 發送 Discord 通知時發生錯誤：{e}")

def channel():
    print("🔄 查看頻道")
    human_click(1816, 516)
    human_click(1816, 470)
    time.sleep(3)
    print("✅ 查看完成")

def change_channel():
    print("🔄 開始換頻")
    human_click(1816, 516)
    human_click(1816, 470)
    human_click(1124, 123)
    human_click(927, 304)
    print("✅ 換頻完成")

def enter_game():
    print("🎮 進入遊戲流程")

    # ✅ 點擊前先確認是否跳出重新連線視窗
    # check_and_close_reconnect()

    time.sleep(3)
    human_click(1123, 282)

    # ✅ 點擊後再檢查一次是否跳出重新連線視窗
    time.sleep(1)
    # check_and_close_reconnect()

    time.sleep(2)
    human_click(1134, 204)

    print("✅ 進入遊戲完成")

def press_key(key, min_hold=0.08, max_hold=0.09):
    hold_time = random.uniform(min_hold, max_hold)
    keyboard.press(key)
    time.sleep(hold_time)
    keyboard.release(key)
    time.sleep(random.uniform(0.03, 0.04))

def is_stealth_active(threshold=0.75):
    """偵測隱身 Buff 是否已啟用"""
    template = cv2.imread(STEALTH_ICON_PATH, cv2.IMREAD_GRAYSCALE)
    if template is None:
        print(f"❌ 隱身圖示圖片讀取失敗：{STEALTH_ICON_PATH}")
        return False

    screenshot = pyautogui.screenshot(region=STEALTH_REGION)
    screen = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)

    result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, _ = cv2.minMaxLoc(result)

    print(f"🔍 隱身圖示相似度：{max_val:.3f}")
    return max_val >= threshold

def ensure_stealth(threshold=0.75):
    print("🛡️ 檢查是否有隱身 Buff 狀態...")
    if is_stealth_active(threshold):
        print("✅ 已處於隱身狀態，繼續操作")
    else:
        print("🫥 尚未隱身，施放 X 鍵一次")
        press_key('c', min_hold=0.05, max_hold=0.07)
        time.sleep(0.5)
        if is_stealth_active(threshold):
            print("✅ 成功進入隱身狀態")
        else:
            print("⚠️ 未偵測到 Buff，仍繼續操作")

def do_action():
    """執行下跳動作（↓ + 空白鍵）"""
    print("🎮 執行下跳動作（↓ + 空白鍵）")
    keyboard.press(Key.down)
    time.sleep(0.1)
    press_key(Key.space, min_hold=0.05, max_hold=0.07)
    keyboard.release(Key.down)
    print("✅ 下跳完成")


def run_actions(max_count=3):
    """啟動隱身後執行指定次數的下跳"""
    print("🫥 嘗試啟動隱身技能（持續按 X 鍵直到 Buff 出現）")
    stealth_timeout = 20  # 最多嘗試秒數
    start_time = time.time()

    while not is_stealth_active():
        press_key('c', min_hold=0.05, max_hold=0.07)
        time.sleep(0.4)
        if time.time() - start_time > stealth_timeout:
            print("❌ 超時未偵測到隱身 Buff，放棄下跳")
            return  # 不做下跳，直接返回

    print("✅ 成功啟動隱身，立即執行下跳")
    
    for i in range(max_count):
        delay = random.uniform(0.6, 0.8)
        print(f"⌛ 等待 {delay:.2f} 秒後執行第 {i+1} 次下跳")
        time.sleep(delay)
        do_action()

def handle_death_and_teleport():
    death_template = cv2.imread("death.png", cv2.IMREAD_GRAYSCALE)
    if death_template is None:
        return
    screenshot = pyautogui.screenshot()
    screen_gray = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)
    result = cv2.matchTemplate(screen_gray, death_template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, _ = cv2.minMaxLoc(result)
    if max_val >= 0.8:
        print("💀 偵測到死亡視窗，相似度：", max_val)
        human_click(1078, 229)  # 確認回城
        time.sleep(4)

        print("🎒 開啟背包並傳送")
        press_key('i')  # 開啟背包
        time.sleep(2)

        human_click(358, 146)  # 點擊道具欄頁籤（若有）
        time.sleep(2)

        for _ in range(2):
            human_click(358, 182)
            time.sleep(0.2)

        human_click(444, 208)  # 點擊地圖上方的分類（或地圖按鈕）
        time.sleep(2)

        human_click(1020, 340)  # 點擊地圖區域位置
        time.sleep(8)

        print("✅ 傳送回場景完成")   

def run_cycle():
    while True:
        boss_found = False

        # ✅ 確保每輪一開始畫面已經是登入畫面（換頻後才會出現）
        if not wait_for_image("enter_ready1.png"):
            print("❌ 未進入登入畫面，跳過本輪")
            continue

        # ✅ 等進入畫面後再調整視窗
        hwnd = find_window(TARGET_TITLE)
        if hwnd:
            if move_window_top_half(hwnd):
                print("🖥️ 已將視窗調整為螢幕二分之一大小")
            else:
                print("🖥️ 視窗大小已正確")
        else:
            print("❌ 找不到 MapleStory 視窗")

        enter_game()
        time.sleep(1.5)
        run_actions(3)
        time.sleep(1.5)
        boss_found = detect_boss()
        if boss_found:
            handle_death_and_teleport()

        time.sleep(0.3)

        print("🔔 前往自由市場")
        human_click(1693, 516, clicks=2)
        time.sleep(3)

        if boss_found:
            print("📌 開始進行頻道偵測與通知...")
            channel()
            channel_id = get_channel_id_from_screen()
            print(f"📌 頻道偵測完成：{channel_id}")
            keyboard.press(Key.esc)
            print("📌 點擊結束按鈕完成")
            message = MESSAGE_TEMPLATE.format(boss_name=BOSS_NAME, channel_id=channel_id)
            send_discord_alert(message)
            print("📌 Discord 通知發送完成")

        else:
            print("❌ 未偵測到 BOSS")
        
        change_channel()
        time.sleep(after_notify_delay)

# =========== 執行主流程 ============
if __name__ == '__main__':
    # ✅ 啟動時先找視窗並調整為上半螢幕
    hwnd = find_window(TARGET_TITLE)
    if hwnd:
        if move_window_top_half(hwnd):
            print("🖥️ 啟動時已將 MapleStory 視窗調整為螢幕二分之一大小")
        else:
            print("🖥️ MapleStory 視窗初始大小已正確")
    else:
        print("❌ 找不到 MapleStory 視窗")

    # ✅ 啟動時立即先進行一次換頻（例如從預設頻道跳開）
    change_channel()

    # ✅ 正式進入主循環
    run_cycle()