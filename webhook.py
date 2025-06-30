import requests

url = 'https://discord.com/api/webhooks/1387971184917872670/8wCR3oKLsZCj9_Cf76_-zkImSRb4F1lvgdx2bM5J_hpO1J5ssAYpMd3fvgaoHGk3-y8s'
data = {
    'content': '🔥🔥請不要一直偷看我們刷王的頻道,在外傳出去被抓到我就全部踢掉🔥🔥'
}

response = requests.post(url, json=data)

print(response.status_code)
print(response.text)
