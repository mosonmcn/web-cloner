import os

def has_extension(path):
    return os.path.splitext(path)[1] != ""