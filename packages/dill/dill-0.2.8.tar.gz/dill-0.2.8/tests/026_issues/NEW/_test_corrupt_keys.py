# generate keys
from klepto.archives import dir_archive

class LargeLists:
    def __init__(self, number):
        self.load = [number] * 10000

lists = [LargeLists(i/13) for i in range(1000)]
archive = dir_archive('path')
for key, obj in enumerate(lists):
    archive[key] = obj
archive.dump()

# if this is interrupted, in some way, there may be an invalid key...


# the following attempts to detect and remove an invalid key

def remove_key_from_archive(key, archive_path):
    dir_name = "K_{}".format(key)
    full_path = os.path.join(archive_path, dir_name)
    try:
        shutil.rmtree(full_path)
    except FileNotFoundError:
        pass

def find_invalid_folders_from_archive(archive_path):
    pattern = "K_I_.*"
    prog = re.compile(pattern, flags=re.IGNORECASE)
    try:
        for elem in os.listdir(archive_path):
            if prog.fullmatch(elem) is not None:
                yield elem
    except FileNotFoundError:
        raise StopIteration

def remove_old_invalid_folders(archive_path, seconds_old=10):
    cnt = 0
    invalid_folders = find_invalid_folders_from_archive(archive_path)
    for folder in invalid_folders:
        full_path = os.path.join(archive_path, folder)
        try:
            time_diff = time() - os.path.getmtime(full_path)
            if time_diff > seconds_old:
                shutil.rmtree(full_path)
                cnt += 1
        except FileNotFoundError:
            continue
    return cnt

def get_loaded_and_validated_archive(path):
    for i in range(10000):
        remove_old_invalid_folders(path)
        archive = dir_archive(path)
        try:
            archive.load()
            return archive
        except KeyError as e:
            remove_key_from_archive(e.args[0], path)
    raise IOError
