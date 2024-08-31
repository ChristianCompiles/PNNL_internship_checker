import discord
import requests
import json
import time
import schedule
import os
import threading
from datetime import datetime
from discord.ext import commands, tasks

class clientWrapper(discord.Client, commands.Cog):
    def __init__(self, intents, config_file_path: str, save_path: str, debug: bool):
        self.config_file_path = config_file_path
        self.save_path  = save_path
        self.debug = debug

        config_file_exists = os.path.isfile(config_file_path)
        if config_file_exists:
            with open(config_file_path, 'r+') as opened_config_file:
                config_data = json.load(opened_config_file)
                self.token = config_data['token'] # secret token: str
                self.guild_id = config_data['guild_id'] # server id: int
                self.channel_id = config_data['channel_id'] # text channel: int 
        else:
            print("Config file does not exist.")
            try:
                self.token = str(input("enter secret token: "))
                self.guild_id = int(input("Enter guild id: "))
                self.channel_id = int(input("Enter channel id: "))
            except:
                print("error gather input for configuration.\nExiting.")
                exit(0)

        super().__init__(intents=intents)
        self.run(self.token)

    async def __wrap_full_process__(self):
        full_json = self.__scrape_site__()
        condensed_list = self.__condense_to_list_of_json__(full_json)
        list_of_new_jobs = self.__check_and_write__(condensed_list)

        if list_of_new_jobs is not None:
            for job in list_of_new_jobs:
                msg = job['link']
                if msg is not None:
                    await self.channel.send(msg)
        else:
            print("No new internships.")

    @tasks.loop(seconds=10.0)
    async def __timed_wrapped_scrapper__(self):
        await self.__wrap_full_process__()  


    # async def __run_scheduler__(self):
    #     threading.Timer(1, await self.__run_scheduler__()).start()

    #     now = datetime.now()
    #     current_time = now.strftime("%H:%M:%S")
    #     if current_time == '18:58:30':
            

    async def on_ready(self):
        if self.debug:
            print(f'{self.user} has connected to Discord!')
            print(f'Bot is in {len(self.guilds)} servers:')
            for guild in self.guilds:
                print(f' - {guild.name} (id: {guild.id})')

        self.guild = self.get_guild(self.guild_id)

        if self.guild is None:
            print(f"Couldn't find a guild with ID: {self.guild_id}")
            return

        self.channel = self.guild.get_channel(self.channel_id)
    
        if self.channel is None:
            await print(f"Couldn't find a channel with ID: {self.channel_id} in the guild {self.guild.name}")
            return
        if self.debug:
            await self.channel.send("bot is online!")
        
        # await self.__wrap_full_process__() # run once
        # await self.__run_scheduler__()

    async def on_message(self, message):
        if message.author == self.user and self.debug:
            print(message.content)
            return

        # if message.content.startswith('!hello'):
        #     await message.channel.send(f'Hello! I am in the server: {message.guild.name}')

        # elif message.content.startswith('!serverinfo'):
        #     guild = message.guild
        #     await message.channel.send(f'Server Name: {guild.name}\n'
        #                                f'Server ID: {guild.id}\n'
        #                                f'Member Count: {guild.member_count}')

    def __scrape_site__(self):
        '''
        Scrape URL with params and headers for jobs json.
        '''

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
            print(f"Failed to fetch data: HTTP {response.status_code}.\nExiting.")
            return

        try:
            jobs_json = response.json()
            return jobs_json
        except json.JSONDecodeError:
            print("Failed to parse JSON response.\nExiting")
            return

    def __check_and_write__(self, pot_new_jobs_list: list):
        '''
        Check if jobs are new.
        Store new jobs in file.
        Return list of new jobs.
        '''

        file_exists = os.path.isfile(self.save_path)
        
        if file_exists and (os.stat(self.save_path).st_size > 0):
            if self.debug:
                print(f"File '{self.save_path}' already exists. Opening file.")
            with open(self.save_path, 'r+') as file:
                list_of_old_jobs = json.load(file)

            matched = False

            list_of_new_jobs = [] # store dicts temporarily and add after all comparisons

            u_k = 'req_id' # check uniqueness via requisition-id

            for pot_new_job in pot_new_jobs_list: # iterate over list of potentially new jobs
                pot_new_req_id = pot_new_job[u_k] 

                for old_job in list_of_old_jobs: # iterate over list of old jobs
                    if pot_new_req_id == old_job[u_k]:
                        if self.debug:
                            print(f"found match: {pot_new_req_id}")
                        matched = True
                        break
                    
                if matched == False: # if they didn't match, then its new, so append to list
                    list_of_new_jobs.append(pot_new_job)
                
                matched = False # reset to not matched
            
            for job in list_of_new_jobs: # now that all checks completed, add new jobs to old jobs list
                list_of_old_jobs.append(job)
            
            if len(list_of_new_jobs) > 0: # if we added to list, then write
                with open(self.save_path, 'w') as file:
                    json.dump(list_of_old_jobs, file)
                return list_of_new_jobs
                    
        else: # file doesn't exist
            with open(self.save_path, 'w') as file:
                json.dump(pot_new_jobs_list, file)
            return pot_new_jobs_list
    
    def __condense_to_list_of_json__(self, json_jobs: json):
        '''
        Condense requested json to list of dicts holding:
        "req_id", "title", "link"
        '''

        internships = []
        list_of_jobs = json_jobs.get('jobs')
        for wrapper_job in list_of_jobs:
            job_info = {}

            job = wrapper_job['data']
            
            if job is None:
                print("Error parsing json.\nExiting")

            title = job.get('title')
            if title is not None:
                job_info['title'] = title
            
            job_id = job.get('req_id')
            if job_id is not None:
                job_info['req_id'] = job_id

            job_info['link'] = f'https://careers.pnnl.gov/jobs/{job_id}'

            internships.append(job_info)
        
        if len(internships) > 0:
            return internships
        else:
            if self.debug:
                print("Empty list of internships, returning: None.")
            return None

def main():
    intents = discord.Intents.default() # Set up intents
    intents.message_content = True
    intents.guilds = True  # Needed to access guild information

    client = clientWrapper(intents=intents, config_file_path="config.json", save_path="scraped_jobs.json", debug = False) # Create an instance of the client

# Run the client
if __name__ == "__main__":
    main()
