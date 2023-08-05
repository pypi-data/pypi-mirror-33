import os
import glob
import shutil

ROOT_DIR = os.path.dirname(os.path.realpath(__file__))

def findreplace(base_dir=ROOT_DIR, find_val='', new_val='', delete=True):
    del_dirs = []
    if '~' in base_dir:
        base_dir = os.path.expanduser(base_dir)
    if find_val and new_val:
        for root, dirs, files in os.walk(base_dir):
            for filename in files:
                path = os.path.join(base_dir, root, filename)
                new_path = ''
                if find_val in root:
                    new_path = path.replace(find_val, new_val)
                    new_dir = os.path.dirname(new_path)
                    os.makedirs(new_dir, exist_ok=True)
                    if delete:
                        path_dir = os.path.dirname(path)
                        del_dirs.append(path_dir)

                if os.path.isfile(path):
                    with open(path, 'r') as file :
                        data = file.read()

                    replace_data = data.replace(find_val, new_val)

                    if replace_data:
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