======================
tripleo-heat-templates
======================

.. _tripleo-heat-templates_6.2.15:

6.2.15
======

.. _tripleo-heat-templates_6.2.15_Bug Fixes:

Bug Fixes
---------

.. releasenotes/notes/convert-resource-name-to-number-80ada6c825554f56.yaml @ bffc619706c6bd751bdfb279a9608759b82e6253

- Previously, get-occ-config.sh could configure nodes out of order when deploying with more than 10 nodes. The script has been updated to properly sort the node resource names by first converting the names to a number.


.. _tripleo-heat-templates_6.2.14:

6.2.14
======

.. _tripleo-heat-templates_6.2.14_New Features:

New Features
------------

.. releasenotes/notes/enable-neutron-lbaas-integration-fa999ccd548ee6b6.yaml @ a7ebbd7d6dce9adf1952a2fb0b011e39c637c250

- Allows the configuration of the Neutron LBaaS agent.


.. _tripleo-heat-templates_6.2.14_Bug Fixes:

Bug Fixes
---------

.. releasenotes/notes/dont-unregister-on-delete-9708f7cbc73a0d2f.yaml @ d0288b450dd65f3f2d93564433dea29aab41f0da

- Don't unregister systems from the portal/satellite when deleting from Heat. There are several reasons why it's compelling to fix this behavior. See https://bugs.launchpad.net/tripleo/+bug/1710144 for full information. The previous behavior can be triggered by setting the DeleteOnRHELUnregistration parameter to "true".

.. releasenotes/notes/fix_nova_host-0b82c88597703353.yaml @ 7df20fd5738e9c00a4daf7e4f633c634f3b81f69

- The nova/neutron/ceilometer host parameter is now explicitly set to the
  same value that is written to /etc/hosts. On a correctly configured
  deployment they should be already be identical. However if the hostname
  or domainname is altered (e.g via DHCP) then the hostname is unlikely to
  resolve to the correct IP address for live-migraiton.
  Related bug: https://bugs.launchpad.net/tripleo/+bug/1758034

.. releasenotes/notes/live_migration_port_range-54c28faf0a67a3fc.yaml @ 832455031baf5e8eb094c208f667cc3ee0ebb23f

- By default, libvirtd uses ports from 49152 to 49215 for live-migration
  as specified in qemu.conf, that becomes a subset of ephemeral ports
  (from 32768 to 61000) used by many linux kernels.
  The issue here is that these ephemeral ports are used for outgoing TCP
  sockets. And live-migration might fail, if there are no port available
  from the specified range.
  Moving the port range out of ephemeral port range to be used only for
  live-migration.


.. _tripleo-heat-templates_6.2.13:

6.2.13
======

.. _tripleo-heat-templates_6.2.13_New Features:

New Features
------------

.. releasenotes/notes/enable-neutron-lbaas-integration-8cc3e9b71e0e3044.yaml @ b6eca3287dd479f702abd8008c673c4d46edabc6

- Allows the configuration of the Neutron LBaaS agent.

.. releasenotes/notes/ovs-dpdk-permissions-50c5b33334ff4711.yaml @ de86346b73577025e5a416dfd423e3aae2e16e41

- Till now, the ovs service file and ovs-ctl command files are patched to allow ovs to run with qemu group. In order to remove this workarounds, a new group hugetlbfs is created which will be shared between ovs and qemu. Use env file ovs-dpdk-permissions.yaml while deploying.


.. _tripleo-heat-templates_6.2.12:

6.2.12
======

.. _tripleo-heat-templates_6.2.12_Security Issues:

Security Issues
---------------

.. releasenotes/notes/memcached_hardening-2529734099da27f4.yaml @ d373df5ff89acaca762623fb3920b42778062f00

- Restrict memcached service to TCP and internal_api network (CVE-2018-1000115).


.. _tripleo-heat-templates_6.2.11:

6.2.11
======

