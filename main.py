import discord
import os
import requests

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

ALLOWED_CHANNEL_ID = 1404440344254353460  # ใส่ ID ห้อง

# 👉 กำหนดความจำ (ยิ่งมากยิ่งจำเยอะ)
MAX_MEMORY = 100

# 👉 เก็บ memory แยกแต่ละ user
user_memory = {}

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'บอทออนไลน์แล้ว: {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.channel.id != ALLOWED_CHANNEL_ID:
        return

    user_id = str(message.author.id)
    user_text = message.content

    # 👉 ถ้ายังไม่มี memory ให้สร้าง
    if user_id not in user_memory:
        user_memory[user_id] = []

    # 👉 เพิ่มข้อความ user
    user_memory[user_id].append({
        "role": "user",
        "content": user_text
    })

    # 👉 จำกัด memory
    user_memory[user_id] = user_memory[user_id][-MAX_MEMORY:]

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
                        "content": "คุณเป็นบอทกวนๆ ฉลาดๆ ตอบมั่นใจ เป็นผู้หญิง ขี้อาย อ่อนหวาน นิสัยดี"
                    }
                ] + user_memory[user_id]
            }
        )

        data = response.json()
        reply = data["choices"][0]["message"]["content"]

        # 👉 เก็บคำตอบบอทด้วย
        user_memory[user_id].append({
            "role": "assistant",
            "content": reply
        })

        await message.channel.send(reply)

    except Exception as e:
        await message.channel.send("❌ error")

client.run(DISCORD_TOKEN)
