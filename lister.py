import os

DIRECTORY = input("Please enter full path of the directory containing your mods: ") if __name__ == "__main__" else None

def listfiles(path: str) -> list:
    files = os.listdir(path)
    files = [f for f in files if os.path.isfile(os.path.join(path, f))]
    return files