import pyautogui
import pytesseract
import re
import time
import numpy as np
import cv2
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

HP_REGION =(496, 38, 139, 32) # 固定血條位置

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


# 測試用
if __name__ == "__main__":
    get_boss_hp_percentage()
