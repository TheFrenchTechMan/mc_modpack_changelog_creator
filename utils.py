from dotenv import load_dotenv
import json
import os
import requests

load_dotenv()
API_KEY = os.getenv("API_KEY")

#MARK: download_file()
def download_file(url: str):
    local_filename = url.split('/')[-1]
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192): 
                f.write(chunk)
    return local_filename

#MARK: get_cf_data()
def get_cf_dl_link(project_id: str, file_id:str) -> str:
    headers = {
        'Accept': 'application/json',
        'x-api-key': API_KEY
        }
    r = requests.get(f'https://api.curseforge.com/v1/mods/{project_id}/files/{file_id}', headers=headers)
    return json.loads(r.content.decode())["data"]["downloadUrl"]

# TESTING
#with open("o.json", "w") as f:
#    f.write(str(get_cf_dl_link("1090999", "6393071")))