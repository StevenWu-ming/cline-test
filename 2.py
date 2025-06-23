import pyautogui
import pytesseract
from PIL import Image
import re
import time

def get_channel_id_from_screen():
    # 裁切畫面區域：這是你提供的頻道 3302 位置
    region = (585, 278, 105, 22)  # (left, top, width, height)
    screenshot = pyautogui.screenshot(region=region)
    screenshot = screenshot.convert("L")  # 灰階提升準確率

    # OCR 辨識頻道號
    text = pytesseract.image_to_string(screenshot, lang='eng', config='--psm 7')
    print(f"🧾 OCR 擷取結果：{text.strip()}")

    # 從文字中擷取數字（頻道號）
    match = re.search(r"\d{3,5}", text)
    if match:
        return match.group()
    return "未知頻道"

# 執行測試
if __name__ == "__main__":
    print("📸 3 秒後擷取頻道畫面，請準備好顯示頻道畫面...")
    time.sleep(3)
    result = get_channel_id_from_screen()
    print(f"🎯 偵測頻道：{result}")
