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

-  ipython(6.0.0 or higher.)
-  tqdm(4.6.1 or higher.)
-  plotly(2.7.0 or lower)

Installation
------------

::

   pip install perfbench

Usage
-----

**plotting a single figure.**

.. code:: python

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

.. figure:: https://raw.githubusercontent.com/Hasenpfote/perfbench/master/docs/plot1.png
   :alt: plot1

   plot1

**plotting multiple figures.**

.. code:: python

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

.. figure:: https://raw.githubusercontent.com/Hasenpfote/perfbench/master/docs/plot2.png
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
