dev-pipeline-cmake
==================
|codacy|
|code-climate|

A CMake_ plugin for `dev-pipeline`_


Installation
------------
The simplest way to install is using pip_.

.. code:: bash

    $ cd /path/to/dev-pipeline-cmake
    $ pip3 install

If you don't have pip available, you can run :code:`setup.py` directly.

.. code:: bash

    $ cd /path/to/dev-pipeline-cmake
    $ python3 setup.py install

You'll need cmake installed.  Doing that is beyond the scope of this document,
but it should be available for pretty much every operating system.


Using
-----
You can use :code:`cmake` as an option for :code:`build` in a
:code:`build.config`.  Information about options you can set are in the
documentation_.


.. |codacy| image:: https://api.codacy.com/project/badge/Grade/de9145db420e4d83a84f3eef8da5b769
    :target: https://www.codacy.com/app/snewell/dev-pipeline-cmake?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=dev-pipeline/dev-pipeline-cmake&amp;utm_campaign=Badge_Grade

.. |code-climate| image:: https://api.codeclimate.com/v1/badges/5dbb268d5b1d1b269b1d/maintainability
   :target: https://codeclimate.com/github/dev-pipeline/dev-pipeline-cmake/maintainability
   :alt: Maintainability


.. _CMake: https://cmake.org
.. _dev-pipeline: https://github.com/dev-pipeline/dev-pipeline
.. _documentation: docs/builder-cmake.rst
.. _pip: https://pypi.python.org/pypi/pip