.. _tripleo-heat-templates_6.2.11_Security Issues:

Security Issues
---------------

.. releasenotes/notes/snmp_firewall-ab17f60ba1ec71d2.yaml @ a67b208476a023fefacff78ddfb1688de8f9cc20

- Change the IPtables rule for SNMP service and open 161 udp port on
  SnmpdIpSubnet parameter instead of 0.0.0.0/0.
  If SnmpdIpSubnet is left empty, SnmpdNetwork will be used.


.. _tripleo-heat-templates_6.2.11_Bug Fixes:

Bug Fixes
---------

.. releasenotes/notes/deployed-server-ssl-c33d6810b889045c.yaml @ eb8de76ad05d1df678a2a18fecb3f43be5b26f2b

- The custom roles for deployed-server in deployed-server-roles-data.yaml will now work when configuring overcloud SSL.

.. releasenotes/notes/drop-manila-generic-driver-templates-b33e8966c263a1fd.yaml @ 298599d9331365d93e4cba907ea6b8c8df722249

- As documented in launchpad bug 1708680 the templates for manila with the
  "generic" back end do not yield a successful manila deployment even if
  they do not cause the overall overcloud deployment to fail, so we are
  dropping these faulty and unmaintained manila "generic" back end templates.

.. releasenotes/notes/fix-heat-condition-for-rhel-reg-311a3dce76cc0ec1.yaml @ f9ded9307b08cdfada3a469cc4ee46b919040aad

- Fix Heat condition for RHEL registration yum update
  There were 2 problems with this condition making the
  rhel-registration.yaml template broken: "conditions" should be "condition"
  and the condition should refer to just a condition name defined in the
  "conditions:" section of the template.  See
  https://bugs.launchpad.net/tripleo/+bug/1709916


.. _tripleo-heat-templates_6.2.9:

6.2.9
=====

.. _tripleo-heat-templates_6.2.9_New Features:

New Features
------------

.. releasenotes/notes/kernel-extra-aa48704056be72cd.yaml @ e9e0206bb4e8f20420a928b77e417c9da9b8ffa5

- Allow to easily personalize Kernel modules and sysctl settings with two new parameters.
  ExtraKernelModules and ExtraSysctlSettings are dictionaries that will take precedence
  over the defaults settings provided in the composable service.


.. _tripleo-heat-templates_6.2.8:

6.2.8
=====

.. _tripleo-heat-templates_6.2.8_Bug Fixes:

Bug Fixes
---------

.. releasenotes/notes/unset-ceph-default-min-size-0297620ed99dab5b.yaml @ 8e8cafcf33347d0a4301a01c9e0db6a8428bbc90

- Removed the hard coding of osd_pool_default_min_size. Setting this value
  to 1 can result in data loss in operating production deployments. Not
  setting this value (or setting it to 0) will allow ceph to calculate the
  value based on the current setting of osd_pool_default_size. If the
  replication count is 3, then the calculated min_size is 2.  If the
  replication count is 1, then the calcualted min_size is 1. For a POC
  deployments using a single OSD, set osd_pool_default_size = 1. See
  description at http://docs.ceph.com/docs/master/rados/configuration/pool-pg-config-ref/
  Added CephPoolDefaultSize to set default replication size. Default value is 3.


.. _tripleo-heat-templates_6.2.7:

6.2.7
=====

.. _tripleo-heat-templates_6.2.7_New Features:

New Features
------------

.. releasenotes/notes/update-on-rhel-registration-afbef3ead983b08f.yaml @ 3b6d480a891a695bd1fb3440ef86d988beb57aab

- Adds a new boolean parameter for RHEL Registration called
  'UpdateOnRHELRegistration' that when enabled will trigger a yum update
  on the node after the registration process completes.

.. releasenotes/notes/vmax_cinder_a6672898724a11e7.yaml @ 2677de31fc9d0f84ddc6d9465375dc606606cc0e

