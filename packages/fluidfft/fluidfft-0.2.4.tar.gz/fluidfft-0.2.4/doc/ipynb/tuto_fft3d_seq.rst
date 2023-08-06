
Tutorial FFT 3D sequential
==========================

In this tutorial, we present how to use fluidfft to perform 3D fft in
sequential.

.. code:: ipython3

    import numpy as np
    from fluidfft.fft3d import methods_seq
    from fluidfft import import_fft_class

.. code:: ipython3

    print(methods_seq)


.. parsed-literal::

    ['fft3d.with_fftw3d', 'fft3d.with_pyfftw']


We import a class and instantiate it:

.. code:: ipython3

    cls = import_fft_class('fft3d.with_pyfftw')

.. code:: ipython3

    o = cls(4, 8, 12)

Let's have a look at the attribute of this objects.

.. code:: ipython3

    print('\n'.join([name for name in dir(o) if not name.startswith('__')]))


.. parsed-literal::

    arrayK
    arrayX
    build_invariant_arrayK_from_2d_indices12X
    build_invariant_arrayX_from_2d_indices12X
    coef_norm
    compute_energy_from_Fourier
    compute_energy_from_K
    compute_energy_from_X
    compute_energy_from_spatial
    create_arrayK
    create_arrayX
    empty_aligned
    fft
    fft3d
    fft_as_arg
    fftplan
    gather_Xspace
    get_dimX_K
    get_is_transposed
    get_k_adim
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
    ifft3d
    ifft_as_arg
    ifft_as_arg_destroy
    ifftplan
    inv_coef_norm
    project_fft_on_realX
    run_benchs
    run_tests
    scatter_Xspace
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

    Internal bench (FFT3DWithPYFFTW)
    time fft (FFT3DWithPYFFTW):  0.000063 s
    time ifft (FFT3DWithPYFFTW): 0.000033 s
    t_fft = 6.344318389892579e-05 s; t_ifft = 3.314018249511719e-05 s


Let's understand how the data is stored:

.. code:: ipython3

    print(o.get_dimX_K())


.. parsed-literal::

    (0, 1, 2)


which means that for this class, in Fourier space, the data is not
transposed...

Now we can get the non dimensional wavenumber in the first and second
dimensions:

.. code:: ipython3

    k0, k1, k2 = o.get_k_adim_loc()
    print('k0:', k0)
    print('k1:', k1)
    print('k2:', k2)


.. parsed-literal::

    k0: [ 0  1  2 -1]
    k1: [ 0  1  2  3  4 -3 -2 -1]
    k2: [0 1 2 3 4 5 6]


.. code:: ipython3

    print(o.get_seq_indices_first_K())


.. parsed-literal::

    (0, 0, 0)


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
