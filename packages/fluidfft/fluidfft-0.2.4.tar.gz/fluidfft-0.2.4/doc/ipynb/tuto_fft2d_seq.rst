
Tutorial FFT 2D sequential
==========================

In this tutorial, we present how to use fluidfft to perform 2d Fast
Fourier Transform in sequential. You will see that it is really very
simple.

If you really want performance, first benchmark the different methods for an array shape representative of what you will use and in the machine where the computations will be done. We explain how to do this in the page :ref:`bench`.

.. code:: ipython3

    import numpy as np
    from fluidfft.fft2d import methods_seq
    from fluidfft import import_fft_class

.. code:: ipython3

    print(methods_seq)


.. parsed-literal::

    ['fft2d.with_fftw1d', 'fft2d.with_fftw2d', 'fft2d.with_cufft', 'fft2d.with_pyfftw']


We import a class and instantiate it:

.. code:: ipython3

    cls = import_fft_class('fft2d.with_pyfftw')

.. code:: ipython3

    o = cls(16, 48)

Let's have a look at the attribute of this objects. They are actually
all methods:

.. code:: ipython3

    print('\n'.join([name for name in dir(o) if not name.startswith('__')]))


.. parsed-literal::

    arrayK
    arrayX
    coef_norm
    compute_energy_from_Fourier
    compute_energy_from_K
    compute_energy_from_X
    compute_energy_from_spatial
    create_arrayK
    create_arrayX
    empty_aligned
    fft
    fft2d
    fft_as_arg
    fftplan
    get_is_transposed
    get_k_adim_loc
    get_local_size_X
    get_seq_indices_first_K
    get_seq_indices_first_X
    get_shapeK_loc
    get_shapeK_seq
    get_shapeX_loc
    get_shapeX_seq
    get_short_name
    get_x_adim_loc
    ifft
    ifft2d
    ifft_as_arg
    ifft_as_arg_destroy
    ifftplan
    inv_coef_norm
    project_fft_on_realX
    run_benchs
    run_tests
    shapeK
    shapeX
    sum_wavenumbers


Let's run a test and benchmark the fft and ifft functions directly from
C++.

.. code:: ipython3

    print(o.run_tests())


.. parsed-literal::

    None


.. code:: ipython3

    t1, t2 = o.run_benchs()
    print('t_fft = {} s; t_ifft = {} s'.format(t1, t2))


.. parsed-literal::

    Internal bench (FFT2DWithPYFFTW)
    time fft (FFT2DWithPYFFTW):  0.000028 s
    time ifft (FFT2DWithPYFFTW): 0.000013 s
    t_fft = 2.7799606323242186e-05 s; t_ifft = 1.3494491577148438e-05 s


Let's understand how the data is stored:

.. code:: ipython3

    print(o.get_is_transposed())


.. parsed-literal::

    False


which means that for this class, in Fourier space, the data is not
transposed...

Now we can get the non dimensional wavenumber in the first and second
dimensions:

.. code:: ipython3

    k0, k1 = o.get_k_adim_loc()
    print('k0:', k0)
    print('k1:', k1)


.. parsed-literal::

    k0: [ 0  1  2  3  4  5  6  7  8 -7 -6 -5 -4 -3 -2 -1]
    k1: [ 0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24]


and check that the shapes of the array in one process are the same than
in sequential (we are in sequential, there is only one process):

.. code:: ipython3

    assert o.get_shapeX_loc() == o.get_shapeX_seq()
    assert o.get_shapeK_loc() == o.get_shapeK_seq()

Now, let's compute fast Fourier transforms. We first initialize arrays:

.. code:: ipython3

    a = np.ones(o.get_shapeX_loc())
    a_fft = np.empty(o.get_shapeK_loc(), dtype=np.complex128)

If we do not have the array where to put the result we can do:

.. code:: ipython3

    a_fft = o.fft(a)

If we already have the array where to put the result we can do:

.. code:: ipython3

    o.fft_as_arg(a, a_fft)

And finally for the inverse Fourier transform:

.. code:: ipython3

    a = o.ifft(a_fft)

.. code:: ipython3

    o.ifft_as_arg(a_fft, a)

Let's mention the existence of the method ``ifft_as_arg_destroy``, which
can be slightly faster than ``ifft_as_arg`` because it avoids one copy.

.. code:: ipython3

    o.ifft_as_arg_destroy(a_fft, a)
