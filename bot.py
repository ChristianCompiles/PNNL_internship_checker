import discord
import requests
import json
import time
import schedule

secret_token = 0
guild_id = 0
channel_id = 0

class MyClient(discord.Client):

    async def __check_internships__(self):
        url = "https://careers.pnnl.gov/api/jobs"
        params = {
            "tags2": "University Internships",
            "limit": 100,
            "page": 1
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        response = requests.get(url, params=params, headers=headers)
        
        if response.status_code != 200:
            print(f"Failed to fetch data: HTTP {response.status_code}")
            return

        try:
            jobs = response.json()
        except json.JSONDecodeError:
            print("Failed to parse JSON response")
            return
    
        internships = []
        list_of_jobs = jobs.get('jobs')
        for wrapper_job in list_of_jobs:
            job = wrapper_job['data']
            title = job.get('title')
            job_id = job.get('req_id')
            link = f'https://careers.pnnl.gov/jobs/{job_id}'
            internships.append(title + " " + link)

        f = open("internships.txt", "w")

        for job in internships:
            f.write(job)
            f.write("\n")
            await self.channel.send(job)

    async def __run_scheduler__(self):
        await schedule.every(10).seconds.do(self.__check_internships__)
        while True:
            schedule.run_pending()
            time.sleep(1)

    async def on_ready(self):
        print(f'Logged on as {self.user}!')
        self.guild = client.get_guild(guild_id)

        if self.guild is None:
            print(f"Couldn't find a guild with ID: {guild_id}")
            return

        # Get the channel by ID within the specified guild
        self.channel = self.guild.get_channel(channel_id)
    
        if self.channel is None:
            await print(f"Couldn't find a channel with ID: {channel_id} in the guild {self.guild.name}")
            return
        await self.channel.send("bot is online!")

        await self.__check_internships__()
        #self.__run_scheduler__()

    async def on_message(self, message):
        print(f'Message from {message.author}: {message.content}')


intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents)
client.run(secret_token)
