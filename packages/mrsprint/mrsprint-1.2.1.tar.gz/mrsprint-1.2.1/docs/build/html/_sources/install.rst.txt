Install
=======

If you are looking for binaries, please refer to Downloads section.

Installing from PyPI - stable, end-user
---------------------------------------

Simple run

``$ pip install mrsprint``

This will install all necessary dependencies then the code.

Installing from code - up to date, developers
---------------------------------------------

Clone from GitLab the `latest code <http://gitlab.com/dpizetta/mrsimulator>`_.
Enter into the folder containing ``setup.py`` file.

``$ cd mrsprint``

Run the install command using developer mode option (\ ``-e``\ )

``$ pip install -e .``

This command will install all necessary dependencies and the code will be
installed in the same place it is, so it is easy to update doing ``git pull``.

Dependencies
------------

* NumPy: Numerical mathematical library;
* SciPy: Scientific library;
* NMRGlue: NMR processing library;
* PyQtGraph: Data visualization library;
* PyQt/Pyside: Graphical framework.

Problems on Windows
-------------------

Windows users may have some problem with some C necessary extensions. We
recommend to visit `Windows Compilers <https://wiki.python.org/moin/WindowsCompilers>`_\ ,
but the first trial should be installing `Visual Studio Build Tools <http://landinghub.visualstudio.com/visual-cpp-build-tools>`_. Sometimes this
is necessary even though using distributions like Anaconda. This include
solutions for vcvarshall.bat missing.