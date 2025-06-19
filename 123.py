import time
import random
from pynput.keyboard import Key, Controller

keyboard = Controller()

def press_key(key, min_hold=0.08, max_hold=0.09):
    hold_time = random.uniform(min_hold, max_hold)
    keyboard.press(key)
    time.sleep(hold_time)
    keyboard.release(key)
    time.sleep(random.uniform(0.03, 0.04))  # 模擬人類鍵與鍵間停頓

def do_action():
    print("🎮 執行動作：← → Option → Delete")
    press_key(Key.left)
    press_key(Key.right)
    # press_key(Key.alt)       # Option 鍵單獨按一下
    press_key(Key.delete)    # 然後再按 Delete
    # press_key('a')

try:
    while True:
        delay = random.uniform(15, 120)
        print(f"⌛ 等待 {delay:.2f} 秒...")

        time.sleep(delay)

        # 偷懶機率（10%）
        if random.random() < 0.1:
            print("😴 偷懶一輪，看起來像 AFK 中...")
            continue

        do_action()

except KeyboardInterrupt:
    print("\n🛑 偵測到手動中斷（Ctrl+C），腳本已結束")
