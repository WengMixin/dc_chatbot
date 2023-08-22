
import os
import openai
import discord
from discord.ext import commands
import asyncio

from discord.utils import get

openai.api_key = os.getenv('OPENAI_API_KEY')
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
model_engine = "gpt-3.5-turbo"

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

bot.user_conversations = {}

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if get(message.mentions, id=bot.user.id):
        user_message = message.content.replace(f'<@!{bot.user.id}>', '').strip()
    else:
        return

    user_id = message.author.id

    if user_id not in bot.user_conversations:
        bot.user_conversations[user_id] = []

    bot.user_conversations[user_id].append({"role": "user", "content": user_message})

    chat_response = openai.ChatCompletion.create(
        model=model_engine,
        messages=bot.user_conversations[user_id],
        max_tokens=600,
        n=1,
        temperature=0.5,
    )

    response = chat_response.choices[0].message['content'].strip()
    bot.user_conversations[user_id].append({"role": "assistant", "content": response})

    await message.channel.send(response)

    # 如果需要，可以在此处清理过长的聊天记录
    # 例如：当聊天记录超过10条时，删除旧消息
    if len(bot.user_conversations[user_id]) > 20:
        bot.user_conversations[user_id].pop(0)
        bot.user_conversations[user_id].pop(0)

bot.run(DISCORD_TOKEN)
