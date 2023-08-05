.. note::
    :class: sphx-glr-download-link-note

    Click :ref:`here <sphx_glr_download_auto_examples_parallel_memmap.py>` to download the full example code
.. rst-class:: sphx-glr-example-title

.. _sphx_glr_auto_examples_parallel_memmap.py:


===============================
NumPy memmap in joblib.Parallel
===============================

This example illustrates some features enabled by using a memory map
(:class:`numpy.memmap`) within :class:`joblib.Parallel`. First, we show that
dumping a huge data array ahead of passing it to :class:`joblib.Parallel`
speeds up computation. Then, we show the possibility to provide write access to
original data.



Speed up processing of a large data array
#############################################################################

 We create a large data array for which the average is computed for several
 slices.



.. code-block:: python


    import numpy as np

    data = np.random.random((int(1e7),))
    window_size = int(5e5)
    slices = [slice(start, start + window_size)
              for start in range(0, data.size - window_size, int(1e5))]







The ``slow_mean`` function introduces a :func:`time.sleep` call to simulate a
more expensive computation cost for which parallel computing is beneficial.
Parallel may not be beneficial for very fast operation, due to extra overhead
(workers creations, communication, etc.).



.. code-block:: python


    import time


    def slow_mean(data, sl):
        """Simulate a time consuming processing."""
        time.sleep(0.01)
        return data[sl].mean()








First, we will evaluate the sequential computing on our problem.



.. code-block:: python


    tic = time.time()
    results = [slow_mean(data, sl) for sl in slices]
    toc = time.time()
    print('\nElapsed time computing the average of couple of slices {:.2f} s'
          .format(toc - tic))





.. rst-class:: sphx-glr-script-out

 Out:

 .. code-block:: none

    Elapsed time computing the average of couple of slices 1.08 s


:class:`joblib.Parallel` is used to compute in parallel the average of all
slices using 2 workers.



.. code-block:: python


    from joblib import Parallel, delayed


    tic = time.time()
    results = Parallel(n_jobs=2)(delayed(slow_mean)(data, sl) for sl in slices)
    toc = time.time()
    print('\nElapsed time computing the average of couple of slices {:.2f} s'
          .format(toc - tic))





.. rst-class:: sphx-glr-script-out

 Out:

 .. code-block:: none

    Elapsed time computing the average of couple of slices 0.80 s


Parallel processing is already faster than the sequential processing. It is
also possible to remove a bit of overhead by dumping the ``data`` array to a
memmap and pass the memmap to :class:`joblib.Parallel`.



.. code-block:: python


    import os
    from joblib import dump, load

    folder = './joblib_memmap'
    try:
        os.mkdir(folder)
    except FileExistsError:
        pass

    data_filename_memmap = os.path.join(folder, 'data_memmap')
    dump(data, data_filename_memmap)
    data = load(data_filename_memmap, mmap_mode='r')

    tic = time.time()
    results = Parallel(n_jobs=2)(delayed(slow_mean)(data, sl) for sl in slices)
    toc = time.time()
    print('\nElapsed time computing the average of couple of slices {:.2f} s\n'
          .format(toc - tic))





.. rst-class:: sphx-glr-script-out

 Out:

 .. code-block:: none

    Elapsed time computing the average of couple of slices 0.77 s


Therefore, dumping large ``data`` array ahead of calling
:class:`joblib.Parallel` can speed up the processing by removing some
overhead.


Writable memmap for shared memory :class:`joblib.Parallel`
##############################################################################

 ``slow_mean_write_output`` will compute the mean for some given slices as in
 the previous example. However, the resulting mean will be directly written on
 the output array.



.. code-block:: python



    def slow_mean_write_output(data, sl, output, idx):
        """Simulate a time consuming processing."""
        time.sleep(0.005)
        res_ = data[sl].mean()
        print("[Worker %d] Mean for slice %d is %f" % (os.getpid(), idx, res_))
        output[idx] = res_








Prepare the folder where the memmap will be dumped.



.. code-block:: python


    output_filename_memmap = os.path.join(folder, 'output_memmap')







Pre-allocate a writable shared memory map as a container for the results of
the parallel computation.



.. code-block:: python


    output = np.memmap(output_filename_memmap, dtype=data.dtype,
                       shape=len(slices), mode='w+')







``data`` is replaced by its memory mapped version. Note that the buffer as
already been dumped in the previous section.



.. code-block:: python


    data = load(data_filename_memmap, mmap_mode='r')







Fork the worker processes to perform computation concurrently



