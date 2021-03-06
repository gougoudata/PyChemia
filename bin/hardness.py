#!/usr/bin/env python

"""
Computes the hardness of a given structure
"""

__author__ = 'Guillermo Avendano Franco'

import os
import sys

import pychemia


def helper():
    print """
Computes the hardness of one or several files

Use:
    hardness.py POSCAR1 [POSCAR2 ...]
"""

if __name__ == '__main__':

    if len(sys.argv) < 2:
        helper()
        sys.exit(1)

    for i in range(1, len(sys.argv)):
        filename = sys.argv[i]
        if not os.path.exists(filename):
            print 'Filename not found ', filename
            continue

        structure = pychemia.code.vasp.read_poscar(filename)
        analysis = pychemia.analysis.StructureAnalysis(structure, supercell=(2, 2, 2))
        print 'File : ', filename
        print 40*'='+' structure '+40*'='
        print structure
        print 40*'='+' structure '+40*'='

        hardness, r_cutoff = analysis.hardness(use_laplacian=True, verbose=True)
        print 'Hardness : ', hardness
        print 'Cutoff radius :', r_cutoff
