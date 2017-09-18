#!/usr/bin/env python

# this is unfinished, do not use without proper testing.
# is supposed to copy all interfaces from one range to another.

import sys
import activate
activate.activate()
from cyder.models import *
from cyder.cydhcp.constants import STATIC, DYNAMIC
from optparse import OptionParser
parser = OptionParser()
parser.add_option("-d","--domain",dest="domain")
parser.add_option("-o","--old-range",dest="oldrange")
parser.add_option("-n","--new-range",dest="newrange")
parser.add_option("-c","--ctnr",dest="ctnr",help="Source Ctnr")
parser.add_option("-a","--append-number",dest="append",action="store_true",default=False)
parser.add_option("-t","--dry-run",dest="dryrun",action="store_true",default=False)
parser.add_option("-w","--workgroup",dest="workgroup")

(options, args) = parser.parse_args()

if not options.oldrange or not options.newrange:
    print "Both the --old-range and --new-range options must be set!"
    sys.exit()
try:
    source_range_start = struct.unpack("!L", socket.inet_aton(options.oldrange))[0]
    source_range = Range.objects.get(start_lower=source_range_start)
    source_range_end = source_range.end_lower
except Range.DoesNotExist, e:
    print "Old range not found - ".format(e)

try:
    target_range_start = struct.unpack("!L", socket.inet_aton(options.newrange))[0]
    target_range = Range.objects.get(start_lower=target_range_start)
    target_range_end = target_range.end_lower
except Range.DoesNotExist, e:
    print "New range not found - ".format(e)

if target_range.range_type == STATIC:
    if not options.domain or not options.ctnr:
        print "Need both a domain and ctnr when copying to static range."
        sys.exit()
else:
    if options.domain:
        print "Domain is not needed when copying to dynamic range."
        sys.exit()
    if not options.ctnr:
        print "Ctnr is required."
        sys.exit()

the_ctnr = Ctnr.objects.get(name=options.ctnr)
the_domain = Domain.objects.get(name=options.domain)
if options.workgroup:
    the_workgroup = Workgroup.objects.get(name=options.workgroup)
else:
    the_workgroup = Workgroup.objects.get(name="Default")

public = View.objects.get(name="public")
private = View.objects.get(name="private")

if options.dryrun:
    print "DRY-RUN MODE. NO CHANGES WILL BE COMMITTED!"

if target_range.range_type == STATIC:
    if source_range.range_type == STATIC:
        all_static_ifaces = StaticInterface.objects.filter(ip_lower__lte=source_range_end,
                                                           ip_lower__gte=source_range_start)
        for static_iface in all_static_ifaces:
            si = StaticInterface(label        = static_iface.label,
                                 domain       = the_domain,
                                 workgroup    = the_workgroup,
                                 ttl          = 86400,
                                 ip_str       = str(target_range.get_next_ip()),
                                 mac          = static_iface.mac,
                                 dns_enabled  = True,
                                 dhcp_enabled = True,
                                 ip_type      = '4',
                                 # create new system or use old one?
                                 system       = static_iface.system)
        try:
            if not options.dryrun:
                si.save()
                si.views.add(public)
                si.views.add(private)
                si.system.save()
            print "ST {0} {1} {2}".format(si.label,si.mac,si.ip_str)
        except ValidationError, e:
            print "skipping {0} {1}".format(static_iface.label, e)
    else:
        all_dynamic_ifaces = DynamicInterface.objects.filter(range=source_range)
        for dynamic_iface in all_dynamic_ifaces:
            si = StaticInterface(label        = dynamic_iface.system.name,
                                 domain       = the_domain,
                                 workgroup    = the_workgroup,
                                 ttl          = 86400,
                                 ip_str       = str(target_range.get_next_ip()),
                                 mac          = dynamic_iface.mac,
                                 dns_enabled  = True,
                                 dhcp_enabled = True,
                                 ip_type      = '4',
                                 system       = dynamic_iface.system)
        try:
            if not options.dryrun:
                si.save()
                si.views.add(public)
                si.views.add(private)
                si.system.save()
            print "ST {0} {1} {2}".format(si.label,si.mac,si.ip_str)
        except ValidationError, e:
            print "skipping {0} {1}".format(static_iface.label, e)
else:
    if source_range.range_type == STATIC:
        all_ifaces = StaticInterface.objects.filter(ip_lower__lte=source_range_end,
                                                    ip_lower__gte=source_range_start)
    else:
        all_ifaces = DynamicInterface.objects.filter(range=source_range)

    for iface in all_ifaces:
        di = DynamicInterface(range        = target_range,
                              workgroup    = the_workgroup,
                              mac          = iface.mac,
                              dhcp_enabled = True,
                              system       = iface.system)
    try:
        if not options.dryrun:
            di.save()
            iface.system.save()
        print "DY {0} {1} {2}".format(di.system.name,di.mac,di.range)
    except ValidationError, e:
        print "skipping {0} {1}".format(iface.mac, e)


