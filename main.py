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
        return info

def get_info_from_id(id: str, snapshot: list):
    return next((i for i in snapshot if isinstance(i, dict) and i.get("id") == id), None)

def generate_changelog(old_mods_file_path: str, new_mods_file_path: str, use_emojis: bool, name_formatting: str, id_formatting: str, version_formatting: str) -> str:
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
    
    use_emojis = False
    name_formatting = ""
    id_formatting = ""
    version_formatting = ""
    
    changelog_message = ""
    for mod in added_mods: #TODO: Rewrite the formatting part because this is horrendous
        info = get_info_from_id(mod, new_mods)
        if isinstance(info, dict):
            info = {
                "human_name": f"{name_formatting}{info["human_name"]}{name_formatting}",
                "version": f"{version_formatting}{info["version"]}{version_formatting}"
            }
        mod = f"{id_formatting}{mod}{id_formatting}"
        
        if info != None:
            changelog_message += f"- {'➕' if use_emojis else '+'} {info["human_name"]} ({mod}) {info["version"]}\n"
        else:
            changelog_message += f"- {'➕' if use_emojis else '+'} {mod}\n"
    
    for mod in removed_mods:
        info = get_info_from_id(mod, old_mods)
        if isinstance(info, dict):
            info = {
                "human_name": f"{name_formatting}{info["human_name"]}{name_formatting}",
                "version": f"{version_formatting}{info["version"]}{version_formatting}"
            }
        mod = f"{id_formatting}{mod}{id_formatting}"
        
        if info != None:
            changelog_message += f"- {'❌' if use_emojis else '+'} {info["human_name"]} ({mod})\n"
        else:
            changelog_message += f"- {'❌' if use_emojis else '+'} {mod}\n"
    
    for mod in updated_mods:
        old_info = get_info_from_id(mod, old_mods)
        new_info = get_info_from_id(mod, new_mods)
        if isinstance(old_info, dict):
            old_info = {
                "human_name": f"{name_formatting}{old_info["human_name"]}{name_formatting}",
                "version": f"{version_formatting}{old_info["version"]}{version_formatting}"
            }
        if isinstance(new_info, dict):
            new_info = {
                "human_name": f"{name_formatting}{new_info["human_name"]}{name_formatting}",
                "version": f"{version_formatting}{new_info["version"]}{version_formatting}"
            }
        mod = f"{id_formatting}{mod}{id_formatting}"
        
        changelog_message += f"- {'📈' if use_emojis else '~'} {old_info["human_name"]} ({mod}) {old_info["version"]} -> {new_info["version"]}\n"
    
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

#MARK: Main loop

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
            default=mods_path,
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
        
        out_file_path = out_path + os.sep if not out_path.endswith(os.sep) else "" + out_file
        generate_snapshot(mods_path=mods_path, out_file_path=out_file_path)
        
        print(f"Successfully generated snapshot at {out_file_path}.")
    
    else: #CHANGELOG
        home_path = "/" if os.name == "posix" else "C:\\"
        
        old_path = inquirer.filepath(
            message="Enter the path to the old snapshot.",
            default=home_path,
            validate=PathValidator(is_file=True, message="Not a directory.")
        ).execute()
        
        new_path = inquirer.filepath(
            message="Enter the path to the new snapshot.",
            default=os.sep.join(old_path.split(os.sep)[:-1])+os.sep,
            validate=PathValidator(is_file=True, message="Not a directory.")
        ).execute()
        
        enable_formatting = inquirer.select(
            message="Do you want to customize the formatting of the changelog?",
            choices=[
                Choice(True, "Yes"),
                Choice(False, "No")
            ]
        ).execute()
        
        if enable_formatting:
            use_emojis = inquirer.select(
                message="Do you want to include emojis in the changelog?",
                choices=[
                    Choice(True, "Yes"),
                    Choice(False, "No")
                ]
            ).execute()
            
            name_formatting = inquirer.text(
            message="What character should be used to surround the mod name (e.g. \"Macaw's Lights and Lamps\")?",
            default=""
            ).execute()
            
            id_formatting = inquirer.text(
            message="What character should be used to surround the mod id (e.g. \"mcwlights\")?",
            default="`"
            ).execute()
            
            version_formatting= inquirer.text(
            message="What character should be used to surround the mod version (e.g. \"Macaw's Lights and Lamps\")?",
            default="**"
            ).execute()
        
        
        print("")
        print(generate_changelog(
            old_mods_file_path=old_path,
            new_mods_file_path=new_path,
            use_emojis=use_emojis,
            name_formatting=name_formatting,
            id_formatting=id_formatting,
            version_formatting=version_formatting))