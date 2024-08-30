# ####################################################
# import discord
# from discord.ext import commands
# import os

# # Define intents
# intents = discord.Intents.default()
# intents.message_content = True

# # Create a bot instance
# bot = commands.Bot(command_prefix='!', intents=intents)

# @bot.event
# async def on_ready():
#         config_file_path = "config.json"
#         config_file_exists = os.path.isfile(config_file_path)
    
#         if config_file_exists:
#             with open(config_file_path, 'r+') as opened_config_file:
#                 config_data = json.load(opened_config_file)
#                 self.secret_token = config_data['token'] # str
#                 self.guild_id = config_data['guild_id'] # (server id) int
#                 self.channel_id = config_data['channel_id'] # int 
        
#         else:
#             print("Config file does not exist.")
#             try:
#                 self.secret_token = str(input("enter secret token: "))
#                 self.guild_id = int(input("Enter guild id: "))
#                 self.channel_id = int(input("Enter channel id: "))
#             except:
#                 print("error gather input for configuration.\nExiting.")

#             if debug:
#                 print(f"Opening config file: \"{config_file_path}\"")

#     print(f'{bot.user} has connected to Discord!')
#     print(f'Logged on as {bot.user}!')
#         guild = bot.get_guild(guild_id)


#         if self.guild is None:
#             print(f"Couldn't find a guild with ID: {self.guild_id}")
#             return

#         self.channel = self.guild.get_channel(self.channel_id)
    
#         if self.channel is None:
#             await print(f"Couldn't find a channel with ID: {self.channel_id} in the guild {self.guild.name}")
#             return
#         if debug:
#             await self.channel.send("bot is online!")

#         full_json = scrape_site()
#         condensed_list = condense_to_list_of_json(full_json)
#         list_of_new_jobs = check_and_write(condensed_list)

#         if list_of_new_jobs is not None:
#             for job in list_of_new_jobs:
#                 msg = job['link']
#                 if msg is not None:
#                     await self.channel.send(msg)
#         else:
#             print("No new internships.")

# @bot.command(name='ping')
# async def ping(ctx):
#     await ctx.send('Pong!')

# @bot.command(name='greet')
# async def greet(ctx, *, name=''):
#     if name:
#         await ctx.send(f'Hello, {name}!')
#     else:
#         await ctx.send('Hello!')

# @bot.event
# async def on_message(message):
#     if message.author == bot.user:
#         return

#     if 'happy birthday' in message.content.lower():
#         await message.channel.send('Happy Birthday! 🎉🎂')

#     await bot.process_commands(message)

# # Run the bot
# if __name__ == "__main__":
#     token = os.getenv('DISCORD_TOKEN')
#     if not token:
#         raise ValueError("No token found. Set your DISCORD_TOKEN environment variable.")
#     bot.run(token)