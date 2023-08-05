Quickstart
============

Introduction
------------

The :class:`debinterface.Interfaces` class contains a list of :class:`debinterface.Adapters` objects, each one representing a network adapter from your computer.
Internally, :class:`debinterface.Interfaces` uses :class:`debinterface.InterfacesReader`, :class:`debinterface.InterfacesWriter` and :class:`debinterface.AdapterValidation` to read, write and try to validate your interfaces.

.. warning::

    I cannot stress enough that validation cannot be bullet proof, so be very cautious of what you modify !


You'll also find two simple classes to manipulate Dnsmasq DNS ranges (:class:`debinterface.DnsmasqRange`) and Hostapd :class:`debinterface.Hostapd` config files. Please read the source code before using them to check they fit your usage.


Code examples
-------------

Quickstart
+++++++++++

.. sourcecode:: python

    import debinterface

    # Parse the interfaces file
    interfaces = debinterface.Interfaces()

    # Get a collection of objects representing the network adapters to print their names and static IP address:
    adapters = interfaces.adapters
    for adapter in adapters:
        ip = 'IP address is DHCP defined'
        if adapter.attributes['source'] == 'static':
            ip = adapter.attributes['address']
        print(adapter.attributes['name'], ip)

    # If you need to use raw python objects, each adapter has an 'export()' method that returns a dictionary of its options.
    for adapter in adapters:
    	item = adapter.export()
    	print(item['name'])


Adapter edition
+++++++++++++++

Any changes made with setter methods will be reflected with the new write. Numerous methods exist in the :class:`debinterface.Adapters` to update common fields, and you have a special method for less common ones

.. sourcecode:: python

    import debinterface

    interfaces = debinterface.Interfaces()
    adapter = interfaces.getAdapter("eth0")

    # Update Gateway with provided setter
    adapter.setGateway("192.168.1.4")

    # Update hwaddress with the special setter
    adapter.setUnknown('hwaddress', 'ether 02:1b:b1:ef:b0:01')
    interfaces.writeInterfaces()


Adapter creation
++++++++++++++++


.. sourcecode:: python

    import debinterface

    options = {
            'addrFam': 'inet',
            'broadcast': '192.168.0.255',
            'name': 'eth9999',
            'up': ['ethtool -s eth0 wol g'],
            'gateway': '192.168.0.254',
            'down': [],
            'source': 'static',
            'netmask': '255.255.255.0',
            'address': '192.168.0.250'
        }

    itfs = debinterface.Interfaces()
    itfs.addAdapter(options)


Adapter up and down
+++++++++++++++++++

You can up and down an adapter easily

.. sourcecode:: python

    import debinterface

    interfaces = debinterface.Interfaces()

    # Activate eth1
    interfaces.upAdapter("eth1")

    # Deactivate wlan0 and check for errors
    success, details = interfaces.downAdapter("wlan0")
    if not success:
        print details


Backups and disaster recovery
+++++++++++++++++++++++++++++

Before a write, a backup is always created and any write error will trigger a restore.
A backup of your old interfaces file will be generated when writing over the previous interfaces file
By defaults these paths are used :

- INTERFACES_PATH='/etc/network/interfaces'
- BACKUP_PATH='/etc/network/interfaces.old'

Paths can be customized when instanciating the Interfaces class:

.. sourcecode:: python

    import debinterface

    interfaces = debinterface.Interfaces(interfaces_path='/home/interfaces', backup_path='/another/custom/path')


Lazy reading
++++++++++++

By defaults, interfaces file is read when instanciating the Interfaces class, but you can do it lazyly if needed:

.. sourcecode:: python

    import debinterface

    interfaces = debinterface.Interfaces(update_adapters=False)
    interfaces.updateAdapters()
