
Tutorial FFT 2D parallel (MPI): Domain decomposition
====================================================

We have seen that FluidFFT provides a unified framework for different
implementations of parallelized FFT 2D libraries using FFTW (with MPI).

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
``ipcluster start -n 4 --engines=MPIEngineSetLauncher``.

.. code:: ipython3

    import ipyparallel as ipp
    rc = ipp.Client()
    dview = rc[:]

We start by importing all the functions that we need

.. code:: ipython3

    %%px
    from fluiddyn.util.info import _print_dict
    from fluidfft.fft2d import get_classes_mpi
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

      - fft2d.mpi_with_fftwmpi2d        : <class 'fluidfft.fft2d.mpi_with_fftwmpi2d.FFT2DMPIWithFFTWMPI2D'>
      - fft2d.mpi_with_fftw1d           : <class 'fluidfft.fft2d.mpi_with_fftw1d.FFT2DMPIWithFFTW1D'>


We now chose a small shape for the purpose of this tutorial, compatible
with FFTW requirements: say :math:`12 \times 8`, and instantiate FFT
operators (or objects) of the above classes. Let us compose a nifty
function which takes an FFT class as the argument, instantiates it with
the shape and prints the information we seek.

.. code:: ipython3

    %%px
    def fft_info(cls):
        """Instanitate and display array shapes"""
        opfft = cls(12, 8)
        print_sorted(
            'Global physical shape:'.rjust(35), opfft.get_shapeX_seq(),
            '\n' + 'Local physical shape :'.rjust(35),  opfft.get_shapeX_loc(),
            '\n' + 'Global FFT shape     :'.rjust(35), opfft.get_shapeK_seq(),
            '\n' + 'Local FFT shape      :'.rjust(35),  opfft.get_shapeK_loc()
        )
        
        del opfft

fft2d.mpi\_with\_fftw1d
-----------------------

.. code:: ipython3

    %%px
    fft_info(dict_classes['fft2d.mpi_with_fftw1d'])


.. parsed-literal::

    [stdout:0] 
    rank 0:
                 Global physical shape: (12, 8) 
                 Local physical shape : (3, 8) 
                 Global FFT shape     : (4, 12) 
                 Local FFT shape      : (1, 12)
    [stdout:1] 
    rank 1:
                 Global physical shape: (12, 8) 
                 Local physical shape : (3, 8) 
                 Global FFT shape     : (4, 12) 
                 Local FFT shape      : (1, 12)
    [stdout:2] 
    rank 2:
                 Global physical shape: (12, 8) 
                 Local physical shape : (3, 8) 
                 Global FFT shape     : (4, 12) 
                 Local FFT shape      : (1, 12)
    [stdout:3] 
    rank 3:
                 Global physical shape: (12, 8) 
                 Local physical shape : (3, 8) 
                 Global FFT shape     : (4, 12) 
                 Local FFT shape      : (1, 12)


fft2d.mpi\_with\_fftwmpi2d
--------------------------

.. code:: ipython3

    %%px
    fft_info(dict_classes['fft2d.mpi_with_fftwmpi2d'])


.. parsed-literal::

    [stdout:0] 
    rank 0:
                 Global physical shape: (12, 8) 
                 Local physical shape : (3, 8) 
                 Global FFT shape     : (5, 12) 
                 Local FFT shape      : (2, 12)
    [stdout:1] 
    rank 1:
                 Global physical shape: (12, 8) 
                 Local physical shape : (3, 8) 
                 Global FFT shape     : (5, 12) 
                 Local FFT shape      : (2, 12)
    [stdout:2] 
    rank 2:
                 Global physical shape: (12, 8) 
                 Local physical shape : (3, 8) 
                 Global FFT shape     : (5, 12) 
                 Local FFT shape      : (1, 12)
    [stdout:3] 
    rank 3:
                 Global physical shape: (12, 8) 
                 Local physical shape : (3, 8) 
                 Global FFT shape     : (5, 12) 
                 Local FFT shape      : (0, 12)


Summary
-------

We have only looked at the default options of the FFT classes. It is
possible to transpose and customize array ordering. Different approaches
are adopted by different FFT libraries both in terms of array ordering
and and distributing processes.

For a physical array ordered like :math:`(n_0,\ n_1)` and with :math:`p`
MPI processes:

+--------------------------------+-------------------+-------------------------------+--------------------------+
| Method                         | FFT array order   | Physical array process grid   | FFT array process grid   |
+================================+===================+===============================+==========================+
| ``fft2d.mpi_with_fftw1d``      | :math:`(1, 0)`    | :math:`(p, 1)`                | :math:`(p, 1)`           |
+--------------------------------+-------------------+-------------------------------+--------------------------+
| ``fft2d.mpi_with_fftwmpi2d``   | :math:`(1, 0)`    | :math:`(p, 1)`                | :math:`(p, 1)`           |
+--------------------------------+-------------------+-------------------------------+--------------------------+

It is also interesting to note that FFTW takes advantage of the fact
that FFT arrays of real physical arrays are hermitian. Therefore only
stores half the size of the array. Due to this :math:`k_1` is exactly
:math:`\frac{n_1}{2}` with ``fft2d.mpi_with_fftw1d`` and is
:math:`(\frac{n_1}{2} + 1)` with ``fft2d.mpi_with_fftwmpi2d``.

We observe that FFTW methods distributes processes only over one index,
i.e. splits the global array into **slabs** or **pencils** (equivalent
in 2D, but different in 3D, as we will see later).
