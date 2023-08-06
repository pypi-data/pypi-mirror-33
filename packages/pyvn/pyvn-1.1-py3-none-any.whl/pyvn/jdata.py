#!/usr/bin/env python3

#import lib.ivscript
#import josen
import re
import dicttoxml
import json
import collections
import os
import sys
import pycurl
import io
import binascii
import random
from datetime import datetime,timezone
from ruamel.yaml.comments import CommentedMap
from pyvn import run
import base64

c={
	"none":"\033[0m",
	"header":"\033[38;5;166m", # naranja
	"group":"\033[1;34m",      # light blue
	"item":"\033[0;36m",       # cian
	"null":"\033[1;30m",       # gris
	#"date":"\033[0;34m",      # blue
	#"date":"\033[38;5;61m",       # xvioleta
	"date":"\033[38;5;105m",       # xvioleta
	"str":"\033[0;32m",        # green
	"int":"\033[1;32m",        # light green
	"float":"\033[38;5;112m",  # xoliva
	"bool":"\033[1;36m",       # white
	"unk":"\033[0;31m",        # red
	"varint":"\033[1;35m",        # magentab
	"varenv":"\033[0;35m",        # magenta
	"varcmd":"\033[1;31m",        # rojo
	"err":"\033[1;31m",        # light red
}

# Imprime un dict por pantalla para humanos de forma bonita
def outhuman(d,header=None,key=None,indent=""):
	indentchars="    "
	if(header): print(c["header"]+header+c["none"]);indent=indent+indentchars

	# Si es diccionario iteramos
	if(type(d)==dict or type(d)==collections.OrderedDict): # or type(d)==CommentedMap):
	#if(type(d)==dict or type(d)==collections.OrderedDict or type(d)==CommentedMap):
	#if hasattr(d,'__iter__') and type(d)!=str:
		if(key!=None): print(indent+c["group"]+key+":"+c["none"]); indent+=indentchars
		if(len(d)==0): print(indent+c["null"]+"empty"+c["none"])
		else:
			for k in d: outhuman(d[k], key=k, indent=indent)
		return


	# Si es lista listamos con [indice]
	#if(type(d)==list):
	#	i=0
	#	print(indent+c["group"]+key+":"+c["none"])
	#	indent=indent+indentchars
	#	# Lista de strings
	#	#if type(key[0])==str:
	#	#	for k in d:
	#	#		print(indent+c["item"]+"["+str(i)+"]: "+c["none"], end='')

	#	#for k in d:
	#	#	#print(indent+c["group"]+key+"["+str(i)+"]:"+c["none"])
	#	#	#outhuman(k, indent=indent+indentchars)
	#	#	#print(indent+c["item"]+"["+str(i)+"]: "+c["none"], end='')
	#	#	outhuman(k, indent=indent+c["item"]+"["+str(i)+"]: ")
	#	#	i=i+1
	#	#	#print(k);
	#	
	#	for k in d:
	#		#print(indent+c["group"]+key+"["+str(i)+"]:"+c["none"])
	#		print(indent+c["group"]+"["+str(i)+"]:"+c["none"])
	#		outhuman(k, indent=indent+indentchars)
	#	#	#print(indent+c["item"]+"["+str(i)+"]: "+c["none"], end='')
	#		#outhuman(k, indent=indent+c["item"]+"["+str(i)+"]: ")
	#		i=i+1
	#		#print(k);
	#	return
	
	if type(d)==list or type(d)==tuple:
		# Vacia
		if len(d)==0:
			if(key!=None):
				print(indent+c["group"]+key+"[]: "+c["null"]+"empty"+c["none"]);
			else:
				print(indent+c["null"]+"empty"+c["none"])
			return

		# Lista de strings o ints
		if type(d[0])==str or type(d[0])==int:
			i=0
			if key!=None:
				print(indent+c["group"]+key+":"+c["none"])
				for k in d:
					outhuman(str(k), key="["+str(i)+"]", indent=indent+indentchars)
					i+=1
			else:
				for k in d:
					outhuman(str(k), key="["+str(i)+"]", indent=indent)
					i+=1
			return

		#for k in d:
		#	#print(indent+c["group"]+key+"["+str(i)+"]:"+c["none"])
		#	#outhuman(k, indent=indent+indentchars)
		#	#print(indent+c["item"]+"["+str(i)+"]: "+c["none"], end='')
		#	outhuman(k, indent=indent+c["item"]+"["+str(i)+"]: ")
		#	i=i+1
		#	#print(k);
		
		# Lista de objetos
		if(type(d[0])==dict or type(d[0])==collections.OrderedDict):
			i=0
			for k in d:
				print(indent+c["group"]+key+"["+str(i)+"]:"+c["none"])
				outhuman(k, indent=indent+indentchars)
				i=i+1
			return
	
		print(c["err"]+"¿list of "+type(d[0]).__name__+"?"+c["none"])
		return
		#print("unknown "+type(d).__name__)
		#return
	
	# Mostramos key
	if(key!=None): print(indent+c["item"]+key+": ", end='')
	else: print(indent, end='')

	# Mostramos valor
	t=type(d)
	if(t==str):
		p=re.compile("\$([a-zA-Z0-9_]*)\$")
		vars=set(p.findall(d))
		for k in vars: d=re.sub("\$"+k+"\$", c["varenv"]+"$"+k+"$"+c["str"], d)
		p=re.compile("\%([a-zA-Z0-9_]*)\%")
		vars=set(p.findall(d))
		for k in vars: d=re.sub("\%"+k+"\%", c["varint"]+"%"+k+"%"+c["str"], d)
		p=re.compile("\(\(([^)]*)\)\)")
		vars=set(p.findall(d))
		for k in vars: d=re.sub("\(\(.*\)\)", c["varcmd"]+"(("+k+"))"+c["str"], d)
		print(c["str"]+str(d)+c["none"])
	elif(t==datetime):
		dtstr=re.sub("\+00:00", "Z", d.isoformat())
		#dtstr=d.__str__()
		print(c["date"]+dtstr+c["none"])
	elif(t==int):
		print(c["int"]+str(d)+c["none"])
	elif(t==float):
		print(c["float"]+str(d)+c["none"])
	elif(t==bool):
		print(c["bool"]+str(d)+c["none"])
