import os
import discord
import requests
from io import BytesIO

# Variáveis de ambiente
TOKEN = os.environ.get("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
client = discord.Client(intents=intents)

# Endpoint Waifu2x online (exemplo público grátis)
WAIFU2X_API = "https://waifu2x.booru.pics/api"

@client.event
async def on_ready():
    print(f"Bot conectado como {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.attachments:
        for attachment in message.attachments:
            if any(attachment.filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg']):
                await message.channel.send("Recebido! Melhorando imagem… ⏳")

                # Baixa a imagem
                img_data = await attachment.read()

                # Envia para Waifu2x API
                files = {"image": (attachment.filename, BytesIO(img_data))}
                data = {"scale": 2, "noise": 1}  # scale=2x, noise=leve (0-3)
                try:
                    r = requests.post(WAIFU2X_API, files=files, data=data)
                    if r.status_code == 200:
                        # Retorna a imagem
                        output_filename = f"enhanced_{attachment.filename}"
                        with open(output_filename, "wb") as f:
                            f.write(r.content)
                        await message.channel.send(file=discord.File(output_filename))
                    else:
                        await message.channel.send(f"Erro na Waifu2x API: {r.status_code}")
                except Exception as e:
                    await message.channel.send(f"Erro ao chamar Waifu2x: {e}")

client.run(TOKEN)
