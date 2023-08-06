
.. image:: screenshots/MRSprintLogo.png
   :align: center
   :scale: 100%
   :alt: MRSPRINT

|pypi-version| |docs-status|


Welcome!
========

**Magnetic resonance experiment simulator and visualization tool**

MRSPRINT is a visual magnetic resonance simulator where you can simulate
a magnetic resonance experiment - spectroscopy or imaging. Its main goal is
to be an education tool that assists the student/staff to understand,
interpret and explore magnetic resonance phenomena.

This tool is totally free (see license), but if you are making use of it,
you need to cite us using both citations. This is very important for us.

* Article: Coming soon!
* Software: Coming soon!

If you are using this piece of software to generate images, gif's, movies,
etc., or using images available on this site, please, also reference us
using those citations.


What can you see?
-----------------

* Precession: spins precessing in static magnetic field;
* Resonance: resonance when a RF pulse is applied;
* Contrast: T1, T2, and density of spins;
* Field inhomogeneity: isochromates can be shown with their dispersion;
* Gradient: magnetic field gradient in action, its intensity and effect over the frequency;
* Evolution: over magnetization with intensity, frequency and phase and the pulse sequence;
* FID: free induction decay, the signal;
* Echo: spin or gradient echo (rephasing/dephasing).


Future planned features
-----------------------

* K-space visualization;
* Multi-nuclei samples/experiments;
* T2* as sample parameter to easily setup field inhomogeneity;
* Graphical sequence editor;
* Chemical interactions;
* View on coordinate laboratory system;
* Flow (spins not fixed in positions).


Documentation
-------------

`Go to documentation on ReadTheDocs! <https://mrsprint.readthedocs.io/en/latest/>`_
It is available on Read The Docs in HTML, EPUB, and PDF.


Download binaries - click-and-run
---------------------------------
Binaries are for those do not wish to install any Python things.
We recommend them to the ones without any programming experience.
Download from links below.

* Portable Windows Binaries: coming soon!
* Portable Linux Binaries: coming soon!
* Portable Mac Binaries: coming soon!

Sou you can just download, decompress, click-and-run.


Installing from PyPI - stable, end-user
---------------------------------------

To install, do

``$ pip install mrsprint``

This will install all necessary dependencies then the code.

To run from terminal

``$ mrsprint``


Dependencies
------------

* NumPy: Numerical mathematical library;
* SciPy: Scientific library;
* NMRGlue: NMR processing library;
* H5Py: Storing and managing data files;
* PyQtGraph: Data visualization library;
* PyQt/Pyside: Graphical framework.

Dependencies are automatically installed when using the method above.


.. |pypi-version| image:: https://img.shields.io/pypi/v/mrsprint.svg
    :alt: PyPI Version
    :scale: 100%
    :target: https://pypi.python.org/pypi/mrsprint

.. |build-status| image:: https://img.shields.io/travis/rtfd/readthedocs.org.svg?style=flat
    :alt: Build Status
    :scale: 100%
    :target: https://travis-ci.org/rtfd/readthedocs.org

.. |docs-status| image:: https://readthedocs.org/projects/mrsprint/badge/?version=latest
    :target: https://mrsprint.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. |mit-license| image:: https://img.shields.io/badge/License-MIT-blue.svg
    :alt: MIT License
    :scale: 100%
    :target: https://lbesson.mit-license.org/

.. |cc-license| image:: image:: https://img.shields.io/badge/License-CC--0-blue.svg
    :alt: MIT License
    :scale: 100%
    :target: https://creativecommons.org/licenses/by-nd/4.0

.. |doi-zenodo| image:: https://zenodo.org/badge/DOI/10.1007/978-3-319-76207-4_15.svg
    :alt: DOI Zenodo
    :scale: 100%
    :target: https://doi.org/10.1007/978-3-319-76207-4_15