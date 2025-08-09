from dotenv import load_dotenv
import errno
import json
import os
import requests
import shutil

load_dotenv()
API_KEY = os.getenv("API_KEY")
TEMP_PATH = os.path.join(os.getcwd(), "cached_files")

#MARK: create_temp_folder()
def create_temp_folder() -> None:
    os.makedirs(TEMP_PATH, exist_ok=True)

#MARK: delete_temp_folder()
def delete_temp_folder() -> None:
    try:
        shutil.rmtree(TEMP_PATH)
    except OSError as e:
        if e.errno != errno.ENOENT:
            raise

#MARK: download_file()
def download_file(url: str, path: str):
    local_filename = f"{path}{os.sep if path[-1] != os.sep else None}{url.split('/')[-1]}"
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192): 
                f.write(chunk)
    return local_filename

#MARK: get_cf_data()
def get_cf_download_url(project_id: str, file_id:str) -> str:
    headers = {
        'Accept': 'application/json',
        'x-api-key': API_KEY
        }
    r = requests.get(f'https://api.curseforge.com/v1/mods/{project_id}/files/{file_id}/download-url', headers=headers)
    if r.content:
        return json.loads(r.content.decode())["data"]
    else:
        return None