.. code-block:: python


    Parallel(n_jobs=2)(delayed(slow_mean_write_output)(data, sl, output, idx)
                       for idx, sl in enumerate(slices))







Compare the results from the output buffer with the expected results



.. code-block:: python


    print("\nExpected means computed in the parent process:\n {}"
          .format(np.array(results)))
    print("\nActual means computed by the worker processes:\n {}"
          .format(output))





.. rst-class:: sphx-glr-script-out

 Out:

 .. code-block:: none

    Expected means computed in the parent process:
     [0.50079196 0.5008632  0.50094051 0.50049972 0.50033204 0.50023325
     0.49963589 0.49950981 0.49998164 0.4996876  0.49966325 0.50007558
     0.49967006 0.50012095 0.50033717 0.50042984 0.50031454 0.50070861
     0.50066426 0.50074905 0.50078666 0.50063752 0.50022318 0.49986199
     0.49993065 0.49968235 0.49958692 0.49980956 0.49935618 0.49911531
     0.4991053  0.49906349 0.49891044 0.49943774 0.49979804 0.49994955
     0.50040467 0.50069015 0.50044969 0.50044167 0.50067149 0.50035263
     0.50012943 0.5001397  0.4995711  0.49936219 0.49953119 0.49968091
     0.50023217 0.50014224 0.49999523 0.50017198 0.50007499 0.49987072
     0.50045854 0.50041402 0.50062371 0.5009856  0.50066168 0.5004586
     0.50061351 0.50054803 0.50033994 0.50041298 0.50050649 0.5007299
     0.50039438 0.5002814  0.5003074  0.50015618 0.49984567 0.49986017
     0.49978594 0.49945788 0.49967062 0.49980354 0.49999309 0.50016253
     0.50057224 0.50024694 0.49981037 0.49963337 0.49914092 0.49922035
     0.49978009 0.50015929 0.49992073 0.50021926 0.49991571 0.49943029
     0.4995942  0.49970331 0.49995745 0.50018105 0.50051205]

    Actual means computed by the worker processes:
     [0.50079196 0.5008632  0.50094051 0.50049972 0.50033204 0.50023325
     0.49963589 0.49950981 0.49998164 0.4996876  0.49966325 0.50007558
     0.49967006 0.50012095 0.50033717 0.50042984 0.50031454 0.50070861
     0.50066426 0.50074905 0.50078666 0.50063752 0.50022318 0.49986199
     0.49993065 0.49968235 0.49958692 0.49980956 0.49935618 0.49911531
     0.4991053  0.49906349 0.49891044 0.49943774 0.49979804 0.49994955
     0.50040467 0.50069015 0.50044969 0.50044167 0.50067149 0.50035263
     0.50012943 0.5001397  0.4995711  0.49936219 0.49953119 0.49968091
     0.50023217 0.50014224 0.49999523 0.50017198 0.50007499 0.49987072
     0.50045854 0.50041402 0.50062371 0.5009856  0.50066168 0.5004586
     0.50061351 0.50054803 0.50033994 0.50041298 0.50050649 0.5007299
     0.50039438 0.5002814  0.5003074  0.50015618 0.49984567 0.49986017
     0.49978594 0.49945788 0.49967062 0.49980354 0.49999309 0.50016253
     0.50057224 0.50024694 0.49981037 0.49963337 0.49914092 0.49922035
     0.49978009 0.50015929 0.49992073 0.50021926 0.49991571 0.49943029
     0.4995942  0.49970331 0.49995745 0.50018105 0.50051205]


Clean-up the memmap
##############################################################################

 Remove the different memmap that we created. It might fail in Windows due
 to file permissions.



.. code-block:: python


    import shutil

    try:
        shutil.rmtree(folder)
    except:  # noqa
        print('Could not clean-up automatically.')






**Total running time of the script:** ( 0 minutes  3.353 seconds)


.. _sphx_glr_download_auto_examples_parallel_memmap.py:


.. only :: html

 .. container:: sphx-glr-footer
    :class: sphx-glr-footer-example



  .. container:: sphx-glr-download

     :download:`Download Python source code: parallel_memmap.py <parallel_memmap.py>`



  .. container:: sphx-glr-download

     :download:`Download Jupyter notebook: parallel_memmap.ipynb <parallel_memmap.ipynb>`


.. only:: html

 .. rst-class:: sphx-glr-signature

    `Gallery generated by Sphinx-Gallery <https://sphinx-gallery.readthedocs.io>`_
