.. note::
    :class: sphx-glr-download-link-note

    Click :ref:`here <sphx_glr_download_auto_examples_compressors_comparison.py>` to download the full example code
.. rst-class:: sphx-glr-example-title

.. _sphx_glr_auto_examples_compressors_comparison.py:


===============================
Improving I/O using compressors
===============================

This example compares the compressors available in Joblib. In the example,
Zlib, LZMA and LZ4 compression only are used but Joblib also supports BZ2 and
GZip compression methods.
For each compared compression method, this example dumps and reloads a
dataset fetched from an online machine-learning database. This gives 3
informations: the size on disk of the compressed data, the time spent to dump
and the time spent to reload the data from disk.



.. code-block:: python


    import os
    import os.path
    import time







Get some data from real-world use cases
---------------------------------------

First fetch the benchmark dataset from an online machine-learning database
and load it in a pandas dataframe.



.. code-block:: python


    import pandas as pd

    url = ("https://archive.ics.uci.edu/ml/machine-learning-databases/"
           "kddcup99-mld/kddcup.data.gz")
    names = ("duration, protocol_type, service, flag, src_bytes, "
             "dst_bytes, land, wrong_fragment, urgent, hot, "
             "num_failed_logins, logged_in, num_compromised, "
             "root_shell, su_attempted, num_root, "
             "num_file_creations, ").split(', ')

    data = pd.read_csv(url, names=names)







Dump and load the dataset without compression
---------------------------------------------

This gives reference values for later comparison.



.. code-block:: python


    from joblib import dump, load

    pickle_file = './pickle_data.joblib'







Start by measuring the time spent for dumping the raw data:



.. code-block:: python

    start = time.time()
    with open(pickle_file, 'wb') as f:
        dump(data, f)
    raw_dump_duration = time.time() - start
    print("Raw dump duration: %0.3fs" % raw_dump_duration)





.. rst-class:: sphx-glr-script-out

 Out:

 .. code-block:: none

    Raw dump duration: 3.734s


Then measure the size of the raw dumped data on disk:



.. code-block:: python

    raw_file_size = os.stat(pickle_file).st_size / 1e6
    print("Raw dump file size: %0.1fMB" % raw_file_size)





.. rst-class:: sphx-glr-script-out

 Out:

 .. code-block:: none

    Raw dump file size: 1509.3MB


Finally measure the time spent for loading the raw data:



.. code-block:: python

    start = time.time()
    with open(pickle_file, 'rb') as f:
        load(f)
    raw_load_duration = time.time() - start
    print("Raw load duration: %0.3fs" % raw_load_duration)





.. rst-class:: sphx-glr-script-out

 Out:

 .. code-block:: none

    Raw load duration: 1.294s


Dump and load the dataset using the Zlib compression method
-----------------------------------------------------------

The compression level is using the default value, 3, which is, in general, a
good compromise between compression and speed.


Start by measuring the time spent for dumping of the zlib data:



.. code-block:: python


    start = time.time()
    with open(pickle_file, 'wb') as f:
        dump(data, f, compress='zlib')
    zlib_dump_duration = time.time() - start
    print("Zlib dump duration: %0.3fs" % zlib_dump_duration)





.. rst-class:: sphx-glr-script-out

 Out:

 .. code-block:: none

    Zlib dump duration: 5.356s


Then measure the size of the zlib dump data on disk:



.. code-block:: python


    zlib_file_size = os.stat(pickle_file).st_size / 1e6
    print("Zlib file size: %0.1fMB" % zlib_file_size)





.. rst-class:: sphx-glr-script-out

 Out:

 .. code-block:: none

    Zlib file size: 19.8MB


Finally measure the time spent for loading the compressed dataset:



.. code-block:: python


    start = time.time()
    with open(pickle_file, 'rb') as f:
        load(f)
    zlib_load_duration = time.time() - start
    print("Zlib load duration: %0.3fs" % zlib_load_duration)





.. rst-class:: sphx-glr-script-out

 Out:

 .. code-block:: none

    Zlib load duration: 2.743s


.. note:: The compression format is detected automatically by Joblib.
   The compression format is identified by the standard magic number present
   at the beginning of the file. Joblib uses this information to determine
   the compression method used.
   This is the case for all compression methods supported by Joblib.


Dump and load the dataset using the LZMA compression method
-----------------------------------------------------------

LZMA compression method has a very good compression rate but at the cost
of being very slow.
In this example, a light compression level, e.g. 3, is used to speed up a
bit the dump/load cycle.


Start by measuring the time spent for dumping the lzma data:



.. code-block:: python


    start = time.time()
    with open(pickle_file, 'wb') as f:
        dump(data, f, compress=('lzma', 3))
    lzma_dump_duration = time.time() - start
    print("LZMA dump duration: %0.3fs" % lzma_dump_duration)





.. rst-class:: sphx-glr-script-out

 Out:

 .. code-block:: none

    LZMA dump duration: 14.718s


Then measure the size of the lzma dump data on disk:



.. code-block:: python


    lzma_file_size = os.stat(pickle_file).st_size / 1e6
    print("LZMA file size: %0.1fMB" % lzma_file_size)





