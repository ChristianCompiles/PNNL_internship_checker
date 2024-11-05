import requests
import json
import time
import schedule

# This script is not used by the Discord bot.
# It was developed to test the scraping and data collection.

def check_internships():
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

def run_scheduler():
    schedule.every(5).minutes.do(check_internships)
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    check_internships()  # Run once immediately
    run_scheduler()  
    