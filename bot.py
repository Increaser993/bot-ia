import os
import discord
import requests
import asyncio

# Pegue seu token do Discord e Replicate das variáveis de ambiente
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
REPLICATE_API_TOKEN = os.environ.get("REPLICATE_API_TOKEN")

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
client = discord.Client(intents=intents)

# Função para chamar o modelo Real-ESRGAN no Replicate
async def upscale_image(image_url: str) -> str:
    headers = {
        "Authorization": f"Token {REPLICATE_API_TOKEN}",
        "Content-Type": "application/json"
    }
    json_data = {
        "version": "latest",
        "model": "nightmareai/real-esrgan",
        "input": {
            "image": image_url,
            "scale": 2,
            "face_enhance": False
        }
    }

    r = requests.post("https://api.replicate.com/v1/predictions", headers=headers, json=json_data)
    if r.status_code != 201:
        return None

    prediction_url = r.json()["urls"]["get"]

    # Espera o processamento terminar
    while True:
        status_res = requests.get(prediction_url, headers=headers).json()
        if status_res["status"] == "succeeded":
            output_urls = status_res["output"]
            enhanced_url = output_urls[0] if isinstance(output_urls, list) else output_urls
            return enhanced_url
        elif status_res["status"] in ["failed", "canceled"]:
            return None
        await asyncio.sleep(1)

@client.event
async def on_ready():
    print(f"Bot conectado como {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.attachments:
        for att in message.attachments:
            if any(att.filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg']):
                await message.channel.send("Recebi a imagem! Enviando para IA... ⏳")
                enhanced_url = await upscale_image(att.url)
                if enhanced_url:
                    await message.channel.send(f"Imagem melhorada: {enhanced_url}")
                else:
                    await message.channel.send("Houve um erro ao processar a imagem.")

client.run(DISCORD_TOKEN)
