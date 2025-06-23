本腳本可自動偵測《Artale（楓之谷 Worlds）》王怪提示並發送 Discord 通知！

📦 環境需求
作業系統：Windows 10 / 11

Python：3.8～3.12

已安裝以下工具：

Tesseract OCR for Windows

pip 套件安裝器

📁 檔案內容
請確保以下檔案與 main.py 同個資料夾：

bash
複製
編輯
main.py                 # 主程式
enter_ready.png         # 登入按鈕畫面圖
4.png                   # BOSS 提示字樣圖
alert.mp3               # 音效（可選）
requirements.txt        # Python 套件清單
README.md               # 本文件


🔧 第一次安裝流程
✅ 安裝 Python
從官網安裝：https://www.python.org/downloads/
✔ 安裝時請勾選 Add Python to PATH

✅ 安裝 Tesseract OCR

下載安裝包：Tesseract for Windows

預設安裝路徑為：
C:\Program Files\Tesseract-OCR\tesseract.exe

✅ 安裝 Python 套件

打開命令提示字元（cmd），進入程式資料夾，輸入：

bash
複製
編輯
pip install -r requirements.txt
📌 修改主程式（只需一次）
如果 Tesseract 安裝路徑是預設，請在 main.py 開頭加上：

python
複製
編輯
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
▶ 執行方式
在 main.py 所在資料夾開啟命令列，輸入：

bash
複製
編輯
python main.py
📷 若座標不符怎麼辦？
遊戲解析度建議：1920x1080 全螢幕

若無法點到、偵測不到畫面：

修改 human_click(x, y) 中的座標

修改 detect_boss() 裡的 region = (...)

修改 get_channel_id_from_screen() 裡的座標範圍

你可以用這段小工具偵測目前滑鼠位置：

python
複製
編輯
import pyautogui
import time

while True:
    print(pyautogui.position(), end="\r")
    time.sleep(0.1)
🧪 測試 Discord 通知是否正常？
你可以單獨測試：

python
複製
編輯
from main import send_discord_alert
send_discord_alert("✅ 測試訊息：Discord 通知正常")



python -m pyautogui
