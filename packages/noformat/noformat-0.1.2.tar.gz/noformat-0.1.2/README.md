# Noformat

Basically, noformat treats a folder structure as a single dict that contains data and attributes.
Pandas dataframe and numpy array can be used for dict values.
```python
import numpy as np
import pandas as pd
from noformat import File
data = File('data/temp', 'w-')
data['first_array'] = np.random.randn(10, 10)
data['second_array'] = pd.DataFrame(data=np.random.randn(10, 4), columns=['1', '2', '3', '4'])
```
Files will be automatically saved upon object destruction.
And loaded later
```python
read_data = File('data/temp', 'w+')
assert(read_data['first_array'].shape == (10, 10))
```
Attributes will be saved in 'attributes.json' files
```python
read_data = File('data/temp', 'w+')
read_data.attrs['first_attribute'] = 64
```
This will create a folder with the following structure
```
data/temp/
|   first_array.npy
|   second_array.msg
└───attributes.json
```
Logging files for the data can be included:
1. in json format with .log extension
2. in cell array format with .mat extension
It can only be written in the first type
