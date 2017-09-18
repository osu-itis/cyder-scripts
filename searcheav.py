#!/usr/bin/env python

# Cyder doesn't search EAVs via the web UI.  This is to make up for the deficiency.

import sys
import activate
activate.activate()
from cyder.models import *
import csv


public = View.objects.get(name="public")
private = View.objects.get(name="private")
attr_location = Attribute.objects.get(name="Location",attribute_type='i')
attr_serial = Attribute.objects.get(name__contains="Serial",attribute_type='i')
attr_hardware = Attribute.objects.get(name__contains="Hardware",attribute_type='i')
attr_owning = Attribute.objects.get(name__contains="Owning",attribute_type='i')

search_terms = ['anything','something']

print "Doing case insensitive search..."
print "Value,Entity,Attribute"

for term in search_terms:
    sa = SystemAV.objects.filter(value__icontains=term)
    for s in sa:
        print "{0},{1},{2}".format(s.value,s.entity,s.attribute)


