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
    # 1. 按住下方向鍵
    print("🎮 執行動作：按住 ↓，再按一下 x")
    keyboard.press(Key.down)
    # 隨機保持 0.5～0.7 秒
    time.sleep(random.uniform(0.5, 0.7))
    # 2. 按一下 x
    press_key('x')
    # 3. 釋放下方向鍵
    keyboard.release(Key.down)

def run_actions(max_count=2):
    """
    每隔隨機時間執行 do_action()，總共執行 max_count 次後停止。
    中途有 10% 機率偷懶，跳過當次動作。
    """
    action_count = 0
    try:
        while action_count < max_count:
            delay = random.uniform(1, 1)
            print(f"⌛ 等待 {delay:.2f} 秒...")
            time.sleep(delay)

            # 偷懶機率（10%）
            if random.random() < 0.1:
                print("😴 偷懶一輪，看起來像 AFK 中...")
                continue

            # 執行動作
            do_action()
            action_count += 1
            print(f"✅ 動作已執行 {action_count} 次")

        print(f"🏁 已執行 {max_count} 次，腳本結束。")
    except KeyboardInterrupt:
        print("\n🛑 偵測到手動中斷（Ctrl+C），腳本已結束")

if __name__ == "__main__":
    run_actions(2)
