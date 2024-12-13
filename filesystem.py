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


def sync_rm(source_dir: str, target_dir: str, strict: bool = False):
    """
    Remove files under target dir if without corresponding files under source dir.

    Args:
        soruce_dir(str): source ffile directory as benchmark.
        target_dir(str): target file directory to be checked.
        strict(bool): True means files must match includes extention name.
    """
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


def read_text_file(path: str):
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    return [line.strip() for line in lines]


def write_text_file(path: str, lines: list, mode: str = "w"):
    with open(path, mode=mode, encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
