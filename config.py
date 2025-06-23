# 支援多隻王的設定
BOSSES = [
    {
        "name": "雪毛怪人",
        "image_path": "boss_yeti.png",
        "region": (717, 300, 469, 33),
        "threshold": 0.3,
        "message_template": "⚠️ 雪毛怪人出現！頻道：{channel_id}，請立刻支援！",
        "discord_webhook": "https://discord.com/api/webhooks/XXX/雪毛怪人webhook"
    },
    {
        "name": "姑姑鐘",
        "image_path": "boss_shadow.png",
        "region": (620, 288, 760, 50),
        "threshold": 0.4,
        "message_template": "⚠️ 暗影領主來襲！頻道：{channel_id}，快打！",
        "discord_webhook": "https://discord.com/api/webhooks/XXX/暗影領主webhook"
    },
    {
        "name": "火焰鳥王",
        "image_path": "boss_phoenix.png",
        "region": (580, 295, 780, 45),
        "threshold": 0.35,
        "message_template": "🔥 火焰鳥王出沒！頻道：{channel_id}，注意避難！",
        "discord_webhook": "https://discord.com/api/webhooks/XXX/火焰鳥王webhook"
    }
]

# 要執行的王（一次一隻）
ENABLED_BOSS_NAMES = ["雪毛怪人"]

# 頻道 OCR 擷取區域
CHANNEL_REGION = (585, 278, 105, 22)

# 每隻王的偵測次數上限（共用設定）
BOSS_MAX_CHECKS = 6
