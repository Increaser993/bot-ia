import os
import discord
import requests
import asyncio

DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
REPLICATE_API_TOKEN = os.environ.get("REPLICATE_API_TOKEN")

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
client = discord.Client(intents=intents)

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

    try:
        r = requests.post("https://api.replicate.com/v1/predictions", headers=headers, json=json_data)
        if r.status_code != 201:
            return f"Erro na requisição: {r.status_code} - {r.text}"

        prediction = r.json()
        prediction_url = prediction.get("urls", {}).get("get")
        if not prediction_url:
            return "Erro: não encontrei URL de status da predição."

        # Espera o processamento terminar
        while True:
            status_res = requests.get(prediction_url, headers=headers).json()
            status = status_res.get("status")
            if status == "succeeded":
                output = status_res.get("output")
                if isinstance(output, list) and output:
                    return output[0]
                elif isinstance(output, str):
                    return output
                else:
                    return "Erro: saída inesperada da API."
            elif status in ["failed", "canceled"]:
                return "Upscale IA falhou."
            await asyncio.sleep(1)

    except Exception as e:
        return f"Erro interno: {str(e)}"

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
                result = await upscale_image(att.url)
                await message.channel.send(result)

client.run(DISCORD_TOKEN)
