import os
import discord
import requests

DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

@client.event
async def on_ready():
    print(f"Bot conectado como {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("!chat "):
        prompt = message.content[6:]
        await message.channel.send("🤖 Pensando...")

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "meta-llama/llama-3-8b-instruct:free",
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }

        try:
            response = requests.post(OPENROUTER_URL, headers=headers, json=data)
            result = response.json()

            if "choices" in result:
                reply = result["choices"][0]["message"]["content"]
                await message.channel.send(reply[:2000])
            else:
                await message.channel.send(f"Erro: {result}")

        except Exception as e:
            await message.channel.send(f"Erro na requisição: {e}")

client.run(DISCORD_TOKEN)
