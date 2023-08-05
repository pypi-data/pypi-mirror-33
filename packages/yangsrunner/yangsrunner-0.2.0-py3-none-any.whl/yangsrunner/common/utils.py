import os


def is_file_exist(file_path):
    is_exist = os.path.isfile(file_path)

    if is_exist is False:
        print('Not found "%s" ...' % file_path)

    return is_exist
