.. note::
    :class: sphx-glr-download-link-note

    Click :ref:`here <sphx_glr_download_auto_examples_memory_basic_usage.py>` to download the full example code
.. rst-class:: sphx-glr-example-title

.. _sphx_glr_auto_examples_memory_basic_usage.py:


========================
How to use joblib.Memory
========================

This example illustrates the usage of :class:`joblib.Memory` with both
functions and methods.



Without :class:`joblib.Memory`
##############################################################################

 ``costly_compute`` emulates a computationally expensive process which later
 will benefit from caching using :class:`joblib.Memory`.



.. code-block:: python


    import time
    import numpy as np


    def costly_compute(data, column_index=0):
        """Simulate an expensive computation"""
        time.sleep(5)
        return data[column_index]








Be sure to set the random seed to generate deterministic data. Indeed, if the
data is not deterministic, the :class:`joblib.Memory` instance will not be
able to reuse the cache from one run to another.



.. code-block:: python


    rng = np.random.RandomState(42)
    data = rng.randn(int(1e5), 10)
    start = time.time()
    data_trans = costly_compute(data)
    end = time.time()

    print('\nThe function took {:.2f} s to compute.'.format(end - start))
    print('\nThe transformed data are:\n {}'.format(data_trans))





.. rst-class:: sphx-glr-script-out

 Out:

 .. code-block:: none

    The function took 5.01 s to compute.

    The transformed data are:
     [ 0.49671415 -0.1382643   0.64768854  1.52302986 -0.23415337 -0.23413696
      1.57921282  0.76743473 -0.46947439  0.54256004]


Caching the result of a function to avoid recomputing
##############################################################################

 If we need to call our function several time with the same input data, it is
 beneficial to avoid recomputing the same results over and over since it is
 expensive. :class:`joblib.Memory` enables to cache results from a function
 into a specific location.



.. code-block:: python


    from joblib import Memory
    location = './cachedir'
    memory = Memory(location, verbose=0)


    def costly_compute_cached(data, column_index=0):
        """Simulate an expensive computation"""
        time.sleep(5)
        return data[column_index]


    costly_compute_cached = memory.cache(costly_compute_cached)
    start = time.time()
    data_trans = costly_compute_cached(data)
    end = time.time()

    print('\nThe function took {:.2f} s to compute.'.format(end - start))
    print('\nThe transformed data are:\n {}'.format(data_trans))





.. rst-class:: sphx-glr-script-out

 Out:

 .. code-block:: none

    The function took 5.08 s to compute.

    The transformed data are:
     [ 0.49671415 -0.1382643   0.64768854  1.52302986 -0.23415337 -0.23413696
      1.57921282  0.76743473 -0.46947439  0.54256004]


At the first call, the results will be cached. Therefore, the computation
time corresponds to the time to compute the results plus the time to dump the
results into the disk.



.. code-block:: python


    start = time.time()
    data_trans = costly_compute_cached(data)
    end = time.time()

    print('\nThe function took {:.2f} s to compute.'.format(end - start))
    print('\nThe transformed data are:\n {}'.format(data_trans))





.. rst-class:: sphx-glr-script-out

 Out:

 .. code-block:: none

    The function took 0.02 s to compute.

    The transformed data are:
     [ 0.49671415 -0.1382643   0.64768854  1.52302986 -0.23415337 -0.23413696
      1.57921282  0.76743473 -0.46947439  0.54256004]


At the second call, the computation time is largely reduced since the results
are obtained by loading the data previously dumped to the disk instead of
recomputing the results.


Using :class:`joblib.Memory` with a method
##############################################################################

 :class:`joblib.Memory` is designed to work with functions with no side
 effects. When dealing with class, the computationally expensive part of a
 method has to be moved to a function and decorated in the class method.



.. code-block:: python



    def _costly_compute_cached(data, column):
        time.sleep(5)
        return data[column]


    class Algorithm(object):
        """A class which is using the previous function."""

        def __init__(self, column=0):
            self.column = column

        def transform(self, data):
            costly_compute = memory.cache(_costly_compute_cached)
            return costly_compute(data, self.column)


    transformer = Algorithm()
    start = time.time()
    data_trans = transformer.transform(data)
    end = time.time()

    print('\nThe function took {:.2f} s to compute.'.format(end - start))
    print('\nThe transformed data are:\n {}'.format(data_trans))





.. rst-class:: sphx-glr-script-out

 Out:

 .. code-block:: none

    The function took 5.05 s to compute.

    The transformed data are:
     [ 0.49671415 -0.1382643   0.64768854  1.52302986 -0.23415337 -0.23413696
      1.57921282  0.76743473 -0.46947439  0.54256004]



.. code-block:: python


    start = time.time()
    data_trans = transformer.transform(data)
    end = time.time()

    print('\nThe function took {:.2f} s to compute.'.format(end - start))
    print('\nThe transformed data are:\n {}'.format(data_trans))





.. rst-class:: sphx-glr-script-out

 Out:

 .. code-block:: none

    The function took 0.02 s to compute.

    The transformed data are:
     [ 0.49671415 -0.1382643   0.64768854  1.52302986 -0.23415337 -0.23413696
      1.57921282  0.76743473 -0.46947439  0.54256004]


As expected, the second call to the ``transform`` method load the results
which have been cached.


Clean up cache directory
##############################################################################



.. code-block:: python


    memory.clear(warn=False)






**Total running time of the script:** ( 0 minutes  15.225 seconds)


.. _sphx_glr_download_auto_examples_memory_basic_usage.py:


.. only :: html

 .. container:: sphx-glr-footer
    :class: sphx-glr-footer-example



  .. container:: sphx-glr-download

     :download:`Download Python source code: memory_basic_usage.py <memory_basic_usage.py>`



  .. container:: sphx-glr-download

     :download:`Download Jupyter notebook: memory_basic_usage.ipynb <memory_basic_usage.ipynb>`


.. only:: html

 .. rst-class:: sphx-glr-signature

    `Gallery generated by Sphinx-Gallery <https://sphinx-gallery.readthedocs.io>`_
