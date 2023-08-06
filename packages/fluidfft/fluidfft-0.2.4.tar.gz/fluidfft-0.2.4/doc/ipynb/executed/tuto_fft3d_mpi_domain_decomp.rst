
Tutorial FFT 3D parallel (MPI): Domain decomposition
====================================================

We have seen that FluidFFT provides a unified framework for different
parallelized FFT 3D libraries, viz. FFTW (with MPI), P3DFFT, and PFFT.

In this tutorial, we will look into how these libraries perform domain
decomposition, and thereby try to balance the load evenly. Understanding
how this is done is important to plan the discretization (i.e. shape of
the arrays).

Always remember:

    "FFTW is best at handling sizes of the form
    :math:`2^a \times 3^b \times 5^c \times 7^d \times 11^e \times 13^f`,
    where :math:`e+f` is either 0 or 1, and the other exponents are
    arbitrary. Other sizes are computed by means of a slow,
    general-purpose routine (which nevertheless retains
    :math:`O(n \log n)` performance, even for prime sizes). (It is
    possible to customize FFTW for different array sizes. See Section
    `Installation and
    Customization <http://www.fftw.org/fftw2_doc/fftw_6.html#SEC66>`__,
    for more information.) Transforms whose sizes are powers of 2 are
    especially fast."

    Source: http://www.fftw.org/fftw2\_doc/fftw\_3.html

Just like, before we start an parallelized IPython/Jupyter session with
``ipcluster start -n 8 --engines=MPIEngineSetLauncher``.

.. code:: ipython3

    import ipyparallel as ipp
    rc = ipp.Client()
    dview = rc[:]

We start by importing all the functions that we need

.. code:: ipython3

    %%px
    from fluiddyn.util.info import _print_dict
    from fluidfft.fft3d import get_classes_mpi
    from fluiddyn.util.mpi import rank, print_sorted, printby0

.. code:: ipython3

    %%px
    dict_classes = get_classes_mpi()

The function ``get_classes_mpi`` creates a dictionary of all available
FFT classes.

.. code:: ipython3

    %%px  --targets 1
    _print_dict(dict_classes)


.. parsed-literal::

      - fft3d.mpi_with_fftw1d           : <class 'fluidfft.fft3d.mpi_with_fftw1d.FFT3DMPIWithFFTW1D'>
      - fft3d.mpi_with_fftwmpi3d        : <class 'fluidfft.fft3d.mpi_with_fftwmpi3d.FFT3DMPIWithFFTWMPI3D'>
      - fft3d.mpi_with_p3dfft           : <class 'fluidfft.fft3d.mpi_with_p3dfft.FFT3DMPIWithP3DFFT'>
      - fft3d.mpi_with_pfft             : <class 'fluidfft.fft3d.mpi_with_pfft.FFT3DMPIWithPFFT'>


We now chose a small shape for the purpose of this tutorial, compatible
with FFTW requirements: say :math:`20 \times 12 \times 16`, and
instantiate FFT operators (or objects) of the above classes. Let us
compose a nifty function which takes an FFT class as the argument,
instantiates it with the shape and prints the information we seek.

.. code:: ipython3

    %%px
    def fft_info(cls):
        """Instanitate and display array shapes"""
        opfft = cls(20, 12, 16)
        printby0('get_dimX_K :'.rjust(35), opfft.get_dimX_K())
        print_sorted(
            'Global physical shape:'.rjust(35), opfft.get_shapeX_seq(),
            '\n' + 'Local physical shape :'.rjust(35),  opfft.get_shapeX_loc(),
            '\n' + 'Global FFT shape     :'.rjust(35), opfft.get_shapeK_seq(),
            '\n' + 'Local FFT shape      :'.rjust(35),  opfft.get_shapeK_loc()
        )
        del opfft

fft3d.mpi\_with\_fftw1d
-----------------------

.. code:: ipython3

    %%px
    fft_info(dict_classes['fft3d.mpi_with_fftw1d'])


