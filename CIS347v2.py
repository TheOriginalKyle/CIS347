# CIS 347 Group 4: Kyle, Ernesto, Brandon, Amy, Ricky, Don, Toby
import requests
import yaml
import logging
import datetime

from jnpr.junos import Device
from jnpr.junos.utils.config import Config
from jnpr.junos.factory.factory_loader import FactoryLoader

# This creates a log file titled 'CIS347.log', sets the level to debug and formats it for 'current time | how big the issue is | the actual message'.
# See https://docs.python.org/2/library/logging.html
logging.basicConfig(filename='CIS347.log',level=logging.DEBUG,format='%(asctime)s | %(levelname)s | %(message)s')
# This script will crash if this file does not exist.
file_object = open('CIS347-Device-List.log', 'a')

# OpenDayLight RESTCONF API settings.
# SET THESE TO MATCH YOUR CONFIG.
odl_ip = "192.168.140.253"
username = "admin"
password = "admin"
odl_url = 'http://' + odl_ip + ':8181/restconf/operational/network-topology:network-topology'
odl_username = username
odl_password = password

# Fetch information from API.
response = requests.get(odl_url, auth=(odl_username, odl_password))

# Find information about nodes in retrieved JSON file.
odl_macs = []

# If the script crashes in one of these two for loops you are parsing the json incorrectly. (Probably because you're running a different version of ODL.)
# Uncomment one of these if its parsing incorrectly.
# print response.json()
# print response.json()['network-topology']['topology']
for nodes in response.json()['network-topology']['topology'][1]:
    # Walk through all node information.
    node_info = response.json()['network-topology']['topology'][1]
    # Look for Mac and IP addresses in node information.
    for node in node_info['node']:
        # If the script crashes in this for loop you would have no idea.
        # This is because of except: pass you'll know if it crashes if nothing is printed from odl parse.
        try:
            ip_address = node['host-tracker-service:addresses'][0]['ip']
            mac_address = node['host-tracker-service:addresses'][0]['mac']
            odl_parse = 'Found host with MAC address %s and IP address %s' % (mac_address, ip_address)
            odl_macs.append(mac_address)
            #print('this is odl parse')
            print(odl_parse)
            #print('done with odl parse')
        except:
            print('\n')
            pass

# Part 2 ---------------------------------------------------------------------------------------------------
# Yaml organization for EthernetSwitchingTable Entries.
yaml_data = '''
---
EtherSwTable:
  rpc: get-interface-ethernet-switching-table
  item: ethernet-switching-table/mac-table-entry[mac-type='Learn']
  key: mac-address
  view: EtherSwView
EtherSwView:
  fields:
    vlan_name: mac-vlan
    mac: mac-address
    mac_type: mac-type
    mac_age: mac-age
    interface: mac-interfaces-list/mac-interfaces
'''
# Login to switch
# CHANGE THIS TO MATCH YOUR CONFIG.
host = "192.168.140.1"
switch_user = "root"
switch_password = "Admin12345"
dev = Device(host='%s' % (host),user='%s' % (switch_user),password='%s' %(switch_password))
dev.open()

# Retrieve EthernetSwitchingTable info
globals().update(FactoryLoader().load(yaml.load(yaml_data)))
table = EtherSwTable(dev)
table.get()

# Organize EthernetSwitchingTable entries
mac_table = []
for i in table:
    print 'vlan_name:', i.vlan_name
    print 'mac:', i.mac
    mac_table.append(i.interface + '|' + i.mac)
    print 'mac_type:', i.mac_type
    print 'mac_age:', i.mac_age
    print 'interface:', i.interface
    print ('\n')

# Compare MACs from ODL and EthernetSwitchingTable Table
# If you never see anything from the cu.diff() line thats because odl_macs is empty.
# Probably because your on a different version and the JSON is different than the one this script is written for. (Nitrogen)
mac_set = [i for e in odl_macs for i in mac_table if e in i]

# Automate the port security for each entry in final list.
config_add =[]
config_light=[]
for i in mac_set:
    mac = [i.split('|', 1)[1]]
    new_mac = mac.pop()
    interface = [i.split('|', 1)[0]]
    interface = [i[:-2] for i in interface]
    new_interface = interface.pop()
    today = datetime.datetime.now()
    # Writes down all mac binded devices to a log file.
    # This script will crash if the file does not exist.
    # Format is 'Current time in year-month-day - Hour:Minute:Second,millisecond | Binding Mac | *some mac address* | *some interface*
    file_object.write(today.strftime('%Y-%m-%d - %H:%M:%S,%f') + ' | ' + 'Binding Mac | ' + new_mac + ' | ' + new_interface + '\n')
    # Adds the mac that will be locked on that interface to the config.
    config_add.append('set interface %s allowed-mac %s' % (new_interface, new_mac))
    # Change to delete to turn led off.
    config_light.append('set poe interface %s' % (new_interface))

# Puts the config in the format Junos is expecting.
set_add = '\n'.join(map(str,config_add))
# These are seperate due to the way config_script sets it.
light_add = '\n'.join(map(str,config_light))

# Probably could merge this with set_add but ¯\_(ツ)_/¯
config_script = """
edit ethernet-switching-options secure-access-port
%s
""" % (set_add)

# Load and Commit the configuration to the switch
cu = Config(dev)
# Merges the config with the currently running config. 
# Probably could've merged light_add with config_script but if it aint broke.
cu.load(config_script, format="set", merge=True)
cu.load(light_add, format="set", merge=True)
# This try catch is here in case there's no difference between the running config and the proposed one.
# If you never see a difference and the ports aren't locking you are on a different version of ODL.
try:
    print 'These are the changes:\n ' + cu.diff()
except:
    print 'Nothing changed?'
# Commits the config. This could be put in the try catch but it won't hurt Junos to commit one with no changes.
cu.commit()
print "Configuration Successful! Goodbye."
dev.close()
