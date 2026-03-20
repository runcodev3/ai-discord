import discord
import os
import requests
import time

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

ALLOWED_CHANNEL_ID = 1404440344254353460

# 🔥 แนะนำ 10-15 พอ
MAX_MEMORY = 12

# ⏱️ กันยิงรัว
COOLDOWN = 3
last_used = 0

# 🧠 memory
user_memory = {}

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'บอทออนไลน์แล้ว: {client.user}')

@client.event
async def on_message(message):
    global last_used

    if message.author == client.user:
        return

    if message.channel.id != ALLOWED_CHANNEL_ID:
        return

    # ❌ กันข้อความสั้น / spam
    if len(message.content.strip()) < 2:
        return

    # ⏱️ cooldown กันโดน rate limit
    now = time.time()
    if now - last_used < COOLDOWN:
        return
    last_used = now

    user_id = str(message.author.id)
    user_text = message.content[:300]  # ตัดข้อความยาวเกิน

    if user_id not in user_memory:
        user_memory[user_id] = []

    # ➕ เพิ่มข้อความ user
    user_memory[user_id].append({
        "role": "user",
        "content": user_text
    })

    # ✂️ จำกัด memory
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
                        "content": "คุณเป็นบอทผู้หญิง น่ารัก ขี้อาย อ่อนหวาน แต่แอบกวนเล็กน้อย ตอบสั้น กระชับ เป็นธรรมชาติ"
                    }
                ] + user_memory[user_id]
            },
            timeout=10  # 🔥 กันค้าง
        )

        data = response.json()

        # ❌ เช็ค error จาก API
        if "choices" not in data:
            await message.channel.send("❌ API error")
            return

        reply = data["choices"][0]["message"]["content"]

        # ➕ เก็บคำตอบบอท
        user_memory[user_id].append({
            "role": "assistant",
            "content": reply
        })

        await message.channel.send(reply)

    except Exception as e:
        await message.channel.send("❌ error")

client.run(DISCORD_TOKEN)
