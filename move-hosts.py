#!/usr/bin/env python
import sys
import activate
activate.activate()
from cyder.models import *
import csv

# move static ifaces from one range to another, and another container (potentially)


with open(sys.argv[1]) as host_list:
    reader = csv.DictReader(host_list)
    print reader.fieldnames
    if 'fqdn' not in reader.fieldnames or 'ctnr' not in reader.fieldnames or 'dest_range' not in reader.fieldnames:
        print "Must at least have fqdn, ctnr, and dest_range fields in your CSV file."
        sys.exit(1)
    for host in reader:
        if not host['fqdn'] or not host['ctnr'] or not host['dest_range']:
            print "Not enough values in row: {0}".format(host)
            continue
        try:
            si = StaticInterface.objects.get(fqdn=host['fqdn'])
            print si.workgroup
        except StaticInterface.DoesNotExist:
            print "FQDN {0} not found, skipping.".format(host['fqdn'])
            continue
        if 'ip' in reader.fieldnames and host['ip']:
            si.ip_str=host['ip']
        else:
            try:
                target_range = Range.objects.get(start_str=host['dest_range'])
                si.ip_str = target_range.get_next_ip()
            except Range.DoesNotExist:
                print "Range {0} not found, skipping {1}.".format(host['dest_range'],host['fqdn'])
                continue
        try:
            new_ctnr = Ctnr.objects.get(name=host['ctnr'])
        except Ctnr.DoesNotExist:
            print "Ctnr {0} not found, skipping {1}.".format(host['ctnr'],host['fqdn'])
            continue
        # might need to change these!
        #si.workgroup = Workgroup.objects.get(name="sccm-engr")
        #si.domain = Domain.objects.get(name="tss.oregonstate.edu")
        si.system.ctnr = new_ctnr
        si.system.save()
        si.save()



