# 頻道 OCR 擷取區域
CHANNEL_REGION = (585, 278, 105, 22)

# 選擇要執行的 BOSS 名稱
SELECTED_BOSS_NAME = "姑姑鐘"  # ✅ 這裡改你要跑的王名稱

# 全域 timeout 設定（秒）
TIMEOUT_CONFIG = {
    "ocr_timeout": 15,           # 頻道擷取最多等待幾秒
    "wait_image_timeout": 30,    # 等待進入遊戲畫面最多幾秒
    "between_steps": 2,          # 換頻後進入遊戲前等待幾秒
    "after_notify_delay": 3      # 通知後延遲幾秒才繼續下一輪
}

# 全部 BOSS 設定列表
BOSSES = [
    {
        "name": "雪毛怪人",
        "image_path": "4.png",
        "region": (717, 300, 469, 33),
        "threshold": 0.3,
        "max_checks": 6,
        "message_template": "⚠️ 雪毛怪人出現！頻道：{channel_id}，請立刻支援！",
        "discord_webhook": "https://discord.com/api/webhooks/1386755368956461156/kwkhDT5hWtmoAlRKycK__8dd7pqVD74Czv0KNNLe2yqF1FiY1kxlsNKFFjonyteiOKhB"
    },
    {
        "name": "姑姑鐘",
        "image_path": "2.png",
        "region": (570, 290, 794, 47),
        "threshold": 0.4,
        "max_checks": 6,
        "message_template": "⚠️ 姑姑鐘來襲！頻道：{channel_id}，快打！",
        "discord_webhook": "https://discord.com/api/webhooks/1386644016560476160/fqvm7j01D0YKfnxkDh17YlGZpLHshNkSSKzNKVMr-GFXFGkYr2BFRjLeTOnU_8m2QXci"
    },
    {
        "name": "巴洛古",
        "image_path": "boss_phenix.png",
        "region": (570, 290, 794, 47),
        "threshold": 0.3,
        "max_checks": 6,
        "message_template": "🔥 巴洛古出沒！頻道：{channel_id}，注意避難！",
        "discord_webhook": "https://discord.com/api/webhooks/1386644116560937082/J2yUFgJ4UvJWqyaFSUa82IL99b1yL4VyWsj6HsiEcjH-k6erkZf0S6JwRs3aBI4pi8Kr"
    },
    {
        "name": "殭屍姑姑王",
        "image_path": "0.png",
        "region": (570, 290, 794, 47),
        "threshold": 0.3,
        "max_checks": 6,
        "message_template": "🔥 殭屍姑姑王出沒！頻道：{channel_id}，注意避難！",
        "discord_webhook": "https://discord.com/api/webhooks/1386643817352134758/EczaVP3aDLtP1Fr74MGGmocBkzTK0bQ7cJPBpNV9987gfVvA8s5nVHoBGmISfpeujclS"
    },
    {
        "name": "厄運死神",
        "image_path": "1.png",
        "region": (570, 290, 794, 47),
        "threshold": 0.3,
        "max_checks": 6,
        "message_template": "🔥 厄運死神出沒！頻道：{channel_id}，注意避難！",
        "discord_webhook": "https://discord.com/api/webhooks/1387077139362484316/P_Ql8eh8bKFdF2G6dtRZHiDJyD76Fq3dwQfwSSrnm1tA5MyNgxvkP0KNbAZrJAhGTsX4"
    }
]

# 自動挑出要執行的王
selected_boss = next((boss for boss in BOSSES if boss["name"] == SELECTED_BOSS_NAME), None)
if not selected_boss:
    raise ValueError(f"❌ config.py 中找不到名稱為「{SELECTED_BOSS_NAME}」的 BOSS 設定")
