import os

DIRECTORY = input("Please enter full path of the directory containing your mods: ")

def listfiles(path: str) -> list:
    files = os.listdir(path)
    files = [f for f in files if os.path.isfile(os.path.join(DIRECTORY, f))]
    return files