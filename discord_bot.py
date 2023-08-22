import os
import openai
import discord
from discord.ext import commands

from discord.utils import get

openai.api_key = os.getenv('OPENAI_API_KEY')
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
model_engine = "gpt-3.5-turbo"

intents = discord.Intents.default()
intents.members = True  # Required to receive member events
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if get(message.mentions, id=bot.user.id):
        user_message = message.content.replace(f'<@!{bot.user.id}>', '').strip()
    else:
        return

    chat_response = openai.ChatCompletion.create(
        model=model_engine,
        messages=[{"role": "user", "content": user_message}],
        max_tokens=600,
        n=1,
        temperature=0.5,
    )

    response = chat_response.choices[0].message.content.strip()

    await message.channel.send(response)


bot.run(DISCORD_TOKEN)
