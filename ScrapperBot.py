import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

load_dotenv() # load all variables from env file
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix='..!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')

    await bot.load_extension('cog.ScraperCog')

bot.run(os.getenv('TOKEN')) # run the bot with the token
