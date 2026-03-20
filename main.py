import discord
import os
import requests

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

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

    if message.content.startswith("!ai"):
        user_text = message.content.replace("!ai", "")

        await message.channel.send("🤖 กำลังคิด...")

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
                        {"role": "user", "content": user_text}
                    ]
                }
            )

            data = response.json()
            reply = data["choices"][0]["message"]["content"]

            await message.channel.send(reply)

        except Exception as e:
            await message.channel.send("❌ error: " + str(e))

client.run(DISCORD_TOKEN)
