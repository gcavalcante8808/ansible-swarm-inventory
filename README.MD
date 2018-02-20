Ansible Swarm Inventory
-----------------------

This project aims to provide a dynamic inventory script that allows admins and software engineers to retrieve
containers information based on the service/stack hierarchy. Of Course, you can use that information to write
playbooks and then execute ad-hoc commands against services in the cluster.

Some simple ideas that comes to mind:

 * Turn WordpressFS(core) writeable, call upgrade API, put it read-only again;
 * Execute databases backups;
 * Execute django ad-hoc commands (manage.py commands);
 * Execute laravel/artisan commands;


How To Use
----------

Use the swarm_inventory.py or the compilled' version with your ansible-playbook command, like:

```
ansible-playbook -i swarm_inventory.py playbook.yml
```

WorkFlow
--------

1. Discover all services and its roles:

We need a tag called com.ansible.role inside every service; if a service don't have this tag, so it ain't gonna be picked in the inventory proccess.

A compose like the following should do the work:

version: '3'
volumes:
  db:

services:
  db:
    image: postgres:9.5
    networks:
     - default
    deploy:
      replicas: 1
      restart_policy:
        condition: on-failure
        delay: 20s
        max_attempts: 3
        window: 120s
      labels:
       - com.df.notify=true
       - com.ansible.role=postgres

    environment:
      POSTGRES_DB: mydb
      POSTGRES_USER: mydb
      POSTGRES_PASSWORD: ultra@secure
    volumes:
     - db:/var/lib/postgresql/data

2. Ansible Structure Inspection:

The service will be the host group, the owners are the swarm nodes (ip) and work_type is the com.ansible.role value.

So we have the following structure:

`"hostgroup" : { "hosts": [], vars: {"owners": [] }}`

For the DB service, the following output would be returned:

service: { "hosts": [tasks], vars: {"owners": [nodes], "work_type": label.role}}`

"db": { "hosts": ["container1","container2"], vars: {"owners": ["node1","node2"], work_type: "mysql"}}

host: "container1" --> ansible_host: "node1"

hosts file

container1  ansible_host: node1
Vars:
    Hosts: A list of containers ID's that will answer for the service.
    Owners: The owners will receive the delegate_to definition from ansible.
    
    Task and Owners should be a tuple.

About
-----

This is a pre-alpha stage for this work. As such, some features are not covered:

```
 * Run the command just in one container even if a service has been scaled to more than 1.
```

Remember, that work is volunteer and, as such, comes with no WARRANTY.

Any PR's or issue submit is more than welcome.

Author: Gabriel Abdalla Cavalcante Silva (gabriel.cavalcante88@gmail.com)
