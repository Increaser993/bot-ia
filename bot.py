import os
import discord
import requests
import base64
import io

# Pegando token e API key do ambiente
TOKEN = os.environ.get("DISCORD_TOKEN")
API_KEY = os.environ.get("IMAGE_API_KEY")

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
client = discord.Client(intents=intents)

# Endpoint Freepik Mystic API
FREEPIK_URL = "https://api.freepik.com/v1/ai/mystic"

@client.event
async def on_ready():
    print(f"Bot conectado como {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # Verifica se o usuário enviou uma imagem
    if message.attachments:
        for attachment in message.attachments:
            if any(attachment.filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg']):
                await message.channel.send("Recebido! Melhorando com IA… ⏳")

                # 1️⃣ Baixa a imagem
                img_data = await attachment.read()
                img_base64 = base64.b64encode(img_data).decode("utf-8")

                # 2️⃣ Monta payload simples para “melhorar a imagem”
                payload = {
                    "prompt": "Improve quality, upscale and enhance details of this image",
                    "input_image": img_base64,
                    "resolution": "2k",
                    "aspect_ratio": "square_1_1",
                    "model": "realism",
                    "creative_detailing": 50,
                    "filter_nsfw": True
                }

                headers = {
                    "Content-Type": "application/json",
                    "x-freepik-api-key": API_KEY
                }

                # 3️⃣ Envia para API Freepik
                response = requests.post(FREEPIK_URL, json=payload, headers=headers)

                if response.status_code == 200:
                    result_json = response.json()
                    # Normalmente a API retorna base64 em 'result_image'
                    enhanced_b64 = result_json.get("result_image")
                    if enhanced_b64:
                        img_bytes = base64.b64decode(enhanced_b64)
                        filename = "enhanced.png"
                        with open(filename, "wb") as f:
                            f.write(img_bytes)
                        await message.channel.send(file=discord.File(filename))
                    else:
                        await message.channel.send("A API não retornou imagem.")
                else:
                    await message.channel.send(f"Erro na API: {response.status_code} {response.text}")

client.run(TOKEN)