.. parsed-literal::

    [stdout:0] 
                           get_dimX_K : (2, 1, 0)
    rank 0:
                 Global physical shape: (20, 12, 16) 
                 Local physical shape : (2, 12, 16) 
                 Global FFT shape     : (8, 12, 20) 
                 Local FFT shape      : (1, 12, 20)
    [stdout:1] 
    rank 1:
                 Global physical shape: (20, 12, 16) 
                 Local physical shape : (2, 12, 16) 
                 Global FFT shape     : (8, 12, 20) 
                 Local FFT shape      : (1, 12, 20)
    [stdout:2] 
    rank 2:
                 Global physical shape: (20, 12, 16) 
                 Local physical shape : (2, 12, 16) 
                 Global FFT shape     : (8, 12, 20) 
                 Local FFT shape      : (1, 12, 20)
    [stdout:3] 
    rank 3:
                 Global physical shape: (20, 12, 16) 
                 Local physical shape : (2, 12, 16) 
                 Global FFT shape     : (8, 12, 20) 
                 Local FFT shape      : (1, 12, 20)
    [stdout:4] 
    rank 4:
                 Global physical shape: (20, 12, 16) 
                 Local physical shape : (2, 12, 16) 
                 Global FFT shape     : (8, 12, 20) 
                 Local FFT shape      : (1, 12, 20)
    [stdout:5] 
    rank 5:
                 Global physical shape: (20, 12, 16) 
                 Local physical shape : (2, 12, 16) 
                 Global FFT shape     : (8, 12, 20) 
                 Local FFT shape      : (1, 12, 20)
    [stdout:6] 
    rank 6:
                 Global physical shape: (20, 12, 16) 
                 Local physical shape : (2, 12, 16) 
                 Global FFT shape     : (8, 12, 20) 
                 Local FFT shape      : (1, 12, 20)
    [stdout:7] 
    rank 7:
                 Global physical shape: (20, 12, 16) 
                 Local physical shape : (2, 12, 16) 
                 Global FFT shape     : (8, 12, 20) 
                 Local FFT shape      : (1, 12, 20)


fft3d.mpi\_with\_fftwmpi3d
--------------------------

.. code:: ipython3

    %%px
    fft_info(dict_classes['fft3d.mpi_with_fftwmpi3d'])


.. parsed-literal::

    [stdout:0] 
                           get_dimX_K : (1, 0, 2)
    rank 0:
                 Global physical shape: (20, 12, 16) 
                 Local physical shape : (3, 12, 16) 
                 Global FFT shape     : (12, 20, 9) 
                 Local FFT shape      : (2, 20, 9)
    [stdout:1] 
    rank 1:
                 Global physical shape: (20, 12, 16) 
                 Local physical shape : (3, 12, 16) 
                 Global FFT shape     : (12, 20, 9) 
                 Local FFT shape      : (2, 20, 9)
    [stdout:2] 
    rank 2:
                 Global physical shape: (20, 12, 16) 
                 Local physical shape : (3, 12, 16) 
                 Global FFT shape     : (12, 20, 9) 
                 Local FFT shape      : (2, 20, 9)
    [stdout:3] 
    rank 3:
                 Global physical shape: (20, 12, 16) 
                 Local physical shape : (3, 12, 16) 
                 Global FFT shape     : (12, 20, 9) 
                 Local FFT shape      : (2, 20, 9)
    [stdout:4] 
    rank 4:
                 Global physical shape: (20, 12, 16) 
                 Local physical shape : (3, 12, 16) 
                 Global FFT shape     : (12, 20, 9) 
                 Local FFT shape      : (2, 20, 9)
    [stdout:5] 
    rank 5:
                 Global physical shape: (20, 12, 16) 
                 Local physical shape : (3, 12, 16) 
                 Global FFT shape     : (12, 20, 9) 
                 Local FFT shape      : (2, 20, 9)
    [stdout:6] 
    rank 6:
                 Global physical shape: (20, 12, 16) 
                 Local physical shape : (2, 12, 16) 
                 Global FFT shape     : (12, 20, 9) 
                 Local FFT shape      : (0, 20, 9)
    [stdout:7] 
    rank 7:
                 Global physical shape: (20, 12, 16) 
                 Local physical shape : (0, 12, 16) 
                 Global FFT shape     : (12, 20, 9) 
                 Local FFT shape      : (0, 20, 9)


fft3d.mpi\_with\_pfft
---------------------

.. code:: ipython3

    %%px
    fft_info(dict_classes['fft3d.mpi_with_pfft'])


.. parsed-literal::

    [stdout:0] 
                           get_dimX_K : (1, 2, 0)
    rank 0:
                 Global physical shape: (20, 12, 16) 
                 Local physical shape : (10, 3, 16) 
                 Global FFT shape     : (12, 9, 20) 
                 Local FFT shape      : (6, 3, 20)
    [stdout:1] 
    rank 1:
                 Global physical shape: (20, 12, 16) 
                 Local physical shape : (10, 3, 16) 
                 Global FFT shape     : (12, 9, 20) 
                 Local FFT shape      : (6, 3, 20)
    [stdout:2] 
    rank 2:
                 Global physical shape: (20, 12, 16) 
                 Local physical shape : (10, 3, 16) 
                 Global FFT shape     : (12, 9, 20) 
                 Local FFT shape      : (6, 3, 20)
    [stdout:3] 
    rank 3:
                 Global physical shape: (20, 12, 16) 
                 Local physical shape : (10, 3, 16) 
                 Global FFT shape     : (12, 9, 20) 
                 Local FFT shape      : (6, 0, 20)
    [stdout:4] 
    rank 4:
                 Global physical shape: (20, 12, 16) 
                 Local physical shape : (10, 3, 16) 
                 Global FFT shape     : (12, 9, 20) 
                 Local FFT shape      : (6, 3, 20)
    [stdout:5] 
    rank 5:
                 Global physical shape: (20, 12, 16) 
                 Local physical shape : (10, 3, 16) 
                 Global FFT shape     : (12, 9, 20) 
                 Local FFT shape      : (6, 3, 20)
    [stdout:6] 
    rank 6:
                 Global physical shape: (20, 12, 16) 
                 Local physical shape : (10, 3, 16) 
                 Global FFT shape     : (12, 9, 20) 
                 Local FFT shape      : (6, 3, 20)
    [stdout:7] 
    rank 7:
                 Global physical shape: (20, 12, 16) 
                 Local physical shape : (10, 3, 16) 
                 Global FFT shape     : (12, 9, 20) 
                 Local FFT shape      : (6, 0, 20)


