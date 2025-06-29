import requests

url = 'https://discord.com/api/webhooks/你的WebhookID/你的Token'
data = {
    'content': '這是 Python 發送的測試訊息'
}

response = requests.post(url, json=data)

print(response.status_code)
print(response.text)
