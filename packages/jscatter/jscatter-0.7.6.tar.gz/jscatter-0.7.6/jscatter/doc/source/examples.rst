.. _label_Examples:

Examples
========

.. automodule:: jscatter.examples
    :noindex:

.. autosummary::
    showExampleList
    showExample
    runExample
    runAll


Image quality is for HTML. Fileformats can jpg, png eps,pdf.... in high resolution in publication quality.
For publication use .eps or .pdf with image width 8.6 cm and 600 dpi (see .save of a plot).

Examples are mainly based on XmGrace for ploting. Change plot commands for other plot tools.
        
In a hurry and short 
--------------------
Daily use example to show how short it can be.

Comments are shown in next examples.

.. literalinclude:: ../../examples/example_daily_use.py
    :language: python
.. image:: ../../examples/DiffusionFit_ErrPlot.jpg
    :align: left
    :height: 300px
    :alt: Picture about diffusion fit with residuals
.. image:: ../../examples/DiffusionFit.jpg
    :align: center
    :height: 300px
    :alt: Picture about diffusion fit
.. image:: ../../examples/effectiveDiffusion.jpg 
    :align: center
    :height: 300px
    :alt: diffusion fit result

How to build simple models
----------------------------
.. literalinclude:: ../../examples/example_buildsimpleModels.py
    :language: python

How to build a more complex model
---------------------------------
.. literalinclude:: ../../examples/example_buildComplexModel.py
    :language: python
.. image:: ../../examples/interactingParticles.jpeg
    :align: center
    :height: 300px
    :alt: Image of interacting particles scattering

Some Sinusoidial fits with different kinds to use data atrributes
------------------------------------------------------------------
.. literalinclude:: ../../examples/example_SinusodialFitting.py
    :language: python
.. image:: ../../examples/SinusoidialFit.png
    :align: left
    :height: 300px
    :alt: SinusoidialFit
.. image:: ../../examples/Sinusoidial3D.png
    :align: center
    :height: 300px
    :alt: Sinusoidial3D


Simple diffusion fit of not so simple diffusion case
----------------------------------------------------
Here the long part with description from first example.

This is the diffusion of a protein in solution.
This is NOT constant as for Einstein diffusion.

These simulated data are similar to data measured by Neutron Spinecho Spectroscopy, which measures on the length scale
of the protein and therefore also rotational diffusion contributes to the signal.
At low wavevectors additional the influence of the structure factor leads to an upturn,
which is neglected in the simulated data. To include look at later Hydrodynamic function.

.. literalinclude:: ../../examples/example_simple_diffusion.py
    :language: python
    :lines: 1-42
.. image:: ../../examples/DiffusionFit.jpg
    :align: center
    :height: 300px
    :alt: Picture about diffusion fit

.. literalinclude:: ../../examples/example_simple_diffusion.py
    :language: python
    :lines: 45-
.. image:: ../../examples/effectiveDiffusion.jpg 
    :align: center
    :height: 300px
    :alt: diffusion fit result


How to smooth Xray data and make an inset in the plot
-----------------------------------------------------

.. literalinclude:: ../../examples/example_smooth_xraydata.py
    :language: python
.. image:: ../../examples/smoothedXraydata.jpg
    :align: center
    :height: 300px
    :alt: Picture about diffusion fit

How to fit SANS data including the resolution for different detector distances
------------------------------------------------------------------------------
First this example shows the influence of smearing, then how to do a fit including
 smearing a la Pedersen in 2 versions.

.. literalinclude:: ../../examples/example_SANSsmearing.py
    :language: python
.. image:: ../../examples/SANSsmearing.jpg
    :align: center
    :height: 300px
    :alt: Picture about SANS smearing

Smearing and desmearing of SAX and SANS data
------------------------------------------------------------
.. literalinclude:: ../../examples/example_SASdesmearing.py
    :language: python
.. image:: ../../examples/SASdesmearing.png
    :align: center
    :height: 300px
    :alt: Picture about smearing/desmearing


A long example for diffusion and how to analyze step by step
------------------------------------------------------------
This is a long example to show possibilities.

A main feature of the fit is that we can change from a constant fit parameters to a parameter
dependent one by simply changing A to [A].


.. literalinclude:: ../../examples/example_fit_diffusion.py
    :language: python

Sedimentation of two particle sizes and resulting scattering: a Simulation
--------------------------------------------------------------------------
.. literalinclude:: ../../examples/example_Sedimentation.py
    :language: python
    :lines: 1-32
.. image:: ../../examples/Sedimentation.jpg
    :align: center
    :height: 300px
    :alt: Picture about diffusion fit

.. literalinclude:: ../../examples/example_Sedimentation.py
    :language: python
    :lines: 33-
