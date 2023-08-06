[![License](https://img.shields.io/badge/license-MIT-brightgreen.svg)](https://github.com/Hasenpfote/fpq/blob/master/LICENSE)
[![Build Status](https://travis-ci.org/Hasenpfote/perfbench.svg?branch=master)](https://travis-ci.org/Hasenpfote/perfbench)
[![PyPI version](https://badge.fury.io/py/perfbench.svg)](https://badge.fury.io/py/perfbench)

perfbench
=========

## About
perfbench is a perfomance benchmarking module for Python code.

## Feature
* The result of the benchmark can be saved locally as html.
* The result of the benchmark can be saved locally as png.  
**Requires installation of [orca](https://github.com/plotly/orca).**

## Compatibility
perfbench works with Python 3.3 or higher.

## Dependencies
* ipython(6.0.0 or higher.)
* tqdm(4.6.1 or higher.)
* plotly(2.7.0 or lower)

## Installation
```
pip install perfbench
```

## Usage
**plotting a single figure.**
```python
import numpy as np
from perfbench.process import *


bm = Benchmark(
    setups=[
        dict(
            func=lambda n: np.random.uniform(low=-1., high=1., size=n).astype(np.float64),
            title='float64'
        )
    ],
    kernels=[
        dict(
            func=lambda x: np.around(x),
            label='around'
        ),
        dict(
            func=lambda x: np.rint(x),
            label='rint'
        )
    ],
    ntimes=[2 ** n for n in range(26)],
    xlabel='samples',
    title='around vs rint',
    logx=True
)
bm.run()
bm.plot()
```
![plot1](https://raw.githubusercontent.com/Hasenpfote/perfbench/master/docs/plot1.png)


**plotting multiple figures.**
```python
import numpy as np
from perfbench.process import *


bm = Benchmark(
    setups=[
        dict(
            func=lambda n: np.random.uniform(low=-1., high=1., size=n).astype(np.float16),
            title='float16'
        ),
        dict(
            func=lambda n: np.random.uniform(low=-1., high=1., size=n).astype(np.float32),
            title='float32'
        ),
        dict(
            func=lambda n: np.random.uniform(low=-1., high=1., size=n).astype(np.float64),
            title='float64'
        )
    ],
    kernels=[
        dict(
            func=lambda x: np.around(x),
            label='around'
        ),
        dict(
            func=lambda x: np.rint(x),
            label='rint'
        )
    ],
    ntimes=[2 ** n for n in range(26)],
    xlabel='samples',
    title='around vs rint',
    logx=True
)
bm.run()
bm.plot()
```
![plot2](https://raw.githubusercontent.com/Hasenpfote/perfbench/master/docs/plot2.png)

**save as html.**
```python
# same as above
bm.save_as_html(filepath='/path/to/file')
```

**save as png.**
```python
# same as above
bm.save_as_png(filepath='/path/to/file')
```

## License
This software is released under the MIT License, see LICENSE.
