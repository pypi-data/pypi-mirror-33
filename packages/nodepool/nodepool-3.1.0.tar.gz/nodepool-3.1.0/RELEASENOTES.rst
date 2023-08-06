========
nodepool
========

.. _nodepool_3.1.0:

3.1.0
=====

.. _nodepool_3.1.0_New Features:

New Features
------------

.. releasenotes/notes/default-format-fb859338909defb9.yaml @ b'6ec75970b3e8b81b2800cb1b4e9c0315a70b903a'

- Nodepool now defaults to building qcow2 diskimages instead of failing if
  the diskimage doesn't specify an image format and the diskimage isn't used
  by any provider. This makes it more convenient to build images without
  uploading them to a cloud provider.

.. releasenotes/notes/security-group-support.yaml @ b'674c9516dc8fa63bde2ab36db60560fc72b09a6b'

- Added support for specifying security-groups for the nodes in openstack
  driver. Pool.security-groups takes list of SGs to attach to the server.

.. releasenotes/notes/static-driver-changes-9692c3ee0dc0bc29.yaml @ b'3e0a822bf67139c13f61c74160f655f8f8388788'

- The static driver now pre-registers its nodes with ZooKeeper at startup
  and on configuration changes. A single node may be registered multiple
  times, based on the value of max-parallel-jobs.


.. _nodepool_3.1.0_Upgrade Notes:

Upgrade Notes
-------------

.. releasenotes/notes/multilabel-999f0d38d02848a2.yaml @ b'77edb84fb681ebdd8ce19a4876f511c9233c4dc5'

- Nodepool can now support multiple node labels, although the OpenStack and
  static node drivers do not yet support specifying multiple labels, so this
  is not yet a user-visible change. This does, however, require shutting down
  all launcher processes before restarting them. Running multiple launchers
  with mixed support of multi-label will cause errors, so a full shutdown is
  required.


.. _nodepool_3.1.0_Bug Fixes:

Bug Fixes
---------

.. releasenotes/notes/paused-handler-fix-6c4932dcf71939ba.yaml @ b'3eab2396ae8b6fdacb631e505ceff82efb0415da'

- Fixed a bug where if a request handler is paused and an exception is thrown
  within the handler, the handler was not properly unpaused and the request
  remained in the list of active handlers.


.. _nodepool_3.0.1:

3.0.1
=====

.. _nodepool_3.0.1_New Features:

New Features
------------

.. releasenotes/notes/diskimage-connection-port-f53b0a9c910cb393.yaml @ b'687f120b3c21b527c217a734144e105d7daead76'

- The connection port can now be configured in the provider diskimages
  section.

.. releasenotes/notes/static-driver-windows-cf80096636dbb428.yaml @ b'da95a817bbc742dbab587953b542686a4c375c89'

- Added support for configuring windows static nodes. A static node can now
  define a ``connection-type``. The ``ssh-port`` option has been renamed
  to ``connection-port``.


.. _nodepool_3.0.1_Deprecation Notes:

Deprecation Notes
-----------------

.. releasenotes/notes/static-driver-windows-cf80096636dbb428.yaml @ b'da95a817bbc742dbab587953b542686a4c375c89'

- ``ssh-port`` in static node config is deprecated. Please update config to
  use ``connection-port`` instead.