.. image:: ../../examples/bimodalScattering.jpg
    :align: center
    :height: 300px

Create a stacked chart of some curves
-------------------------------------
.. literalinclude:: ../../examples/example_grace_stackeddata.py
    :language: python
    :lines: 1-32
.. image:: ../../examples/stackedGaussians.jpeg
    :align: center
    :height: 300px
    :alt: Picture about diffusion fit

A comparison of different dynamic models in frequency domain
------------------------------------------------------------
.. literalinclude:: ../../examples/example_dynamics.py
    :language: python
    :lines: 1-63
.. image:: ../../examples/DynamicModels.png
    :align: center
    :height: 300px
    :alt: Picture about diffusion fit

Protein incoherent scattering in frequency domain
------------------------------------------------------------
.. literalinclude:: ../../examples/example_inelasticNeutronScattering.py
    :language: python
    :lines: 1-155
.. image:: ../../examples/inelasticNeutronScattering.png
    :align: center
    :height: 300px
    :alt: Picture about diffusion fit
.. image:: ../../examples/Ribonuclease_inelasticNeutronScattering.png
    :align: center
    :height: 300px
    :alt: Picture about diffusion fit

Fitting a multiShellcylinder in various ways
------------------------------------------------------------
.. literalinclude:: ../../examples/example_fit_multicylinder.py
    :language: python
    :lines: 1-73

Hydrodynamic function
------------------------------------------------------------
.. literalinclude:: ../../examples/example_HydrodynamicFunction.py
    :language: python
    :lines: 1-42
.. image:: ../../examples/HydrodynamicFunction.png
    :align: center
    :height: 300px
    :alt: Picture HydrodynamicFunction

Multilamellar Vesicles
----------------------
.. literalinclude:: ../../examples/example_multilamellarVesicle.py
    :language: python
    :lines: 1-180
.. image:: ../../examples/multilamellar1.png
    :align: center
    :height: 300px
    :alt: Picture multilamellar1
.. image:: ../../examples/multilamellar2.png
    :align: center
    :height: 300px
    :alt: Picture multilamellar2
.. image:: ../../examples/multilamellar3.png
    :align: center
    :height: 300px
    :alt: Picture multilamellar3
.. image:: ../../examples/multilamellar5.png
    :align: center
    :height: 300px
    :alt: Picture multilamellar5

2D oriented scattering
-----------------------

**Formfactors of oriented particles or particle complexes**

.. literalinclude:: ../../examples/example_2D_orientedScattering.py
    :language: python
    :lines: 1-109
.. image:: ../../examples/2D_5coreshell.png
    :align: left
    :height: 300px
    :alt: 2D scattering coreshell
.. image:: ../../examples/2D_5spheres.png
    :align: center
    :height: 300px
    :alt: 2D scattering

**Oriented crystal structure factors in 2D**

.. literalinclude:: ../../examples/example_2D_structurefactors.py
    :language: python
    :lines: 5-
.. image:: ../../examples/smallCubeAsymetric.png
    :align: center
    :height: 300px
    :alt: 2D scattering coreshell
.. image:: ../../examples/smallCube10degreeRotation.png
    :align: center
    :height: 300px
    :alt: 2D scattering



A nano cube build of different lattices
---------------------------------------
.. include:: ../../examples/example_comparisonLattices.py
    :start-after: """
    :end-before:  END

.. literalinclude:: ../../examples/example_comparisonLattices.py
    :language: python
    :lines: 23-69
.. image:: ../../examples/LatticeComparison.png
    :align: center
    :height: 300px
    :alt: LatticeComparison

.. include:: ../../examples/example_comparisonLattices.py
    :start-after: #start2
    :end-before:  #end2
.. literalinclude:: ../../examples/example_comparisonLattices.py
    :language: python
    :lines: 83-113
.. image:: ../../examples/LatticeComparison2.png
    :align: center
    :height: 300px
    :alt: LatticeComparison2


.. include:: ../../examples/example_comparisonLattices.py
    :start-after: #start3
    :end-before:  #end3
.. literalinclude:: ../../examples/example_comparisonLattices.py
    :language: python
    :lines: 128-
.. image:: ../../examples/LatticeComparison3.png
    :align: center
    :height: 300px
    :alt: LatticeComparison3

Using cloudscattering as fit model
----------------------------------
At the end a complex shaped object: A cube decorated with spheres of different scattering length.


.. literalinclude:: ../../examples/example_cloudscattering.py
    :lines: 1-
.. image:: ../../examples/cubeWithSpheres.png
    :align: center
    :height: 300px
    :alt: cubeWithSpheres


.. automodule:: jscatter.examples
    :members:
