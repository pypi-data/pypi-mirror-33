
Tutorial FFT 3D parallel (MPI)
==============================

In this tutorial, we present how to use fluidfft to perform 3D fft in
sequential.

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


.. code:: ipython3

    %%px
    import numpy as np
    from fluidfft.fft3d import methods_mpi
    from fluidfft import import_fft_class

.. code:: ipython3

    %%px --targets 1
    print(methods_mpi)


.. parsed-literal::

    ['fft3d.mpi_with_fftw1d', 'fft3d.mpi_with_fftwmpi3d', 'fft3d.mpi_with_p3dfft', 'fft3d.mpi_with_pfft']


We import a class and instantiate it:

.. code:: ipython3

    %%px
    cls = import_fft_class('fft3d.mpi_with_fftw1d')

.. code:: ipython3

    %%px
    o = cls(4, 8, 16)

Let's have a look at the attribute of this objects.

.. code:: ipython3

    %%px --targets 1
    print('\n'.join([name for name in dir(o) if not name.startswith('__')]))


.. parsed-literal::

    build_invariant_arrayK_from_2d_indices12X
    build_invariant_arrayX_from_2d_indices12X
    comm
    compute_energy_from_K
    compute_energy_from_X
    create_arrayK
    create_arrayX
    fft
    fft_as_arg
    gather_Xspace
    get_dimX_K
    get_dim_first_fft
    get_k_adim_loc
    get_local_size_X
    get_seq_indices_first_K
    get_seq_indices_first_X
    get_shapeK_loc
    get_shapeK_seq
    get_shapeX_loc
    get_shapeX_seq
    get_short_name
    ifft
    ifft_as_arg
    ifft_as_arg_destroy
    nb_proc
    rank
    run_benchs
    run_tests
    scatter_Xspace
    sum_wavenumbers


Let's run a test and benchmark the fft and ifft functions directly from
C++.

.. code:: ipython3

    %%px
    _ = o.run_tests()

.. code:: ipython3

    %%px
    results = o.run_benchs()
    if rank == 0:
        print('t_fft = {} s; t_ifft = {} s'.format(*results))


.. parsed-literal::

    [stdout:0] t_fft = 0.0029698 s; t_ifft = 4.11e-05 s


Let's understand how the data is stored:

.. code:: ipython3

    %%px
    print(o.get_dimX_K())


.. parsed-literal::

    [stdout:0] (2, 1, 0)
    [stdout:1] (2, 1, 0)
    [stdout:2] (2, 1, 0)
    [stdout:3] (2, 1, 0)


which means that for this class, in Fourier space, the data is
transposed...

Now we can get the non dimensional wavenumber in the first and second
dimensions:

.. code:: ipython3

    %%px
    k0, k1, k2 = o.get_k_adim_loc()
    print('k0:', k0)
    print('k1:', k1)
    print('k2:', k2)


.. parsed-literal::

    [stdout:0] 
    k0: [0 1]
    k1: [ 0  1  2  3  4 -3 -2 -1]
    k2: [ 0  1  2 -1]
    [stdout:1] 
    k0: [2 3]
    k1: [ 0  1  2  3  4 -3 -2 -1]
    k2: [ 0  1  2 -1]
    [stdout:2] 
    k0: [4 5]
    k1: [ 0  1  2  3  4 -3 -2 -1]
    k2: [ 0  1  2 -1]
    [stdout:3] 
    k0: [6 7]
    k1: [ 0  1  2  3  4 -3 -2 -1]
    k2: [ 0  1  2 -1]


.. code:: ipython3

    %%px
    print(o.get_seq_indices_first_K())


.. parsed-literal::

    [stdout:0] (0, 0, 0)
    [stdout:1] (2, 0, 0)
    [stdout:2] (4, 0, 0)
    [stdout:3] (6, 0, 0)


and get the shape of the arrays in real and Fourier space

.. code:: ipython3

    %%px
    print(o.get_shapeX_seq(), o.get_shapeX_loc())


.. parsed-literal::

    [stdout:0] (4, 8, 16) (1, 8, 16)
    [stdout:1] (4, 8, 16) (1, 8, 16)
    [stdout:2] (4, 8, 16) (1, 8, 16)
    [stdout:3] (4, 8, 16) (1, 8, 16)


.. code:: ipython3

    %%px
    print(o.get_shapeK_seq(), o.get_shapeK_loc())


.. parsed-literal::

    [stdout:0] (8, 8, 4) (2, 8, 4)
    [stdout:1] (8, 8, 4) (2, 8, 4)
    [stdout:2] (8, 8, 4) (2, 8, 4)
    [stdout:3] (8, 8, 4) (2, 8, 4)


Now, let's compute fast Fourier transforms. We first initialize arrays:

.. code:: ipython3

    %%px
    a = np.ones(o.get_shapeX_loc())
    a_fft = np.empty(o.get_shapeK_loc(), dtype=np.complex128)

If we do not have the array where to put the result we can do:

.. code:: ipython3

    %%px
    a_fft = o.fft(a)

If we already have the array where to put the result we can do:

.. code:: ipython3

    %%px
    o.fft_as_arg(a, a_fft)

And finally for the inverse Fourier transform:

.. code:: ipython3

    %%px
    a = o.ifft(a_fft)

.. code:: ipython3

    %%px
    o.ifft_as_arg(a_fft, a)
