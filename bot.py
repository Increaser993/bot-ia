import discord
import requests
import numpy as np
import cv2
import io
import os

TOKEN = os.environ.get("DISCORD_TOKEN")

if not TOKEN:
    raise ValueError("DISCORD_TOKEN não definido!")

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


# 🔥 Função de melhoria profissional CPU
def enhance_image(img, scale=4):

    # 1️⃣ Upscale com Lanczos (melhor interpolação CPU)
    height, width = img.shape[:2]
    new_size = (width * scale, height * scale)
    upscaled = cv2.resize(img, new_size, interpolation=cv2.INTER_LANCZOS4)

    # 2️⃣ Melhorar contraste local (CLAHE)
    lab = cv2.cvtColor(upscaled, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)

    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l = clahe.apply(l)

    lab = cv2.merge((l, a, b))
    contrast_img = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)

    # 3️⃣ Unsharp Mask balanceado (sem exagero)
    gaussian = cv2.GaussianBlur(contrast_img, (0, 0), 1.5)
    sharpened = cv2.addWeighted(contrast_img, 1.4, gaussian, -0.4, 0)

    return sharpened


@client.event
async def on_ready():
    print(f"Bot conectado como {client.user}")


@client.event
async def on_message(message):

    if message.author == client.user:
        return

    if message.content.startswith("!melhorar"):

        partes = message.content.split()
        scale = 4  # padrão

        # 🎯 Verifica escala digitada
        if len(partes) > 1:
            try:
                scale = int(partes[1])
                if scale < 1 or scale > 8:
                    await message.channel.send("❌ Use escala entre 1 e 8.")
                    return
            except:
                await message.channel.send("❌ Escala inválida. Ex: !melhorar 4")
                return

        if not message.attachments:
            await message.channel.send("❌ Envie uma imagem junto com o comando.")
            return

        attachment = message.attachments[0]

        if not attachment.filename.lower().endswith((".png", ".jpg", ".jpeg")):
            await message.channel.send("❌ Use PNG ou JPG.")
            return

        await message.channel.send(f"🖼️ Melhorando imagem em x{scale}...")

        try:
            img_data = requests.get(attachment.url).content
            nparr = np.frombuffer(img_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            result = enhance_image(img, scale=scale)

            # 🔥 Limite máximo para evitar erro 413
            max_dimension = 3000
            h, w = result.shape[:2]

            if max(h, w) > max_dimension:
                ratio = max_dimension / max(h, w)
                result = cv2.resize(
                    result,
                    (int(w * ratio), int(h * ratio)),
                    interpolation=cv2.INTER_AREA
                )

            # 🔥 Compressão inteligente
            quality = 95
            while True:
                encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
                _, buffer = cv2.imencode(".jpg", result, encode_param)
                size_mb = len(buffer) / (1024 * 1024)

                if size_mb <= 7.5 or quality <= 60:
                    break

                quality -= 5

            file = discord.File(
                io.BytesIO(buffer.tobytes()),
                filename="enhanced.jpg"
            )

            await message.channel.send(file=file)

        except Exception as e:
            await message.channel.send(f"❌ Erro ao processar imagem: {e}")


client.run(TOKEN)
