import shutil
from distutils.dir_util import copy_tree
from pathlib import Path


class Result:
    def to(self, dest):
        dest = dest
        dest.mkdir(exist_ok=True)
        return self._to(dest)

    def _to(self, dest):
        raise NotImplementedError()


class Copy(Result):
    def __init__(self, item, destination="", rename=False):
        self._item = Path(item)
        self._rename = rename
        self._dest = destination

    def to(self, dest):
        return super().to(dest / self._dest)

    @staticmethod
    def _copy_item(item, dest, rename):
        raise NotImplementedError()

    def _to(self, dest):
        name = self._item.name if not self._rename else self._rename
        self._copy_item(self._item, dest, name)
        return [dest / name]


class File(Copy):
    @staticmethod
    def _copy_item(item, dest, name):
        dest = dest / name
        shutil.copy2(str(item), str(dest))


class Directory(Copy):
    @staticmethod
    def _copy_item(item, dest, name):
        copy_tree(str(item), str(dest / name))
