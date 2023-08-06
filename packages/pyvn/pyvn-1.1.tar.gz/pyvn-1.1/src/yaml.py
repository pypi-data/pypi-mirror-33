#!/usr/bin/env python3
# v2018.05.11

import sys
import ruamel.yaml

def modify(filename,var,val,node=None):
	yaml=ruamel.yaml.YAML()
	yaml.width=4096
	f=open(filename,"r")
	data=yaml.load(f.read())
	datamod=data
	if node:
		for n in node:
			datamod=datamod.get(n)
	datamod[var]=val
	f=open(filename, "w")
	yaml.dump(data, f)

def read(filename):
	# Cargar yaml en ordereddict
	import collections
	ruamel.yaml.representer.RoundTripRepresenter.add_representer(
	collections.OrderedDict, ruamel.yaml.representer.RoundTripRepresenter.represent_ordereddict)
	f=open(filename,"r")
	data=ruamel.yaml.load(f.read(), Loader=ruamel.yaml.Loader)
	return data
