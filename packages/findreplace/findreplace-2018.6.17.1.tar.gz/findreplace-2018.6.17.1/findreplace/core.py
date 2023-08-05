import os
import glob

ROOT_DIR = os.path.dirname(os.path.realpath(__file__))

def findreplace(base_dir=ROOT_DIR, find_val='', new_val=''):    
    if '~' in base_dir:
        base_dir = os.path.expanduser(base_dir)
    print(base_dir)
    if find_val and new_val:
        for root, dirs, files in os.walk(base_dir):
            for filename in files:
                path = os.path.join(base_dir, root, filename)
                print(path)
                if os.path.isfile(path):
                    with open(path, 'r') as file :
                        data = file.read()

                    replace_data = data.replace(find_val, new_val)

                    if replace_data:
                        with open(path, 'w') as file:
                            file.write(replace_data)
                    
                    if not os.access(path, os.W_OK):
                        st = os.stat(path)
                        new_permissions = stat.S_IMODE(st.st_mode) | stat.S_IWUSR
                        os.chmod(path, new_permissions)
