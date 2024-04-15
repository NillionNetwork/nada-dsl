========
nada_dsl
========

Nada is an embedded domain-specific language (DSL) for building MPC programs for the Nillion Network.

Development
-----------
All installation and development dependencies are fully specified in ``pyproject.toml``. The ``project.optional-dependencies`` object is used to `specify optional requirements <https://peps.python.org/pep-0621>`__ for various development tasks. This makes it possible to specify additional options (such as ``docs``, ``lint``, and so on) when performing installation using `pip <https://pypi.org/project/pip>`__:

.. code-block:: bash

    python -m pip install .'[docs,lint]'

Documentation
^^^^^^^^^^^^^
The documentation can be generated automatically from the source files using `Sphinx <https://www.sphinx-doc.org>`__:

.. code-block:: bash

    python -m pip install .'[docs]'
    cd docs
    make html

Testing and Conventions
^^^^^^^^^^^^^^^^^^^^^^^
Unit tests are executed and their coverage is measured when using `pytest <https://docs.pytest.org>`__ (see the ``pyproject.toml`` file for configuration details):

.. code-block:: bash

    python -m pip install .'[test]'
    python -m pytest

Style conventions are enforced using `Pylint <https://pylint.readthedocs.io>`__:

.. code-block:: bash

    python -m pip install .'[lint]'
    python -m pylint nada_dsl
