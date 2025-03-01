import json
from typing import List, Tuple, Dict, Any, Union

from utils import Struct


class AttriManager(object):
    def __init__(self, items: Union[List, Tuple, Dict]) -> None:
        if isinstance(items, dict):
            self.table = items
        elif isinstance(items, (list, tuple)):
            self.table = {item: Struct() for item in items}
        else:
            raise NotImplementedError

    @classmethod
    def from_file(cls, path: str) -> "AttriManager":
        with open(path, "r", encoding="utf-8") as f:
            info = json.load(f)
        return cls(info)

    def add_item(self, item, value) -> bool:
        if item in self.table:
            return False
        self.table[item] = value
        return True

    def set_attri(self, name: Any, value: Any, items: list = None):
        if items is not None:
            for item in items:
                self.table[item][name] = value
        else:
            for k, _ in self.table.items():
                self.table[k][name] = value

    def select(self, conditions: list) -> dict:
        """
        Select items according to conditions.

        Conditions like:
        `[("attri1", "==", True), ("attri2", ">", 0.5), ("attri3", "==", "apple"), ...]`
        """
        targets = {}
        for k, v in self.table.items():
            flag = True
            for attri, oper, value in conditions:
                var = "'" + v[attri] + "'" if isinstance(v[attri], str) else v[attri]
                value = "'" + value + "'" if isinstance(value, str) else value
                flag = flag and eval("%s%s%s" % (var, oper, value))
                if flag is False:
                    break
            if flag:
                targets[k] = v
        return targets

    def dump(self, path: str) -> None:
        with open(path, "w") as f:
            json.dump(self.table, f, indent=2)

    def update(self, source: Union[str, dict]) -> None:
        if isinstance(source, str):
            with open(source, "r", encoding="utf-8") as f:
                info = json.load(f)
            self.table = info
        elif isinstance(source, dict):
            self.table = source
        else:
            raise NotImplementedError

    @property
    def attri_names(self) -> List[str]:
        return list(self.table[list(self.table.keys())[0]].keys())

    def __len__(self) -> int:
        return len(self.table)
