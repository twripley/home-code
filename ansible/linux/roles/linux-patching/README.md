linux-patching
=========

This role automates patching of a Linux server.  It will take a vCenter snapshot of the guest, then start patching.
Once patching is done it will automatically reboot if needed.
Emails are sent out to notify users of the patching progress.

Requirements
------------

@TODO
Any pre-requisites that may not be covered by Ansible itself or the role should be mentioned here. For instance, if the role uses the EC2 module, it may be a good idea to mention in this section that the boto package is required.

Role Variables
--------------

@TODO
A description of the settable variables for this role should go here, including any variables that are in defaults/main.yml, vars/main.yml, and any variables that can/should be set via parameters to the role. Any variables that are read from other roles and/or the global scope (ie. hostvars, group vars, etc.) should be mentioned here as well.

Dependencies
------------

@TODO
Ansible VMware modules (vmware_guest and vmware_guest_snapshot)
A list of other roles hosted on Galaxy should go here, plus any details in regards to parameters that may need to be set for other roles, or variables that are used from other roles.

Example Playbook
----------------

@TODO
Including an example of how to use your role (for instance, with variables passed in as parameters) is always nice for users too:

    - hosts: servers
      roles:
         - { role: username.rolename, x: 42 }

License
-------

@TODO
BSD

Author Information
------------------

@TODO
An optional section for the role authors to include contact information, or a website (HTML is not allowed).
