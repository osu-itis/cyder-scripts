#!/usr/bin/env python
import sys
import activate
activate.activate()
from cyder.models import *
import csv

# read CSV and make System/SI from file.
# tries to get around name conflicts by appending letter to hostname

public = View.objects.get(name="public")
private = View.objects.get(name="private")
attr_location = Attribute.objects.get(name="Location",attribute_type='i')
attr_serial = Attribute.objects.get(name__contains="Serial",attribute_type='i')
attr_hardware = Attribute.objects.get(name__contains="Hardware",attribute_type='i')
attr_owning = Attribute.objects.get(name__contains="Owning",attribute_type='i')
attr_department = Attribute.objects.get(name__contains="Department",attribute_type='i')
attr_os = Attribute.objects.get(name__contains="Operating",attribute_type='i')

with open(sys.argv[1]) as host_list:
    reader = csv.DictReader(host_list)
    print reader.fieldnames
    if 'mac' not in reader.fieldnames or 'ctnr' not in reader.fieldnames or 'dest_range' not in reader.fieldnames or 'fqdn' not in reader.fieldnames:
        print "Must at least have mac, ctnr, fqdn, and dest_range fields in your CSV file."
        sys.exit(1)

    for host in reader:
        if not host['mac'] or not host['ctnr'] or not host['dest_range'] or not host['fqdn']:
            print "Not enough values in row: {0}".format(host)
            continue
        # Find Range
        try:
            the_range = Range.objects.get(start_str=host['dest_range'])
        except:
            print "Range {0} not found, skipping {1}!".format(host['dest_range'],host['mac'])
            continue
        # Find Ctnr
        try:
            new_ctnr = Ctnr.objects.get(name=host['ctnr'])
        except Ctnr.DoesNotExist:
            print "Ctnr {0} not found, skipping {1}!".format(host['ctnr'],host['mac'])
            continue
        # Find Workgroup
        if 'workgroup' in host:
            the_workgroup = Workgroup.objects.get(name=host['workgroup'])
        else:
            the_workgroup = Workgroup.objects.get(name='Default')
        # Static/Dynamic?
        if the_range.range_type == 'dy':
            if the_range.dynamicinterface_set.filter(mac=host['mac']):
                print "Interface with this MAC already exists in range."
                continue
            new_system = System(ctnr=new_ctnr,
                                name=host['fqdn'])
            new_system.save()

            iface = DynamicInterface(range=the_range,
                                     system=new_system,
                                     workgroup=the_workgroup,
                                     mac=host['mac'],
                                     dhcp_enabled=True)
            try:
                iface.save()
                print "Saved {0}".format(host['fqdn'])
            except ValidationError:
                print "Can't create interface for {0} - skipping!".format(host['mac'])
                new_system.delete()
                continue
        else:
            if the_range.staticinterfaces.filter(mac=host['mac']):
                print "Interface with this MAC already exists in dest_range: {0}, skipping {1}!".format(host['mac'],host['fqdn'])
                continue
            new_system = System(ctnr=new_ctnr,name=host['fqdn'].split('.')[0])
            new_system.save()
            # Domain valid?
            new_domain = Domain.objects.get(name=host['fqdn'].split('.',1)[1])

            if 'ip' in host:
                the_ip_str = host['ip']
            else:
                the_ip_str = str(the_range.get_next_ip())
            iface = StaticInterface(ctnr=new_ctnr,
                                 system=new_system,
                                 label=new_system.name,
                                 domain=new_domain,
                                 workgroup=the_workgroup,
                                 mac=host['mac'],
                                 ip_str=the_ip_str,
                                 dhcp_enabled=True,
                                 dns_enabled=True,
                                 ttl=86400,
                                 ip_type='4')
            try:
                iface.save()
                print "Saved {0}.".format(host['fqdn'])
            except ValidationError,e:
                print e
                original_label = iface.label
                iface.label = iface.label+'a'
                try:
                    iface.save()
                    print "Saved {0} after appending 'a'.".format(host['fqdn'])
                except ValidationError,e:
                    iface.label = original_label+'b'
                    try:
                        iface.save()
                    except:
                        print "Failed to create {0}".format(host['fqdn'])
                        new_system.delete()
                        continue
                    print "Saved {0} after appending 'b'.".format(host['fqdn'])
            iface.views.add(public)
            iface.views.add(private)
        if 'serial_number' in host:
            eav = SystemAV(entity=iface.system, attribute=attr_serial, value=host['serial_number'])
            eav.full_clean()
            eav.save()
        if 'location' in host:
            eav = SystemAV(entity=iface.system, attribute=attr_location, value=host['location'])
            eav.full_clean()
            eav.save()
        if 'hardware_type' in host:
            eav = SystemAV(entity=iface.system, attribute=attr_hardware, value=host['hardware_type'])
            eav.full_clean()
            eav.save()
        if 'owning_unit' in host:
            eav = SystemAV(entity=iface.system, attribute=attr_owning, value=host['owning_unit'])
            eav.full_clean()
            eav.save()
        if 'department' in host:
            eav = SystemAV(entity=iface.system, attribute=attr_department, value=host['department'])
            eav.full_clean()
            eav.save()
        if 'operating_system' in host:
            eav = SystemAV(entity=iface.system, attribute=attr_os, value=host['operating_system'])
            eav.full_clean()
            eav.save()
