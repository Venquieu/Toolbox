import os
import json
from glob import glob
from typing import Union, List, Dict


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


def read_text_file(path: str) -> list:
    """
    Load text file -> strip each line -> return list of lines.
    """
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    return [line.strip() for line in lines]


def write_text_file(path: str, lines: list, mode: str = "w") -> None:
    with open(path, mode=mode, encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def read_json_file(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def write_json_file(path: str, data: dict, mode: str = "w", indent: int = 4) -> None:
    with open(path, mode=mode, encoding="utf-8") as f:
        json.dump(data, f, indent=indent)


def read_file(path: str) -> Union[List, Dict]:
    ext = os.path.splitext(path)[1]
    if ext == ".txt":
        return read_text_file(path)
    elif ext == ".json":
        return read_json_file(path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")


def write_file(path: str, data: Union[List, Dict], mode: str = "w", **kargs) -> None:
    ext = os.path.splitext(path)[1]
    if ext == ".txt":
        write_text_file(path, data, mode, **kargs)
    elif ext == ".json":
        write_json_file(path, data, mode, **kargs)
    else:
        raise ValueError(f"Unsupported file type: {ext}")
