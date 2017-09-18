#!/usr/bin/env python

# delete systems that have no interfaces

import activate
activate.activate()

from cyder.models import *

s = System.objects.filter()
x = 0
for a in s:
    if a.staticinterface_set.count() == 0:
        if a.dynamicinterface_set.count() == 0:
            print a.name
            a.delete()
            x += 1
print x
