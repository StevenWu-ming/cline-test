import requests
from config import (
    selected_boss,
)
url = selected_boss['discord_webhook']
data = {
    'content': '好像是要7/9號結束才會解鎖 ',
}

response = requests.post(url, json=data)

print(response.status_code)
print(response.text)
