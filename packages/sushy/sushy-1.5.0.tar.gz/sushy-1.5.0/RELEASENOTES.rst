=====
sushy
=====

.. _sushy_1.5.0:

1.5.0
=====

.. _sushy_1.5.0_New Features:

New Features
------------

.. releasenotes/notes/indicator-led-mappings-e7b34da03f6abb06.yaml @ b'0b9497dfa6add5c6bdf46903da17b0464400ccaa'

- Adds mappings and constants for possible values of the Indicator LED
  value in the System class.


.. _sushy_1.5.0_Bug Fixes:

Bug Fixes
---------

.. releasenotes/notes/fix-malformed-boot-mode-1ba1117cad8dcc47.yaml @ b'31cdd0f951bcd6c8a9b2d3f9628468aef5e7883b'

- Fixes malformed value of the ``BootSourceOverrideMode`` element which goes
  against the Redfish schema and causes some of the boot mode calls to
  fail.


.. _sushy_1.4.0:

1.4.0
=====

.. _sushy_1.4.0_New Features:

New Features
------------

.. releasenotes/notes/add-processor-id-and-status-b81d4c6e6c14c25f.yaml @ b'43ea0c0bd86663501d930c58c7eae8d93821cb4a'

- Adds the processor status and id fields to the ``Processor`` class.

.. releasenotes/notes/add-system-status-field-41b3f2a8c4b85f38.yaml @ b'6983511582ed91db3255ae7ede932b82b9a80b66'

- Adds the system status field to show the system status.


.. _sushy_1.4.0_Critical Issues:

Critical Issues
---------------

.. releasenotes/notes/bug-1754514-ca6ebe16c4e4b3b0.yaml @ b'8c12c2505c488d4e1974b496dc8308e3fb2ce662'

- Fixes authentication failure when SessionService attribute is
  not present in the root resource.

