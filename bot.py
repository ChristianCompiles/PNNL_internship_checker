import discord
import requests
import json
import time
import schedule
import os

secret_token = '' # str
guild_id = 0 # (server id) int
channel_id = 0 # int 
debug = False

def scrape_site():
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

def check_and_write(pot_new_jobs_list: list):
    '''
    Check if jobs are new.
    Store new jobs in file.
    Return list of new jobs.
    '''

    file_path = "bot_internships.json"
    file_exists = os.path.isfile(file_path)
    
    if file_exists:
        if debug:
            print(f"File '{file_path}' already exists. Opening file.")
        with open(file_path, 'r+') as file:
            list_of_old_jobs = json.load(file)

        matched = False

        list_of_new_jobs = [] # store dicts temporarily and add after all comparisons

        u_k = 'req_id' # check uniqueness via requisition-id

        for pot_new_job in pot_new_jobs_list: # iterate over list of potentially new jobs
            pot_new_req_id = pot_new_job[u_k] 

            for old_job in list_of_old_jobs: # iterate over list of old jobs
                if pot_new_req_id == old_job[u_k]:
                    if debug:
                        print(f"found match: {pot_new_req_id}")
                    matched = True
                    break
                
            if matched == False: # if they didn't match, then its new, so append to list
                list_of_new_jobs.append(pot_new_job)
            
            matched = False # reset to not matched
        
        for job in list_of_new_jobs: # now that all checks completed, add new jobs to old jobs list
            list_of_old_jobs.append(job)
        
        if len(list_of_new_jobs) > 0: # if we added to list, then write
            with open(file_path, 'w') as file:
                json.dump(list_of_old_jobs, file)
            return list_of_new_jobs
                
    else: # file doesn't exist
        with open(file_path, 'w') as file:
            json.dump(pot_new_jobs_list, file)
        return pot_new_jobs_list

def condense_to_list_of_json(json_jobs: json):
        '''
        Condense requested json to list of dicts holding:
        req-id, title, application link
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
            if debug:
                print("Empty list of internships, returning: None.")
            return None

class MyClient(discord.Client):
    async def on_ready(self):
        print(f'Logged on as {self.user}!')
        self.guild = client.get_guild(guild_id)

        if self.guild is None:
            print(f"Couldn't find a guild with ID: {guild_id}")
            return

        self.channel = self.guild.get_channel(channel_id)
    
        if self.channel is None:
            await print(f"Couldn't find a channel with ID: {channel_id} in the guild {self.guild.name}")
            return
        if debug:
            await self.channel.send("bot is online!")

        full_json = scrape_site()
        condensed_list = condense_to_list_of_json(full_json)
        list_of_new_jobs = check_and_write(condensed_list)

        if list_of_new_jobs is not None:
            for job in list_of_new_jobs:
                msg = job['link']
                if msg is not None:
                    await self.channel.send(msg)
        else:
            print("No new internships.")

        #await self.__check_internships__()
        #self.__run_scheduler__()

    async def on_message(self, message):
        print(f'Message from {message.author}: {message.content}')

intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents)
client.run(secret_token)
