from pprint import pprint
from jnpr.junos import Device

dev = Device(host='10.1.5.222', user='admin', password='admin@123')
dev.open()

pprint(dev.facts)

dev.close()
