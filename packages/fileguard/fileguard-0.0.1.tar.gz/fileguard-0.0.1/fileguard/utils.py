from pathlib import Path

def path_is_dir(path):
    path = Path(path)
    return path.is_dir()
