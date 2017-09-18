#!/usr/bin/env python

# Add csv of interfaces to existing systems based on fqdn...dumb

import sys
import activate
activate.activate()
from cyder.models import *
import csv

public = View.objects.get(name="public")
private = View.objects.get(name="private")

with open(sys.argv[1]) as host_list:
    reader = csv.DictReader(host_list)
    print reader.fieldnames
    if 'fqdn' not in reader.fieldnames or 'mac' not in reader.fieldnames or 'dest_range' not in reader.fieldnames:
        print "Must at least have fqdn, ctnr, and dest_range fields in your CSV file."
        sys.exit(1)
    for host in reader:
        if not host['fqdn'] or not host['mac'] or not host['dest_range']:
            print "Not enough values in row: {0}".format(host)
            continue
        try:
            si = StaticInterface.objects.get(fqdn=host['fqdn'])
        except StaticInterface.DoesNotExist:
            #print "FQDN {0} not found, checking dynamic.".format(host['fqdn'])
            try:
                si = DynamicInterface.objects.get(mac=host['mac'],system__name=host['fqdn'].split('.')[0])
            except DynamicInterface.DoesNotExist:
                print "Dynamic interface not found, skipping {0}.".format(host['fqdn'])
        if 'ip' in reader.fieldnames:
            if host['ip']:
                the_ip_str=host['ip']
        else:
            try:
                target_range = Range.objects.get(start_str=host['dest_range'])
                the_ip_str = target_range.get_next_ip()
            except Range.DoesNotExist:
                print "Range {0} not found, skipping {1}.".format(host['dest_range'],host['fqdn'])
                continue
        new_si = StaticInterface(ctnr=si.system.ctnr,
                             system=si.system,
                                 label=host['fqdn'].split('.')[0],
                                 domain=Domain.objects.get(name=host['fqdn'].split('.',1)[1]),
                                 workgroup=Workgroup.objects.get(name="Default"),
                                 mac=host['mac'],
                                 ip_str=the_ip_str,
                                 dhcp_enabled=True,
                                 dns_enabled=True,
                                 ttl=86400,
                                 ip_type='4')
        try:
            new_si.save()
            new_si.views.add(public)
            new_si.views.add(private)
            print "Saved {0}.".format(new_si.fqdn)
        except ValidationError,e:
            original_label = si.label
            new_si.label = new_si.label+'-1'
            #new_si.domain = Domain.objects.get(name="cosine.oregonstate.edu")
            try:
                new_si.save()
                new_si.views.add(public)
                new_si.views.add(private)
                print "Saved {0} after changing domain.".format(new_si.fqdn)
            except ValidationError,e:
                print "Failed to add SI for {0}: {1}".format(new_si.system.name,str(e))
