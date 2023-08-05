=========
kuryr-lib
=========

.. _kuryr-lib_0.7.0:

0.7.0
=====

.. _kuryr-lib_0.7.0_New Features:

New Features
------------

.. releasenotes/notes/multiple-binding-driver-512a6a7f620c758e.yaml @ b'da736d115bfeb10c9adf8d019696203bba5cbf8d'

- Add support for multiple binding drivers. Introduce a new config
  called 'enabled_drivers' which specifies a list of binding drivers
  allowed to use.


.. _kuryr-lib_0.7.0_Deprecation Notes:

Deprecation Notes
-----------------

.. releasenotes/notes/multiple-binding-driver-512a6a7f620c758e.yaml @ b'da736d115bfeb10c9adf8d019696203bba5cbf8d'

- Rename the config 'driver' to 'default_driver' in 'binding' group.
  This is for making it clear that it is allowed to have more than
  one type of bindings.

