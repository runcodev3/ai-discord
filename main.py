import discord
import os
import requests

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# 👉 ใส่ ID ห้องที่ต้องการให้บอทตอบ
ALLOWED_CHANNEL_ID = 1404440344254353460  # เปลี่ยนเป็น ID ห้องของนาย

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'บอทออนไลน์แล้ว: {client.user}')

@client.event
async def on_message(message):
    # ❌ ไม่ตอบตัวเอง
    if message.author == client.user:
        return

    # ❌ ตอบเฉพาะห้องที่กำหนด
    if message.channel.id != ALLOWED_CHANNEL_ID:
        return

    user_text = message.content

    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "openrouter/free",
                "messages": [
                    {
                        "role": "system",
                        "content": "คุณเป็นบอทกวนๆ ฉลาดนิดๆ ตอบสั้น กระชับ มั่นใจ มีความกวนแบบน่ารัก"
                    },
                    {
                        "role": "user",
                        "content": user_text
                    }
                ]
            }
        )

        data = response.json()
        reply = data["choices"][0]["message"]["content"]

        await message.channel.send(reply)

    except Exception as e:
        await message.channel.send("❌ error")

client.run(DISCORD_TOKEN)
