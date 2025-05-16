#MARK: Libraries
import ast
from InquirerPy import inquirer
from InquirerPy.base.control import Choice
import os
import sys
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
    Returns the toml info from a jar file into a dict
    """
    with zipfile.ZipFile(file=jar) as f:
        toml_files = [file for file in f.namelist() if file.endswith('.toml')]
        
        if len(toml_files) > 1:
            print(f"Found more than one TOML file for mod \"{jar}\":\n{'\n'.join(toml_files)}")
            sys.exit()
        else:
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

def get_toml_info(toml_file:dict, jar: str) -> dict:
    """
    Returns a dict containing mod id, human name and version for the specified jar mod
    """
    toml_file = toml_file["mods"][0]
    infos = {
        "id": toml_file["modId"],
        "human_name": toml_file["displayName"],
        "version": toml_file["version"]
    }
    if infos["version"].startswith("$"):
        for line in get_manifest(jar).splitlines():
            if line.lower().startswith('implementation-version:'):
                infos["version"] = line.split(":")[1].strip()
    return infos

def generate_changelog(old_mods: list, new_mods: list) -> str: # type: ignore
    old_mods = sorted(old_mods, key=lambda mod: mod.get("id"))
    new_mods = sorted(new_mods, key=lambda mod: mod.get("id"))
    #print(old_mods)
    for i in range(max(len(old_mods), len(new_mods))):
        print(f"{old_mods[i]["id"]} ({old_mods[i]["human_name"]})")

def generate_snapshot(mods_path: str, out_file: str):
    files = os.listdir(path=mods_path)
    for file in files:
        if not file.endswith(".jar"):
            print(f"File \"{file}\" isn't a JAR file!")
            sys.exit()
        else:
            file_path = mods_path + "\\" + file
            print(get_toml_info(get_toml_file(file_path), file_path))


FILE = "ars_nouveau-1.21.1-5.8.2-all.jar"
EXAMPLE_OLD_MODS = [{'human_name': 'Epic Extension','id': 'epic_extension','version': '2.15.34'},{'human_name': 'Amazing Plugin','id': 'amazing_plugin','version': '6.5.32-alpha'},{'human_name': 'Advanced Extension','id': 'advanced_extension','version': '2.13.34'},{'human_name': 'Reliable Mod', 'id': 'reliable_mod', 'version': '5.13.15'},{'human_name': 'Epic Addon','id': 'epic_addon','version': '2.8.24-beta+release.20240514'},{'human_name': 'Amazing Plugin','id': 'amazing_plugin','version': '3.17.43-exp'},{'human_name': 'Fast Addon','id': 'fast_addon','version': '0.9.33-rc.1+sha.abc123'},{'human_name': 'Advanced Feature','id': 'advanced_feature','version': '5.12.39'},{'human_name': 'Crazy Feature','id': 'crazy_feature','version': '5.12.45-test+build.001'},{'human_name': 'Fast Extension','id': 'fast_extension','version': '3.4.6-beta+sha.abc123'}]
#print(get_toml_file("ars_nouveau-1.21.1-5.8.2-all.jar"))
#print(type(get_toml_file("ars_nouveau-1.21.1-5.8.2-all.jar")))
#print(get_toml_info(get_toml_file(FILE), FILE))
#print(get_manifest("ars_nouveau-1.21.1-5.8.2-all.jar"))
#print(generate_changelog(old_mods=EXAMPLE_OLD_MODS, new_mods=EXAMPLE_OLD_MODS))
#generate_changelog(old_mods=EXAMPLE_OLD_MODS, new_mods=EXAMPLE_OLD_MODS)

"""
if __name__ == "__main__":
    mode = inquirer.select(
        message="What would you like to do?",
        choices=[
            Choice(0, "Generate a changelog"),
            Choice(1, "Generate a version snapshot")
        ]
    ).execute()
    if mode == 0:
        pass
    else:
        pass
"""

generate_snapshot("C:\\Users\\Camille Massardier\\curseforge\\minecraft\\Instances\\BIOME SMP 2-CURSEFORGE (1)\\mods", None)