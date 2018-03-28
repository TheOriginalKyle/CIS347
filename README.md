# CIS347 Python Script

This code is for a Software Defined Networking (SDN) project using Open Daylight (ODL) in CIS347 Telecommunications Networks. Before this script will run you need to change the ip and access credentials hardcoded in the script.

## Dependencies (May not be 100% correct)
* Python 2
* Yaml
  * Ubuntu 12.04: https://launchpad.net/ubuntu/precise/+package/python-yaml
* Logging
  * Should be included by default in Python 2
* Datetime
  * Should be included by default in Python 2
* py-junos-eznc (PYEZ)
  * See: https://github.com/Juniper/py-junos-eznc
  * You will probably need pip. https://launchpad.net/ubuntu/precise/+package/python-pip
* ODL Nitrogen SR2
  * See: https://www.opendaylight.org/technical-community/getting-started-for-developers/downloads-and-documentation


## Be sure to change hardcoded ip's and credentials to match your config.
```python
odl_ip = "*your ip here*"
username = "*your opendaylight username*"
password = "*your opendaylight password*"

host = "*your switch's ip (the same one you use for ssh*"
switch_user = "*Your switch's username*"
switch_password = "*Your switch's password*"
```

## Also be sure to create the file CIS347-Device-Log.log
Otherwise the script will crash. This log contains a list of every node whose mac is be bound and to what port it was bound to. CIS347.log also contains all the debug related output.

## Note by default ODL Nitrogen does not come with **ANY** features installed by default.
You also should **NOT** install all of the features. About half of them are incompatible with eachother. 
The features you need are: 
* odl-dluxapps-applications (To make your life easier you don't actually need it)
* odl-restconf
* odl-l2switch-switch-ui
* odl-ovsdb-southbound-impl-ui(?) 

See here: http://docs.opendaylight.org/en/stable-nitrogen/getting-started-guide/installing_opendaylight.html

AND here: http://www.brianlinkletter.com/using-the-opendaylight-sdn-controller-with-the-mininet-network-emulator/

The full effects of this script is that everytime it is ran it will ask ODL for all the nodes it will see. It will then parse through that JSON object for all the mac addresses then compare it with the Ethernet Switching table. When they match up it will lock the ports on each individual interface to the mac ODL sees. 

## Troubleshooting
1. Do you see any nodes in the Yang-Ui Topology?

  > The script **WILL** crash if the JSON object it recieves is empty. This could probably be fixed but I found this bug helpful as if it were fixed nothing would happen with no error messages.

2. Do you have all the libraries? 

  > I just included the ones I could remember if there's one that should be added do let me know.
  
3. Is the alarm set to POE?

  > This script uses python2.
  
5. Is it parsing the JSON correctly? Or are you on the right version?

  > I wrote this for Nitrogen it wont parse correctly on most other versions.

