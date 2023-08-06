Extending/Contributing/Fortran
==============================

There are different ways to extend jscatter by new models.
 - Write a python function.
 - Write a Fortran function (prefered >f90) with a wrapper that contains the documentation.
 - Use Cython or numba .... (for experts, not the scope here).

The simplest way is writing a python function as most functions are written like that.
The function should contain the basic model without background or other trivial contributions needed
for fitting of real data. These should be added in user defined functions as the user may be better
know how he wants to treat the background.

Contribution of a single function or a complete module dealing with a new topic are welcome.
As Users should know what it is about, the documentation is important and should contain
a scientific reference about the models.

**Contributors accept that all new modules or functions inluded will be covered by the GPLv3.**

If modules or code from other projects under OpenSource are used the respective License
and Copyright should be mentioned and respected in the source code.
Please give important contributions also in the documentation.


**Using Fortran**

`Premature optimization is the root of all evil -- DonaldKnuth <http://wiki.c2.com/?PrematureOptimization>`_

The speedup to use more sophisticated methods is not too big (not x100) if the numpy and scipy functions were used.
Here an example with a factor of about 6:

The main part of the cloudScattering function is evaluation of

.. math:: F(q)= \sum_N b_i(q) e^{iqr}

For e.g. N=20000 . We calc :math:`S(Q)=F(q) \cdot F^*(q) = |F(q)|^2` and pass :math:`F(q)`
for calculation of :math:`S(q) = < |F(q)|^2 >` and :math:`beta =|< F(q) >|^2 / < |F(q)|^2 >`
for spherical averaging.

::

    def _scattering(point,r,q,blength,formfactor):
         fa=blength*np.interp(q, formfactor[0, :], formfactor[1, :])
         qx=q*point
         iqr=np.einsum('i,ji',qx,r)*1j
         beiqrsum=np.einsum('i,i',fa,np.exp(iqr))
         Sq=beiqrsum*beiqrsum.conj()
         return q,Sq.real,beiqrsum.real

The main work is done in np.einsum and np.exp(iqr) which both are already compiled C functions
(standard numpy function). We may loose time in comming back to python between these steps.

We can reach a speedup of a factor of 6 if we use a Fortran function and use this in _scattering.
The speedup is higher if the computation was done in loops (very inefficient),
but we use numpy not to do this in loops. The speedup depends strongly on the model and how it is implemented.
Often one is happy if the python meanders.

The Fortran function/subroutine should be encapsulated in a module as it looks cleaner
and the module may contain several functions. Additional it workes smoothest in combination with f2py to use
a module of functions only (always give intent(in) properly for smooth workin).
To avoid conflicts and dependency problems it is convenient to copy all needed routines into this module.
Please respect Copyrights ::

    module cloud
        implicit none
        use typesandconstants
        use utils
    contains

    function ffq(point,r,q,blength,formfactor) result(ff)
        ! point point on unit sphere 3 x 1
        real(dp), intent(in) :: point(:)
        real(dp)             :: ff(3)
        .....see fortran/cloud.f95 for all declarations

        fa=blength*interpolatesorted(sizerms*q, formfactor(1,:), formfactor(2,:))
        qx=q*point
        iqr= j1 * matmul( r,qx)
        Fq= sum( fa* exp(iqr) )
        ff(1)=q
        ff(2)=real(Fq*conjg( Fq ) )
        ff(3)=real(Fq)

    end function ffq
    end module

A function interface and the compilation is done by f2py resulting in a shared object file
here fsca.so::

    f2py -c filename.f95 -m fsca

The module can be imported and used like any other function in a module::

    import fsca
    def scattering_f(point,r,q,blength,formfactor):
        """ A doc is needed if it should be used
        Parameters...
        Returns.....
        """
        ret=fsca.cloud.ffq(point,r,q,blength,formfactor)
        return ret

The wrapper is also needed if this function should be called by parallel (multiprocessing).
The reason is that the parallel processed function needs to be serialized and f2py functions cannot.
The wrapper can.

If multiprocessing is desired and each process needs to get large arrays
the python multiprocessing uses a lot of memory (without shared memory each process gets a pickled copy)
In this case Fortran with OpenMP is easier for multiprocessing with shared memory.

This is used in cloudScattering and tested with gfortran.
Different compiler options for OpenMP with other compilers may lead to failure.
The speedup is not very big. In a similar example as above (with individual atomic formfactors)
its about 1.5 speedup on 6 core ryzen for a very complex function. In that case the reduced memory was worth it.


**Including in jscatter clone**

To include a function in jscatter package we only need to place the working Fortran module in the
Fortran folder and reinstall jscatter.

This should be done in a clone of the repository. To use the jscatter clone use ::

 python setup.py develop --no-deps  # in the clone directory

The setup procedure compiles and builds the wrapper for all Fortran files in this folder.
The function is accessible in a jscatter module after import. ::

 from . import fscatter
 data=fscatter.cloud.ffq(q,..... )

The module can be imported were needed and the python wrapper with documentation
can be placed in the appropriate module.

If you are happy and want to contribute, sent it to the author or use a branch on gitlab.