- Add support for Dell EMC VMAX Iscsi cinder driver


.. _tripleo-heat-templates_6.2.7_Bug Fixes:

Bug Fixes
---------

.. releasenotes/notes/fix-split-stack-os-collect-config-service-c4ad4e4e29a9e3b8.yaml @ 828bc54f84c4eb06d5b0bdfb470cff7014adf58b

- Enable the os-collect-config service on the system when using the
  get-occ-config.sh method of split stack configuration. LP#1734783


.. _tripleo-heat-templates_6.2.6:

6.2.6
=====

.. _tripleo-heat-templates_6.2.6_Bug Fixes:

Bug Fixes
---------

.. releasenotes/notes/enable-ntp-iburst-efbc24a43a72daae.yaml @ c1bc124c8e0a64af8735864b7a8a96348223fe44

- Enable the ntp iburst configuration for each server by default. As some
  services are very sensitive to time syncronization, this will help speed
  up the syncronization when servers are unavailable for a time. See
  LP#1731883


.. _tripleo-heat-templates_6.2.5:

6.2.5
=====

.. _tripleo-heat-templates_6.2.5_New Features:

New Features
------------

.. releasenotes/notes/rhsm_proxy_verify-548f104c97cf5f90.yaml @ d5c62813a67b94d84158ab5e12c94e2369279ccd

- When using RHSM proxy, TripleO will now verify that the proxy can be reached
  otherwise we'll stop early and not try to subscribe nodes.


.. _tripleo-heat-templates_6.2.5_Upgrade Notes:

Upgrade Notes
-------------

.. releasenotes/notes/sat-tools-0d0f0c53de9d34a5.yaml @ cc9f7a7d98c4bdcce3b96cdb8726598e8a54cd06

- When deploying with RHSM, sat-tools 6.2 will be installed instead of 6.1.
  The new version is supported by RHEL 7.4 and provides katello-agent package.


.. _tripleo-heat-templates_6.2.5_Bug Fixes:

Bug Fixes
---------

.. releasenotes/notes/workaround-unset-fqdn-for-rhel-reg-be9c4620146096be.yaml @ 5a5f546333668bcb3cf32c36afebaa68fc351eb8

- Workaround systems getting registered as "localhost" during RHEL registration if they don't have a fqdn set by first rm'ing the /etc/rhsm/facts directory. When the directory does not exist, the katello-rshm-consumer which runs when installing the katello-ca-consumer will not set the hostname.override fact to "localhost". See https://bugs.launchpad.net/tripleo/+bug/1711435


.. _tripleo-heat-templates_6.2.4:

6.2.4
=====

.. _tripleo-heat-templates_6.2.4_Bug Fixes:

Bug Fixes
---------

.. releasenotes/notes/sat_capsule-bb59fad44c17f97f.yaml @ b8680d53b82aed219ec006451add8f112b199451

- For deployments running on RHEL with Satellite 6 (or beyond) with Capsule (Katello API enabled),
  the Katello API is available on 8443 port, so the previous API ping didn't work for this case.
  Capsule is now supported since we just check if katello-ca-consumer-latest rpm is available
  to tell that Satellite version is 6 or beyond.


.. _tripleo-heat-templates_6.2.3:

6.2.3
=====

.. _tripleo-heat-templates_6.2.3_New Features:

New Features
------------

.. releasenotes/notes/snmp_listen-2364188f73d43b14.yaml @ 69b03c45dae8e0b63a2e6c641ba7cd6b6c7e2669

- Adding a new parameter to SNMP profile, SnmpdBindHost
  so users can change the binding addresses on SNMP daemon.
  The parameter is an array and takes the default value that
  were previously hardcoded in puppet-tripleo.


.. _tripleo-heat-templates_6.2.3_Bug Fixes:

Bug Fixes
---------