fft3d.mpi\_with\_p3dfft
-----------------------

.. code:: ipython3

    %%px
    fft_info(dict_classes['fft3d.mpi_with_p3dfft'])


.. parsed-literal::

    [stdout:0] 
                           get_dimX_K : (0, 1, 2)
    rank 0:
                 Global physical shape: (20, 12, 16) 
                 Local physical shape : (5, 6, 16) 
                 Global FFT shape     : (20, 12, 9) 
                 Local FFT shape      : (20, 3, 4)
    [stdout:1] 
    rank 1:
                 Global physical shape: (20, 12, 16) 
                 Local physical shape : (5, 6, 16) 
                 Global FFT shape     : (20, 12, 9) 
                 Local FFT shape      : (20, 3, 5)
    [stdout:2] 
    rank 2:
                 Global physical shape: (20, 12, 16) 
                 Local physical shape : (5, 6, 16) 
                 Global FFT shape     : (20, 12, 9) 
                 Local FFT shape      : (20, 3, 4)
    [stdout:3] 
    rank 3:
                 Global physical shape: (20, 12, 16) 
                 Local physical shape : (5, 6, 16) 
                 Global FFT shape     : (20, 12, 9) 
                 Local FFT shape      : (20, 3, 5)
    [stdout:4] 
    rank 4:
                 Global physical shape: (20, 12, 16) 
                 Local physical shape : (5, 6, 16) 
                 Global FFT shape     : (20, 12, 9) 
                 Local FFT shape      : (20, 3, 4)
    [stdout:5] 
    rank 5:
                 Global physical shape: (20, 12, 16) 
                 Local physical shape : (5, 6, 16) 
                 Global FFT shape     : (20, 12, 9) 
                 Local FFT shape      : (20, 3, 5)
    [stdout:6] 
    rank 6:
                 Global physical shape: (20, 12, 16) 
                 Local physical shape : (5, 6, 16) 
                 Global FFT shape     : (20, 12, 9) 
                 Local FFT shape      : (20, 3, 4)
    [stdout:7] 
    rank 7:
                 Global physical shape: (20, 12, 16) 
                 Local physical shape : (5, 6, 16) 
                 Global FFT shape     : (20, 12, 9) 
                 Local FFT shape      : (20, 3, 5)


Summary
-------

We have only looked at the default options of the FFT classes. It is
possible to transpose and customize array ordering. Different approaches
are adopted by different FFT libraries both in terms of array ordering
and distributing processes.

Note that FFTW methods distributes processes only over one index, i.e.
splits the global array into **slabs**. On the other hand P3DFFT and
PFFT distributes processes over 2 indices, i.e. splitting the global
array in 2 dimensions (also known as **pencil decomposition**). With
this method, there is a 2d process grid with shape :math:`(p_0, p_1)`
such as :math:`p = p_0 p_1` is the total number of MPI processes. In our
example, :math:`p = 8`, :math:`p_0 = 2` and :math:`p_1 = 4`.

+--------------------------------+-----------------------+-------------------------------+---------------------------+
| Method                         | FFT array order       | Physical decomposition grid   | FFT decomposition grid    |
+================================+=======================+===============================+===========================+
| ``fft3d.mpi_with_fftw1d``      | :math:`(2,\ 1,\ 0)`   | :math:`(p,\ 1,\ 1)`           | :math:`(p,\ 1,\ 1)`       |
+--------------------------------+-----------------------+-------------------------------+---------------------------+
| ``fft3d.mpi_with_fftwmpi3d``   | :math:`(1,\ 0,\ 2)`   | :math:`(p,\ 1,\ 1)`           | :math:`(p,\ 1,\ 1)`       |
+--------------------------------+-----------------------+-------------------------------+---------------------------+
| ``fft3d.mpi_with_pfft``        | :math:`(1,\ 2,\ 0)`   | :math:`(p_0,\ p_1,\ 1)`       | :math:`(p_0,\ p_1,\ 1)`   |
+--------------------------------+-----------------------+-------------------------------+---------------------------+
| ``fft3d.mpi_with_p3dfft``      | :math:`(0,\ 1,\ 2)`   | :math:`(p_1,\ p_2,\ 1)`       | :math:`(1,\ p_1,\ p_0)`   |
+--------------------------------+-----------------------+-------------------------------+---------------------------+
