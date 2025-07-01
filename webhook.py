import requests
from config import (
    selected_boss,
)
url = selected_boss['discord_webhook']
data = {
    'content': 'TEST'
}

response = requests.post(url, json=data)

print(response.status_code)
print(response.text)
