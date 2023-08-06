.. This file is part of Sympathy for Data.
..
..  Copyright (c) 2017 System Engineering Software Society
..
..     Sympathy for Data is free software: you can redistribute it and/or modify
..     it under the terms of the GNU General Public License as published by
..     the Free Software Foundation, either version 3 of the License, or
..     (at your option) any later version.
..
..     Sympathy for Data is distributed in the hope that it will be useful,
..     but WITHOUT ANY WARRANTY; without even the implied warranty of
..     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
..     GNU General Public License for more details.
..     You should have received a copy of the GNU General Public License
..     along with Sympathy for Data. If not, see <http://www.gnu.org/licenses/>.

Installation instructions
=========================

For Windows
-----------
Download the latest version of Sympathy from the `official
homepage <https://www.sympathyfordata.com/>`_. If you are using any
custom node libraries then make sure to select the same Python version
(Python 2 or Python 3) as the libraries have been written for.

After downloading, run the installer and follow the
instructions. This will install Sympathy as well as a custom
Python version with all dependencies for it.


For Mac OS
----------

These instructions are written for MacOS X 10.13.3, using MacPorts.

Start by installing Xcode from the App Store (that will download an XCode
installer, so this is a two-stage process).

.. code-block:: bash

   sudo xcode-select --install
   sudo xcodebuild -license


You can install Sympathy either for Python 3 (recommended) or
Python 2.7. The common installation steps are needed for both cases.

Installing Python 3 environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Download and install `MacPorts <http://www.macports.org>`__.
Before continuing, it is recommended to run

.. code-block:: bash

   sudo port selfupdate

Then install the dependencies

.. code-block:: bash

   sudo port install python36 unixODBC

Since modern MacPorts has a later version of Python 3 (3.5 or later) not directly
supported by PySide (and it therefore cannot be built like it can for Python 2),
you will have to get a wheel. See :ref:`whl_pyside` for information about how
to download or build your own. Make sure to choose a wheel built for the
matching minor version of Python in your system (3.5 or 3.6), which you can find
out with

.. code-block:: bash

   python3 --version

Now, navigate to a directory in which you want to create the virtual
environment, and use the following commands (adjust the PySide wheel
filename as necessary):

.. code-block:: bash

   python3 -m venv env-sympathy
   source env-sympathy/bin/activate
   pip install -U pip setuptools wheel
   pip install PySide-1.2.4-cp36-cp36m-macosx_10_13_x86_64.whl


Installing Python 2 environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Download and install `MacPorts <http://www.macports.org>`__.
Before continuing, it is recommended to run

.. code-block:: bash

   sudo port selfupdate

Then install the dependencies

.. code-block:: bash

   sudo port install python27 py27-virtualenv unixODBC

With Python 2, you can optionally also install a pre-built wheel of PySide, see
:ref:`whl_pyside`; if you don’t do that, you’ll also need to install
``qt4-mac``, ``pkgconfig`` and ``cmake`` with port, and the installation will
build a fresh version of PySide – a process which takes about 20 minutes.

Now, navigate to a directory in which you want to create the virtual
environment, and use the following commands (adjust the PySide wheel
filename as necessary):

.. code-block:: bash

   virtualenv-2.7 --python=python2.7 env-sympathy
   source env-sympathy/bin/activate
   pip install PySide-1.2.4-cp27-cp27m-macosx_10_13_x86_64.whl  # optional


.. _whl_install_macos:

Install Sympathy wheel
~~~~~~~~~~~~~~~~~~~~~~

We can download the Sympathy python wheel file from the `official homepage
<https://www.sympathyfordata.com/>`_.  Assuming that you have downloaded it as
the file *Sympathy-<VERSION>-py2.py3-none-any.whl* you can install it by running
the following commands *from the folder where you downloaded it*:

.. code-block:: bash

    pip install Sympathy-<VERSION>-py2.py3-none-any.whl
    python -m sympathy_app install

For other Mac OS versions than 10.13.3: if you see any text in
red during the execution of above command, this would typically mean that
some library is missing in your system. Read the error message, and
install the required library, including the associated development
headers, before trying again. For example, if you get an error while
installing pyodbc, that typically means you need to install a package
named unixODBC.

Now we are ready to run Sympathy! See :ref:`whl_run_unix`.


For Linux
---------
These installation instructions have been written for Ubuntu 16.04
which is the only officially supported Linux distribution for Sympathy
for Data. Nonetheless, these instructions should also serve as a
starting point for later versions of Ubuntu or other Linux
distributions.

Before you start either installation, make sure that your computer is
internet connected and has the latest version of all packages. If
unsure, run the commands:

.. code-block:: bash

   sudo apt-get update
   sudo apt-get dist-upgrade

You can install Sympathy either for Python 3 (recommended) or Python 2.7.
The common installation steps are needed for both cases. We recommend
installing Sympathy into a virtual Python environment. It is also possible
to install it system-wide with ``sudo pip install``, but keep in mind that
there's a chance that some of the Python packages that get installed this
way will conflict with other packages installed with apt.


Installing Python 3 environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Start by installing the required prerequisites

.. code-block:: bash

   sudo apt-get install build-essential python3-dev python3-venv unixodbc-dev

Since modern Ubuntu has a later version of Python 3 (3.5 or later) not directly
supported by PySide (and it therefore cannot be built like it can for Python 2),
you will have to get a wheel. See :ref:`whl_pyside` for information about how
to download or build your own. Make sure to choose a wheel built for the
matching minor version of Python in your system (3.5 or 3.6), which you can find
out with

.. code-block:: bash

   python3 --version

Now, navigate to a directory in which you want to create the virtual
environment, and use the following commands (adjust the PySide wheel
filename as necessary):

