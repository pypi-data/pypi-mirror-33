===========
oslo.config
===========

.. _oslo.config_6.3.0:

6.3.0
=====

.. _oslo.config_6.3.0_New Features:

New Features
------------

.. releasenotes/notes/support-fatal-deprecations-ea0513aa58a395ca.yaml @ b'5f8b0e0185dafeb68cf04590948b9c9f7d727051'

- oslo.config now supports the fatal-deprecations option from oslo.log.  This
  behavior is only enabled if oslo.log is installed, but oslo.log is still
  not a hard requirement to avoid a circular dependency.


.. _oslo.config_6.3.0_Upgrade Notes:

Upgrade Notes
-------------

.. releasenotes/notes/support-fatal-deprecations-ea0513aa58a395ca.yaml @ b'5f8b0e0185dafeb68cf04590948b9c9f7d727051'

- Because support for fatal-deprecations was added in this release, users who
  have fatal-deprecations enabled and have deprecated config opts in use
  (which previously was not a problem because oslo.config didn't respect the
  fatal-deprecations option) will need to resolve that before upgrading or
  services may fail to start.

