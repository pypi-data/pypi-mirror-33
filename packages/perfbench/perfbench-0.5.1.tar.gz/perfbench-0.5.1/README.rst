`License <https://github.com/Hasenpfote/fpq/blob/master/LICENSE>`__
`Build Status <https://travis-ci.org/Hasenpfote/perfbench>`__ `PyPI
version <https://badge.fury.io/py/perfbench>`__

perfbench
=========

About
-----

perfbench is a perfomance benchmarking module for Python code.

Feature
-------

-  The result of the benchmark can be saved locally as html.
-  The result of the benchmark can be saved locally as png.
   **Requires installation
   of**\ `orca <https://github.com/plotly/orca>`__\ **.**

Compatibility
-------------

perfbench works with Python 3.3 or higher.

Dependencies
------------

-  `ipython <https://github.com/ipython/ipython>`__\ (6.0.0 or higher.)
-  `tqdm <https://github.com/tqdm/tqdm>`__\ (4.6.1 or higher.)
-  `plotly <https://github.com/plotly/plotly.py>`__\ (2.7.0 or lower)

Installation
------------

::

   pip install perfbench

Usage
-----

| **plotting a single figure.**
| `Here <https://plot.ly/~Hasenpfote/7/perfbench-demo1/>`__ is the
  demonstration.

.. code:: python

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

.. figure:: https://raw.githubusercontent.com/Hasenpfote/perfbench/master/docs/plot1.png
   :alt: plot1

   plot1

| **plotting multiple figures.**
| `Here <https://plot.ly/~Hasenpfote/6/perfbench-demo2/>`__ is the
  demonstration.

.. code:: python

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

.. figure:: https://raw.githubusercontent.com/Hasenpfote/perfbench/master/docs/plot2.png
   :alt: plot2

   plot2

.. figure:: https://raw.githubusercontent.com/Hasenpfote/perfbench/master/docs/plot2_2.png
   :alt: plot2

   plot2

**save as html.**

.. code:: python

   # same as above
   bm.save_as_html(filepath='/path/to/file')

**save as png.**

.. code:: python

   # same as above
   bm.save_as_png(filepath='/path/to/file')

License
-------

This software is released under the MIT License, see LICENSE.