#	elif(t==list):
#		print
#		for i in d:
#			outhuman(i,header="x",indent=indent)
#			#print(indent+indentchars+c["str"]+i)
#			#print(d)
	elif(t==type(None)):
		print(c["null"]+"null"+c["none"])
	else:
		print(c["err"]+"¿"+str(t.__name__)+"?"+c["none"])

# Por cada item en d reemplaza %fb%fichero% por el contenido del fichero en b64
# Por cada item en d reemplaza %var% por val de la lista varlist
def replacevars(d, varlist, unknownempty=False, emptyremove=None):
	o=collections.OrderedDict()
	for k in d:
		if(type(d[k])==dict or type(d[k])==collections.OrderedDict):
			d[k]=replacevars(d[k], varlist, unknownempty=unknownempty, emptyremove=emptyremove)
			o[k]=d[k]
			continue
		else:
			if(type(d[k])==str):
				#if(d[k][0]=='$'):
				#	var=d[k][1:-1]
				#	v=varlist.get(var)
				#	if(v): o[k]=v
				#else:
				#	o[k]=d[k]

				# Buscamos variables en varlist
				p=re.compile("\%([a-zA-Z0-9_]*)\%")
				vars=set(p.findall(d[k]))
				# No hay variables
				if(vars==None):
					o[k]=d[k]
					continue
				# Hay variables
				for sk in vars:
					val=varlist.get(sk)
					if(val==None):
						if(unknownempty): val=""
						else: continue
					d[k]=re.sub("\%"+sk+"\%", val, d[k])

				if(d[k]=="" and emptyremove): continue
				o[k]=d[k]
			else:
				o[k]=d[k]
	return o

# Por cada item en d reemplaza $var$ por variable de entorno
def replaceenv(d, unknownempty=False, emptyremove=None):
	o=collections.OrderedDict()
	for k in d:
		if(type(d[k])==dict or type(d[k])==collections.OrderedDict):
			d[k]=replaceenv(d[k], unknownempty=unknownempty, emptyremove=emptyremove)
			o[k]=d[k]
			continue
		else:
			if(type(d[k])==str):
				p=re.compile("\$([a-zA-Z0-9_]*)\$")
				vars=set(p.findall(d[k]))
				# No hay variables
				if(vars==None):
					o[k]=d[k]
					continue
				# Hay variables
				for sk in vars:
					val=os.environ.get(sk)
					if(val==None):
						if(unknownempty): val=""
						else: continue
					d[k]=re.sub("\$"+sk+"\$", val, d[k])

				if(d[k]=="" and emptyremove): continue
				o[k]=d[k]
			else:
				o[k]=d[k]
	return o