.. releasenotes/notes/add-hostgroup-default-for-host-parameter-02e3d48de1f69765.yaml @ 87d4bdf6932f6e10867d6c3ae4717c25e9ad93a4

- Set "host" parameter in manila.conf to 'hostgroup' when running manila share service under pacemaker.  This labels instances of the service on different nodes with the same "host" as cinder does in this circumstance so that the instances are considered by OpenStack to provide the same service and manila share is able to maintain management of shares on the backend after failover and failback.


.. _tripleo-heat-templates_6.2.2:

6.2.2
=====

.. _tripleo-heat-templates_6.2.2_Bug Fixes:

Bug Fixes
---------

.. releasenotes/notes/fix-neutron_admin_auth_url-c88224251d8eb807.yaml @ 1897de9f6f205b18e466da2e8f7966e63ad515d1

- The "neutron_admin_auth_url" is now properly set using KeystoneInternal rather than using the NeutronAdmin endpoint.


.. _tripleo-heat-templates_6.2.1:

6.2.1
=====

.. _tripleo-heat-templates_6.2.1_Bug Fixes:

Bug Fixes
---------

.. releasenotes/notes/fix-rpm-deploy-artifact-urls-03d5694073ad159d.yaml @ 703ff06d0f11f2a8cfdab7ce524febabe6e42f9f

- Fix support for RPMs to be installed via DeployArtifactURLs. LP#1697102

.. releasenotes/notes/leave-satellite-repo-enabled-8b60528bd5450c7b.yaml @ 2321346969e4e5f0b2ba056736dfcf1e005bbcad

- Previously the RHEL registration script disabled the satellite repo after
  installing the necessary packages from it.  This makes it awkward to
  update those packages later, so the repo will no longer be disabled.


.. _tripleo-heat-templates_6.2.0:

6.2.0
=====

.. _tripleo-heat-templates_6.2.0_New Features:

New Features
------------

.. releasenotes/notes/add-cinder-nas-secure-parameters-53f9d6a6e9bc129b.yaml @ 21eb374fa155131081e40bd3ec75c16ef6b454e4

- Add parameters to control the Cinder NAS security settings associated with the NFS and NetApp Cinder back ends. The settings are disabled by default.


.. _tripleo-heat-templates_6.2.0_Upgrade Notes:

Upgrade Notes
-------------

.. releasenotes/notes/change-rabbitmq-ha-mode-policy-default-6c6cd7f02181f0e0.yaml @ ff4db0db59184d23795ffde209974c9f57a63e2a

- We are not changing the rabbitmq ha-mode policy during upgrades any longer.
  The policy chosen at deploy time will remain the same but can be changed
  manually.

.. releasenotes/notes/disable-manila-cephfs-snapshots-by-default-d5320a05d9b501cf.yaml @ 12f0f6ca435e97984adc0d818370bd06be87c164

- Disabled cephfs snapshot support (ManilaCephFSNativeCephFSEnableSnapshots
  parameter) in manila by default.


.. _tripleo-heat-templates_6.2.0_Bug Fixes:

Bug Fixes
---------

.. releasenotes/notes/baremetal-cell-hosts-cd5cf5aa8a33643c.yaml @ 97c3806ccf1f5f38eeedcbea6524571b8b3ef040

- When ``environments/services/ironic.yaml`` is used, enable periodic task
  in nova-scheduler to automatically discover new nodes. Otherwise a user
  has to run nova management command on controllers each time.

.. releasenotes/notes/change-rabbitmq-ha-mode-policy-default-6c6cd7f02181f0e0.yaml @ ff4db0db59184d23795ffde209974c9f57a63e2a

- Due to https://bugs.launchpad.net/tripleo/+bug/1686337 we switch the
  default of rabbitmq back ha-mode "all". This is to make the installation
  more robust in the face of network issues.

.. releasenotes/notes/disable-ceilo-middleware-6853cb92e3e08161.yaml @ f762bbc3610cad472b9e10cac3609818384ed520

