import sys
import os
from .macros import *

def funcPrintDependencies():
	f=open(dependenciesfile,'rb')
	for line in f:
		print line[:-1]
	f.close()


def funcRunDependenciesCheck():
	# Python
	print "Python "+str(sys.version_info[0])+"."+str(sys.version_info[1])+"."+str(sys.version_info[2])
	# Numpy
	import numpy
	print "Numpy "+numpy.version.version
	# MDTraj
	import mdtraj
	print "MDTraj "+mdtraj.version.full_version
	# MSMBuilder
	import msmbuilder.version
	print "MSMBuilder "+msmbuilder.version.full_version
	# Osprey
	cmd="osprey --version"
	print os.popen(cmd).read()
