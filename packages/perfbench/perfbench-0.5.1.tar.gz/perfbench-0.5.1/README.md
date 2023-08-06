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
* [ipython](https://github.com/ipython/ipython)(6.0.0 or higher.)
* [tqdm](https://github.com/tqdm/tqdm)(4.6.1 or higher.)
* [plotly](https://github.com/plotly/plotly.py)(2.7.0 or lower)

## Installation
```
pip install perfbench
```

## Usage
**plotting a single figure.**  
[Here](https://plot.ly/~Hasenpfote/7/perfbench-demo1/) is the demonstration.
```python
import numpy as np
from perfbench.process import *


bm = Benchmark(
    datasets=[
        dict(
            stmt=lambda n: np.random.uniform(low=-1., high=1., size=n).astype(np.float64),
            title='float64'
        )
    ],
    dataset_sizes=[2 ** n for n in range(26)],
    kernels=[
        dict(
            stmt=lambda x: np.around(x),
            label='around'
        ),
        dict(
            stmt=lambda x: np.rint(x),
            label='rint'
        )
    ],
    xlabel='samples',
    title='around vs rint',
    logx=True
)
bm.run()
bm.plot()
```
![plot1](https://raw.githubusercontent.com/Hasenpfote/perfbench/master/docs/plot1.png)


**plotting multiple figures.**  
[Here](https://plot.ly/~Hasenpfote/6/perfbench-demo2/) is the demonstration.
```python
import numpy as np
from perfbench.process import *


bm = Benchmark(
    datasets=[
        dict(
            stmt=lambda n: np.random.uniform(low=-1., high=1., size=n).astype(np.float16),
            title='float16'
        ),
        dict(
            stmt=lambda n: np.random.uniform(low=-1., high=1., size=n).astype(np.float32),
            title='float32'
        ),
        dict(
            stmt=lambda n: np.random.uniform(low=-1., high=1., size=n).astype(np.float64),
            title='float64'
        )
    ],
    dataset_sizes=[2 ** n for n in range(26)],
    kernels=[
        dict(
            stmt=lambda x: np.around(x),
            label='around'
        ),
        dict(
            stmt=lambda x: np.rint(x),
            label='rint'
        )
    ],
    xlabel='samples',
    title='around vs rint',
    logx=True
)
bm.run()
bm.plot()
```
![plot2](https://raw.githubusercontent.com/Hasenpfote/perfbench/master/docs/plot2.png)

![plot2](https://raw.githubusercontent.com/Hasenpfote/perfbench/master/docs/plot2_2.png)

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
