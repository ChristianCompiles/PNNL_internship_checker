import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

load_dotenv() # load all variables from env file
intents = discord.Intents.default()
bot = commands.Bot(intents)
bot.load_extension('DailyScrape')

bot.run(os.getenv('TOKEN')) # run the bot with the token
