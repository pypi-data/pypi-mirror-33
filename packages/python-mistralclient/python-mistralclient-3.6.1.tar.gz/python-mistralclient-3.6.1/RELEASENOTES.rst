====================
python-mistralclient
====================

.. _python-mistralclient_3.6.0:

3.6.0
=====

.. _python-mistralclient_3.6.0_Bug Fixes:

Bug Fixes
---------

.. releasenotes/notes/fix-regression-with-execution-force-delete-af8d1968cb2673ef.yaml @ b'146d1c17e24f936f8bc365c69bf9f72a084e62ae'

- mistralclient 3.5.0 introduced a new --force option to delete executions
  that are still running. However, this had the unintended impact of passing
  force=false when it wasn't provided. This is incompatible with previous
  releases of the Mistral API which reject requests as they don't recognise
  "force".


.. _python-mistralclient_3.5.0:

3.5.0
=====

.. _python-mistralclient_3.5.0_New Features:

New Features
------------

.. releasenotes/notes/force-delete-executions-d08ce88a5deb3291.yaml @ b'e400bed6b0888247eafc90ff338165cfe01e037f'

- Adding a --force optional parameter to delete excetutions. Without it only
  finished executions can be deleted. If --force is passed the execution
  will be deleted but mistral will generate some errors as expected objects
  in memory no longer exist

