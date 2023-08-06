#!/usr/bin/env python3

import sys,os

# Directorio del script principal
#scriptdir=sys.path[0]

# Cambiamos al directorio del script principal
#os.chdir(scriptdir)

# Utilizamos scriptdir/lib como path para los import
#sys.path.insert(1,scriptdir+'/lib')

# Cambiamos el nombre del proceso al del script
import setproctitle,os
setproctitle.setproctitle(os.path.basename(sys.argv[0]))

# Excepciones coloreadas
import colored_traceback.always

# Exportamos scriptdir al script principal
#import __main__
#__main__.scriptdir=scriptdir
