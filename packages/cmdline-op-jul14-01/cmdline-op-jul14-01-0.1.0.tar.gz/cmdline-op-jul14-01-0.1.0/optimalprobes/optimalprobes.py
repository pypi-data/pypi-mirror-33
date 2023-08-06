__version__ = "0.1.0"

import sys
import os
from .macros import *
from .dependencies import *
import argparse

def funcPrintHelp():
	f=open(helpfile,'rb')
	for line in f:
		print line[:-1]
	f.close()

def funcParserHelp(errmsg):
	funcPrintHelp()
	sys.exit()

def funcResiduemapping(traj,top):
	import mdtraj as md
	t=md.load(traj,top=top)

	f=open(residuemappingfilename,"wb")
	R=t.topology.n_residues

	for i in range(R):
		f.write(str(i)+"\t"+str(t.topology.residue(i))+"\n")
	f.close()

def main():
	
	if len(sys.argv)<2:
		funcPrintHelp()

	elif sys.argv[1]=="--help" or sys.argv[1]=="-h":
		funcPrintHelp()

	elif sys.argv[1]=="--version" or sys.argv[1]=="-v":
		print("Optimal Probes version %s" % __version__)

	elif sys.argv[1]=="--dependencies":
		print("Optimal Probes version %s" % __version__)
		if len(sys.argv)==3:
			if sys.argv[2]=="check":
				funcRunDependenciesCheck()
			else:
				funcPrintHelp()
		else:
			funcPrintDependencies()

	elif sys.argv[1]=="residue_mapping":
		if len(sys.argv)!=6:
				funcPrintHelp()
		else:
			parser=argparse.ArgumentParser(description="")
			parser.add_argument('residue_mapping',metavar='')
			parser.add_argument('-traj',metavar='trajectory file')
			parser.add_argument('-top',metavar='topology file')
			parser.error = funcParserHelp
			args = parser.parse_args()
			funcResiduemapping(args.traj,args.top)
		
	else:
		funcPrintHelp()