- Disable ceilometer in the swift proxy middleware pipeline out of the box. This generates a lot of events with gnocchi and swift backend and causes heavy load. It should be easy to enable if needed.

.. releasenotes/notes/expose-metric-processing-delay-0c098d7ec0af0728.yaml @ c9afae93f2abc1a8622737c5a4c878b0ca3faad4

- Expose metric_processing_delay to tweak gnocchi performance.

.. releasenotes/notes/fix-glance-api-network-4f9d7c20475a5994.yaml @ fa37664af5d9aea73b77807e078b4ccde0afdb53

- Incorrect network used for Glance API service.

.. releasenotes/notes/stack-name-input-73f4d4d052f1377e.yaml @ d8e27308c7296442106f4b4f2b615eaef17aad58

- The stack name can now be overridden in the get-occ-config.sh script for deployed-server's by setting the $STACK_NAME variable in the environment.

.. releasenotes/notes/swap-prepuppet-and-postpuppet-to-preconfig-and-postconfig-debd5f28bc578d51.yaml @ ffb7ba51e19caba276ee256f7083833e9bcf3b76

- This commit merges both [Pre|Post]Puppet and [Pre|Post]Config resources, giving an agnostic name for the configuration steps. The [Pre|Post]Puppet resource is removed and should not be used anymore.


.. _tripleo-heat-templates_6.2.0_Other Notes:

Other Notes
-----------

.. releasenotes/notes/enable-arp_accept-6296b0113bc56b10.yaml @ 0b6ce86e7ae59f25a6502269b216f16e2189708a

- All nodes now enable ``arp_accept`` sysctl setting to help with honoring
  gratuitous ARP packets in their ARP tables. While sources of gratuitous ARP
  packets are diverse, this comes especially useful for Neutron floating IP
  addresses that roam between devices, and for which Neutron L3 agent sends
  gratuitous ARP packets to update all network nodes about IP address new
  locations.


.. _tripleo-heat-templates_6.1.0:

6.1.0
=====

.. _tripleo-heat-templates_6.1.0_New Features:

New Features
------------

.. releasenotes/notes/add-ldap-backend-0bda702fb0aa24bf.yaml @ 4db1c9f8e4b82e9430e76b1d02542dd6d6b65ef5

- Add capabilities to configure LDAP backends as for keystone domains. This can be done by using the KeystoneLDAPDomainEnable and KeystoneLDAPBackendConfigs parameters.

.. releasenotes/notes/migration_over_ssh-003e2a92f5f5374d.yaml @ 1eeedbc095c432082c9a6d08c4d15ece36769a52

- Add support for cold migration over ssh.
  
  This enables nova cold migration.
  
  This also switches to SSH as the default transport for live-migration.
  The tripleo-common mistral action that generates passwords supplies the
  MigrationSshKey parameter that enables this.

.. releasenotes/notes/ssh_known_hosts-287563590632d1aa.yaml @ 68d7196d472b5195c19e871e960996e89a7bcb9c

- SSH host key exchange. The ssh host keys are collected from each host, combined, and written to /etc/ssh/ssh_known_hosts.

.. releasenotes/notes/sshd-service-extensions-0c4d0879942a2052.yaml @ cbf997e73771735d9c8536376b7de075bc8256e1

- Added ability to manage MOTD Banner
  Enabled SSHD composible service by default. Puppet-ssh manages the sshd config.


.. _tripleo-heat-templates_6.1.0_Known Issues:

Known Issues
------------

.. releasenotes/notes/ovs-2.5-2.6-composable-upgrades-workaround-73f4e56127c910b4.yaml @ d3f47eb0b97bab298759021162efebed45c658d0

- During the ovs upgrade for 2.5 to 2.6 we need to workaround the classic yum update command by handling the upgrade of the package separately to not loose the IPs and the connectivity on the nodes. The workaround is discussed here https://bugs.launchpad.net/tripleo/+bug/1669714


