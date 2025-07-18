import json
import os
import toml
import zipfile

from utils import *

def load_toml_file(file: str) -> dict:
    with open(file, "r", encoding="utf-8") as f:
        return toml.load(f)

#MARK: get_toml_file()
def get_toml_file_from_jar(jar: str) -> dict:
    """
    Returns the raw toml info from a jar file into a dict
    """
    with zipfile.ZipFile(file=jar) as f:
        toml_files = [file for file in f.namelist() if file.endswith('mods.toml')]
        if toml_files != []:
            with f.open(toml_files[0]) as t:
                return toml.loads(t.read().decode())

#MARK: get_manifest()
def get_manifest(jar: str) -> str:
    """
    Returns the MANIFEST.MF file as a string
    """
    with zipfile.ZipFile(file=jar) as f:
        manifest = [file for file in f.namelist() if file.endswith("MANIFEST.MF")][0]
        with f.open(manifest) as m:
            return m.read().decode()

#MARK: get_toml_info()
def get_toml_info(toml_file:dict) -> dict:
    """
    Returns a dict containing mod id, human name and version from a toml dict
    """
    if toml_file:
        toml_file = toml_file["mods"][0]
        infos = {
            "id": toml_file["modId"],
            "human_name": toml_file["displayName"],
            "version": toml_file["version"]
        }
        return infos

#MARK: get_manifest_version()
def get_manifest_version(mf_file: str):
    """
    Returns the mod version from a Manifest string
    """
    version = ""
    for line in mf_file.split("\n"):
        match line.split(":")[0]:
            case "Implementation-Version":
                version = line.split(":")[1].lower().strip()
    return version

#MARK: get_metadata()
def get_metadata(jar: str):
    info = get_toml_info(get_toml_file_from_jar(jar))
    if not info:
        return jar.split(os.sep)[-1]
    else:
        if info["version"] == "${file.jarVersion}":
            info["version"] = get_manifest_version(get_manifest(jar))
        return info

#MARK: get_packwiz_dl()
def get_packwiz_dl(toml_file: dict):
    if "metadata:curseforge" in str(toml_file):
        project_id = str(toml_file["update"]["curseforge"]["project-id"])
        file_id = str(toml_file["update"]["curseforge"]["file-id"])
        return get_cf_download_url(project_id=project_id, file_id=file_id)

def get_data_from_temp_file(file_url: str) -> dict:
    if not file_url:
        return None
    else:
        f = download_file(url=file_url, path=TEMP_PATH)
        print(f"Downloaded file {f}")
        return get_toml_info(get_toml_file_from_jar(f))

#MARK: generate_snapshot()
def generate_snapshot(mods_path: str, out_file_path: str) -> None:
    snapshot = []
    files = os.listdir(path=mods_path)
    for file in files:
        if not file.endswith(".jar"):
            print(f"File \"{file}\" isn't a JAR file!")
        else:
            file_path = mods_path + os.sep + file
            snapshot.append(get_metadata(file_path))
    
    with open(out_file_path, "w") as f:
        json.dump(snapshot, f)

def generate_pw_snapshot(tomls_path: str, out_file_path: str) -> None:
    create_temp_folder()
    snapshot = []
    files = os.listdir(tomls_path)
    for file in files:
        if not file.endswith(".toml"):
            print(f"File \"{file}\" isn't a TOML file!")
        else:
            file_path = os.path.join(tomls_path, file)
            data = get_data_from_temp_file(get_packwiz_dl(load_toml_file(file_path)))
            if data:
                snapshot.append(data)
            else:
                snapshot.append(load_toml_file(file_path)["filename"])
    delete_temp_folder()
    
    with open(out_file_path, "w") as f:
        json.dump(snapshot, f)