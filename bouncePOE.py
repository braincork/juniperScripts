from jnpr.junos import Device
from pprint import pprint as pp
import yaml
from jnpr.junos.factory.factory_loader import FactoryLoader
from jnpr.junos.utils.config import Config
import time
from getpass import getpass

networkDevice = raw_input("Enter IP Address of Switch: ")
userName = raw_input("Login Username: ")
password = getpass("Login Password: ")
mac = raw_input("MAC Address of device to reset(this format - a1:b2:c3:d4:e5:f6): ")

yml = '''
---
EtherSwTable:
  rpc: get-ethernet-switching-table-information
  item: l2ng-l2ald-mac-entry-vlan/l2ng-mac-entry
  key:
      - l2ng-l2-mac-address
      - mac-count-global
      - learnt-mac-count
      - l2ng-l2-mac-routing-instance
      - l2ng-l2-vlan-id
      - l2ng-mac-entry
  view: EtherSwView

EtherSwView:
  fields:
    vlan_name: l2ng-l2-vlan-name
    mac: l2ng-l2-mac-address
    interface: l2ng-l2-mac-logical-interface
'''

globals().update(FactoryLoader().load(yaml.load(yml)))

dev = Device( user=userName, host=networkDevice, password=password ).open()

table = EtherSwTable(dev).get(address=mac)
print table.values()
print

for i in table:
    print 'interface: ', i.interface
    ifaceName = i.interface.replace(".0", "")
    print 'mac: ', i.mac
    print
    print ifaceName

with Config(dev, mode='private') as cu:
    cu.load("set poe interface " + ifaceName + " disable", format='set', merge=True)
    cu.pdiff()
    print("Disabling POE on interface {}".format(ifaceName))
    cu.commit(timeout=30)
    print("Waiting 60 seconds to rollback configuration.")
    time.sleep(60)
    print("Re-enabling POE on interface {}".format(ifaceName))
    cu.rollback(rb_id=1)
    cu.commit(timeout=30)

dev.close() 
