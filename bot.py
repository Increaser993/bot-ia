import os
import discord
import openai
import asyncio

# Pegando tokens do ambiente
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# Configurando intents para ler mensagens
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
client = discord.Client(intents=intents)

# Evento ao conectar
@client.event
async def on_ready():
    print(f"Bot conectado como {client.user}")

# Evento ao receber mensagem
@client.event
async def on_message(message):
    if message.author == client.user:
        return  # Ignora mensagens do próprio bot

    # Comando para ChatGPT
    if message.content.startswith("!chat "):
        prompt = message.content[6:]  # remove "!chat "
        await message.channel.send("🤖 Formulando resposta.")

        try:
            # Chamada à API do OpenAI
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",  # ou "gpt-4" se você tiver acesso
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.7
            )
            reply = response.choices[0].message.content
            await message.channel.send(reply)
        except Exception as e:
            await message.channel.send(f"❌ Erro na API: {e}")

client.run(DISCORD_TOKEN)
