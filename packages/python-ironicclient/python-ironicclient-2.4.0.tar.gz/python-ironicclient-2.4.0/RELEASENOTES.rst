===================
python-ironicclient
===================

.. _python-ironicclient_2.4.0:

2.4.0
=====

.. _python-ironicclient_2.4.0_New Features:

New Features
------------

.. releasenotes/notes/deprecate-http-client-8d664e5ec50ec403.yaml @ b'58c39b7a80583dd54165cf292ae5dc621e9da361'

- The client now supports ``none`` authorization method, which should be
  used if the Identity service is not present in the deployment that the
  client talks to. To use it:
  
  - openstack baremetal CLI -- supported starting with ``osc-lib`` version
    ``1.10.0``, by providing ``--os-auth-type none`` and ``--os-endpoint``
    argument to ``openstack`` command
  
  - ironic CLI -- just specify the ``--ironic-url`` or ``--os-endpoint``
    argument in the ``ironic`` command (or set the corresponding environment
    variable)
  
  - python API -- specify the ``endpoint_override`` argument to the
    ``client.get_client()`` method (in addition to the required
    ``api_version``)

.. releasenotes/notes/node-fault-adbe74fd600063ee.yaml @ b'78902bfd0c56ba08642cd1ec0b21408c19ab2839'

- Supports the node's ``fault`` field, introduced in the Bare Metal API
  version 1.42, including displaying or querying nodes by this field.

.. releasenotes/notes/osc-baremetal-node-bios-setting-list-b062b31d0d4de337.yaml @ b'2fabfa41036199a3db7aac60145ae3ec082b2d06'

- Adds two new commands.
  
  * ``openstack baremetal node bios setting list <node_ident>``
  * ``openstack baremetal node bios setting show <node_ident> <setting_name>``
  
  The first command returns a list of BIOS settings for a given node,
  the second command returns a specified BIOS setting from the given node.
  
  Also adds support of bios_interface for the commands below.
  
  * ``openstack baremetal node create``
  * ``openstack baremetal node show``
  * ``openstack baremetal node set``
  * ``openstack baremetal node unset``
  * ``openstack baremetal driver list``
  * ``openstack baremetal driver show``

.. releasenotes/notes/version-overrides-4e9ba1266a238c6a.yaml @ b'144ce25e42ee7e5456deaa3ed19ce168cc9d4c07'

- Adds support for ``NodeManager.set_provision_state``,
  ``NodeManager.update``, ``NodeManager.get``, and ``NodeManager.list``
  to accept an ``os_ironic_api_version`` keyword argument to override
  the API version for that specific call to the REST API.
  
  When overridden, the API version is not preserved, and if an unsupported
  version is requested from the remote API, an ``UnsupportedVersion``
  exception is raised.


.. _python-ironicclient_2.4.0_Deprecation Notes:

Deprecation Notes
-----------------

.. releasenotes/notes/deprecate-http-client-8d664e5ec50ec403.yaml @ b'58c39b7a80583dd54165cf292ae5dc621e9da361'

- ``common.http.HTTPClient`` class is deprecated and will be removed in
  the Stein release. If you initialize the ironic client via
  ``v1.client.Client`` class directly, please pass the `keystoneauth
  <https://docs.openstack.org/keystoneauth/latest/>`_ session to the Client
  constructor, so that ``common.http.SessionClient`` is used instead.

.. releasenotes/notes/deprecate-http-client-8d664e5ec50ec403.yaml @ b'58c39b7a80583dd54165cf292ae5dc621e9da361'

- As part of standardizing argument naming to the one used by `keystoneauth
  <https://docs.openstack.org/keystoneauth/latest/>`_, the following
  arguments to ``client.get_client`` method are deprecated and will be
  removed in Stein release:
  
  * ``os_auth_token``: use ``token`` instead
  
  * ``os_username``: use ``username`` instead
  
  * ``os_password``: use ``password`` instead
  
  * ``os_auth_url``: use ``auth_url`` instead
  
  * ``os_project_id``: use ``project_id`` instead
  
  * ``os_project_name``: use ``project_name`` instead
  
  * ``os_tenant_id``: use ``tenant_id`` instead
  
  * ``os_tenant_name``: use ``tenant_name`` instead
  
  * ``os_region_name``: use ``region_name`` instead
  
  * ``os_user_domain_id``: use ``user_domain_id`` instead
  
  * ``os_user_domain_name``: use ``user_domain_name`` instead
  
  * ``os_project_domain_id``: use ``project_domain_id`` instead
  
  * ``os_project_domain_name``: use ``project_domain_name`` instead
  
  * ``os_service_type``: use ``service_type`` instead
  
  * ``os_endpoint_type``: use ``interface`` instead
  
  * ``ironic_url``: use ``endpoint`` instead
  
  * ``os_cacert``, ``ca_file``: use ``cafile`` instead
  
  * ``os_cert``, ``cert_file``: use ``certfile`` instead
  
  * ``os_key``, ``key_file``: use ``keyfile`` instead

.. releasenotes/notes/deprecate-http-client-8d664e5ec50ec403.yaml @ b'58c39b7a80583dd54165cf292ae5dc621e9da361'

- The ``endpoint`` argument to the ``v1.client.Client`` constructor is
  deprecated and will be removed in Stein release. Instead, please use the
  standard `keystoneauth <https://docs.openstack.org/keystoneauth/latest/>`_
  argument name ``endpoint_override``.


.. _python-ironicclient_2.4.0_Bug Fixes:

Bug Fixes
---------

.. releasenotes/notes/wait-for-prov-last-error-5f49b1c488879775.yaml @ b'8940d72521ea69cbb63cd813baa720c65f70b86f'

- Waiting for a provision state to be reached (via CLI ``--wait`` argument or
  the ``wait_for_provision_state`` function) no longer aborts when the node's
  ``last_error`` field gets populated. It can cause a normal deployment to
  abort if a heartbeat from the ramdisk fails because of locking - see
  `story 2002094 <https://storyboard.openstack.org/#!/story/2002094>`_.


.. _python-ironicclient_2.3.0:

2.3.0
=====

.. _python-ironicclient_2.3.0_New Features:

New Features
------------

.. releasenotes/notes/add-rescue-interface-to-node-and-driver-e3ff9b5df2628e5a.yaml @ b'e0d8b16161163e66908c2063a8013f14512cb94b'

- Adds support for rescue_interface for the commands below.
  They are available starting with ironic API microversion 1.38.
  
  * ``openstack baremetal node create``
  * ``openstack baremetal node show``
  * ``openstack baremetal node set``
  * ``openstack baremetal node unset``
  * ``openstack baremetal driver list``
  * ``openstack baremetal driver show``

.. releasenotes/notes/add-rescue-unrescue-support-f78266514ca59346.yaml @ b'fce885bf641712bdb5fa0088050fd37dc4f05686'

- Adds the below commands to OSC to support rescue mode for ironic
  available starting with API version 1.38:
  
  * ``openstack baremetal node rescue``
  * ``openstack baremetal node unrescue``

