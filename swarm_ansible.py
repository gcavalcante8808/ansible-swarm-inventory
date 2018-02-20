#!/usr/bin/env python 

import pdb
import docker
import json


cli = docker.from_env()

"""
1. Discover all services and its roles:

We need a tag called role inside every service. A compose like the following should do the work:

version: '3'
volumes:
  db:
    driver: convoy

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
       - com.ansible.role = postgres

    environment:
      POSTGRES_DB: gogs
      POSTGRES_USER: gogs
      POSTGRES_PASSWORD: bjork8d336@rfb
    volumes:
     - gogsdb:/var/lib/postgresql/data

2. Ansible Structure Inspection:


"hostgroup" : { "hosts": [], vars: {"owners": [] }}
service: { "hosts": [tasks], vars: {"owners": [nodes], "work_type": label.role}}

Full Example:

"semaphore_db": { "hosts": ["container1","container2"], vars: {"owners": ["node1","node2"], work_type: "mysql"}}

host: "container1" --> ansible_host: "node1"

hosts file

container1  ansible_host: node1
Vars:
    Hosts: A list of containers ID's that will answer for the service.
    Owners: The owners will receive the delegate_to definition from ansible.
    
    Task and Owners should be a tuple.
"""

def get_owners_list(service):
    """ return a list of owner's ip's """
    tasks = service.tasks()
    nodes_list = [ task.get('NodeID') for task in tasks ]
    nodes = [ {'node': cli.nodes.get(node).attrs["Description"]["Hostname"],
               'addr': cli.nodes.get(node).attrs['Status']['Addr'] 
              } for node in nodes_list ]

    return nodes

def get_owner(container):
    """ Docker Swarm mode refers to containers as tasks when running in cluster.
    This function get the owner(docker node) where the container is running.
    """
    node_id = container.get('NodeID')
    node = {'node': cli.nodes.get(node_id).attrs["Description"]["Hostname"], 'addr': cli.nodes.get(node_id).attrs['ManagerStatus']['Addr'].split(":")[0] }
    return node

services_list = cli.services.list()

services = [ service for service in services_list 
             if service.attrs['Spec']['Labels'].get('com.ansible.role', False) ]

inventory = {}


#TODO: Just return running containers

if services:
    for service in services:
        stack =  service.attrs['Spec']['Labels'].get('com.docker.stack.namespace')
        inventory.update({service.name: {"hosts": [], "vars": {}}})
        for container in service.tasks():
            if 'running' in container['Status']['State']:
                inventory[service.name]["hosts"].append(container['Status']['ContainerStatus']['ContainerID'])
                inventory[service.name]["vars"].update({'role': service.attrs['Spec']['Labels'].get('com.ansible.role', False)})
                inventory[service.name]["vars"].update({'stack': stack})
                inventory[service.name]["vars"].update({'ansible_host': get_owner(container).get('addr')})

print(json.dumps(inventory, indent=2))
