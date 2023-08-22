
import os
import discord
from discord.ext import commands

# 创建一个 Intents 对象
intents = discord.Intents().all()

# 创建 Bot 实例时指定 intents 参数
bot = commands.Bot(command_prefix='!', description='ChatMixin', intents=intents)

# 在连接成功时打印机器人的用户名和 ID
@bot.event
async def on_ready():
    print('Logged in as {0} ({0.id})'.format(bot.user))

# 定义一个简单的命令
@bot.command()
async def hello(ctx):
    await ctx.send('Hello {}!'.format(ctx.author))

bot.run(os.environ['DISCORD_TOKEN'])
