"""main file for noformat, defines file and attribute classes that treat a folder as a hdf5-like file """
from typing import Dict, Tuple, Hashable
from collections.abc import MutableMapping
import json
from json.decoder import JSONDecodeError
from os import walk, listdir, remove, rmdir, makedirs
from os.path import splitext, isdir, join, isfile, exists, abspath

from .formats import formats

__all__ = ['File']


class File(MutableMapping):
    """defines the main file class, uses a dict of accessors for real files in folder """
    def __init__(self, file_name: str, mode: str = 'r') -> None:
        self._create_folder(file_name, mode)
        self.file_name = file_name
        self.mode = mode
        self.attrs = Attributes(file_name)
        self._item_list: Dict[str, Tuple[str, str]] = dict()
        for file in listdir(file_name):
            file_base, ext = splitext(file)
            if ext in formats:
                if file_base in self._item_list:
                    raise IOError('duplicate items in file!', join(file_name, file_base))
                self._item_list[file_base] = (ext, file)

    @staticmethod
    def _create_folder(file_name: str, mode: str):  # file system side effect
        is_folder = isdir(file_name) and exists(file_name)
        if mode not in {'r', 'w', 'r+', 'wr', 'rw', 'w+', 'w-'}:
            raise ValueError('mode not supported!', mode)
        if mode in {'r', 'r+', 'rw'}:
            if not is_folder:
                raise IOError('file not exist!', file_name)
            if not exists(join(file_name, 'attributes.json')):
                raise IOError('file not in noformat format!', file_name)
        elif mode == 'w-' and is_folder:
            raise IOError('file already exist!', file_name)
        elif mode == 'w' and is_folder:
            empty_dir(file_name)
        elif not is_folder:
            makedirs(file_name)

    def _remove(self, file_name: str):
        remove(join(self.file_name, self._item_list[file_name][1]))
        del self._item_list[file_name]

    def __contains__(self, item: Hashable) -> bool:
        if not isinstance(item, str):
            raise ValueError("noformat File components can only have str names")
        return item in self._item_list

    def __getitem__(self, item: str):
        if item not in self._item_list:
            raise IOError('item does not exist!', join(self.file_name, item))
        ext, _ = self._item_list[item]
        return formats[ext].load(join(self.file_name, item))

    def __setitem__(self, key: str, value):
        if self.mode == 'r':
            raise IOError('cannot write under read mode')
        if key in self._item_list:
            self._remove(key)
        for ext, file_format in formats.items():
            if file_format.is_(value):
                full_name = join(self.file_name, key)
                file_format.save(full_name, value)
                self._item_list[key] = (ext, key + ext)
                break

    def __iter__(self):
        return (file for file, (ext, full_path) in self._item_list.items() if ext in formats)

    def __delitem__(self, key):
        if key not in self._item_list:
            raise IOError('value not in file', key)
        else:
            self._remove(key)

    def __len__(self):
        return len(self._item_list)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        del exc_type, exc_val, exc_tb
        del self.attrs


class Attributes(MutableMapping):
    """manipulates attributes, save when changed"""
    def __init__(self, file_name):
        self.changed = False
        self.file_name = abspath(join(file_name, 'attributes.json'))
        if isfile(self.file_name) and exists(self.file_name):
            try:
                self.dict = json.load(open(self.file_name, 'r'))
            except JSONDecodeError as e:
                print("failed to load attributes of ", self.file_name)
                raise e
        else:
            self.dict = dict()

    def __iter__(self):
        return self.dict.__iter__()

    def __len__(self):
        return self.dict.__len__()

    def __setitem__(self, key, value):
        self.changed = True
        self.dict[key] = value

    def __delitem__(self, key):
        self.changed = True
        del self.dict[key]

    def __contains__(self, key):
        return key in self.dict

    def __getitem__(self, key):
        return self.dict[key]

    def __del__(self):
        if self.changed:
            json.dump(self.dict, open(self.file_name, 'w'), indent=4)


def empty_dir(top: str) -> None:
    """recursively delete all files inside folder 'top'"""
    if top == '/' or top == "\\":
        return
    for root, dirs, files in walk(top, topdown=False):
        for name in files:
            remove(join(root, name))
        for name in dirs:
            folder_path = join(root, name)
            empty_dir(folder_path)
            rmdir(folder_path)


def isFile(folder: str) -> bool:
    """Check if a folder makes a valid noformat file."""
    attribute_file = join(folder, "attributes.json")
    try:
        json.load(open(attribute_file))
        return True
    except (IOError, ValueError):
        return False
