Piccolo5/Piccolo6/Picalor6 Python API calling interface

What is it?
-----------
A python package enabling users to call a set of Picwin32.dll or Ganessa_SIM.dll API functions and subroutines within python scripts. 

Installation
------------
:Windows only: 

	pip install ganessa

Requirements
------------

  #) python requirements: numpy 1.7 or above (python 2.7) / numpy 1.12.1 or above (python 3.5 - 3.6)
  #) Piccolo or Picalor kernel library (picwin32.dll), starting from version 5 (141203) for python 2.7 / version 6 for python 3.x
  #) valid Piccolo or Picalor license

This tool requires Picwin32.dll to be in the PATH or in one of the following folders:
 [ C: or D: ] / ['Program Files/Adelior/Piccolo5_' or 
				 'Program Files (x86)/Gfi Progiciels/Piccolo6_'  or
				 'Program Files (x86)/Gfi Progiciels/Picalor6_']
				 'Program Files (x86)/Safege/Ganessa_']
			  + ['fr' or 'uk' or 'esp' or 'eng'] + ['' or '_ck']

    Or one of Ganessa_SIM.dll or Ganessa_TH.dll in:
 [ C: or D: ] / ['Program Files (x86)/Safege/Ganessa_']
			  + ['fr' or 'uk' or 'esp' or 'eng']

PICCOLO_DIR or GANESSA_DIR environment variables can be used for custom installations. 

Content
-------

The package provides:
 #) 'sim' package:
     - a few basic functions for reading or loading a model, running simulations
     - 'getter' functions for individual objects and attributes, time series vectors, attribute vector of all object
     - iterators over links, nodes, tanks, demands, and tables, or over Piccolo selections
 #) 'th' package: same functions except running extended period simulations and time series getters
 #) 'util' package: miscellaneous functions
 #) 'OpenFileMMI' provides classes for opening dialog frame for a .dat/.bin model file, and output (result) file. It should be imported after 'sim'.
 #) 'sort' provides a heapsort based on heapq
 #) 'midfile' provides minimal mif/mid functions similar to shp/dbf shapefile handler (pyshp package)
 #) 'epanet' provides epanet2 python API for win32 (thanks to Assela Pathirana - mailto: assela@pathirana.net) similar to EpanetTools-0.4.0; with epanet.getlinknodes corrected (from 0.9.2)
 #) 'parallel' provides a simple parallel simulations handling framework based on multiprocessing.

Model objects and parameters can be modified using Piccolo command language (see cmd, cmdfile and execute)
A documentation is provided as pyGanessa.html in the intallation folder.

History of the document
-----------------------
Created 2013-07-04
Revised 2015-05-03: since 2014-12-04 Picwin32.dll is compatible with this API
Revised 2016-07-07: provided as .rst
Revised 2017-08-08: install using pip; Piccolo/Ganessa dll folder search order.
Revised 2017-09-12: split sim into core, core_sim, core_th
Revised 2017-11-13: added sort, midfile, epanet modules
Revised 2017-11-30: added parallel
Revised 2018-03-29: minor changes / extension to python 3.5-3.6
Revised 2018-06-08: OpenFileMMI and epanet details, added example.

Example
-------
# -*- coding: utf-8 -*-
from __future__ import (print_function, unicode_literals)
import os
import ganessa.sim as pic
import matplotlib as mpl
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt

# This code sample runs under python 2.7, 3.5, 3.6

if __name__ == '__main__':
    wkfold = os.path.dirname(__file__)
    os.chdir(wkfold)
    # will create work files here
    pic.init(wkfold)			
    # loads the model - change the name here...
    pic.cmdfile('model.dat')
    # select small pipe (diameter below 155)
    # using iterator and D getter, by id
    pipefilter = lambda d: (d > 0 and d < 155)
    pipes = [p for p in pic.Links() if pipefilter(pic.linkattr(p, 'D')) ]
    # using iterator and D getter, by index (less concise but slightly faster)
    pipes = [pic.getid(pic.LINK, k) for k in range(1, pic.nbobjects(pic.LINK)) 
                                    if pipefilter(pic.nlinkattr(k, 'D')) ]
    # Most Piccoloic, using (french) command language selection
    pic.setlang('French')
    pipes = [p for p, _t in pic.Selected('TUYAU (D < 155) FIN')]
    # minimal setter functions for links, nodes, tanks attributes
    id = pipes[len(pipes)//2]
    diam = pic.linkattr(id, 'D')
    pic.setlinkattr(id, 'D', diam*2)
    # Use command language to set / modify / delete objects
    pic.execute('MODIF', 'DETR ARC {} FIN'.format(id))
    pic.execute('MODIF', 'FUSION NOEU (AA = 1) FIN',
                         'FUSION NOEU (AA = 1) FIN')
    # or change parameters
    pic.execute('SIMUL', 'CRITX 0.05', 'MXITER 75')
    # Unlike epanet, first run simulation then browse/ query results
    pic.full_solveH(silent= True, retry= True)
    pic.browseH(3600*8.5)
    fig = plt.figure(figsize=(16-1, 9-1))
    # plot 3D elevation and hydraulic head 
    ax = fig.gca(projection='3d')
    for a in pic.Links():
        x, y, z, v, nb = pic.linkXYZV(a, 'CH')
        if nb > 0: 
            ax.plot(x, y, z, 'r-')
            ax.plot(x, y, v, 'b-')
    plt.title(u'Plan de charge a t= 08:30')
    plt.show()
    # print min/max pressure over the EPS
    attr = 'P'
    for id, vmin, vmax, vmoy in pic.getMinMax(pic.NODE, attr):
        print(id, attr+'min:', vmin, attr+'max:', vmax)
    # get current volume simulation (internal variable steps) and measurement TS
    for id in pic.Tanks():
        t1, v1, nb1 = pic.tsval(pic.TANK, id, 'VC')
        t2, v2, nb2 = pic.msval(pic.TANK, id, 'VC')
    # get current volume simulation results at measurement sampling
    for id in pic.Tanks():
        t3, v3, nb3 = pic.tsvalbymts(pic.TANK, id, 'VC')
    # export as Epanet .inp
    pic.exportEpanet('model.inp')
    print('Done.')
	# use reset() for switching model, close() to terminate
    pic.close()


