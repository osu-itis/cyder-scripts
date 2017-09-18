#!/usr/bin/env python
import activate
activate.activate()
from cyder.models import *

# this script needs work.. its very simple, as in, dumb.  It is modified to
# to meet the needs of whatever change is requested beyond changing fqdns.
# Also updates system name to match.


attr_location = Attribute.objects.get(name="Location",attribute_type='i')
attr_serial = Attribute.objects.get(name__contains="Serial",attribute_type='i')
attr_hardware = Attribute.objects.get(name__contains="Hardware",attribute_type='i')
attr_owning = Attribute.objects.get(name__contains="Owning",attribute_type='i')
attr_department = Attribute.objects.get(name__contains="Department",attribute_type='i')
attr_os = Attribute.objects.get(name__contains="Operating",attribute_type='i')

fd = open('rename-hosts.csv','r')

networks_list = []
changed = False

for line in fd.readlines():
    entry = line.strip('\t\r\n ').split(',')
    try:
        the_host = StaticInterface.objects.get(fqdn=entry[0])
    except StaticInterface.DoesNotExist:
        print "{0} does not exist, doing nothing.".format(entry[0])
        continue
    if the_host.system.name != entry[1].split('.',1)[0]:
        print "System: {0} -> {1}".format(the_host.system.name, entry[1].split('.',1)[0])
        the_host.system.name = entry[1].split('.',1)[0]
        the_host.system.save()
    new_label, new_domain = entry[1].split('.',1)
    if the_host.label != new_label:
        changed=True
        print "Updating label."
        the_host.label = new_label
    if the_host.domain != Domain.objects.get(name=new_domain):
        changed=True
        print "Updating domain."
        the_host.domain = Domain.objects.get(name=new_domain)
    if len(entry) > 2:
        print "Updating IP"
        the_host.ip_str = entry[2]
        # might need to change workgroup because of permissions, net changes
        #the_host.workgroup = Workgroup.objects.get(name="Default")
        changed=True
    if len(entry) > 3:
        print "Changing ctnr"
        the_host.system.ctnr=Ctnr.objects.get(name=entry[3])
        the_host.system.save()
        changed=True
    if len(entry) > 4:
        print "changing serial number"
        eav = SystemAV(entity=the_host.system, attribute=attr_serial, value=entry[4])
        try:
            eav.full_clean()
            eav.save()
        except:
            print "not changing serial"
    if changed:
        the_host.save()
        changed=False
