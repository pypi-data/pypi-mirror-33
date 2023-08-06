=======================================
admobilizeapis python package generator
=======================================

Repo contains python package generator for `admobilizeapis <https://bitbucket.org/admobilize/admobilizeapis>`_ proto interface.

Building the python package
---------------------------

Make sure you install `pipenv <https://github.com/pypa/pipenv>`_ and the dependencies contained in the ``Pipfile``.

.. code-block::

  # Install dependencies via pipenv
  $ pipenv install
  $ ./build.sh 0.0.2

The ``dist/``  folder will now contain the built package that can be installed in upstream projects.
