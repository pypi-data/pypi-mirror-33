Overview
========

Main screens
------------

Context editors are specialized to edit each step of experiment, see below.

.. image:: screenshots/toolbar-context.png
   :align: center
   :scale: 100%
   :alt: Contexts Menu

Sample
^^^^^^

You can open and/or create samples to run with MR experiment. Each sample
element have three characteristics: t1,t2 and density of spins.

.. image:: screenshots/screen-sample.png
   :align: center
   :scale: 70%
   :alt: Sample Screen

System
^^^^^^

Here you can set static magnetic field and add inhomogeneity to it.

.. image:: screenshots/screen-system.png
   :align: center
   :scale: 70%
   :alt: System Screen

Sequence
^^^^^^^^

You can choose a pulse sequence for your experiment, that includes the RF
and gradient pulses. The sequence is programmed in Python at this moment.

.. image:: screenshots/screen-sequence.png
   :align: center
   :scale: 70%
   :alt: Sequence Screen

Simulator
^^^^^^^^^

At this point you can set simulation mode and other details about
simulation , e.g. time resolution.

.. image:: screenshots/screen-simulator.png
   :align: center
   :scale: 70%
   :alt: Simulator Screen

Processing
^^^^^^^^^^

Finally you can process your data to plot the spectrum, imaging or
other features.

.. image:: screenshots/screen-processing.png
   :align: center
   :scale: 70%
   :alt: Processing Screen

2D Editor
---------

This editor provides a table that represents the current selected
slice of the 3D view. In this table you can edit the values of each
element property(ies). Colors also help you to pre visualize the intensity
of chosen value.

3D View
-------

3D view is used to show contexts objects such as sample, magnet field
inhomogeneity, and the evolution of magnetization. You can move the cam
to adjust the perspective.

Data
----

Data can be saved using HDF5 files. For each context we adopted an
extension to distinguish from each other. HDF5 files can be easily
modified with other external tool if necessary.
