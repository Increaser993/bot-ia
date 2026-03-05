import os
import discord
import time
from openai import OpenAI

DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")

if not DISCORD_TOKEN:
    raise ValueError("DISCORD_TOKEN não definido!")

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# 🔥 Cliente Hermes (OpenAI compatível)
client_ai = OpenAI(
    base_url="https://hermes.ai.unturf.com/v1",
    api_key="choose-any-value"  # geralmente não valida
)

MODEL = "adamo1139/Hermes-3-Llama-3.1-8B-FP8-Dynamic"

# 🔥 Controle de cooldown
user_cooldowns = {}
COOLDOWN_TIME = 10  # segundos entre usos por usuário

@client.event
async def on_ready():
    print(f"✅ Bot conectado como {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("!jeff "):

        # 🛑 Sistema anti-spam
        user_id = message.author.id
        now = time.time()

        if user_id in user_cooldowns:
            if now - user_cooldowns[user_id] < COOLDOWN_TIME:
                await message.channel.send("⏳ Espere alguns segundos antes de usar novamente.")
                return

        user_cooldowns[user_id] = now

        prompt = message.content[6:]
        await message.channel.send("🤖 Isso me fez coçar a cabeça...")

        try:
            response = client_ai.chat.completions.create(
                model=MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "Você é um assistente inteligente e responde sempre em português."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=300
            )

            reply = response.choices[0].message.content
            await message.channel.send(reply[:2000])

        except Exception as e:
            await message.channel.send(f"❌ Erro na requisição: {e}")

client.run(DISCORD_TOKEN)
