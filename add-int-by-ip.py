#!/usr/bin/env python

# Another form of add-int.py.. used to meet some specific change needs at some
# point.  Just locates existing system by IP of existing Static Interface.
# If a duplicate name exists, it attempts to get around it.

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
    if 'ip' not in reader.fieldnames or 'mac' not in reader.fieldnames or 'dest_range' not in reader.fieldnames or 'domain' not in reader.fieldnames:
        print "Must at least have ip, ctnr, dest_range, and domain fields in your CSV file."
        sys.exit(1)
    for host in reader:
        if not host['ip'] or not host['mac'] or not host['dest_range'] or not host['domain']:
            print "Not enough values in row: {0}".format(host)
            continue
        try:
            si = StaticInterface.objects.get(ip_str=host['ip'])
        except StaticInterface.DoesNotExist:
            print "FQDN {0} not found, skipping.".format(host['ip'])
            continue
        if 'new_ip' in reader.fieldnames:
            if host['new_ip']:
                the_ip_str=host['new_ip']
        else:
            try:
                target_range = Range.objects.get(start_str=host['dest_range'])
                the_ip_str = target_range.get_next_ip()
            except Range.DoesNotExist:
                print "Range {0} not found, skipping {1}.".format(host['dest_range'],host['ip'])
                continue
        new_si = StaticInterface(ctnr=si.system.ctnr,
                             system=si.system,
                                 label=host['name'].split('.')[0],
                                 #domain=Domain.objects.get(name=host['fqdn'].split('.',1)[1]),
                                 domain=Domain.objects.get(name=host['domain']),
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
            new_si.label = new_si.label+'n'
            try:
                new_si.save()
                new_si.views.add(public)
                new_si.views.add(private)
            except ValidationError,e:
                print "Failed to add SI for {0}: {1}".format(new_si.system.name,str(e))