.. code-block:: bash

   python3 -m venv env-sympathy
   source env-sympathy/bin/activate
   pip install -U pip setuptools wheel
   pip install PySide-1.2.4-cp35-cp35m-linux_x86_64.whl


Installing Python 2 environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Start by installing the required prerequisites

.. code-block:: bash

   sudo apt-get install build-essential python3-dev python3-venv unixodbc-dev

With Python 2, you can optionally also install a pre-built wheel of PySide, see
:ref:`whl_pyside`; if you don't do that, you'll also need to install ``cmake``
and ``qt4-default`` with ``apt-get``, and the installation will build a fresh
version of PySide -- a process which takes about 20 minutes.

Now, navigate to a directory in which you want to create the virtual
environment, and use the following commands (adjust the PySide wheel
filename as necessary):

.. code-block:: bash

   virtualenv --python=python2.7 env-sympathy
   source env-sympathy/bin/activate
   pip install PySide-1.2.4-cp27-cp27mu-linux_x86_64.whl  # optional


.. _whl_install_linux:

Install Sympathy wheel
~~~~~~~~~~~~~~~~~~~~~~

We can download the Sympathy python wheel file from the `official homepage
<https://www.sympathyfordata.com/>`_.  Assuming that you have downloaded it as
the file *Sympathy-<VERSION>-py2.py3-none-any.whl* you can install it by running
the following commands *from the folder where you downloaded it*:

.. code-block:: bash

    pip install Sympathy-<VERSION>-py2.py3-none-any.whl
    python -m sympathy_app install

For other Linux distributions than Ubuntu 16.04: if you see any text in
red during the execution of above command, this would typically mean that
some library is missing in your system. Read the error message, and
install the required library, including the associated development
headers, before trying again. For example, if you get an error while
installing pyodbc, that typically means you need to install a package
named unixodbc-dev, or unixODBC-devel (the names tend to vary across Linux
distributions).

Now we are ready to run Sympathy! See :ref:`whl_run_unix`.


.. _whl_run_unix:

Running Sympathy on Linux and MacOS
-----------------------------------

In order to run Sympathy using python, first make sure that the virtual
environment used in the installation steps is active. You can run Sympathy
either with a GUI (first command below), or for data processing applications in
head-less mode (second command). The third command provides access to various
top level commands, such as *tests* for running the accompanying test suite,
see :ref:`launch_options` for more info.

.. code-block:: bash

  python -m sympathy_app gui
  python -m sympathy_app cli <my workflow>
  python -m sympathy_app

Installing the wheel also creates additional executables for your virtual
environment. These are typically located in folder called Scripts, on Windows,
and bin, on Unix. These run sympathy in the same way as above but does not
require the virtual environment to be activated beforehand.

.. code-block:: bash

  sympathy-gui
  sympathy-cli <my workflow>
  sympathy


.. _whl_pyside:

Patched PySide wheels
---------------------

Pre built wheels
~~~~~~~~~~~~~~~~

Ubuntu:

    Python 3.6:

        - `PySide-1.2.4-cp36-cp36m-linux_x86_64.whl <https://www.sympathyfordata.com/download/PySide-1.2.4-cp36-cp36m-linux_x86_64.whl>`_

    Python 3.5:

        - `PySide-1.2.4-cp35-cp35m-linux_x86_64.whl <https://www.sympathyfordata.com/download/PySide-1.2.4-cp35-cp35m-linux_x86_64.whl>`_

    Python 2.7:

        - `PySide-1.2.4-cp27-cp27mu-linux_x86_64.whl <https://www.sympathyfordata.com/download/PySide-1.2.4-cp27-cp27mu-linux_x86_64.whl>`_

Mac OS:

    Python 3.6:

        - `PySide-1.2.4-cp36-cp36m-macosx_10_13_x86_64.whl <https://www.sympathyfordata.com/download/PySide-1.2.4-cp36-cp36m-macosx_10_13_x86_64.whl>`_

    Python 2.7:

        - `PySide-1.2.4-cp27-cp27m-macosx_10_13_x86_64.whl <https://www.sympathyfordata.com/download/PySide-1.2.4-cp27-cp27m-macosx_10_13_x86_64.whl>`_

Build your own
~~~~~~~~~~~~~~

If for some reason, you cannot or do not want to use the pre-built wheels;
you can build one on your own, a process which takes about 20 minutes.

Mac OS:

    Python 3.6, 3.5:

    .. code-block:: bash

        sudo port install qt4-mac, pkgconfig, cmake, curl
        source <path-to-env-sympathy>/bin/activate
        pip download pyside
        tar xf PySide-1.2.4.tar.gz
        curl -O https://www.sympathyfordata.com/download/PySide-1.2.4.patch
        patch -p1 < PySide-1.2.4.patch
        cd PySide-1.2.4
        python setup.py bdist_wheel --qmake /opt/local/libexec/qt4/bin/qmake

    Python 2.7:

    .. code-block:: bash

        sudo port install qt4-mac, pkgconfig, cmake, curl
        source <path-to-env-sympathy>/bin/activate
        pip download pyside
        tar xf PySide-1.2.4.tar.gz
        cd PySide-1.2.4
        python setup.py bdist_wheel --qmake /opt/local/libexec/qt4/bin/qmake

Finally, after the command finishes,
*dist/PySide-1.2.4-<specific-build-version>.whl* is created and is ready to be
installed. See the appropriate section for setting up the environment.

Linux:

    Should build following the same steps as used for Mac OS, except for
    the qmake argument to setup.py -- change the path to point to where qmake
    is installed or remove it entirely to rely on automatic detection.
