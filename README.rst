Water drop method
=================

A desktop app based on tkinter to implement the Water Drop Method and determine the structural stability of soil aggregates.

Project structure
-----------------

* ``src/Water_drop_method``: application package.
* ``tests``: automated tests.
* ``output``: local build artifacts (ignored by git).

Requirements
------------

* Python 3.10+
* Packages: ``pillow``, ``numpy``, ``matplotlib``

Install (editable)
------------------

.. code-block:: bash

	python -m venv .venv
	.venv\\Scripts\\activate
	pip install -e .

Run
---

.. code-block:: bash

	python -m Water_drop_method

Run tests
---------

.. code-block:: bash

	pytest -q

State files
-----------

Runtime state is saved in a per-user directory:

* Windows: ``%APPDATA%\\WaterDropMethod``
* Fallback: ``<home>/WaterDropMethod``

Files persisted there:

* ``threshold.txt``
* ``hole_area.txt``

Legacy migration
----------------

If old ``threshold.txt`` or ``hole_area.txt`` files are found in the current
working directory, the app performs a one-time best-effort copy to the per-user
state directory when those values are requested.

These runtime files are intentionally excluded from version control.


