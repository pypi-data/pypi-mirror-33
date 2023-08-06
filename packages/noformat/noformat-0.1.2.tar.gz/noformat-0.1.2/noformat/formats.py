"""define the difference formats that can be read inside the noformat folder """
from typing import Iterable, Dict, Any
from collections import namedtuple
import json

import numpy as np

__all__ = ["FileFormat", "formats"]

FileFormat = namedtuple('FileFormat', ['ext', 'is_', 'save', 'load'])

np_array_ext = '.npy'
np_array = FileFormat(np_array_ext,
                      lambda x: isinstance(x, np.ndarray),
                      lambda name, value: np.save(name + np_array_ext, value),
                      lambda name: np.load(name + np_array_ext))

np_arrays_ext = '.npz'
def np_arrays_save(name: str, value_dict: Dict[str, Iterable]) -> None:
    np.savez_compressed(name + np_arrays_ext, **value_dict)


def is_np_arrays(x: Any) -> bool:
    if not isinstance(x, dict):
        return False
    for value in x.values():
        if not isinstance(value, Iterable) or isinstance(value, dict):
            return False
    return True


np_arrays = FileFormat(np_arrays_ext,
                       is_np_arrays,
                       np_arrays_save,
                       lambda name: np.load(name + np_arrays_ext))

csv_ext = '.csv'
csv_file = FileFormat(csv_ext,
                      lambda x: False,  # never save as such
                      None,
                      lambda name: np.loadtxt(name + csv_ext))

log_ext = '.log'
def is_json(x: Any) -> bool:
    if not isinstance(x, dict):
        return False
    for value in x.values():
        if not isinstance(value, Iterable) or isinstance(value, dict):
            return True
    return False


log_file = FileFormat(log_ext,
                      is_json,
                      lambda name, value: json.dump(value, open(name + log_ext, 'w'), indent=4),
                      lambda name: json.load(open(name + log_ext, 'r')))

try:
    from scipy.io import loadmat
    from .utils import cell2array
    mat_ext = '.mat'
    mat_file = FileFormat(mat_ext,
                          lambda x: False,  # never save as such
                          None,
                          lambda name: cell2array(loadmat(name + log_ext)))
except ImportError:
    loadmat = None
    mat_file = None

try:
    import pandas as pd

    pd_ext = '.msg'
    pd_data = FileFormat(pd_ext,
                         lambda x: isinstance(x, pd.DataFrame),
                         lambda name, value: pd.to_msgpack(name + pd_ext, value),
                         lambda name: pd.read_msgpack(name + pd_ext))
except ImportError:
    pd = None
    pd_data = None

_format_list = [np_array, np_arrays, pd_data, log_file, mat_file]
formats = {cls.ext: cls for cls in _format_list if cls is not None}
