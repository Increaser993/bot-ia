import os
import discord
import requests

DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

if not DISCORD_TOKEN:
    raise ValueError("DISCORD_TOKEN não definido!")

if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY não definido!")

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

@client.event
async def on_ready():
    print(f"✅ Bot conectado como {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("!chat "):
        prompt = message.content[6:]
        await message.channel.send("🤖 Pensando...")

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://discord-bot.local",
            "X-Title": "MeuBotDiscord"
        }

        data = {
            "model": "meta-llama/llama-3-8b-instruct:free",
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }

        try:
            response = requests.post(OPENROUTER_URL, headers=headers, json=data)

            if response.status_code != 200:
                await message.channel.send(f"❌ Erro {response.status_code}: {response.text}")
                return

            result = response.json()

            reply = result["choices"][0]["message"]["content"]

            # Discord limita mensagem a 2000 caracteres
            await message.channel.send(reply[:2000])

        except Exception as e:
            await message.channel.send(f"❌ Erro na requisição: {e}")

client.run(DISCORD_TOKEN)
