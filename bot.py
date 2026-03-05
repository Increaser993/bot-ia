import os
import discord
import requests
import time
import numpy as np
import cv2

# ==========================
# VARIÁVEIS DE AMBIENTE
# ==========================
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

if not DISCORD_TOKEN:
    raise ValueError("DISCORD_TOKEN não definido!")

if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY não definido!")

# ==========================
# CONFIG DO BOT
# ==========================
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# ==========================
# COOLDOWN IA
# ==========================
user_cooldowns = {}
COOLDOWN_TIME = 10  # segundos

# ==========================
# FUNÇÃO MELHORAR IMAGEM
# ==========================
def enhance_image(img, scale=4):
    height, width = img.shape[:2]
    new_width = width * scale
    new_height = height * scale

    upscaled = cv2.resize(
        img,
        (new_width, new_height),
        interpolation=cv2.INTER_CUBIC
    )

    kernel = np.array([[0, -1, 0],
                       [-1, 5, -1],
                       [0, -1, 0]])

    sharpened = cv2.filter2D(upscaled, -1, kernel)

    return sharpened

# ==========================
# EVENTOS
# ==========================
@client.event
async def on_ready():
    print(f"✅ Bot conectado como {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # ==========================
    # COMANDO IA (!jeff)
    # ==========================
    if message.content.startswith("!jeff "):

        user_id = message.author.id
        now = time.time()

        if user_id in user_cooldowns:
            if now - user_cooldowns[user_id] < COOLDOWN_TIME:
                await message.channel.send("⏳ Espere alguns segundos antes de usar novamente.")
                return

        user_cooldowns[user_id] = now

        prompt = message.content[6:]
        await message.channel.send("Pensando...")

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "arcee-ai/trinity-large-preview:free",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 300,
            "temperature": 0.7
        }

        try:
            response = requests.post(OPENROUTER_URL, headers=headers, json=data)

            if response.status_code == 429:
                await message.channel.send("🚦 Rate limit atingido.")
                return

            if response.status_code != 200:
                await message.channel.send(f"❌ Erro {response.status_code}")
                return

            result = response.json()
            reply = result["choices"][0]["message"]["content"]

            await message.channel.send(reply[:2000])

        except Exception as e:
            await message.channel.send(f"❌ Erro: {e}")

        return

    # ==========================
    # COMANDO MELHORAR (!melhorar)
    # ==========================
    if message.content.startswith("!melhorar"):

        if not message.attachments:
            await message.channel.send("❌ Envie uma imagem junto com o comando.")
            return

        attachment = message.attachments[0]

        if not attachment.filename.lower().endswith((".png", ".jpg", ".jpeg")):
            await message.channel.send("❌ Formato inválido. Use PNG ou JPG.")
            return

        await message.channel.send("🖼️ Melhorando imagem em x4...")

        try:
            img_data = requests.get(attachment.url).content
            nparr = np.frombuffer(img_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            result = enhance_image(img, scale=8)

            output_file = "enhanced.png"
            cv2.imwrite(output_file, result)

            await message.channel.send(file=discord.File(output_file))

        except Exception as e:
            await message.channel.send(f"❌ Erro ao processar imagem: {e}")

# ==========================
# INICIA BOT
# ==========================
client.run(DISCORD_TOKEN)
