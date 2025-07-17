import json
import os
import toml
import zipfile

from utils import *

def load_toml_file(file: str) -> dict:
    with open(file, "r") as f:
        return toml.load(f)

#MARK: get_toml_file()
def get_toml_file(jar: str ) -> dict:
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
    info = get_toml_info(get_toml_file(jar))
    if not info:
        return jar.split(os.sep)[-1]
    else:
        if info["version"] == "${file.jarVersion}":
            info["version"] = get_manifest_version(get_manifest(jar))
        return info

#MARK: parse_packwiz_toml()
def parse_packwiz_toml(toml_file: dict): #TODO:
    return get_cf_data(toml_file[update])

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

def generate_pw_snapshot(mods_path: str, out_file_path: str) -> None:
    snapshot = [] #TODO: