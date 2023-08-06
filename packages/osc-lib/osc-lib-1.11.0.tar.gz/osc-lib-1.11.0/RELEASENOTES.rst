=======
osc-lib
=======

.. _osc-lib_1.11.0:

1.11.0
======

.. _osc-lib_1.11.0_Upgrade Notes:

Upgrade Notes
-------------

.. releasenotes/notes/direct-openstacksdk-535a179f3c645cc0.yaml @ b'ee79f6166e2f91725d08f17dc2ee59ca6487cd9b'

- The dependency on ``os-client-config`` has been removed in favor of
  direct use of ``openstacksdk``.


.. _osc-lib_1.10.0:

1.10.0
======

.. _osc-lib_1.10.0_New Features:

New Features
------------

.. releasenotes/notes/find-project-203bf867619c557e.yaml @ b'deec32d7e00b984d199f91fde037d1392d2fc757'

- Adds ``osc_lib.cli.identity.find_project()``. This function can be
  used to look up a project ID from command-line options like:
  
  .. code-block:: python
  
     find_project(self.app.client_manager.sdk_connection,
                  parsed_args.project, parsed_args.project_domain)

.. releasenotes/notes/find-project-203bf867619c557e.yaml @ b'deec32d7e00b984d199f91fde037d1392d2fc757'

- Adds ``osc_lib.cli.identity.add_project_owner_option_to_parser()``
  to register project and project domain options to CLI.


.. _osc-lib_1.10.0_Bug Fixes:

Bug Fixes
---------

.. releasenotes/notes/none-auth-cli-48ab0e48d4852941.yaml @ b'b764efc46fcee48394761620672a3a1e117aa3db'

- It is now possible to specify the ``none`` auth type (via ``--os-auth-type`` CLI argument or
  ``OS_AUTH_TYPE`` environment variable). To use it, ``--os-endpoint`` CLI argument or
  ``OS_ENDPOINT`` environment variable must be specified. See `the bug
  <https://bugs.launchpad.net/python-openstackclient/+bug/1724283>`_ for more detail.

