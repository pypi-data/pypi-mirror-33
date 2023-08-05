=============
keystoneauth1
=============

.. _keystoneauth1_3.8.0:

3.8.0
=====

.. _keystoneauth1_3.8.0_New Features:

New Features
------------

.. releasenotes/notes/status-code-retries-75052a43efa4edb2.yaml @ b'3c2cf44e1ccc7774c1316d07e375c4ed9113842b'

- Addes support for retrying certain HTTP status codes when doing requests
  via the new ``status_code_retries`` and ``retriable_status_codes``
  parameters for ``Session`` and ``Adapter``.


.. _keystoneauth1_3.7.0:

3.7.0
=====

.. _keystoneauth1_3.7.0_New Features:

New Features
------------

.. releasenotes/notes/collect-timing-85f007f0d86c8b26.yaml @ b'244780fba84f008ddb2892b4c24ca2eb3fbcb0db'

- Added ``collect_timing`` option to ``keystoneauth1.session.Session``.
  The option, which is off by default, causes the ``Session`` to collect
  API timing information for every call it makes. Methods ``get_timings``
  and ``reset_timings`` have been added to allow getting and clearing the
  data.

.. releasenotes/notes/oslo-config-split-loggers-6bda266d657fe921.yaml @ b'80323289c71a39603166a9cfe4a56cb4d5784356'

- Added ``split-loggers`` option to the oslo.config Session options.

.. releasenotes/notes/version-between-b4b0bcf4cecfb9e4.yaml @ b'9e45781eaba457afc90650c13306c309b907f77a'

- Exposed ``keystoneauth1.discover.version_between`` as a public function
  that can be used to determine if a given version is within a range.


.. _keystoneauth1_3.6.2:

3.6.2
=====

.. _keystoneauth1_3.6.2_Bug Fixes:

Bug Fixes
---------

.. releasenotes/notes/bug-1766235wq-0de60d0f996c6bfb.yaml @ b'35de6ebe93b94076964f4250bf3fa9b8ff1f8463'

- [`bug 1766235 <https://bugs.launchpad.net/keystoneauth/+bug/1766235>`_]
  Fixed an issue where passing headers in as bytes rather than strings
  would cause a sorting issue.


.. _keystoneauth1_3.6.1:

3.6.1
=====

.. _keystoneauth1_3.6.1_Bug Fixes:

Bug Fixes
---------

.. releasenotes/notes/fix-get-all-version-data-a01ee58524755b9b.yaml @ b'0bebdaf0f90deef5121234ac98daa58e6f1f0f77'

- The docstring for ``keystoneauth1.session.Session.get_all_version_data``
  correctly listed ``'public'`` as the default value, but the argument list
  had ``None``. The default has been fixed to match the documented value.


.. _keystoneauth1_3.6.0:

3.6.0
=====

.. _keystoneauth1_3.6.0_New Features:

New Features
------------

.. releasenotes/notes/expose-endpoint-status-6195a6b76d8a8de8.yaml @ b'43c6e378f944227068ed815d84c124d6a7cc9d08'

- Added a 'status' field to the `EndpointData` object which contains a
  canonicalized version of the information in the status field of discovery
  documents.

.. releasenotes/notes/serice-type-aliases-249454829c57f39a.yaml @ b'79cd91e75580511171a3a61dc6f3c70e275f6348'

- Added support for service-type aliases as defined in the Service Types
  Authority when doing catalog lookups.

