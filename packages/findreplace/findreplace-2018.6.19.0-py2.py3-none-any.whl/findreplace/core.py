import os
import glob
import shutil

ROOT_DIR = os.path.dirname(os.path.realpath(__file__))

def replace_file(data, find_val, new_val):
    return data.replace(find_val, new_val)


def findreplace(base_dir=ROOT_DIR, find_replace_dict={}, delete=True):
    del_dirs = []
    if '~' in base_dir:
        base_dir = os.path.expanduser(base_dir)
    if find_replace_dict:
        find_keys = find_replace_dict.keys()
        for root, dirs, files in os.walk(base_dir):
            for filename in files:
                replace_data = None
                path = os.path.join(base_dir, root, filename)
                new_path = ''

                for find_val in find_keys:
                    if find_val in root:
                        new_path = path.replace(find_val, find_replace_dict.get(find_val))
                        new_dir = os.path.dirname(new_path)
                        os.makedirs(new_dir, exist_ok=True)
                        if delete:
                            path_dir = os.path.dirname(path)
                            if not any(del_dirs in path_dir for del_dirs in del_dirs):
                                del_dirs.append(path_dir)

                if os.path.isfile(path):
                    with open(path, 'r') as file :
                        data = file.read()

                    replace_data = data
                    for find_val in find_keys:
                        replace_data = replace_file(replace_data, find_val, find_replace_dict.get(find_val))

                    if replace_data != data:
                        file_path = new_path if new_path else path
                        with open(file_path, 'w') as file:
                            file.write(replace_data)

                    if not os.access(path, os.W_OK):
                        st = os.stat(path)
                        new_permissions = stat.S_IMODE(st.st_mode) | stat.S_IWUSR
                        os.chmod(path, new_permissions)
    if delete:
        for del_dir in del_dirs:
            shutil.rmtree(del_dir)