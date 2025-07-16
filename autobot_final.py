import pyautogui
import cv2
import numpy as np
import time
from pynput.keyboard import Controller, Key

# === 參數設定 ===
FREE_MARKET_BTN = (1471, 1031)
PORTAL_IMAGE_PATH = "portal.png"
FREEMARK_IMAGE_PATH = "freemark.png"
# PORTAL_X = 330
ENTER_KEY_REPEAT = 3
WAIT_INSIDE = 4 * 60          # 在自由市場等待時間（秒）
# MAX_MOVE_TRY = 30
STEP_TIME = 0.3
CONF_THRESHOLD = 0.4
MAX_ENTER_ATTEMPTS = 10
HOLD_LEFT_TIME = 2.5            # 失敗時按住左鍵持續時間（秒）
UP_PRESS_INTERVAL = 0.05         # 按上鍵間隔（秒）

keyboard = Controller()

# 圖像比對，回傳中心座標與信心值
def match_image(template_path):
    screen = pyautogui.screenshot()
    screen_np = np.array(screen)
    gray = cv2.cvtColor(screen_np, cv2.COLOR_RGB2GRAY)
    tmpl = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
    if tmpl is None:
        return None, 0.0
    res = cv2.matchTemplate(gray, tmpl, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(res)
    center_x = max_loc[0] + tmpl.shape[1] // 2
    center_y = max_loc[1] + tmpl.shape[0] // 2
    return (center_x, center_y), max_val

# 向左走一步
def step_left(duration=STEP_TIME):
    pyautogui.keyDown('left')
    time.sleep(duration)
    pyautogui.keyUp('left')

# # 移動至固定 portal X
# def move_to_portal():
#     print("🚶 開始向左移動至傳送門 X=330")
#     for _ in range(MAX_MOVE_TRY):
#         (loc, conf) = match_image(PORTAL_IMAGE_PATH)
#         if conf < CONF_THRESHOLD or loc is None:
#             print(f"❌ 傳送門信心值低（{conf:.3f}），執行一步左移")
#             step_left()
#             continue
#         portal_x = loc[0]
#         delta = portal_x - PORTAL_X
#         print(f"📍 Portal x={portal_x}, 差距={delta}px")
#         if abs(delta) < 10:
#             print("✅ 已靠近傳送門 X=330")
#             return
#         step_left()
#     print("⚠️ 未能精準靠近傳送門")

# 嘗試進門並確認離開：偵測不到 freemark.png 表示已離開自由市場
# 偵測到 freemark.png 代表仍在自由市場，按住左鍵並持續按上鍵重試
def try_enter_and_confirm():
    for attempt in range(1, MAX_ENTER_ATTEMPTS + 1):
        print(f"⬆️ 第 {attempt} 次按上鍵傳送")
        for _ in range(ENTER_KEY_REPEAT):
            keyboard.press(Key.up)
            time.sleep(0.1)
            keyboard.release(Key.up)
            time.sleep(0.2)
        time.sleep(1)
        (_, conf) = match_image(FREEMARK_IMAGE_PATH)
        print(f"🔍 freemark 信心值 = {conf:.3f}")
        if conf < CONF_THRESHOLD:
            print("✅ 未偵測到 freemark，已離開自由市場")
            return
        else:
            print("❌ 偵測到 freemark，仍在自由市場，按住左鍵並持續按上鍵重試")
            # 按住左鍵並持續按上鍵
            pyautogui.keyDown('left')
            start = time.time()
            while time.time() - start < HOLD_LEFT_TIME:
                keyboard.press(Key.up)
                time.sleep(UP_PRESS_INTERVAL)
                keyboard.release(Key.up)
                time.sleep(UP_PRESS_INTERVAL)
            pyautogui.keyUp('left')
    print("⚠️ 已達最大嘗試次數，跳過本輪")

# 主循環
if __name__ == '__main__':
    print("✅ 自動掛機腳本 (固定走位+freemark 判斷+持續左移+按上鍵) 啟動")
    time.sleep(2)
    while True:
        print("🌀 按 Shift 施放技能")
        keyboard.press(Key.shift)
        time.sleep(0.3)
        keyboard.release(Key.shift)

        print("🏪 點擊自由市場")
        pyautogui.click(FREE_MARKET_BTN)
        time.sleep(5)

        print(f"⏱ 在自由市場等待 {WAIT_INSIDE//60} 分鐘...")
        time.sleep(WAIT_INSIDE)

        # move_to_portal()
        try_enter_and_confirm()

