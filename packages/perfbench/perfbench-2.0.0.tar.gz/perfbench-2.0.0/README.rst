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

-  It is possible to select measurement modes.
-  It is possible to switch between layout sizes dynamically.
-  It is possible to switch between axes scales dynamically.
-  It is possible to switch between subplots dynamically.
-  The result of the benchmark can be saved locally as a html.
-  The result of the benchmark can be saved locally as a png.
   **Requires installation
   of**\ `orca <https://github.com/plotly/orca>`__\ **.**
   **When not to use the function, you do not need to install orca
   separately.**

Compatibility
-------------

perfbench works with Python 3.3 or higher.

Dependencies
------------

-  `enum34 <https://pypi.org/project/enum34/>`__
-  `tqdm <https://github.com/tqdm/tqdm>`__\ (4.6.1 or higher.)
-  `cerberus <https://github.com/pyeve/cerberus>`__\ (1.1 or higher.)
-  `plotly <https://github.com/plotly/plotly.py>`__\ (3.0.0 or higher)
-  `notebook <https://github.com/jupyter/notebook>`__\ (5.3 or higher.)
-  `ipywidgets <https://github.com/jupyter-widgets/ipywidgets>`__\ (7.2
   or higher.)

Installation
------------

::

   pip install perfbench

Usage
-----

| **Plotting a single figure.**
| `Here <https://plot.ly/~Hasenpfote/8/perfbench-demo1/>`__ is the
  demonstration.

.. code:: python

   import numpy as np
   from perfbench.process import *


   bm = Benchmark(
       datasets=[
           Dataset(
               stmt=lambda n: np.random.uniform(low=-1., high=1., size=n).astype(np.float64),
               title='float64'
           )
       ],
       dataset_sizes=[2 ** n for n in range(26)],
       kernels=[
           Kernel(
               stmt=lambda x: np.around(x),
               label='around'
           ),
           Kernel(
               stmt=lambda x: np.rint(x),
               label='rint'
           )
       ],
       xlabel='dataset sizes',
       title='around vs rint'
   )
   bm.run()
   bm.plot()

.. figure:: https://raw.githubusercontent.com/Hasenpfote/perfbench/master/docs/plotting_a_single_figure.png
   :alt: plot1

   plot1

| **Plotting multiple plots on a single figure.**
| `Here <https://plot.ly/~Hasenpfote/9/perfbench-demo2/>`__ is the
  demonstration.

.. code:: python

   import numpy as np
   from perfbench.process import *


   bm = Benchmark(
       datasets=[
           Dataset(
               stmt=lambda n: np.random.uniform(low=-1., high=1., size=n).astype(np.float16),
               title='float16'
           ),
           Dataset(
               stmt=lambda n: np.random.uniform(low=-1., high=1., size=n).astype(np.float32),
               title='float32'
           ),
           Dataset(
               stmt=lambda n: np.random.uniform(low=-1., high=1., size=n).astype(np.float64),
               title='float64'
           )
       ],
       dataset_sizes=[2 ** n for n in range(26)],
       kernels=[
           Kernel(
               stmt=lambda x: np.around(x),
               label='around'
           ),
           Kernel(
               stmt=lambda x: np.rint(x),
               label='rint'
           ),
       ],
       xlabel='dataset sizes',
       title='around vs rint'
   )
   bm.run()
   bm.plot()

.. figure:: https://raw.githubusercontent.com/Hasenpfote/perfbench/master/docs/plotting_multiple_plots_on_a_single_figure.png
   :alt: plot2

   plot2

.. figure:: https://raw.githubusercontent.com/Hasenpfote/perfbench/master/docs/switching_between_subplots.png
   :alt: plot2

   plot2

**Switching between layout sizes.**

.. code:: python

   import numpy as np
   from perfbench.process import *


   bm = Benchmark(
       datasets=[
           Dataset(
               stmt=lambda n: np.random.uniform(low=-1., high=1., size=n).astype(np.float64),
               title='float64'
           )
       ],
       dataset_sizes=[2 ** n for n in range(26)],
       kernels=[
           Kernel(
               stmt=lambda x: np.around(x),
               label='around'
           ),
           Kernel(
               stmt=lambda x: np.rint(x),
               label='rint'
           )
       ],
       xlabel='dataset sizes',
       title='around vs rint',
       layout_sizes=[
           LayoutSize(width=640, height=480, label='VGA'),
           LayoutSize(width=800, height=600, label='SVGA'),
           LayoutSize(width=1024, height=768, label='XGA'),
           LayoutSize(width=1280, height=960, label='HD 720p'),
       ]
   )
   bm.run()
   bm.plot()

.. figure:: https://raw.githubusercontent.com/Hasenpfote/perfbench/master/docs/switching_between_layout_sizes.png
   :alt: plot3

   plot3

**Save as a html.**

.. code:: python

   # same as above
   bm.save_as_html(filepath='/path/to/file')

**Save as a png.**

.. code:: python

   # same as above
   bm.save_as_png(filepath='/path/to/file', width=1280, height=960)

License
-------

This software is released under the MIT License, see LICENSE.
