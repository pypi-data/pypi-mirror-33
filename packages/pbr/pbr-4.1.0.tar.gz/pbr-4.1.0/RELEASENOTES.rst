===
pbr
===

.. _pbr_4.0.0:

4.0.0
=====

.. _pbr_4.0.0_New Features:

New Features
------------

.. releasenotes/notes/v_version-457b38c8679c5868.yaml @ b'4c775e7890e90fc2ea77c66020659e52d6a61414'

- Support version parsing of git tag with the ``v<semver>`` pattern
  (or ``V<semver>``), in addition to ``<semver>``.


.. _pbr_4.0.0_Upgrade Notes:

Upgrade Notes
-------------

.. releasenotes/notes/remove-command-hooks-907d9c2325f306ca.yaml @ b'32c90ba598d7740e52bf21bc5e920fb5df08645a'

- Support for entry point command hooks has been removed. This feature was
  poorly tested, poorly documented, and broken in some environments.
  Support for global hooks is not affected.


.. _pbr_4.0.0_Deprecation Notes:

Deprecation Notes
-----------------

.. releasenotes/notes/deprecate-pyN-requirements-364655c38fa5b780.yaml @ b'9be181e8e60cc41f3ad685e236b0c4cdc29dbd3c'

- Support for ``pyN``-suffixed requirement files has been deprecated:
  environment markers should be used instead.

.. releasenotes/notes/deprecate-testr-nose-integration-56e3e11248d946fc.yaml @ b'113685e1b94df9dd2945adbdda757a545b09598c'

- *testr* and *nose* integration has been deprecated. This feature allowed
  *pbr* to dynamically configure the test runner used when running
  ``setup.py test``. However, this target has fallen out of favour in both
  the OpenStack and broader Python ecosystem, and both *testr* and *nose*
  offer native setuptools commands that can be manually aliased to ``test``
  on a per-project basis, if necessary. This feature will be removed in a
  future release.

