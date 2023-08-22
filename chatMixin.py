
import os
import openai
import discord
from discord.ext import commands
import asyncio

from discord.utils import get

from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv('OPENAI_API_KEY')
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
model_engine = "gpt-3.5-turbo"

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

bot.user_conversations = {}

user_settings = {}


@bot.command(name='history', help='查看与 bot 的对话历史')
async def history(ctx, num: int = 1):  # 默认显示5条，但可以通过参数更改
    user_id = ctx.message.author.id
    if user_id not in bot.user_conversations:
        await ctx.send('没有找到与你的对话历史')
        return

    if num > 5:
        await ctx.send('最多只能显示5条消息，将显示最近的5条消息。')
        num = 5
    elif num < 1:
        await ctx.send('请指定一个介于1到5之间的数字。')
        return

    if num > len(bot.user_conversations[user_id]):
        num = len(bot.user_conversations[user_id])

    # 从对话历史中取最后num条消息
    conversation_history = bot.user_conversations[user_id][-num:]
    history_text = '\n'.join(
        [f'{msg["role"]}: {msg["content"]}' for msg in conversation_history])
    await ctx.send(history_text)


@bot.command(name='set_temperature', help='设置模型的 temperature')
async def set_temperature(ctx, temp: float):
    user_id = ctx.message.author.id
    if user_id not in user_settings:
        user_settings[user_id] = {}  # 初始化用户设置
    if 0 <= temp <= 1:
        user_settings[user_id]['temperature'] = temp
        await ctx.send(f'设置 temperature 为 {temp}')
    else:
        await ctx.send('temperature 必须在0到1之间')


@bot.event
async def on_message(message):

    await bot.process_commands(message)

    if message.author == bot.user:
        return

    if get(message.mentions, id=bot.user.id):
        user_message = message.content.replace(
            f'<@!{bot.user.id}>', '').strip()
    else:
        return

    user_id = message.author.id

    if user_id not in bot.user_conversations:
        bot.user_conversations[user_id] = []

    bot.user_conversations[user_id].append(
        {"role": "user", "content": user_message})

    # 在与用户交互时：
    temp = user_settings.get(user_id, {}).get('temperature', 0.7)  # 使用默认值0.7
    chat_response = openai.ChatCompletion.create(
        model=model_engine,
        messages=bot.user_conversations[user_id],
        max_tokens=600,
        n=1,
        temperature=temp,
    )

    response = chat_response.choices[0].message['content'].strip()
    bot.user_conversations[user_id].append(
        {"role": "assistant", "content": response})

    await message.channel.send(response)

    # 如果需要，可以在此处清理过长的聊天记录
    # 例如：当聊天记录超过10条时，删除旧消息
    if len(bot.user_conversations[user_id]) > 20:
        bot.user_conversations[user_id].pop(0)
        bot.user_conversations[user_id].pop(0)

bot.run(DISCORD_TOKEN)
