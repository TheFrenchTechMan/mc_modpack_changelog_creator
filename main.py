#MARK: Libraries

import datetime
from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.validator import PathValidator
import os

#External code
from changelog import *
from utils import *
from snapshot import *

#MARK: Main loop

if __name__ == "__main__":
    mode = inquirer.select(
        message="What would you like to do?",
        choices=[
            Choice(0, "Generate a version snapshot"),
            Choice(1, "Generate a changelog")
        ]
    ).execute()
    
    if mode == 0: #MARK: SNAPSHOT
        home_path = os.getcwd()
        pw = inquirer.select(
            message="Do you want to use a Packwiz folder? (WARNING: This method will download all of the mods in a temporary folder, which takes time and requires enough empty space depending on the size of the modpack)",
            choices=[
                Choice(True, "Yes"),
                Choice(False, "No")
            ]
        ).execute()
        
        if not pw:
            mods_path = inquirer.filepath(
                message="Enter the path to the mods folder.",
                default=home_path,
                validate=PathValidator(is_dir=True, message="Not a directory.")
            ).execute()
        
        else:
            mods_path = inquirer.filepath(
                message="Enter the path to the Packwiz folder (containing files ending in .pw.toml).",
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
        if not pw:
            generate_snapshot(mods_path=mods_path, out_file_path=out_file_path)
        else:
            generate_pw_snapshot(tomls_path=mods_path, out_file_path=out_file_path)
        
        print(f"Successfully generated snapshot at {out_file_path}.")
    
    else: #MARK: CHANGELOG
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
        else:
            use_emojis = False
            name_formatting = ""
            id_formatting = ""
            version_formatting = ""
        
        print("")
        print(generate_changelog(
            old_mods_file_path=old_path,
            new_mods_file_path=new_path,
            use_emojis=use_emojis,
            name_formatting=name_formatting,
            id_formatting=id_formatting,
            version_formatting=version_formatting))