.. _tripleo-heat-templates_6.1.0_Upgrade Notes:

Upgrade Notes
-------------

.. releasenotes/notes/ovs-2.5-2.6-composable-upgrades-workaround-73f4e56127c910b4.yaml @ d3f47eb0b97bab298759021162efebed45c658d0

- The upgrade from openvswitch 2.5 to 2.6 is handled gracefully and there should be no user impact in particular no restart of the openvswitch service. For more information please see the related bug above which also links the relevant code reviews. The workaround (transparent to the user/doesn't require any input) is to download the OVS package and install with --nopostun and --notriggerun options provided by the rpm binary.

.. releasenotes/notes/replace-references-to-old-ctlplane-0df7f2ae8910559c.yaml @ d381054c8e92c8341e243179e2de447cf11242b3

- The default network for the ctlplane changed from 192.0.2.0/24 to
  192.168.24.0/24. All references to the ctlplane network in the templates
  have been updated to reflect this change. When upgrading from a previous
  release, if the default network was used for the ctlplane (192.0.2.0/24),
  then it is necessary to provide as input, via environment file, the correct
  setting for all the parameters that previously defaulted to 192.0.2.x and
  now default to 192.168.24.x; there is an environment file which could be
  used on upgrade `environments/updates/update-from-192_0_2-subnet.yaml` to
  cover a simple scenario but it won't be enough for scenarios using an
  external load balancer, Contrail or Cisto N1KV. Follows a list of params to
  be provided on upgrade.
  From contrail-net.yaml: EC2MetadataIp, ControlPlaneDefaultRoute
  From external-loadbalancer-vip-v6.yaml: ControlFixedIPs
  From external-loadbalancer-vip.yaml: ControlFixedIPs
  From network-environment.yaml: EC2MetadataIp, ControlPlaneDefaultRoute
  From neutron-ml2-cisco-n1kv.yaml: N1000vVSMIP, N1000vMgmtGatewayIP
  From contrail-vrouter.yaml: ContrailVrouterGateway


.. _tripleo-heat-templates_6.1.0_Deprecation Notes:

Deprecation Notes
-----------------

.. releasenotes/notes/migration_over_ssh-003e2a92f5f5374d.yaml @ 1eeedbc095c432082c9a6d08c4d15ece36769a52

- The TCP transport is no longer used for live-migration and the firewall
  port has been closed.


.. _tripleo-heat-templates_6.1.0_Security Issues:

Security Issues
---------------

.. releasenotes/notes/etcdtoken-4c46bdfac940acda.yaml @ 8f728b395328ae1231ef026a8f6c1c06a0b880a9

- Secure EtcdInitialClusterToken by removing the default value
  and make the parameter hidden.
  Fixes `bug 1673266 <https://bugs.launchpad.net/tripleo/+bug/1673266>`__.


.. _tripleo-heat-templates_6.1.0_Bug Fixes:

Bug Fixes
---------

.. releasenotes/notes/allow-neutron-dhcp-agents-per-network-calculation-536c70391497256d.yaml @ 9c91720199242174151b5d01803785e8266a4db7

- NeutronDhcpAgents had a default value of 3 that, even though unused in
  practice was a bad default value. Changing the default value to a
  sentinel value and making the hiera conditional allows deploy-time
  logic in puppet to provide a default value based on the number of dhcp
  agents being deployed.

.. releasenotes/notes/big-switch-agent-4c743a2112251234.yaml @ f9d2ce123bf0fcebb50a97fce4db7412d0d70e38

- Updated bigswitch environment file to include the bigswitch agent
  installation and correct support for the restproxy configuration.

.. releasenotes/notes/deployed-server-firewall-purge-9d9fe73faf925056.yaml @ 33e63c2c77fde0af65e33d404dc99036785ee94a

- The initial firewall will now be purged by the deployed-server bootstrap scripts. This is needed to prevent possible issues with bootstrapping the initial Pacemaker cluster. See https://bugs.launchpad.net/tripleo/+bug/1679234

.. releasenotes/notes/fix-cinder-nfs-share-usage-0968f88eff7ffb99.yaml @ 8b7a995df3014d1da312424278dc4753a34f44a6

- Fixes an issue when using the CinderNfsServers parameter_defaults setting.  It now works using a single share as well as a comma-separated list of shares.

.. releasenotes/notes/fix-neutron-dpdk-firewall-436aee39a0d7ed65.yaml @ e6fbc8e45d4d4df0caec8abc32280ac61c5efe26

- Fixes firewall rules from neutron OVS agent not being inherited correctly and applied in neutron OVS DPDK template.

.. releasenotes/notes/fix-odl-provider-mapping-hiera-5b3472184be490e2.yaml @ a17f6c6816b617c9ba5cbc2079f02f6cd2e0d492

- Fixes OpenDaylightProviderMappings parsing on a comma delimited list.

.. releasenotes/notes/install-openstack-selinux-d14b2e26feb6d04e.yaml @ ac98fcfc5cff830556c3b006a0d980856857fe3c

- openstack-selinux is now installed by the deployed-server bootstrap scripts. Previously, it was not installed, so if SELinux was set to enforcing, all OpenStack policy was missing.

.. releasenotes/notes/make-panko-default-8d0e824fc91cef56.yaml @ f8d229285bf4a4786e6adf0f60e1a8046cf46972

- Since panko is enabled by default, include it the default dispatcher for ceilometer events.

.. releasenotes/notes/restrict-mongodb-memory-de7bf6754d7234d9.yaml @ c25a96357cbdddf2af2a3c5e3da65d8fbd00a99b

- Add knobs to limit memory comsumed by mongodb with systemd

.. releasenotes/notes/set-ceilometer-auth-flag-382f68ddb2cbcb6b.yaml @ b8855022563dda29aa78590a67386db35c5c6687

- We need ceilometer user in cases where ceilometer API is disabled. This is to ensure other ceilometer services can still authenticate with keystone.

.. releasenotes/notes/sriov-pci-passthrough-8f28719b889bdaf7.yaml @ 8a4c6cbdf5e70b92f2e6b123f36545c957425d08

- The ``pci_passthrough`` hiera value should be passed as a string (`bug 1675036 <https://bugs.launchpad.net/tripleo/+bug/1675036>`__).

.. releasenotes/notes/token-flush-twice-a-day-d4b00a2953a6b383.yaml @ c1fc74c0f3a8ba34032ac40ee67ef3bc4b7c9d3e

- The token flush cron job has been modified to run hourly instead of once a day. This is because this was causing issues with larger deployments, as the operation would take too long and sometimes even fail because of the transaction being so large. Note that this only affects people using the UUID token provider.


.. _tripleo-heat-templates_6.0.0:

6.0.0
=====

.. _tripleo-heat-templates_6.0.0_Prelude:

Prelude
-------

.. releasenotes/notes/manila-with-managed-ceph-e5178fd06127624f.yaml @ 38cbdc5424096de93c73116123f45436a35a6884

Support for Manila/CephFS with TripleO managed Ceph cluster


.. _tripleo-heat-templates_6.0.0_New Features:

New Features
------------

.. releasenotes/notes/manila-with-managed-ceph-e5178fd06127624f.yaml @ 38cbdc5424096de93c73116123f45436a35a6884

- It is now possible to configure Manila with CephFS to use a
  TripleO managed Ceph cluster. When using the Heat environment
  file at environments/manila-cephfsnative-config.yaml Manila
  will be configured to use the TripleO managed Ceph cluster
  if CephMDS is deployed as well, which can be done using the
  file environments/services/ceph-mds.yaml

