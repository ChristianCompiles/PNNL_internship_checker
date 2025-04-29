from discord.ext import commands, tasks
import discord
from io import BytesIO
import datetime
import requests
import json
import os

class DailyScrape(commands.Cog):
    def __init__(self, bot, save_path, debug) -> None:
       
        self.bot = bot
        self.save_path = save_path
        self.debug = debug     
        self.my_task.start()  

    @tasks.loop(hours= 1)
    async def my_task(self) -> None:
        print("Scraping:", datetime.datetime.now(), flush=True)
        await self.__wrap_full_process__()

    async def __wrap_full_process__(self):
        full_json = self.__scrape_site__()
        condensed_list = self.__condense_to_list_of_json__(full_json)
        list_of_new_jobs = self.__check_and_write__(condensed_list)
       
        if list_of_new_jobs is None:
            print("No new internships.", flush=True)
            return
        
        for job in list_of_new_jobs:
            msg = job['link']
            if msg is None:
                continue

            title = job['title']
            description = job['description']
            responsibilities = job['responsibilities']
            
            attachment = title + "\n" + msg + "\n\n" + "Responsibilities:\n" + responsibilities + "\n\n" + "Description:\n" + description
            attachment_io = BytesIO(attachment.encode('utf-8'))
            
            await self.bot.wait_until_ready()
            for guild in self.bot.guilds: # iterate over all servers

                if guild.name == "Coding Cougs On Campus":
                    if title is not None:
                        if "High School" in title: # skip high school opportunities
                            continue
                        if "Post" in title and "Masters" in title: # skip Post Masters opportunities
                            continue
                        if "PhD" in title: # skip PhD opportunities
                            continue

                print(guild.id, flush=True)
                channel = discord.utils.get(guild.text_channels, name="job-postings")
                attachment_name = title + ".txt"
                if channel is not None:
                    await channel.send(msg, file=discord.File(fp=attachment_io, filename=attachment_name))
                else:
                    if self.debug:
                        print(f"guild: {guild.name} does not have channel name", flush=True)
        
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
            print(f"Failed to fetch data: HTTP {response.status_code}.\nExiting.", flush=True)
            return

        try:
            jobs_json = response.json()
            return jobs_json
        except json.JSONDecodeError:
            print("Failed to parse JSON response.\nExiting", flush=True)
            return

    def __check_and_write__(self, pot_new_jobs_list: list):
        '''
        Check if jobs are new.
        Store new jobs in file.
        Return list of new jobs.
        '''
        
        if os.path.isfile(self.save_path) and (os.stat(self.save_path).st_size > 0):
            if self.debug:
                print(f"File '{self.save_path}' already exists. Opening file.", flush=True)
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
                            print(f"found match: {pot_new_req_id}", flush=True)
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
                print("Error parsing json.\nExiting", flush=True)

            title = job.get('title')
            if title is not None:
                job_info['title'] = title
            
            job_id = job.get('req_id')
            if job_id is not None:
                job_info['req_id'] = job_id

            job_info['link'] = f'https://careers.pnnl.gov/jobs/{job_id}'

            description = job.get('description')
            if description is not None:
                job_info['description'] = description

            responsibilities = job.get('responsibilities')
            if responsibilities is not None:
                job_info['responsibilities'] = responsibilities

            internships.append(job_info)
        
        if len(internships) > 0:
            return internships
        else:
            if self.debug:
                print("Empty list of internships, returning: None.", flush=True)
            return None

    @commands.Cog.listener()
    async def on_guild_join(self, guild): # give enter scraped list on server join
        print("joined guild!")
        channel = discord.utils.get(guild.text_channels, name="job-postings", flush=True)
        if channel is None:
            return
        if not os.path.isfile(self.save_path) or (os.stat(self.save_path).st_size <= 0):
            return
        
        with open(self.save_path, 'r+') as file:
            list_of_jobs = json.load(file)

            if list_of_jobs is None:
                return
            
            for job in list_of_jobs:
                app_link = job["link"]
                if app_link is None:
                    return
                await channel.send(app_link)
                
async def setup(bot) -> None:
    await bot.add_cog(DailyScrape(bot, save_path="scraped_jobs.json", debug = True))
