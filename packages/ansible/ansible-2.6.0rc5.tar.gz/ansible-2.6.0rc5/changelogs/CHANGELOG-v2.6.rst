========================================
Ansible 2.6 "Heartbreaker" Release Notes
========================================

v2.6.0rc5
=========

Release Summary
---------------

| Release Date: 2018-06-26
| `Porting Guide <https://docs.ansible.com/ansible/devel/porting_guides.html>`_


Bugfixes
--------

- allow set_options to be called multiple times https://github.com/ansible/ansible/pull/41913
- group_by - support implicit localhost (https://github.com/ansible/ansible/pull/41860)
- lineinfile - fix insertbefore when used with BOF to not insert duplicate lines (https://github.com/ansible/ansible/issues/38219)
- password lookup - Do not load password lookup in network filters, allowing the password lookup to be overriden (https://github.com/ansible/ansible/pull/41907)
- win_iis_webapppool - redirect some module output to null so Ansible can read the output JSON https://github.com/ansible/ansible/issues/40874

v2.6.0rc4
=========

Release Summary
---------------

| Release Date: 2018-06-25
| `Porting Guide <https://docs.ansible.com/ansible/devel/porting_guides.html>`_


Minor Changes
-------------

- Raise AnsibleParserError which was missing previously

Bugfixes
--------

- Changed the output to "text" for "show vrf" command as default "json" output format with respect to "eapi" transport was failing (https://github.com/ansible/ansible/pull/41470)
- added missing 'raise' to exception definition https://github.com/ansible/ansible/pull/41690
- correct debug display for all cases https://github.com/ansible/ansible/pull/41331
- correctly check hostvars for vars term https://github.com/ansible/ansible/pull/41819
- correctly handle yaml inventory files when entries are null dicts https://github.com/ansible/ansible/issues/41692
- file module - The touch subcommand had its diff output broken during the 2.6.x development cycle.  This is now fixed (https://github.com/ansible/ansible/issues/41755)
- fix apt-mark on debian6 (https://github.com/ansible/ansible/pull/41530)
- fixed config required handling, specifically for _terms in lookups https://github.com/ansible/ansible/pull/41740
- win_updates - Fixed issue where running win_updates on async fails without any error
- winrm - ensure pexpect is set to not echo the input on a failure and have a manual sanity check afterwards https://github.com/ansible/ansible/issues/41865

v2.6.0rc3
=========

Release Summary
---------------

| Release Date: 2018-06-18
| `Porting Guide <https://docs.ansible.com/ansible/devel/porting_guides.html>`_


Bugfixes
--------

- **Security Fix** - Some connection exceptions would cause no_log specified on a task to be ignored.  If this happened, the task information, including any private information could have been displayed to stdout and (if enabled, not the default) logged to a log file specified in ansible.cfg's log_path. Additionally, sites which redirected stdout from ansible runs to a log file may have stored that private information onto disk that way as well. (https://github.com/ansible/ansible/pull/41414)
- Fix added for Digital Ocean Volumes API change causing Ansible to recieve an unexpected value in the response. (https://github.com/ansible/ansible/pull/41431)
- Fix iosxr_config module to handle route-policy, community-set, prefix-set, as-path-set and rd-set blocks. All these blocks are part of route-policy language of iosxr.
- gce_net - Fix sorting of allowed ports (https://github.com/ansible/ansible/pull/41567)
- uses correct conn info for reset_connection  https://github.com/ansible/ansible/issues/27520

v2.6.0rc2
=========

Release Summary
---------------

| Release Date: 2018-06-08
| `Porting Guide <https://docs.ansible.com/ansible/devel/porting_guides.html>`_


Bugfixes
--------

- Changed the admin_users config option to not include "admin" by default as admin is frequently used for a non-privileged account  (https://github.com/ansible/ansible/pull/41164)
- allow custom endpoints to be used in the aws_s3 module (https://github.com/ansible/ansible/pull/36832)
- ansible-doc - fixed traceback on missing plugins (https://github.com/ansible/ansible/pull/41167)
- cast the device_mapping volume size to an int in the ec2_ami module (https://github.com/ansible/ansible/pull/40938)
- fix BotoCoreError exception handling
- fix async for the aws_s3 module by adding async support to the action plugin (https://github.com/ansible/ansible/pull/40826)
- fix decrypting vault files for the aws_s3 module (https://github.com/ansible/ansible/pull/39634)
- fix errors with S3-compatible APIs if they cannot use ACLs for buckets or objects
- fix permission handling to try to download a file even if the user does not have permission to list all objects in the bucket

v2.6.0rc1
=========

Release Summary
---------------

| Release Date: 2018-06-05
| `Porting Guide <https://docs.ansible.com/ansible/devel/porting_guides.html>`_


v2.6.0a2
========

Release Summary
---------------

| Release Date: 2018-05-30
| `Porting Guide <https://docs.ansible.com/ansible/devel/porting_guides.html>`_


Minor Changes
-------------

- The aws_ses_identity module supports check mode

Removed Features (previously deprecated)
----------------------------------------

- removed the deprecated always_run task option, please use `check_mode: no` instead

Bugfixes
--------

- powershell - use the tmpdir set by `remote_tmp` for become/async tasks instead of the generic $env:TEMP - https://github.com/ansible/ansible/pull/40210
- selinux - correct check mode behavior to report same changes as normal mode (https://github.com/ansible/ansible/pull/40721)
- synchronize - Ensure the local connection created by synchronize uses _remote_is_local=True, which causes ActionBase to build a local tmpdir (https://github.com/ansible/ansible/pull/40833)
- win_updates - Added the ability to run on a scheduled task for older hosts so async starts working again - https://github.com/ansible/ansible/issues/38364
- winrm - Add better error handling when the kinit process fails
- xenserver_facts - ensure module works with newer versions of XenServer (https://github.com/ansible/ansible/pull/35821)

New Plugins
-----------

Inventory
~~~~~~~~~

- gcp_compute - Google Cloud Compute Engine inventory source

New Modules
-----------

Cloud
~~~~~

amazon
^^^^^^

- aws_config_aggregation_authorization - Manage cross-account AWS Config authorizations
- aws_config_aggregator - Manage AWS Config aggregations across multiple accounts
- aws_config_delivery_channel - Manage AWS Config delivery channels
- aws_config_recorder - Manage AWS Config Recorders
- aws_config_rule - Manage AWS Config resources
- aws_glue_connection - Manage an AWS Glue connection
- aws_glue_job - Manage an AWS Glue job
- elb_network_lb - Manage a Network Load Balancer

azure
^^^^^

- azure_rm_resource - Create any Azure resource.
- azure_rm_resource_facts - Generic facts of Azure resources.

google
^^^^^^

- gcp_compute_disk - Creates a GCP Disk
- gcp_compute_firewall - Creates a GCP Firewall
- gcp_compute_forwarding_rule - Creates a GCP ForwardingRule
- gcp_compute_global_address - Creates a GCP GlobalAddress
- gcp_compute_global_forwarding_rule - Creates a GCP GlobalForwardingRule
- gcp_compute_image - Creates a GCP Image
- gcp_compute_instance_group - Creates a GCP InstanceGroup
- gcp_compute_instance_group_manager - Creates a GCP InstanceGroupManager
- gcp_compute_ssl_certificate - Creates a GCP SslCertificate
- gcp_compute_target_pool - Creates a GCP TargetPool
- gcp_compute_target_ssl_proxy - Creates a GCP TargetSslProxy
- gcp_compute_url_map - Creates a GCP UrlMap

heroku
^^^^^^

- heroku_collaborator - Add or delete app collaborators on Heroku

memset
^^^^^^

- memset_dns_reload - Request reload of Memset's DNS infrastructure,
- memset_zone_domain - Create and delete domains in Memset DNS zones.
- memset_zone_record - Create and delete records in Memset DNS zones.

misc
^^^^

- cloud_init_data_facts - Retrieve facts of cloud-init.

opennebula
^^^^^^^^^^

- one_service - Deploy and manage OpenNebula services

Network
~~~~~~~

f5
^^

- bigip_gtm_monitor_external - Manages external GTM monitors on a BIG-IP
- bigip_monitor_external - Manages external LTM monitors on a BIG-IP
- bigiq_utility_license - Manage utility licenses on a BIG-IQ

meraki
^^^^^^

- meraki_admin - Manage administrators in the Meraki cloud
- meraki_snmp - Manage organizations in the Meraki cloud

netconf
^^^^^^^

- netconf_rpc - Execute operations on NETCONF enabled network devices.

slxos
^^^^^

- slxos_l3_interface - Manage L3 interfaces on Extreme Networks SLXOS network devices.
- slxos_vlan - Manage VLANs on Extreme Networks SLX-OS network devices

Packaging
~~~~~~~~~

os
^^

- flatpak - Manage flatpaks
- flatpak_remote - Manage flatpak repository remotes

Storage
~~~~~~~

glusterfs
^^^^^^^^^

- gluster_peer - Attach/Detach peers to/from the cluster

netapp
^^^^^^

- na_ontap_aggregate - Manage NetApp ONTAP aggregates.
- na_ontap_broadcast_domain_ports - Manage NetApp Ontap broadcast domain ports
- na_ontap_cifs - Manage NetApp cifs-share
- na_ontap_cifs_acl - Manage NetApp cifs-share-access-control
- na_ontap_cifs_server - cifs server configuration
- na_ontap_cluster - Create/Join ONTAP cluster. Apply license to cluster
- na_ontap_cluster_ha - Manage HA status for cluster
- na_ontap_export_policy - Manage NetApp ONTAP export-policy
- na_ontap_export_policy_rule - Manage ONTAP Export rules
- na_ontap_igroup - ONTAP iSCSI igroup configuration
- na_ontap_interface - ONTAP LIF configuration
- na_ontap_iscsi - Manage NetApp Ontap iscsi service
- na_ontap_job_schedule - Manage NetApp Ontap Job Schedule
- na_ontap_license - Manage NetApp ONTAP protocol and feature licenses
- na_ontap_lun - Manage  NetApp Ontap luns
- na_ontap_lun_map - Manage NetApp Ontap lun maps
- na_ontap_net_ifgrp - Create, modify, destroy the network interface group
- na_ontap_net_port - Manage NetApp Ontap network ports.
- na_ontap_net_routes - Manage NetApp Ontap network routes
- na_ontap_net_vlan - Manage NetApp Ontap network vlan
- na_ontap_nfs - Manage Ontap NFS status
- na_ontap_ntp - Create/Delete/modify_version ONTAP NTP server
- na_ontap_qtree - Manage qtrees
- na_ontap_service_processor_network - Manage NetApp Ontap service processor network
- na_ontap_snapshot - Manage NetApp Sanpshots
- na_ontap_snmp - Manage NetApp SNMP community
- na_ontap_svm - Manage NetApp Ontap svm
- na_ontap_ucadapter - ONTAP UC adapter configuration
- na_ontap_user - useradmin configuration and management
- na_ontap_user_role - useradmin configuration and management
- na_ontap_volume - Manage NetApp ONTAP volumes.
- na_ontap_volume_clone - Manage NetApp Ontap volume clones.

Web Infrastructure
~~~~~~~~~~~~~~~~~~

- acme_account - Create, modify or delete accounts with Let's Encrypt

v2.6.0a1
========

Release Summary
---------------

| Release Date: 2018-05-21
| `Porting Guide <https://docs.ansible.com/ansible/devel/porting_guides.html>`_


Minor Changes
-------------

- Added an ``encoding`` option to the ``b64encode`` and ``b64decode`` filters to specify the encoding of the string that is base64 encoded.
- PowerShell modules that use Convert-ToSID in Ansible.ModuleUtils.SID.psm1 like win_user_right now accept an actual SID as an input string. This means any local or domain accounts that are named like a SID need to be prefixed with the domain, hostname, or . to ensure it converts to that accounts SID https://github.com/ansible/ansible/issues/38502
- `postgresql_user` module changed `encrypted=yes` to be the default. This shouldn't break any current playbooks, the module will just store passwords hashed by default. This change was done because Postgres 10 dropped support for `UNENCRYPTED` passwords and because all versions since Postgres 7.2 support storing encrypted passwords.
- azure_rm_loadbalancer - add support for sku
- azure_rm_publicipaddress - add support for sku
- cloudflare_dns module - Removed restriction from protocol to allow other protocols than tcp and udp to be specified.
- command module - Added argv option to allow command to be specified as a list vs. a string (https://github.com/ansible/ansible/issues/19392)
- gem - add ability to specify a custom directory for installing gems (https://github.com/ansible/ansible/pull/38195)
- import/include - Cache task_vars to speed up IncludedFile.process_include_results (https://github.com/ansible/ansible/pull/39026)
- postgresql_user module - Changed encrypted=yes to be the default. This shouldn't break any current playbooks, the module will just store passwords hashed by default. This change was done because Postgres 10 dropped support for UNENCRYPTED passwords and because all versions since Postgres 7.2 support storing encrypted passwords.
- vmware_target_canonical_facts module - The target_id parameter is an optional parameter.

Deprecated Features
-------------------

- nxos_igmp_interface module - The oif_prefix and oif_source properties are deprecated. Use the oif_ps parameter with a dictionary of prefix and source to values instead.

Removed Features (previously deprecated)
----------------------------------------

- win_chocolatey - removed deprecated upgrade option and choco_* output return values
- win_feature - removed deprecated reboot option
- win_iis_webapppool - removed the ability to supply attributes as a string in favour of a dictionary
- win_package - removed deprecated name option
- win_regedit - removed deprecated support for specifying HKCC as HCCC

Bugfixes
--------

- Document mode=preserve for both the copy and template module
- Fix an encoding issue when parsing the examples from a plugins' documentation
- Fix mode=preserve with remote_src=True for the copy module
- Implement mode=preserve for the template module
- The yaml callback plugin now allows non-ascii characters to be displayed.
- Various grafana_* modules - Port away from the deprecated b64encodestring function to the b64encode function instead. https://github.com/ansible/ansible/pull/38388
- copy - fixed copy to only follow symlinks for files in the non-recursive case
- copy module - The copy module was attempting to change the mode of files for remote_src=True even if mode was not set as a parameter.  This failed on filesystems which do not have permission bits (https://github.com/ansible/ansible/pull/40099)
- copy module - fixed recursive copy with relative paths (https://github.com/ansible/ansible/pull/40166)
- dynamic includes - Allow inheriting attributes from static parents (https://github.com/ansible/ansible/pull/38827)
- dynamic includes - Don't treat undefined vars for conditional includes as truthy (https://github.com/ansible/ansible/pull/39377)
- dynamic includes - Fix IncludedFile comparison for free strategy (https://github.com/ansible/ansible/pull/37083)
- dynamic includes - Improved performance by fixing re-parenting on copy (https://github.com/ansible/ansible/pull/38747)
- dynamic includes - Use the copied and merged task for calculating task vars (https://github.com/ansible/ansible/pull/39762)
- file - fixed the default follow behaviour of file to be true
- file module - Eliminate an error if we're asked to remove a file but something removes it while we are processing the request (https://github.com/ansible/ansible/pull/39466)
- file module - Fix error when recursively assigning permissions and a symlink to a nonexistent file is present in the directory tree (https://github.com/ansible/ansible/issues/39456)
- file module - Fix error when running a task which assures a symlink to a nonexistent file exists for the second and subsequent times (https://github.com/ansible/ansible/issues/39558)
- file module - The file module allowed the user to specify src as a parameter when state was not link or hard.  This is documented as only applying to state=link or state=hard but in previous Ansible, this could have an effect in rare cornercases.  For instance, "ansible -m file -a 'state=directory path=/tmp src=/var/lib'" would create /tmp/lib.  This has been disabled and a warning emitted (will change to an error in Ansible-2.10).
- import/include - Ensure role handlers have the proper parent, allowing for correct attribute inheritance (https://github.com/ansible/ansible/pull/39426)
- import_playbook - Pass vars applied to import_playbook into parsing of the playbook as they may be needed to parse the imported plays (https://github.com/ansible/ansible/pull/39521)
- include_role/import_role - Don't overwrite included role handlers with play handlers on parse (https://github.com/ansible/ansible/pull/39563)
- include_role/import_role - Fix parameter templating (https://github.com/ansible/ansible/pull/36372)
- include_role/import_role - Use the computed role name for include_role/import_role so to diffentiate between names computed from host vars (https://github.com/ansible/ansible/pull/39516)
- include_role/import_role - improved performance and recursion depth (https://github.com/ansible/ansible/pull/36470)
- pause - ensure ctrl+c interrupt works in all cases (https://github.com/ansible/ansible/issues/35372)
- spwd - With python 3.6 spwd.getspnam returns PermissionError instead of KeyError if user does not have privileges (https://github.com/ansible/ansible/issues/39472)
- template - Fix for encoding issues when a template path contains non-ascii characters and using the template path in ansible_managed (https://github.com/ansible/ansible/issues/27262)
- template action plugin - fix the encoding of filenames to avoid tracebacks on Python2 when characters that are not present in the user's locale are present. (https://github.com/ansible/ansible/pull/39424)
- user - only change the expiration time when necessary (https://github.com/ansible/ansible/issues/13235)
- win_environment - Fix for issue where the environment value was deleted when a null value or empty string was set - https://github.com/ansible/ansible/issues/40450
- win_file - fix issue where special chars like [ and ] were not being handled correctly https://github.com/ansible/ansible/pull/37901
- win_get_url - fixed a few bugs around authentication and force no when using an FTP URL
- win_template - fix when specifying the dest option as a directory with and without the trailing slash https://github.com/ansible/ansible/issues/39886
- win_updates - Fix logic when using a whitelist for multiple updates
- win_updates - Fix typo that hid the download error when a download failed
- windows become - Show better error messages when the become process fails
- winrm - allow `ansible_user` or `ansible_winrm_user` to override `ansible_ssh_user` when both are defined in an inventory - https://github.com/ansible/ansible/issues/39844
- winrm connection plugin - Fix exception messages sometimes raising a traceback when the winrm connection plugin encounters an unrecoverable error.  https://github.com/ansible/ansible/pull/39333

New Plugins
-----------

Callback
~~~~~~~~

- cgroup_memory_recap - Profiles maximum memory usage of tasks and full execution using cgroups
- grafana_annotations - send ansible events as annotations on charts to grafana over http api.
- sumologic - Sends task result events to Sumologic

Connection
~~~~~~~~~~

- httpapi - Use httpapi to run command on network appliances

Inventory
~~~~~~~~~

- foreman - foreman inventory source
- generator - Uses Jinja2 to construct hosts and groups from patterns
- nmap - Uses nmap to find hosts to target

Lookup
~~~~~~

- onepassword - fetch field values from 1Password
- onepassword_raw - fetch raw json data from 1Password

New Modules
-----------

Cloud
~~~~~

amazon
^^^^^^

- aws_caller_facts - Get facts about the user and account being used to make AWS calls.
- aws_inspector_target - Create, Update and Delete Amazon Inspector Assessment Targets
- aws_ses_identity_policy - Manages SES sending authorization policies
- aws_sgw_facts - Fetch AWS Storage Gateway facts
- ec2_eip_facts - List EC2 EIP details
- ec2_vpc_vpn_facts - Gather facts about VPN Connections in AWS.
- rds_instance_facts - obtain facts about one or more RDS instances
- rds_snapshot_facts - obtain facts about one or more RDS snapshots

azure
^^^^^

- azure_rm_aks - Manage a managed Azure Container Service (AKS) Instance.
- azure_rm_aks_facts - Get Azure Kubernetes Service facts.

cloudstack
^^^^^^^^^^

- cs_role_permission - Manages role permissions on Apache CloudStack based clouds.

digital_ocean
^^^^^^^^^^^^^

- digital_ocean_account_facts - Gather facts about DigitalOcean User account
- digital_ocean_certificate_facts - Gather facts about DigitalOcean certificates
- digital_ocean_domain_facts - Gather facts about DigitalOcean Domains
- digital_ocean_image_facts - Gather facts about DigitalOcean images
- digital_ocean_load_balancer_facts - Gather facts about DigitalOcean load balancers
- digital_ocean_region_facts - Gather facts about DigitalOcean regions
- digital_ocean_size_facts - Gather facts about DigitalOcean Droplet sizes
- digital_ocean_snapshot_facts - Gather facts about DigitalOcean Snapshot
- digital_ocean_tag_facts - Gather facts about DigitalOcean tags
- digital_ocean_volume_facts - Gather facts about DigitalOcean volumes

google
^^^^^^

- gcp_compute_address - Creates a GCP Address
- gcp_compute_backend_bucket - Creates a GCP BackendBucket
- gcp_compute_backend_service - Creates a GCP BackendService
- gcp_compute_health_check - Creates a GCP HealthCheck
- gcp_compute_http_health_check - Creates a GCP HttpHealthCheck
- gcp_compute_https_health_check - Creates a GCP HttpsHealthCheck
- gcp_compute_instance - Creates a GCP Instance
- gcp_compute_instance_template - Creates a GCP InstanceTemplate
- gcp_compute_network - Creates a GCP Network
- gcp_compute_route - Creates a GCP Route
- gcp_compute_subnetwork - Creates a GCP Subnetwork
- gcp_compute_target_http_proxy - Creates a GCP TargetHttpProxy
- gcp_compute_target_https_proxy - Creates a GCP TargetHttpsProxy
- gcp_compute_target_tcp_proxy - Creates a GCP TargetTcpProxy
- gcp_container_cluster - Creates a GCP Cluster
- gcp_container_node_pool - Creates a GCP NodePool
- gcp_dns_resource_record_set - Creates a GCP ResourceRecordSet
- gcp_pubsub_subscription - Creates a GCP Subscription
- gcp_pubsub_topic - Creates a GCP Topic
- gcp_storage_bucket - Creates a GCP Bucket
- gcp_storage_bucket_access_control - Creates a GCP BucketAccessControl

memset
^^^^^^

- memset_zone - Creates and deletes Memset DNS zones.

opennebula
^^^^^^^^^^

- one_host - Manages OpenNebula Hosts
- one_image - Manages OpenNebula images
- one_image_facts - Gather facts about OpenNebula images
- one_vm - Creates or terminates OpenNebula instances

openstack
^^^^^^^^^

- os_server_metadata - Add/Update/Delete Metadata in Compute Instances from OpenStack
- os_volume_snapshot - Create/Delete Cinder Volume Snapshots

scaleway
^^^^^^^^

- scaleway_compute - Scaleway compute management module
- scaleway_sshkey - Scaleway SSH keys management module

vmware
^^^^^^

- vmware_cluster_facts - Gather facts about clusters available in given vCenter
- vmware_datastore_cluster - Manage VMware vSphere datastore clusters
- vmware_datastore_maintenancemode - Place a datastore into maintenance mode
- vmware_guest_disk_facts - Gather facts about disks of given virtual machine
- vmware_guest_snapshot_facts - Gather facts about virtual machine's snapshots in vCenter
- vmware_host_capability_facts - Gathers facts about an ESXi host's capability information
- vmware_host_powerstate - Manages power states of host systems in vCenter
- vmware_local_user_facts - Gather facts about users on the given ESXi host
- vmware_portgroup_facts - Gathers facts about an ESXi host's portgroup configuration
- vmware_resource_pool_facts - Gathers facts about resource pool information
- vmware_tag - Manage VMware tags
- vmware_tag_facts - Manage VMware tag facts
- vmware_vswitch_facts - Gathers facts about an ESXi host's vswitch configurations

Clustering
~~~~~~~~~~

k8s
^^^

- k8s - Manage Kubernetes (K8s) objects

Commands
~~~~~~~~

- psexec - Runs commands on a remote Windows host based on the PsExec model

Monitoring
~~~~~~~~~~

- spectrum_device - Creates/deletes devices in CA Spectrum.

zabbix
^^^^^^

- zabbix_group_facts - Gather facts about Zabbix hostgroup

Net Tools
~~~~~~~~~

ldap
^^^^

- ldap_passwd - Set passwords in LDAP.

Network
~~~~~~~

aci
^^^

- aci_l3out - Manage Layer 3 Outside (L3Out) objects (l3ext:Out)

avi
^^^

- avi_autoscalelaunchconfig - Module for setup of AutoScaleLaunchConfig Avi RESTful Object
- avi_l4policyset - Module for setup of L4PolicySet Avi RESTful Object
- avi_useraccount - Avi UserAccount Module

cnos
^^^^

- cnos_command - Run arbitrary commands on Lenovo CNOS devices
- cnos_config - Manage Lenovo CNOS configuration sections

exos
^^^^

- exos_command - Run commands on remote devices running Extreme EXOS

f5
^^

- bigip_data_group - Manage data groups on a BIG-IP
- bigip_device_license - Manage license installation and activation on BIG-IP devices
- bigip_gtm_global - Manages global GTM settings
- bigip_gtm_monitor_bigip - Manages F5 BIG-IP GTM BIG-IP monitors
- bigip_gtm_monitor_firepass - Manages F5 BIG-IP GTM FirePass monitors
- bigip_gtm_monitor_http - Manages F5 BIG-IP GTM http monitors
- bigip_gtm_monitor_https - Manages F5 BIG-IP GTM https monitors
- bigip_gtm_monitor_tcp - Manages F5 BIG-IP GTM tcp monitors
- bigip_gtm_monitor_tcp_half_open - Manages F5 BIG-IP GTM tcp half-open monitors
- bigip_gtm_pool_member - Manage GTM pool member settings
- bigip_gtm_virtual_server - Manages F5 BIG-IP GTM virtual servers
- bigip_log_destination - Manages log destinations on a BIG-IP.
- bigip_log_publisher - Manages log publishers on a BIG-IP
- bigip_management_route - Manage system management routes on a BIG-IP
- bigip_profile_dns - Manage DNS profiles on a BIG-IP
- bigip_profile_tcp - Manage TCP profiles on a BIG-IP
- bigip_profile_udp - Manage UDP profiles on a BIG-IP
- bigip_service_policy - Manages service policies on a BIG-IP.
- bigip_smtp - Manages SMTP settings on the BIG-IP
- bigip_snmp_community - Manages SNMP communities on a BIG-IP.
- bigip_timer_policy - Manage timer policies on a BIG-IP
- bigip_trunk - Manage trunks on a BIG-IP
- bigiq_application_fasthttp - Manages BIG-IQ FastHTTP applications
- bigiq_application_fastl4_tcp - Manages BIG-IQ FastL4 TCP applications
- bigiq_application_fastl4_udp - Manages BIG-IQ FastL4 UDP applications
- bigiq_application_http - Manages BIG-IQ HTTP applications
- bigiq_application_https_offload - Manages BIG-IQ HTTPS offload applications
- bigiq_application_https_waf - Manages BIG-IQ HTTPS WAF applications
- bigiq_regkey_license_assignment - Manage regkey license assignment on BIG-IPs from a BIG-IQ.

files
^^^^^

- net_get - Copy files from a network device to Ansible Controller
- net_put - Copy files from Ansibe controller to a network device

fortios
^^^^^^^

- fortios_webfilter - Configure webfilter capabilities of FortiGate and FortiOS.

meraki
^^^^^^

- meraki_network - Manage networks in the Meraki cloud
- meraki_organization - Manage organizations in the Meraki cloud

netconf
^^^^^^^

- netconf_get - Fetch configuration/state data from NETCONF enabled network devices.

slxos
^^^^^

- slxos_command - Run commands on remote devices running Extreme Networks SLX-OS
- slxos_config - Manage Extreme Networks SLX-OS configuration sections
- slxos_facts - Collect facts from devices running Extreme SLX-OS
- slxos_interface - Manage Interfaces on Extreme SLX-OS network devices
- slxos_l2_interface - Manage Layer-2 interface on Extreme Networks SLXOS devices.
- slxos_linkagg - Manage link aggregation groups on Extreme Networks SLXOS network devices

Packaging
~~~~~~~~~

language
^^^^^^^^

- yarn - Manage node.js packages with Yarn

Source Control
~~~~~~~~~~~~~~

- gitlab_deploy_key - Manages GitLab project deploy keys.
- gitlab_hooks - Manages GitLab project hooks.

Storage
~~~~~~~

netapp
^^^^^^

- na_ontap_broadcast_domain - Manage NetApp ONTAP broadcast domains.

purestorage
^^^^^^^^^^^

- purefa_ds - Configure FlashArray Directory Service
- purefa_facts - Collect facts from Pure Storage FlashArray
- purefa_pgsnap - Manage protection group snapshots on Pure Storage FlashArrays
- purefb_fs - Manage filesystemon Pure Storage FlashBlade`
- purefb_snap - Manage filesystem snapshots on Pure Storage FlashBlades

System
~~~~~~

- sysvinit - Manage SysV services.

Windows
~~~~~~~

- win_domain_computer - Manage computers in Active Directory
- win_hostname - Manages local Windows computer name.
- win_pester - Run Pester tests on Windows hosts
