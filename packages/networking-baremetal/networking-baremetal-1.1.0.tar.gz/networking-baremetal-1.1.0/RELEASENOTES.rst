====================
networking-baremetal
====================

.. _networking-baremetal_1.1.0:

1.1.0
=====

.. _networking-baremetal_1.1.0_New Features:

New Features
------------

.. releasenotes/notes/sighup-service-reloads-configs-11cd374cc33aac83.yaml @ b'8554146d7147c2f7fd064ac77112e75d729106db'

- Issuing a SIGHUP (e.g. ``pkill -HUP ironic-neutron-agent``) to the agent
  service will cause the service to reload and use any changed values for
  *mutable* configuration options.
  
  Mutable configuration options are indicated as such in the `sample
  configuration file <https://docs.openstack.org/networking-baremetal/latest/configuration/sample-config.html>`_
  by ``Note: This option can be changed without restarting``.
  
  A warning is logged for any changes to immutable configuration options.

