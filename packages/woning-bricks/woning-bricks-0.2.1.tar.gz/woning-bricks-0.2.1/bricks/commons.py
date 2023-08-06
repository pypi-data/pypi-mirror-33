import os.path


def get_name():
    return os.path.split(os.path.abspath('.'))[-1]
