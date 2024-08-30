# PNNL_internship_checker
Description: Script to check PNNL for university internships. Writes titles and application links to file.

Setup: In script directory, create config.json following pattern:
{
    "token": "long string",
    "guild_id": 0123456789,
    "channel_id": 0123456789
}

Specify a save path for the scraped jobs in the clientWrapper instantation.