from typing import Union
import numpy as np

def cell2array(array) -> Union[np.ndarray, dict, None, list]:
    """The main conversion function"""
    if isinstance(array, np.ndarray):
        if not array.dtype.fields:
            if len(array) == 0:
                return None
            if len(array) == 1:
                return cell2array(array[0])
            elif array.dtype == np.dtype('O'):
                return [cell2array(item) for item in array]
            else:
                return array
        else:
            if len(array) == 0:
                return None
            result = dict()
            for field in array.dtype.fields.keys():
                result[field] = cell2array(array[field][0])
            return result
    elif isinstance(array, dict):
        return {key: cell2array(value) for key, value in array.items()}
    else:
        return array
