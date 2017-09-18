#!/usr/bin/env python

# delete wireless registrations for non-existent ONID users

import activate
activate.activate()

from cyder.models import *
import re

dino = re.compile('^[a-zA-Z]{3}_.*')
names = []
fd = open('onids.csv')
for line in fd:
    names.append(line.strip('\r\n ').lower())
names = set(names)

at = Attribute.objects.get(name__startswith="Other",attribute_type='i')

s = System.objects.filter(ctnr=Ctnr.objects.get(name="zone.public"))
x = 0
for a in s:
    try:
        eav = SystemAV.objects.get(entity=a, attribute=at)
    except:
        continue
    if eav.value.lower() not in names:
        if dino.match(eav.value.lower()):
            print "ignoring "+eav.value
        else:
            print eav.value+','+a.name+','+str(a.created)
            a.delete()
        x += 1
print x
