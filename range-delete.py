#!/usr/bin/env python

# purge a network of its interfaces and ranges.

import activate
activate.activate()

from cyder.models import *

net = '128.193.190.0/23'

n = Network.objects.get(network_str=net)
rs = n.range_set.filter()

for r in rs:
    print r
    if r.range_type == 'st':
        r.staticinterfaces.delete()
        r.delete()
    else:
        a = r.dynamicinterface_set.filter()
        for b in a:
            b.delete()
        r.delete()


#Range.objects.get(start_lower__gte=ip_start, end_lower__lte=ip_end).delete()

