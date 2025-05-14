#MARK: Libraries
import argparse
import ast
import os
import sys
import toml
import zipfile

#MARK: Arg parser
parser = argparse.ArgumentParser(description="A program to auto generate changelogs based on a list of files", )

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

def get_toml_info(file:dict, jar: str) -> dict:
    """
    Returns a dict containing mod id, human name and version for the specified jar mod
    """
    file = file["mods"][0]
    infos = {
        "id": file["modId"],
        "human_name": file["displayName"],
        "version": file["version"]
    }
    if infos["version"].startswith("$"):
        for line in get_manifest(jar).splitlines():
            if line.lower().startswith('implementation-version:'):
                infos["version"] = line.split(":")[1].strip()
    return infos

FILE = "ars_nouveau-1.21.1-5.8.2-all.jar"

#print(get_toml_file("ars_nouveau-1.21.1-5.8.2-all.jar"))
#print(type(get_toml_file("ars_nouveau-1.21.1-5.8.2-all.jar")))
print(get_toml_info(get_toml_file(FILE), FILE))
#print(get_manifest("ars_nouveau-1.21.1-5.8.2-all.jar"))