.. rst-class:: sphx-glr-script-out

 Out:

 .. code-block:: none

    LZMA file size: 8.1MB


Finally measure the time spent for loading the lzma data:



.. code-block:: python


    start = time.time()
    with open(pickle_file, 'rb') as f:
        load(f)
    lzma_load_duration = time.time() - start
    print("LZMA load duration: %0.3fs" % lzma_load_duration)





.. rst-class:: sphx-glr-script-out

 Out:

 .. code-block:: none

    LZMA load duration: 3.244s


Dump and load the dataset using the LZ4 compression method
----------------------------------------------------------

LZ4 compression method is known to be one of the fastest available
compression method but with a compression rate a bit lower than Zlib. In
most of the cases, this method is a good choice.


.. note:: In order to use LZ4 compression with Joblib, the
   `lz4 <http://https://pypi.python.org/pypi/lz4>`_ package must be installed
   on the system.


Start by measuring the time spent for dumping the lz4 data:



.. code-block:: python


    start = time.time()
    with open(pickle_file, 'wb') as f:
        dump(data, f, compress='lz4')
    lz4_dump_duration = time.time() - start
    print("LZ4 dump duration: %0.3fs" % lz4_dump_duration)





.. rst-class:: sphx-glr-script-out

 Out:

 .. code-block:: none

    LZ4 dump duration: 0.807s


Then measure the size of the lz4 dump data on disk:



.. code-block:: python


    lz4_file_size = os.stat(pickle_file).st_size / 1e6
    print("LZ4 file size: %0.1fMB" % lz4_file_size)





.. rst-class:: sphx-glr-script-out

 Out:

 .. code-block:: none

    LZ4 file size: 34.4MB


Finally measure the time spent for loading the lz4 data:



.. code-block:: python


    start = time.time()
    with open(pickle_file, 'rb') as f:
        load(f)
    lz4_load_duration = time.time() - start
    print("LZ4 load duration: %0.3fs" % lz4_load_duration)





.. rst-class:: sphx-glr-script-out

 Out:

 .. code-block:: none

    LZ4 load duration: 1.728s


Comparing the results
---------------------



.. code-block:: python


    import numpy as np
    import matplotlib.pyplot as plt

    N = 4
    load_durations = (raw_load_duration, lz4_load_duration, zlib_load_duration,
                      lzma_load_duration)
    dump_durations = (raw_dump_duration, lz4_dump_duration, zlib_dump_duration,
                      lzma_dump_duration)
    file_sizes = (raw_file_size, lz4_file_size, zlib_file_size, lzma_file_size)
    ind = np.arange(N)
    width = 0.5

    plt.figure(1)
    p1 = plt.bar(ind, dump_durations, width)
    p2 = plt.bar(ind, load_durations, width, bottom=dump_durations)
    plt.ylabel('Time in seconds')
    plt.title('Dump and load durations')
    plt.xticks(ind, ('Raw', 'LZ4', 'Zlib', 'LZMA'))
    plt.yticks(np.arange(0, 30, 5))
    plt.legend((p1[0], p2[0]), ('Dump duration', 'Load duration'))




.. image:: /auto_examples/images/sphx_glr_compressors_comparison_001.png
    :class: sphx-glr-single-img




Compared with other compressors, LZ4 is clearly the fastest, especially for
dumping compressed data on disk. In this particular case, it can even be
faster than the raw dump.
Also note that dump and load durations depend on the I/O speed of the
underlying storage: for example, with SSD hard drives the LZ4 compression
will be slightly slower than raw dump/load, whereas with spinning hard disk
drives (HDD) or remote storage (NFS), LZ4 is faster in general.

LZMA and Zlib, even if always slower for dumping data, are quite fast when
re-loading compressed data from disk.



.. code-block:: python


    plt.figure(2)
    plt.bar(ind, file_sizes, width, log=True)
    plt.ylabel('File size in MB')
    plt.xticks(ind, ('Raw', 'LZ4', 'Zlib', 'LZMA'))




.. image:: /auto_examples/images/sphx_glr_compressors_comparison_003.png
    :class: sphx-glr-single-img




Compressed data obviously takes a lot less space on disk than raw data. LZMA
is the best compression method in terms of compression rate. Zlib also has a
better compression rate than LZ4.



.. code-block:: python


    plt.show()







Clear the pickle file
---------------------



.. code-block:: python


    import os
    os.remove(pickle_file)






**Total running time of the script:** ( 1 minutes  14.074 seconds)


.. _sphx_glr_download_auto_examples_compressors_comparison.py:


.. only :: html

 .. container:: sphx-glr-footer
    :class: sphx-glr-footer-example



  .. container:: sphx-glr-download

     :download:`Download Python source code: compressors_comparison.py <compressors_comparison.py>`



  .. container:: sphx-glr-download

     :download:`Download Jupyter notebook: compressors_comparison.ipynb <compressors_comparison.ipynb>`


.. only:: html

 .. rst-class:: sphx-glr-signature

    `Gallery generated by Sphinx-Gallery <https://sphinx-gallery.readthedocs.io>`_