# Por cada item en d reemplaza ((cmd)) por la ejecución de cmd
# Por cada item en d reemplaza #b#file# por el fichero en b64
# Por cada item en d reemplaza #t#file# por el contenido del fichero
def runvars(d, unknownempty=False, emptyremove=None):
	o=collections.OrderedDict()
	for k in d:
		if(type(d[k])==dict or type(d[k])==collections.OrderedDict):
			d[k]=runvars(d[k], unknownempty=unknownempty, emptyremove=emptyremove)
			o[k]=d[k]
			continue
		else:
			if(type(d[k])==str):
				modified=False

				# Comando a ejecutar
				r_buscacmd=re.compile("\(\((.*)\)\)")
				vars=set(r_buscacmd.findall(d[k]))
				# No hay variables
				if(vars==None):
					o[k]=d[k]
				#	continue
				else:
					modified=True
					# Hay variables
					for sk in vars:
						# fb|fichero -> base64 fichero
						sk=re.sub(r"^f\|(.*)$", r"cat '\g<1>'", sk)
						sk=re.sub(r"^b\|(.*)$", r"cat '\g<1>'|base64 -w0", sk)
						pars=["bash","-c",sk]
						ex=run.cmd(pars)
						#if ex.retcode==0:
						val=ex.out
						if(val==None):
							if(unknownempty): val=""
							else: continue
						#d[k]=re.sub("\(\("+sk+"\)\)", val, d[k])
						d[k]=re.sub("\(\(.*\)\)", val, d[k])

				# Fichero base64
				r_buscacmd=re.compile(r"#b#(.*)#")
				vars=set(r_buscacmd.findall(d[k]))
				# No hay variables
				if(vars==None):
					o[k]=d[k]
				else:
					modified=True
					# Hay variables
					for sk in vars:
						f=open(sk, "rb")
						fdata=base64.b64encode(f.read()).decode()
						d[k]=re.sub(r"#b#.*#", fdata, d[k])
				
				# Fichero directo
				r_buscacmd=re.compile(r"#f#(.*)#")
				vars=set(r_buscacmd.findall(d[k]))
				# No hay variables
				if(vars==None):
					o[k]=d[k]
				else:
					modified=True
					# Hay variables
					for sk in vars:
						f=open(sk, "r")
						fdata=f.read()
						d[k]=re.sub(r"#f#.*#", fdata, d[k])

				if modified and d[k]=="" and emptyremove: continue
				o[k]=d[k]
			else:
				o[k]=d[k]
	return o

# JSON -> OrderedDict
def json_parser_hook(js):
	out=collections.OrderedDict(js)
	for (key, value) in out.items():
		# Hora con timezone sin milisegundos
		try:
			dt=re.sub("Z$", "UTC",value)
			dt=datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S%Z")
			#dt=dt.replace(tzinfo=datetime.timezone(datetime.timedelta(0)))
			dt=dt.replace(tzinfo=timezone.utc)
			out[key]=dt
			continue
		except: pass
		# Hora con timezone con milisegundos
		try:
			dt=re.sub("Z$", "UTC",value)
			dt=datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S.%f%Z")
			dt=dt.replace(tzinfo=timezone.utc)
			out[key]=dt
			continue
		except: pass
		# Hora sin timezone sin milisegundos
		try:
			out[key]=datetime.strptime(value, "%Y-%m-%dT%H:%M:%S")
			continue
		except: pass
		# Hora sin timezone con milisegundos
		try:
			out[key]=datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%f")
			continue
		except: pass
	return out
def fromjson(jsondata):
	return json.loads(jsondata,object_pairs_hook=json_parser_hook)

# OrderedDict -> json
def json_serializer_hook(o):
	if isinstance(o, datetime):
		return re.sub("\+00:00", "Z", o.isoformat())
def tojson(data):
	return json.dumps(data,separators=(',',':'),default=json_serializer_hook)

# XML -> OrderedDict
def fromxml(xmldata):
	return xmltodict.parse("<xml>"+xmldata+"</xml>", disable_entities=True)[xml]

