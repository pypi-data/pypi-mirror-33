#!/usr/bin/env python3
# v2018.02.26

import re
import sys
import os.path
import fileinput
#import json
import collections
from pyvn import jdata

# Ejemplo multilinea
#soap3: {
#	xml="\\
#<?xml version="1.0"?>
#<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">
#<s:Body>
#<SignHash xmlns="tag:ivnosys.net,2016:KeymanService">
#<token>$token</token>
#<request>$request</request>
#</SignHash>
#</s:Body>
#</s:Envelope>
#"\\
#}

def tojson(data):

	# quitamos comentarios y líneas vacías
	data=re.sub("(?m)^[\t ]*(#.*|)$\n", "", data)

	# soporte para multilineas
	data2=""
	inmulti=False
	for l in data.splitlines():
		#l=line.strip()
		if(l.find("\\\\")!=-1):
			l=re.sub(r'\\\\','',l)
			if(inmulti):
				data2=data2+l+"\n"
			else:
				data2=data2+l
			inmulti=not inmulti
		else:
			if(inmulti):
				l=re.sub(r'"', '\\"', l)
				l=re.sub(r'	', '\\\\t', l)
				data2=data2+l+"\\n"
			else:
				data2=data2+l+"\n"
	data=data2

	# soporte para llaves oneline, p.ej: var: { subvar1="data", subvar2=["v1"] }
	# Nota: Algunos son peligrosos, podrían reemplazar datos, habría que procesar carácter a carácter para saber si estamos en datos o variables
	data=re.sub("}", "\\n}", data)
	data=re.sub("{", "{\\n", data)
	data=re.sub("],", "]\\n", data)
	data=re.sub("\",", "\"\\n", data)
	data=re.sub("\",", "\"\\n", data)
	data=re.sub(", *([a-zA-Z0-9_]*=)", "\\n\\1", data)

	# convertimos sintaxis
	j="{"
	for line in data.splitlines():
		l=line.strip()
		if len(l)==0: continue
		#if l[0]=="#": continue
		if l=="EOF": break
		#l=re.sub(r'([a-zA-Z0-9_]*)[=:] *', '"\\1":', l)
		l=re.sub(r'^([\t a-zA-Z0-9_]*)=', '"\\1":', l)
		l=re.sub(r'^([\t a-zA-Z0-9_]*): ','"\\1":', l)
		#l=re.sub(r' (["a-zA-Z0-9_]*:)', ',\\1', l)
		j=j+l+","
	j=j+"}"
	j=re.sub(r'([{\[]),','\\1',j)
	j=re.sub(r',([}\]])','\\1',j)

	return j

def todict(josen):
	j=tojson(josen)
	#return json.loads(j)
	#return json.loads(j,object_pairs_hook=json_parser_hook)
	return jdata.fromjson(j)

def filetodict(filename):
	j=filetojson(filename)
	d=jdata.fromjson(j)
	#d=json.loads(j,object_pairs_hook=json_parser_hook)
	return d

def filetojson(filename):
	f=open(filename, "r")
	fdata=f.read()
	j=tojson(fdata)
	return j
