#MARK: Libraries
import datetime
from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.validator import PathValidator
import json
import os
import toml
import zipfile

#MARK: Functions
def list_files(path: str) -> list:
    """
    List the files in a specified folder
    """
    files = os.listdir(path)
    files = [f for f in files if os.path.isfile(os.path.join(path, f))]
    return files

def get_toml_file(jar: str ) -> dict:
    """
    Returns the raw toml info from a jar file into a dict
    """
    with zipfile.ZipFile(file=jar) as f:
        toml_files = [file for file in f.namelist() if file.endswith('mods.toml')]
        if toml_files != []:
            with f.open(toml_files[0]) as t:
                return toml.loads(t.read().decode())

def get_manifest(jar: str) -> str:
    """
    Returns the MANIFEST.MF file as a string
    """
    with zipfile.ZipFile(file=jar) as f:
        manifest = [file for file in f.namelist() if file.endswith("MANIFEST.MF")][0]
        with f.open(manifest) as m:
            return m.read().decode()

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

def get_metadata(jar: str):
    info = get_toml_info(get_toml_file(jar))
    if not info:
        return jar.split("\\")[-1]
    else:
        if info["version"] == "${file.jarVersion}":
            info["version"] = get_manifest_version(get_manifest(jar))
        print(info)
        return info

def get_info_from_id(id: str, snapshot: list):
    return next((i for i in snapshot if isinstance(i, dict) and i.get("id") == id), None)

def generate_changelog(old_mods_file_path: str, new_mods_file_path: str) -> str:
    kept_or_updated_mods = []
    removed_mods = []
    added_mods = []
    
    with open(old_mods_file_path, "r") as o:
        old_mods = json.load(o)
        
    with open(new_mods_file_path, "r") as n:
        new_mods = json.load(n)
    
    old_mods_ids = [mod["id"] if isinstance(mod, dict) else mod for mod in old_mods]
    new_mods_ids = [mod["id"] if isinstance(mod, dict) else mod for mod in new_mods]
    
    while len(old_mods_ids) > 0:
        mod = old_mods_ids[0]
        if mod in new_mods_ids:
            kept_or_updated_mods.append(mod)
            new_mods_ids.pop(new_mods_ids.index(mod))
        else:
            removed_mods.append(mod)
        old_mods_ids.pop(0)
    
    while len(new_mods_ids) > 0:
        added_mods.append(new_mods_ids[0])
        new_mods_ids.pop(0)
    
    kept_mods = []
    updated_mods = []
    
    for mod in kept_or_updated_mods:
        old_version = get_info_from_id(mod, old_mods)
        new_version = get_info_from_id(mod, new_mods)
        if old_version == new_version:
            kept_mods.append(mod)
        else:
            updated_mods.append(mod)
    
    changelog_message = ""
    for mod in added_mods:
        info = get_info_from_id(mod, new_mods)
        if info != None:
            changelog_message += f"- + {info["human_name"]} ({mod}) **{info["version"]}**\n"
        else:
            changelog_message += f"- + {mod}\n"
    
    for mod in removed_mods:
        info = get_info_from_id(mod, old_mods)
        changelog_message += f"- X {info["human_name"]} ({mod})\n"
    
    for mod in updated_mods:
        old_info = get_info_from_id(mod, old_mods)
        new_info = get_info_from_id(mod, new_mods)
        changelog_message += f"- ~ {old_info["human_name"]} ({mod}) **{old_info["version"]} -> {new_info["version"]}**\n"
    
    return changelog_message

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



if __name__ == "__main__":
    mode = inquirer.select(
        message="What would you like to do?",
        choices=[
            Choice(0, "Generate a version snapshot"),
            Choice(1, "Generate a changelog")
        ]
    ).execute()
    
    if mode == 0: #SNAPSHOT
        home_path = "/" if os.name == "posix" else "C:\\"
        mods_path = inquirer.filepath(
            message="Enter the path to the mods folder.",
            default=home_path,
            validate=PathValidator(is_dir=True, message="Not a directory.")
        ).execute()
        out_path = inquirer.filepath(
            message="Enter the path to the output directory.",
            default=home_path,
            validate=PathValidator(is_dir=True, message="Not a directory.")
        ).execute()
        out_file= inquirer.text(
            message="Enter the name for the output file, leave empty to auto-generate."
        ).execute()
        if out_file == "":
            now = datetime.datetime.now()
            timestamp = now.strftime("%Y-%m-%d-%H-%M-%S")
            out_file = f"snapshot-{timestamp}.json"
        elif not out_file.endswith(".json"):
            out_file += ".json"
        
    
    
    else: #CHANGELOG
        pass

#print(generate_changelog("smp_old.json", "smp_new.json"))