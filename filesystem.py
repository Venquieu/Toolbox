import os
from glob import glob


def make_dataset(root: str, ext: str = None, followlinks: bool = False):
    """
    Args:
        root(str): file directory for scaning files.
        ext(str): extention name of target files, like `.jpg`.
        followlinks(bool): whether scan files under a filelink, default False.
    """
    file_list = []
    for root, _, files in os.walk(root, followlinks=followlinks):
        for file in files:
            if ext is None or file.endswith(ext):
                file_list.append(os.path.join(root, file))
    return file_list


def sync_rm(root: str, source: str, target: str, strict: bool = False):
    """
    Remove files under target dir if without corresponding files under source dir.

    Args:
        root(str): root directory
        soruce(str): source folder under root.
        strict(bool): True means files must match includes extention name.
    """
    source_dir = os.path.join(root, source)
    target_dir = os.path.join(root, target)
    assert os.path.exists(source_dir) and os.path.exists(target_dir)

    target_list = make_dataset(target_dir)
    for target_file in target_list:
        source_file = target_file.replace(target_dir, source_dir)
        if strict:
            found_list = [source_file] if os.path.exists(source_file) else []
        else:
            source_file = os.path.splitext(source_file)[0] + ".*"
            found_list = glob(source_file)

        if len(found_list) == 0:
            os.remove(target_file)
