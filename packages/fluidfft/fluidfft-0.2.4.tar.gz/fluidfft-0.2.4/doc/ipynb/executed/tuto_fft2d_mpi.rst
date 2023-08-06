
Tutorial FFT 2D parallel (MPI)
==============================

In this tutorial, we present how to use fluidfft to perform 2D fft in
parallel.

As in sequential, the first step would normally to benchmark the different methods for your case as explained in the page :ref:`bench`.

Because, we are doing this tutorial in parallel with jupyter and
ipyparallel, we first need to create an ipyparallel client and create a
direct view as explained `here <http://ipyparallel.readthedocs.io>`__.
We previously started an ipcluster with the command
``ipcluster start -n 4 --engines=MPIEngineSetLauncher``. This is just a
jupyter/ipython thing and it has nothing to do with fluidfft.

.. code:: ipython3

    import ipyparallel as ipp
    rc = ipp.Client()
    dview = rc[:]

Afterwards, we will execute all cells in parallel so we always need to
add the magic command ``%%px`` (see
`here <http://ipyparallel.readthedocs.io/en/latest/magics.html>`__)

.. code:: ipython3

    %%px
    from fluiddyn.util.mpi import rank, nb_proc
    print("Hello world! I'm rank {}/{}".format(rank, nb_proc))


.. parsed-literal::

    [stdout:0] Hello world! I'm rank 0/4
    [stdout:1] Hello world! I'm rank 1/4
    [stdout:2] Hello world! I'm rank 2/4
    [stdout:3] Hello world! I'm rank 3/4


Then it is very similar as in sequential so we do not need to explain
too much!

.. code:: ipython3

    %%px
    import numpy as np
    from fluidfft.fft2d import methods_mpi
    from fluidfft import import_fft_class

.. code:: ipython3

    %%px
    if rank == 0:
        print(methods_mpi)


.. parsed-literal::

    [stdout:0] ['fft2d.mpi_with_fftwmpi2d', 'fft2d.mpi_with_fftw1d']


.. code:: ipython3

    %%px
    cls = import_fft_class('fft2d.mpi_with_fftw1d')
    o = cls(48, 32)

.. code:: ipython3

    %%px
    _ = o.run_tests()
    print(_)


.. parsed-literal::

    [stdout:0] 1
    [stdout:1] 1
    [stdout:2] 1
    [stdout:3] 1


.. code:: ipython3

    %%px
    times = o.run_benchs()
    if rank == 0:
        print('t_fft = {} s; t_ifft = {} s'.format(*times))


.. parsed-literal::

    [stdout:0] t_fft = 7.07e-05 s; t_ifft = 2.05e-05 s


.. code:: ipython3

    %%px 
    print(o.get_is_transposed())


.. parsed-literal::

    [stdout:0] True
    [stdout:1] True
    [stdout:2] True
    [stdout:3] True


.. code:: ipython3

    %%px 
    k0, k1 = o.get_k_adim_loc()
    print('k0:', k0)
    print('k1:', k1)


.. parsed-literal::

    [stdout:0] 
    k0: [0 1 2 3]
    k1: [  0   1   2   3   4   5   6   7   8   9  10  11  12  13  14  15  16  17
      18  19  20  21  22  23  24 -23 -22 -21 -20 -19 -18 -17 -16 -15 -14 -13
     -12 -11 -10  -9  -8  -7  -6  -5  -4  -3  -2  -1]
    [stdout:1] 
    k0: [4 5 6 7]
    k1: [  0   1   2   3   4   5   6   7   8   9  10  11  12  13  14  15  16  17
      18  19  20  21  22  23  24 -23 -22 -21 -20 -19 -18 -17 -16 -15 -14 -13
     -12 -11 -10  -9  -8  -7  -6  -5  -4  -3  -2  -1]
    [stdout:2] 
    k0: [ 8  9 10 11]
    k1: [  0   1   2   3   4   5   6   7   8   9  10  11  12  13  14  15  16  17
      18  19  20  21  22  23  24 -23 -22 -21 -20 -19 -18 -17 -16 -15 -14 -13
     -12 -11 -10  -9  -8  -7  -6  -5  -4  -3  -2  -1]
    [stdout:3] 
    k0: [12 13 14 15]
    k1: [  0   1   2   3   4   5   6   7   8   9  10  11  12  13  14  15  16  17
      18  19  20  21  22  23  24 -23 -22 -21 -20 -19 -18 -17 -16 -15 -14 -13
     -12 -11 -10  -9  -8  -7  -6  -5  -4  -3  -2  -1]


.. code:: ipython3

    %%px
    print(o.get_shapeX_loc())
    print(o.get_shapeK_loc())


.. parsed-literal::

    [stdout:0] 
    (12, 32)
    (4, 48)
    [stdout:1] 
    (12, 32)
    (4, 48)
    [stdout:2] 
    (12, 32)
    (4, 48)
    [stdout:3] 
    (12, 32)
    (4, 48)


.. code:: ipython3

    %%px
    print(o.get_seq_indices_first_X())


.. parsed-literal::

    [stdout:0] (0, 0)
    [stdout:1] (12, 0)
    [stdout:2] (24, 0)
    [stdout:3] (36, 0)


.. code:: ipython3

    %%px
    print(o.get_seq_indices_first_K())


.. parsed-literal::

    [stdout:0] (0, 0)
    [stdout:1] (4, 0)
    [stdout:2] (8, 0)
    [stdout:3] (12, 0)


.. code:: ipython3

    %%px
    a = np.ones(o.get_shapeX_loc())
    a_fft = o.fft(a)

.. code:: ipython3

    %%px
    a_fft = np.empty(o.get_shapeK_loc(), dtype=np.complex128)
    o.fft_as_arg(a, a_fft)

.. code:: ipython3

    %%px
    o.ifft_as_arg(a_fft, a)

.. code:: ipython3

    %%px
    a = o.ifft(a_fft)
