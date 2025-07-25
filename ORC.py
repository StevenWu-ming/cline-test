import cv2
import numpy as np
from PIL import Image
import pytesseract
import pyautogui
import time
import re
import os
from datetime import datetime
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"



# 頻道畫面擷取區域（根據你的測試圖定義）
CHANNEL_REGION = (613, 245, 63, 34)

# 儲存 debug 圖片用資料夾
DEBUG_FOLDER = "ocr_debug"
os.makedirs(DEBUG_FOLDER, exist_ok=True)

# 預處理影像以增強 OCR 成效
def preprocess_for_ocr(image):
    gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
    _, thresh = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY)
    kernel = np.ones((1, 1), np.uint8)
    processed = cv2.dilate(thresh, kernel, iterations=1)
    return processed

# 執行 OCR 偵測頻道號碼
def get_channel_id_from_screen(timeout=5):
    start = time.time()
    has_saved = False  # 標誌，用來確保只保存一次失敗圖片
    
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
                if not has_saved:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    Image.fromarray(processed).save(os.path.join(DEBUG_FOLDER, f"fail_{timestamp}.png"))
                    has_saved = True  # 只保存一次
        else:
            print("❌ 未偵測成功，重試中...")
            if not has_saved:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                Image.fromarray(processed).save(os.path.join(DEBUG_FOLDER, f"fail_{timestamp}.png"))
                has_saved = True  # 只保存一次
        
        time.sleep(0.5)
    
    print("⚠️ 頻道擷取超時，回傳預設值")
    return "未知頻道"

# 測試執行
if __name__ == "__main__":
    print("🚀 開始頻道號碼 OCR 偵測測試...")
    get_channel_id_from_screen()
