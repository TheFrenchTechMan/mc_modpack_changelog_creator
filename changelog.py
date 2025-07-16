import json

#MARK: get_info_from_id()
def get_info_from_id(id: str, snapshot: list):
    return next((i for i in snapshot if isinstance(i, dict) and i.get("id") == id), None)

#MARK: generate_changelog()
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
    
    changelog_message = ""
    for mod in added_mods: #TODO: Rewrite the formatting part because this is horrendous
        info = get_info_from_id(mod, new_mods)
        if isinstance(info, dict):
            info = {
                "human_name": f"{name_formatting}{info['human_name']}{name_formatting}",
                "version": f"{version_formatting}{info['version']}{version_formatting}"
            }
        mod = f"{id_formatting}{mod}{id_formatting}"
        
        if info != None:
            changelog_message += f"- {'➕' if use_emojis else '+'} {info['human_name']} ({mod}) {info['version']}\n"
        else:
            changelog_message += f"- {'➕' if use_emojis else '+'} {mod}\n"
    
    for mod in removed_mods:
        info = get_info_from_id(mod, old_mods)
        if isinstance(info, dict):
            info = {
                "human_name": f"{name_formatting}{info['human_name']}{name_formatting}",
                "version": f"{version_formatting}{info['version']}{version_formatting}"
            }
        mod = f"{id_formatting}{mod}{id_formatting}"
        
        if info != None:
            changelog_message += f"- {'❌' if use_emojis else '+'} {info['human_name']} ({mod})\n"
        else:
            changelog_message += f"- {'❌' if use_emojis else '+'} {mod}\n"
    
    for mod in updated_mods:
        old_info = get_info_from_id(mod, old_mods)
        new_info = get_info_from_id(mod, new_mods)
        if isinstance(old_info, dict):
            old_info = {
                "human_name": f"{name_formatting}{old_info['human_name']}{name_formatting}",
                "version": f"{version_formatting}{old_info['version']}{version_formatting}"
            }
        if isinstance(new_info, dict):
            new_info = {
                "human_name": f"{name_formatting}{new_info['human_name']}{name_formatting}",
                "version": f"{version_formatting}{new_info['version']}{version_formatting}"
            }
        mod = f"{id_formatting}{mod}{id_formatting}"
        
        changelog_message += f"- {'📈' if use_emojis else '~'} {old_info['human_name']} ({mod}) {old_info['version']} -> {new_info['version']}\n"
    
    return changelog_message