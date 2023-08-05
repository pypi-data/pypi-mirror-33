[![License](https://img.shields.io/badge/license-MIT-brightgreen.svg)](https://github.com/Hasenpfote/fpq/blob/master/LICENSE)

perfbench
=========

## About

## Feature

## Compatibility
perfbench works with Python 3.3 or higher.

## Dependencies
* ipython(6.0.0 or higher.)
* tqdm(4.6.1 or higher.)
* plotly(2.7.0 or lower)

## Installation

## Usage
case1:
```python
import numpy as np
from perfbench.process import *


setups = [
    {'func': lambda n: np.random.uniform(low=-1., high=1., size=n).astype(np.float64), 'title': 'float64'}
]

kernels = [
    {'func': lambda x: np.around(x), 'label': 'around'},
    {'func': lambda x: np.rint(x), 'label': 'rint'}
]

ntimes = [2 ** n for n in range(15)]

bm = Benchmark(
    setups=setups,
    kernels=kernels,
    ntimes=ntimes,
    xlabel='samples',
    title='test',
    logx=True
)
bm.run()
bm.show()
```
![plot1](https://raw.githubusercontent.com/Hasenpfote/perfbench/master/docs/plot1.png)


case2:
```python
import numpy as np
from perfbench.process import *


setups = [
    {'func': lambda n: np.random.uniform(low=-1., high=1., size=n).astype(np.float16), 'title': 'float16'},
    {'func': lambda n: np.random.uniform(low=-1., high=1., size=n).astype(np.float32), 'title': 'float32'},
    {'func': lambda n: np.random.uniform(low=-1., high=1., size=n).astype(np.float64), 'title': 'float64'}
]

kernels = [
    {'func': lambda x: np.around(x), 'label': 'around'},
    {'func': lambda x: np.rint(x), 'label': 'rint'}
]

ntimes = [2 ** n for n in range(5)]

bm = Benchmark(
    setups=setups,
    kernels=kernels,
    ntimes=ntimes,
    xlabel='samples',
    title='test',
    logx=True
)
bm.run()
bm.show()
```
![plot2](https://raw.githubusercontent.com/Hasenpfote/perfbench/master/docs/plot2.png)

## License
This software is released under the MIT License, see LICENSE.
