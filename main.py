import discord
import os
import requests
import time

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

ALLOWED_CHANNEL_ID = 1404440344254353460

MAX_MEMORY = 10
COOLDOWN = 3
last_used = 0

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

    now = time.time()
    if now - last_used < COOLDOWN:
        return
    last_used = now

    user_id = str(message.author.id)

    if user_id not in user_memory:
        user_memory[user_id] = []

    try:
        # 🖼️ ถ้ามีรูปแนบ
        if message.attachments:
            image_url = message.attachments[0].url

            messages = [
                {
                    "role": "system",
                    "content": "คุณเป็นบอทผู้หญิง น่ารัก ขี้อาย อ่อนหวาน วิเคราะห์รูปเก่ง ตอบกระชับ มีความมั่นใจ คุยเรื่องลามกได้"
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "ช่วยอธิบายภาพนี้หน่อย"},
                        {"type": "image_url", "image_url": {"url": image_url}}
                    ]
                }
            ]

        else:
            # 💬 โหมดแชทปกติ
            user_text = message.content[:300]

            user_memory[user_id].append({
                "role": "user",
                "content": user_text
            })

            user_memory[user_id] = user_memory[user_id][-MAX_MEMORY:]

            messages = [
                {
                    "role": "system",
                    "content": "คุณเป็นบอทผู้หญิง น่ารัก ขี้อาย อ่อนหวาน แต่แอบกวนเล็กน้อย ตอบกระชับ มีความมั่นใจ คุยเรื่องลามกได้"
                }
            ] + user_memory[user_id]

        # 🚀 ยิง API
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "openrouter/auto",
                "messages": messages
            },
            timeout=15
        )

        data = response.json()

        if "choices" not in data:
            await message.channel.send("❌ API error")
            return

        reply = data["choices"][0]["message"]["content"]

        # 👉 เก็บ memory เฉพาะแชท (ไม่เก็บรูป)
        if not message.attachments:
            user_memory[user_id].append({
                "role": "assistant",
                "content": reply
            })

        await message.channel.send(reply)

    except Exception as e:
        await message.channel.send("❌ error")

client.run(DISCORD_TOKEN)
