from __future__ import division, print_function, absolute_import

import argparse
import sys
import logging

from backmap import __version__

__author__ = "ranjanmannige"
__copyright__ = "Ranjan Mannige"
__license__ = "MIT"

_logger = logging.getLogger(__name__)

helpme = """
============================================
  ____             _    __  __          _____  
 |  _ \           | |  |  \/  |   /\   |  __ \ 
 | |_) | __ _  ___| | _| \  / |  /  \  | |__) |
 |  _ < / _` |/ __| |/ / |\/| | / /\ \ |  ___/ 
 | |_) | (_| | (__|   <| |  | |/ ____ \| |     
 |____/ \__,_|\___|_|\_\_|  |_/_/    \_\_|     
                       (Multi-angle Picture)                                             

This tool provides easily readable "pictures" of protein conformations, 
ensembles, and trajectories saved as either a combined protein databank 
(PDB) structure file, or a directory of such files, and produces graphs.
-----
Usage
-----
python plotmap.py -pdb ProteinDatabankStructureFilename.pdb
python plotmap.py -pdb /directory/containing/pdbs/
------
Output (the x-axis always represents the models/structures listed in the PDB)
------
filename.rcode.eps      (y-axis: residue #; color: R number based on "-signed" and <rcode_cmap>)
filename.rcode.his.eps  (y-axis: Ramachandran number (R); color: frequency of R in model)
filename.rcode.rmsf.eps (y-axis: residue #; color: RMSF in R from the previous model)
---------------
Additional tags
---------------
-h       -     Prints this message
-ss      -     Color the ramachandran number codes (R-codes) by 
               secondary structure (default: color by chirality and sign)
-signed  -     Use the signed version of the ramachandran number
-rmsd    -     Also producee "filename.rcode.rmsd.eps"
               (y-axis: residue #; color: RMSD in R from first model)
---------------
Each graph is also accompanied by "_colorbar.eps", which are keys.
---------------
The Ramachandran number concept is discussed in the following manuscripts (this tool is discussed in the first reference):
1. Mannige (2018) "A simpler Ramachandran number can simplify the life of a protein simulator" Manuscript Prepared/Submitted
2. Mannige, Kundu, Whitelam (2016) "The Ramachandran number: an order parameter for protein geometry" PLoS ONE 11(8): e0160023. 
Full Text: https://doi.org/10.1371/journal.pone.0160023
============================================
"""

# Standard imports
import sys,re,os,math

# Commonly available imports
import copy,string,glob
import numpy as np

# matplotlib imports
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
# Biopython (can do without)
try:
	biopython = True
	from Bio import PDB
except:
	biopython = False
#

def normalized_ramachandran_number(phi,psi,signed=False):
	r = (phi+psi+360)/720.0
	#
	if signed:
		if psi >= phi:
			r = r * -1.0
		#
	#
	return r
#

def ramachandran_number(phi,psi,signed=False):
	return normalized_ramachandran_number(phi,psi,signed)
#

def r(phi,psi,signed=False):
	return normalized_ramachandran_number(phi,psi,signed)
#

def R(phi,psi,signed=False):
	return normalized_ramachandran_number(phi,psi,signed)
#

#sys.path.insert(0, "./local_imports/") # for the local imports
#import Geometry, PeptideBuilder, locallib

signed = 0
rrange = [0,1]
colortype = "Chirality" # can be SecondaryStructure

showeps = 0
dofilter = 0

showrcode = 1
showhis   = 1
showrmsf  = 1
showrmsd  = 0
do_vmd_etc = 1

bins = 100
pdbfn = ""

# python plotmap.py -pdb /home/ranjan/Desktop/old/pairing_functions/for_sharing/structures/nanosheet_birth_U7.pdb
# python plotmap.py -pdb /home/ranjan/Desktop/old/pairing_functions/for_sharing/structures/nanosheet_traj.pdb
# python plotmap.py -pdb /home/ranjan/Desktop/old/pairing_functions/for_sharing/structures/class_a_alpha_1MBA.pdb
# python plotmap.py -pdb /home/ranjan/Desktop/old/pairing_functions/for_sharing/structures/class_c_a_plus_b_2ACY.pdb


forcedmax = False
forcedmin = False

show_graphs = 1
default_fontsize = 22
colorbarXscaling = 0.08
defaultXscaling  = 2.0

SCALE = 10.0 # For the postscript output


# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# SETTING UP SOME COLORMAPS

COLORSWITCH = 0.5  # THIS IS THE POINT, FOR THE RED/BLUE AND RED/BLUE/YELLOW/BLACK 
                   # COLOR SCHEME, WHERE THE SWITCH IN COLOR HAPPENS (NAIVELY 0.5, 
                   # BUT BETA SHEETS SPILL TO THE "D" PORTION OF THE PLOT, SO IT 
                   # IS 0.45

# First, some definitions:
# DEFINING COLORS BY CHIRALITY:
# c stands for color, bc stands for background color             
             #    when R ranges from   [-1,1]  ("Signed R")     [0,1] (Traditional R)
             #                         ------------             -----------
c1 = [0,0,0] # black                   | \_ c4  / |             |\_    c4 |
c2 = [1,1,0] # yellow                  |   \_ /   |             |  \_     |
c3 = [1,0,0] # red                 psi |c3  /\_c2 |         psi |    \_   |
c4 = [0,0,1] # blue                    |  /    \_ |             |      \_ |
bc = [1,1,1] # white                   |/  c1    \|             |c3      \|
             #                         ------------             -----------
             #                             phi                      phi
# DEFINING POSITIONS AND COLORS BY SECONDARY STRUCTURE:
# POSITIONS
helix_start = 0.31 # the start of the helical region (all assuming R in [0,1])
helix_end   = 0.39 # the end of the helical region
sheet_start = 0.45 # the start of the sheet region
sheet_end   = 0.62 # the end of the sheet region
polyproline_end = 0.66 # the end of the polyprolineII region 
                       # (the start coincides with the sheet region, 
                       # so it just begins after the sheet region ends)
# COLORS
helixR      = (1.,0.,0.)
sheet       = (0.,0.,1.)
polyproline = (0.,1.,1.)

# ----------------
# NEW COLOR SCHEME: color by backbone twist (expected range: R=[0,1])
# ----------------
# This lets you later on get the cmap by name 'TwoColor': cmap = plt.get_cmap('TwoColor')
# POSITION: 0        COLORSWITCH         1
#    COLOR: | white - red | blue - white |
cdict = {
#                         white  white          red    blue          white  white
	'red':   ((0.00,  bc[0], bc[0]), (COLORSWITCH,  c3[0], c4[0]), (1.0, bc[0], bc[0])), 
	'green': ((0.00,  bc[1], bc[1]), (COLORSWITCH,  c3[1], c4[1]), (1.0, bc[1], bc[1])),
	'blue':  ((0.00,  bc[2], bc[2]), (COLORSWITCH,  c3[2], c4[2]), (1.0, bc[2], bc[2])) 
}
cmap = LinearSegmentedColormap('Chirality', cdict)
plt.register_cmap(cmap=cmap)
# ----------------
# NEW COLOR SCHEME: color by backbone twist, variant (expected range: R=[0,1])
# ----------------
cdict = {
#                         white  white          blue   blue
	'red':   ((0.00,  bc[0], bc[0]), (1.0,  c4[0], c4[0])), 
	'green': ((0.00,  bc[1], bc[1]), (1.0,  c4[1], c4[1])),
	'blue':  ((0.00,  bc[2], bc[2]), (1.0,  c4[2], c4[2]))
}
cmap = LinearSegmentedColormap('deleteme', cdict)
plt.register_cmap(cmap=cmap)
cdict = {
#                                       white  white         blue   blue
	'red':   ((0.00,  1, 1), (0.5,  bc[0], bc[0]), (1.0, c4[0], c4[0])), 
	'green': ((0.00,  0, 0	), (0.5,  bc[1], bc[1]), (1.0, c4[1], c4[1])),
	'blue':  ((0.00,  1, 1), (0.5,  bc[2], bc[2]), (1.0, c4[2], c4[2])) 
}
cmap = LinearSegmentedColormap('deletemeSigned', cdict)
plt.register_cmap(cmap=cmap)
# ----------------
# NEW COLOR SCHEME: color by backbone twist, variant (expected range: R=[0,1])
# ----------------
# This lets you later on get the cmap by name 'TwoColorInverted': cmap = plt.get_cmap('TwoColorInverted')
# POSITION: 0              0.25             0.5           0.75            1
#    COLOR: | white - black | yellow - white | white - red | blue - white |
cdict = {
#                         red    red                    white  white         blue   blue
	'red':   ((0.00,  c3[0], c3[0]), (COLORSWITCH,  bc[0], bc[0]), (1.0, c4[0], c4[0])), 
	'green': ((0.00,  c3[1], c3[1]), (COLORSWITCH,  bc[1], bc[1]), (1.0, c4[1], c4[1])),
	'blue':  ((0.00,  c3[2], c3[2]), (COLORSWITCH,  bc[2], bc[2]), (1.0, c4[2], c4[2])) 
}
cmap = LinearSegmentedColormap('Chirality_r', cdict)
plt.register_cmap(cmap=cmap)
# ----------------
# NEW COLOR SCHEME: color by backbone twist (expected range: R=[-1,1])
# ----------------
# This lets you later on get the cmap by name 'FourColor': cmap = plt.get_cmap('FourColor')
# POSITION: 0              0.25             0.5           0.75            1
#    COLOR: | white - black | yellow - white | white - red | blue - white |
cdict = {
#                         white  white           black  yellow         white  white           white  white         blue   blue
	'red':   ((0.00,  bc[0], bc[0]), (0.25,  c1[0], c2[0]), (0.50, bc[0], bc[0]), (0.75,  c3[0], c4[0]), (1.0, bc[0], bc[0])), 
	'green': ((0.00,  bc[1], bc[1]), (0.25,  c1[1], c2[1]), (0.50, bc[1], bc[1]), (0.75,  c3[1], c4[1]), (1.0, bc[1], bc[1])),
	'blue':  ((0.00,  bc[2], bc[2]), (0.25,  c1[2], c2[2]), (0.50, bc[2], bc[2]), (0.75,  c3[2], c4[2]), (1.0, bc[2], bc[2])) 
}
cmap = LinearSegmentedColormap('ChiralityFourColor', cdict)
plt.register_cmap(cmap=cmap)
# ----------------
# NEW COLOR SCHEME: color by backbone twist, variant (expected range: R=[-1,1])
# ----------------
# This lets you later on get the cmap by name 'FourColorInverted': cmap = plt.get_cmap('FourColorInverted')
# POSITION: 0              0.25             0.5           0.75            1
#    COLOR: | black - white | white - yellow | red - white | white - blue |
cdict = {
#                         black  black           white  white         yellow  red             white  white         blue   blue
	'red':   ((0.00,  c1[0], c1[0]), (0.25,  bc[0], bc[0]), (0.50, c2[0], c3[0]), (0.75,  bc[0], bc[0]), (1.0, c4[0], c4[0])), 
	'green': ((0.00,  c1[1], c1[1]), (0.25,  bc[1], bc[1]), (0.50, c2[1], c3[1]), (0.75,  bc[1], bc[1]), (1.0, c4[1], c4[1])),
	'blue':  ((0.00,  c1[2], c1[2]), (0.25,  bc[2], bc[2]), (0.50, c2[2], c3[2]), (0.75,  bc[2], bc[2]), (1.0, c4[2], c4[2])) 
}
cmap = LinearSegmentedColormap('Chirality_rFourColor', cdict)
plt.register_cmap(cmap=cmap)
# -------------------------
# NEW COLOR SCHEME: secondary structure (expected range: R=[0,1])
# ----------------
# This lets you later on get the cmap by name 'SecondaryStructure': cmap = plt.get_cmap('SecondaryStructure')
#
#                         white  white                  white        red                      red  white                  white      blue                    blue            cyan                               cyan              white white
cdict = {  #                  |      |                      |          |                        |      |                      |         |                       |               |                                  |                  |     |
           'red': ((0.00,  bc[0], bc[0]), (helix_start,  bc[0], helixR[0]), (helix_end,  helixR[0], bc[0]), (sheet_start,  bc[0], sheet[0]), (sheet_end,  sheet[0], polyproline[0]), (polyproline_end, polyproline[0], bc[0]), (1, bc[0],bc[0])), 
         'green': ((0.00,  bc[1], bc[1]), (helix_start,  bc[1], helixR[1]), (helix_end,  helixR[1], bc[1]), (sheet_start,  bc[1], sheet[1]), (sheet_end,  sheet[1], polyproline[1]), (polyproline_end, polyproline[1], bc[1]), (1, bc[1],bc[1])),
          'blue': ((0.00,  bc[2], bc[2]), (helix_start,  bc[2], helixR[2]), (helix_end,  helixR[2], bc[2]), (sheet_start,  bc[2], sheet[2]), (sheet_end,  sheet[2], polyproline[2]), (polyproline_end, polyproline[2], bc[2]), (1, bc[2],bc[2]))
        }
cmap = LinearSegmentedColormap('SecondaryStructureHard', cdict)
plt.register_cmap(cmap=cmap)
# -------------------------
# NEW COLOR SCHEME: secondary structure (expected range: R=[0,1])
def border_mod(v):
	# Old min/max
	#  0               1
	#  |   v           |
	# to:
	# New min/max
	#             0.9  1
	#              |v  |
	old_min = 0.0; old_max=1.0
	new_min = 0.9; new_max=1.0
	return new_min + (new_max-new_min)*(v-old_min)/(old_max-old_min)
#
#                         white  white                  white                   red (ish)                                   red        red                             red(ish)  white                  white                 blue(ish)                                 blue      blue                               blue(ish)        cyan                                      cyan(ish)  white       white white
cdict = {  #                  |      |                      |                     |                                           |          |                                   |       |                      |                    |                                         |         |                                  |                |                                             |       |           |     |                  
           'red': ((0.00,  bc[0], bc[0]), (helix_start,  bc[0], border_mod(helixR[0])), ((helix_start+helix_end)/2.0,  helixR[0], helixR[0]), (helix_end,  border_mod(helixR[0]), bc[0]), (sheet_start,  bc[0], border_mod(sheet[0])), ((sheet_start+sheet_end)/2.0,  sheet[0], sheet[0]), (sheet_end,  border_mod(sheet[0]), polyproline[0]), (polyproline_end, border_mod(polyproline[0]), bc[0]), (1, bc[0],bc[0])),
         'green': ((0.00,  bc[1], bc[1]), (helix_start,  bc[1], border_mod(helixR[1])), ((helix_start+helix_end)/2.0,  helixR[1], helixR[1]), (helix_end,  border_mod(helixR[1]), bc[1]), (sheet_start,  bc[1], border_mod(sheet[1])), ((sheet_start+sheet_end)/2.0,  sheet[1], sheet[1]), (sheet_end,  border_mod(sheet[1]), polyproline[1]), (polyproline_end, border_mod(polyproline[1]), bc[1]), (1, bc[1],bc[1])), 
          'blue': ((0.00,  bc[2], bc[2]), (helix_start,  bc[2], border_mod(helixR[2])), ((helix_start+helix_end)/2.0,  helixR[2], helixR[2]), (helix_end,  border_mod(helixR[2]), bc[2]), (sheet_start,  bc[2], border_mod(sheet[2])), ((sheet_start+sheet_end)/2.0,  sheet[2], sheet[2]), (sheet_end,  border_mod(sheet[2]), polyproline[2]), (polyproline_end, border_mod(polyproline[2]), bc[2]), (1, bc[2],bc[2]))
        }
cmap = LinearSegmentedColormap('SecondaryStructure', cdict)
plt.register_cmap(cmap=cmap)
# ----------------
# NEW COLOR SCHEME: color by secondary structure (expected range: R=[-1,1])
# ----------------
# POSITION (MIRRORRED AROUND 0): 0          helix_start       helix_end       sheet_start     sheet_end             polyproline_end            1
#                         COLOR: | white - white | helixR - helixR | white - white | sheet - sheet | polyproline - polyproline | white - white |
cdict = {  
           'red': [[-1,  bc[0], bc[0]], [polyproline_end*-1, bc[0],polyproline[0]], [sheet_end*-1,  polyproline[0],sheet[0]], [sheet_start*-1,  sheet[0], bc[0]], [helix_end*-1, bc[0],helixR[0]], [helix_start*-1, helixR[0],bc[0]], [helix_start,  bc[0], helixR[0]], [helix_end,  helixR[0], bc[0]], [sheet_start,  bc[0], sheet[0]], [sheet_end,  sheet[0], polyproline[0]], [polyproline_end, polyproline[0], bc[0]], [1, bc[0],bc[0]]],
         'green': [[-1,  bc[1], bc[1]], [polyproline_end*-1, bc[1],polyproline[1]], [sheet_end*-1,  polyproline[1],sheet[1]], [sheet_start*-1,  sheet[1], bc[1]], [helix_end*-1, bc[1],helixR[1]], [helix_start*-1, helixR[1],bc[1]], [helix_start,  bc[1], helixR[1]], [helix_end,  helixR[1], bc[1]], [sheet_start,  bc[1], sheet[1]], [sheet_end,  sheet[1], polyproline[1]], [polyproline_end, polyproline[1], bc[1]], [1, bc[1],bc[1]]], 
          'blue': [[-1,  bc[2], bc[2]], [polyproline_end*-1, bc[2],polyproline[2]], [sheet_end*-1,  polyproline[2],sheet[2]], [sheet_start*-1,  sheet[2], bc[2]], [helix_end*-1, bc[2],helixR[2]], [helix_start*-1, helixR[2],bc[2]], [helix_start,  bc[2], helixR[2]], [helix_end,  helixR[2], bc[2]], [sheet_start,  bc[2], sheet[2]], [sheet_end,  sheet[2], polyproline[2]], [polyproline_end, polyproline[2], bc[2]], [1, bc[2],bc[2]]]  
        } 
# this cdict is not normalized from 0 to 1, which is required for the line following the "for" loop.
minpos = False
maxpos = False
for color in  list(cdict.keys()):
	for i in range(len(cdict[color])):
		if minpos == False:
			minpos = cdict[color][i][0]
		if maxpos == False:
			maxpos = cdict[color][i][0]
		if minpos > cdict[color][i][0]:
			minpos = cdict[color][i][0]
		if maxpos < cdict[color][i][0]:
			maxpos = cdict[color][i][0]
for color in  list(cdict.keys()):
	for i in range(len(cdict[color])):
		cdict[color][i][0] = float(cdict[color][i][0]-minpos)/(maxpos-minpos)
cmap = LinearSegmentedColormap('SecondaryStructureFourColor', cdict)
plt.register_cmap(cmap=cmap)


#rcode_cmap = plt.get_cmap('Chirality')
#rcode_cmap = plt.get_cmap('Chirality_r')
rcode_cmap = plt.get_cmap('ChiralityFourColor')
#rcode_cmap = plt.get_cmap('ChiralityFourColor_r')
#rcode_cmap = plt.get_cmap('SecondaryStructure')
#rcode_cmap = plt.get_cmap('SecondaryStructureFourColor')


#secondarystructure_cmap = my_cmap
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
f = open("templates/postscript.ps","r")
postscript_template = f.read()
f.close()

# ===================================================================================

# Simple smoothing function
def median_filter(vals,nearest_neighbors=1):
	new_vals = []
	len_vals = len(vals)
	for i in range(len_vals):
		val = vals[i]
		if i-nearest_neighbors >= 0 and i+nearest_neighbors < len_vals:
			val = np.median(vals[i-nearest_neighbors:i+nearest_neighbors+1])
		new_vals.append(val)
	return new_vals

# important if you want to take our XYZ data and use it to create images using MATPLOTLIB
def xyz_to_image(X,Y,Z):
	xset = sorted(set(X))
	yset = sorted(set(Y))
	imagex = np.ones((len(yset)+1,len(xset)+1))
	imagey = np.ones((len(yset)+1,len(xset)+1))
	imagez = np.ones((len(yset)  ,len(xset)  ))
	#
	xstep = float(xset[0])
	if len(xset) > 1:
		xstep = float(xset[1])-float(xset[0])
	ystep = float(yset[0])
	if len(yset) > 1:
		ystep = float(yset[1])-float(yset[0])
	#
	for x,y,z in zip(X,Y,Z):
		xi = xset.index(x)
		yi = yset.index(y)
		imagex[yi+1][xi+1] = x - xstep/2
		imagey[yi+1][xi+1] = y
		imagez[yi][xi] = z
	#
	for x in xset:
		imagex[0][xset.index(x)+1] = x #+ xstep
	for y in yset:
		imagey[yset.index(y)+1][0] = y
	#
	#imagex[0][0] = xset[-1] + xstep
	#imagey[0][0] = yset[-1] 
	#
	return imagex,imagey,imagez

# SOMETHING THAT PICKS DECENT VALUES FOR TICKMARKS WITHIN A GRAPH'S AXIS GIVEN THE RANGE IN DATA
# A modified version of the alpha version of the Talbot, Lin, Hanrahan tick mark generator for matplotlib.
# Described in "An Extension of Wilkinson's Algorithm for Positioning Tick Labels on Axes"
# by Justin Talbot, Sharon Lin, and Pat Hanrahan, InfoVis 2010. http://vis.stanford.edu/files/2010-TickLabels-InfoVis.pdf
# Implementation modified by Ranjan Mannige from that provided by Justin Talbot
def Extended(vmin, vmax, density_val = 1, steps = None):
	if steps is None:
		steps = [1, 5, 2, 2.5, 4, 3]
	
	def coverage(dmin, dmax, lmin, lmax):
		range = dmax-dmin
		return 1 - 0.5 * (math.pow(dmax-lmax, 2)+math.pow(dmin-lmin, 2)) / math.pow(0.1 * range, 2)
	
	def coverage_max(dmin, dmax, span):
		range = dmax-dmin
		if span > range:
			half = (span-range)/2.0
			return 1 - math.pow(half, 2) / math.pow(0.1*range, 2)
		else:
			return 1
	
	def density(k, m, dmin, dmax, lmin, lmax):
		r = (k-1.0) / (lmax-lmin)
		rt = (m-1.0) / (max(lmax, dmax) - min(lmin, dmin))
		return 2 - max( r/rt, rt/r )
	
	def density_max(k, m):
		if k >= m:
			return 2 - (k-1.0)/(m-1.0)
		else:
			return 1
	
	def simplicity(q, Q, j, lmin, lmax, lstep):
		eps = 1e-10
		n = len(Q)
		i = Q.index(q)+1
		v = 1 if ((lmin % lstep < eps or (lstep - lmin % lstep) < eps) and lmin <= 0 and lmax >= 0) else 0
		return (n-i)/(n-1.0) + v - j
	
	def simplicity_max(q, Q, j):
		n = len(Q)
		i = Q.index(q)+1
		v = 1
		return (n-i)/(n-1.0) + v - j
	
	def legibility(lmin, lmax, lstep):
		return 1
	
	def legibility_max(lmin, lmax, lstep):
		return 1
	
	def extended(dmin, dmax, m, Q=[1,5,2,2.5,4,3], only_inside=False, w=[0.25,0.2,0.5,0.05]):
		n = len(Q)
		best_score = -2.0

		j = 1.0
		while j < float('infinity'):
			for q in Q:
				sm = simplicity_max(q, Q, j)

				if w[0] * sm + w[1] + w[2] + w[3] < best_score:
					j = float('infinity')
					break

				k = 2.0
				while k < float('infinity'):
					dm = density_max(k, m)

					if w[0] * sm + w[1] + w[2] * dm + w[3] < best_score:
						break

					delta = (dmax-dmin)/(k+1.0)/j/q
					z = math.ceil(math.log(delta, 10))
		
					while z < float('infinity'):
						step = j*q*math.pow(10,z)
						cm = coverage_max(dmin, dmax, step*(k-1.0))

						if w[0] * sm + w[1] * cm + w[2] * dm + w[3] < best_score:
							break

						min_start = math.floor(dmax/step)*j - (k-1.0)*j
						max_start = math.ceil(dmin/step)*j

						if min_start > max_start:
							z = z+1
							break

						for start in range(int(min_start), int(max_start)+1):
							lmin = start * (step/j)
							lmax = lmin + step*(k-1.0)
							lstep = step

							s = simplicity(q, Q, j, lmin, lmax, lstep)
							c = coverage(dmin, dmax, lmin, lmax)
							d = density(k, m, dmin, dmax, lmin, lmax)
							l = legibility(lmin, lmax, lstep)

							score = w[0] * s + w[1] * c + w[2] * d + w[3] * l

							if score > best_score and (not only_inside or (lmin >= dmin and lmax <= dmax)):
								best_score = score
								best = (lmin, lmax, lstep, q, k)
						z = z+1
					k = k+1
			j = j+1
		return best

	#vmin, vmax = axis.get_view_interval()
	size = 5 #_figure.get_size_inches()[_which]
	# density * size gives target number of intervals,
	# density * size + 1 gives target number of tick marks,
	# the density function converts this back to a density in data units (not inches)
	# should probably make this cleaner.
	best = extended(vmin, vmax, density_val * size + 1.0, only_inside=True, w=[0.25, 0.2, 0.5, 0.05])
	locs = np.arange(best[4]) * best[2] + best[0]
	return locs
#

def calculate_dihedral_angle(p):
	b = p[:-1] - p[1:]
	b[0] *= -1
	v = np.array( [ v - (v.dot(b[1])/b[1].dot(b[1])) * b[1] for v in [b[0], b[2]] ] )
	# Normalize vectors
	v /= np.sqrt(np.einsum('...i,...i', v, v)).reshape(-1,1)
	b1 = b[1] / np.linalg.norm(b[1])
	x = np.dot(v[0], v[1])
	m = np.cross(v[0], b1)
	y = np.dot(m, v[1])
	d = np.degrees(np.arctan2( y, x ))
	return d

aa_three_to_one = {'CYS': 'C', 'ASP': 'D', 'SER': 'S', 'GLN': 'Q', 'LYS': 'K',
     'ILE': 'I', 'PRO': 'P', 'THR': 'T', 'PHE': 'F', 'ASN': 'N', 
     'GLY': 'G', 'HIS': 'H', 'LEU': 'L', 'ARG': 'R', 'TRP': 'W', 
     'ALA': 'A', 'VAL':'V', 'GLU': 'E', 'TYR': 'Y', 'MET': 'M'}
#
	
def read_pdb_biopython(fn,signed=0):
	p=PDB.PDBParser() #(PERMISSIVE=1)
	structure=p.get_structure(fn[:-len(".pdb")], fn)
	#for model in structure:
	#	print [model.id]
	model_to_chain_to_resno_atom_to_vals = {}
	# structure (models) -> model -> chain -> residue -> atom
	for model in structure:
		model_number = model.id
		#
		if not model_number in model_to_chain_to_resno_atom_to_vals:
			model_to_chain_to_resno_atom_to_vals[model_number] = {}
		#
		for chain in model:
			segname = chain.id
			if not segname in model_to_chain_to_resno_atom_to_vals[model_number]:
				model_to_chain_to_resno_atom_to_vals[model_number][segname] = {}
			
			for residue in chain:
				resname = residue.resname
				resno   = residue.id[1]
				
				#
				i = resno
				im = i-1
				ip = i+1
				
				neighbors_found = 1
				try:
					a = structure[model_number][segname][im]["C"].coord
					b = structure[model_number][segname][i]["N"].coord
					c = structure[model_number][segname][i]["CA"].coord
					d = structure[model_number][segname][i]["C"].coord
					e = structure[model_number][segname][ip]["N"].coord
					
					if not resno in model_to_chain_to_resno_atom_to_vals[model_number][segname]:
						model_to_chain_to_resno_atom_to_vals[model_number][segname][resno] = {}
					
					model_to_chain_to_resno_atom_to_vals[model_number][segname][resno]["resname"] = resname
					singleaa = resname
					if resname in aa_three_to_one:
						singleaa = aa_three_to_one[resname]
					model_to_chain_to_resno_atom_to_vals[model_number][segname][resno]["aa"] = singleaa
					model_to_chain_to_resno_atom_to_vals[model_number][segname][i]["n"]  = b
					model_to_chain_to_resno_atom_to_vals[model_number][segname][i]["ca"] = c
					model_to_chain_to_resno_atom_to_vals[model_number][segname][i]["c"]  = d
				
				except:
					neighbors_found = 0
				
				if neighbors_found: #im in resids and ip in resids:
					phi = calculate_dihedral_angle(np.array([a,b,c,d]))
					psi = calculate_dihedral_angle(np.array([b,c,d,e]))
					rho = normalized_ramachandran_number(phi,psi,signed)
					#
					model_to_chain_to_resno_atom_to_vals[model_number][segname][i]["phi"] = phi
					model_to_chain_to_resno_atom_to_vals[model_number][segname][i]["psi"] = psi
					model_to_chain_to_resno_atom_to_vals[model_number][segname][i]["R"] = rho
					#
				#
			#
		#
		if not len(model_to_chain_to_resno_atom_to_vals[model_number]):
			del model_to_chain_to_resno_atom_to_vals[model_number]
	#
	
	
	return model_to_chain_to_resno_atom_to_vals

# OLD VERSION (IN HOUSE). IT IS FASTER THAN THE CURRENT "read_pdb", WHICH IS BIOPDB RUN, BUT IT IS NOT 
# AS WELL TESTED.
def read_pdb_inhouse(fn,signed=0):
	"""
	ATOM     10 1H   LYS A   1       0.763   3.548  -0.564
	ATOM     11 2H   LYS A   1       1.654   2.664   0.488
	ATOM    482  N   PRO A  61      27.194  -5.761  14.684  1.00  9.09           N  
	ATOM      2  CA  BLYSX   1     -77.937 -26.325   6.934  1.00  0.00      U1    
	ATOM      3  CB  BLYSX   1     -79.612 -24.499   7.194  1.00  0.00      U1    
	ATOM      4  CE  BLYSX   1     -80.894 -24.467   8.039  1.00  0.00      U1    
	ATOM      5  NZ  BLYSX   1     -80.687 -24.160   9.434  1.00  0.00      U1    
	ATOM      2  HT1 MET U   1       0.208   0.762 -12.141  0.00  0.00      UBIQ  
	ATOM      3  HT2 MET U   1      -1.052  -0.551 -12.281  0.00  0.00      UBIQ  
	          |   |   |  |   |        |       |       |                     |
	     atomno   |   |  |   |        x       y       z                 segname
	       atom type  |  |   |                                          (CHAIN)
	            restype  |   3resno
	                 chainID
	"""
	
	f = open(fn,"r")
	pdbblock = f.read()
	f.close()
	
	getlines = re.compile("ATOM\s+(?P<atomno>\d+)\s+(?P<atomtype>\S+)\s+.(?P<resname>...)..\s+(?P<resno>\d+)\s+(?P<x>\-*\d+\.*\d*)\s+(?P<y>\-*\d+\.*\d*)\s+(?P<z>\-*\d+\.*\d*).{17}(?P<segname>.{5})",re.M)
	getlines_short = re.compile("ATOM\s+(?P<atomno>\d+)\s+(?P<atomtype>\S+)\s+(?P<resname>...).(?P<segname>.)\s+(?P<resno>\d+)\s+(?P<x>\-*\d+\.*\d*)\s+(?P<y>\-*\d+\.*\d*)\s+(?P<z>\-*\d+\.*\d*)",re.M)
	
	resnos = []
	#models = pdbblock.split("\nEND\n")
	models = re.split("\nEND|\nMODEL|\nTER",pdbblock)
	
	model_number = 0
	model_to_chain_to_resno_atom_to_vals = {}
	# structure (models) -> model -> chain -> residue -> atom
	
	#t0 = time.time()
	#print "#\treading...",
	for model_index in range(len(models)):
		model = models[model_index]
		if len(model.rstrip()) > 1:
			model_number+=1
			if not model_number in model_to_chain_to_resno_atom_to_vals:
				model_to_chain_to_resno_atom_to_vals[model_number] = {}
			
			segname_exists = 1
			currentlines = getlines.finditer(model)
			if not getlines.search(model):
				currentlines = getlines_short.finditer(model)
				segname_exists = 0
			
			for i in currentlines:
				vals = i.groupdict()
				atomtype = vals["atomtype"] #line[11:17].lstrip().rstrip()
				
				if atomtype=="CA" or atomtype =="N" or atomtype =="C":
					resno = int(vals["resno"]) #int(resno) #int(line[22:26].lstrip().rstrip())
					xyz = np.array([float(vals["x"]),float(vals["y"]),float(vals["z"])])
					
					segname = "A"
					if segname_exists:
						segname = vals["segname"].lstrip().rstrip()
					
					if not segname in model_to_chain_to_resno_atom_to_vals[model_number]:
						model_to_chain_to_resno_atom_to_vals[model_number][segname] = {}
					
					if not resno in model_to_chain_to_resno_atom_to_vals[model_number][segname]:
						model_to_chain_to_resno_atom_to_vals[model_number][segname][resno] = {}
					
					model_to_chain_to_resno_atom_to_vals[model_number][segname][resno][atomtype.lower()] = xyz
					model_to_chain_to_resno_atom_to_vals[model_number][segname][resno]["resname"] = vals["resname"]
			
			if not len(model_to_chain_to_resno_atom_to_vals[model_number]):
				del model_to_chain_to_resno_atom_to_vals[model_number]
				model_number-=1
	#
	for model in sorted(model_to_chain_to_resno_atom_to_vals.keys()):
		for chain in sorted(model_to_chain_to_resno_atom_to_vals[model].keys()):
			for resno in sorted(model_to_chain_to_resno_atom_to_vals[model][chain].keys()):
				triplet_found = 0
				if "ca" in model_to_chain_to_resno_atom_to_vals[model][chain][resno]:
					triplet_found+=1
				if "n" in model_to_chain_to_resno_atom_to_vals[model][chain][resno]:
					triplet_found+=1
				if "c" in model_to_chain_to_resno_atom_to_vals[model][chain][resno]:
					triplet_found+=1
				if triplet_found == 3:
					i = resno
					im = i-1
					ip = i+1
					
					neighbors_found = 0
					if im in model_to_chain_to_resno_atom_to_vals[model][chain]:
						if "c" in model_to_chain_to_resno_atom_to_vals[model][chain][im]:
							neighbors_found += 1
					if ip in model_to_chain_to_resno_atom_to_vals[model][chain]:
						if "n" in model_to_chain_to_resno_atom_to_vals[model][chain][ip]:
							neighbors_found += 1
					
					if neighbors_found == 2: #im in resids and ip in resids:
						a = model_to_chain_to_resno_atom_to_vals[model][chain][im]["c"] # resno_to_coordC[before]
						b = model_to_chain_to_resno_atom_to_vals[model][chain][i]["n"] # resno_to_coordN[current]
						c = model_to_chain_to_resno_atom_to_vals[model][chain][i]["ca"] #resno_to_coordCA[current]
						d = model_to_chain_to_resno_atom_to_vals[model][chain][i]["c"] # resno_to_coordC[current]
						e = model_to_chain_to_resno_atom_to_vals[model][chain][ip]["n"]  # resno_to_coordN[after]
						
						phi = calculate_dihedral_angle(np.array([a,b,c,d]))
						psi = calculate_dihedral_angle(np.array([b,c,d,e]))
						rho = normalized_ramachandran_number(phi,psi,signed)
						
						model_to_chain_to_resno_atom_to_vals[model][chain][i]["phi"] = phi
						model_to_chain_to_resno_atom_to_vals[model][chain][i]["psi"] = psi
						model_to_chain_to_resno_atom_to_vals[model][chain][i]["R"] = rho
	#
	return model_to_chain_to_resno_atom_to_vals
#

def check_pdb(fn):
	"""
	ATOM     10 1H   LYS A   1       0.763   3.548  -0.564
	ATOM     11 2H   LYS A   1       1.654   2.664   0.488
	ATOM    482  N   PRO A  61      27.194  -5.761  14.684  1.00  9.09           N  
	ATOM      2  CA  BLYSX   1     -77.937 -26.325   6.934  1.00  0.00      U1    
	ATOM      3  CB  BLYSX   1     -79.612 -24.499   7.194  1.00  0.00      U1    
	ATOM      4  CE  BLYSX   1     -80.894 -24.467   8.039  1.00  0.00      U1    
	ATOM      5  NZ  BLYSX   1     -80.687 -24.160   9.434  1.00  0.00      U1    
	ATOM      2  HT1 MET U   1       0.208   0.762 -12.141  0.00  0.00      UBIQ  
	ATOM      3  HT2 MET U   1      -1.052  -0.551 -12.281  0.00  0.00      UBIQ  
	          |   |   |  |   |        |       |       |                     |
	     atomno   |   |  |   |        x       y       z                 segname
	       atom type  |  |   |                                          (CHAIN)
	            restype  |   resno
	                 chainID
	"""
	
	chainIDindex = 21
	chainIDindexMinusOne = chainIDindex-1
	lenATOM = len("ATOM ")
	
	chainIDpossibilities = ""
	chainIDpossibilities+=string.uppercase # 'A' through 'Z'.
	for i in range(10):
		chainIDpossibilities+=str(i)
	chainIDpossibilities+=string.lowercase # 'a' through 'z'.
	lenchainIDpossibilities = len(chainIDpossibilities)
	largestchainIDindex = 0
	
	made_changes = 0
	f = open(fn,"r")
	lines = f.readlines()
	f.close()
	pdb_is_possibly_problematic = 0
	segname_to_chainID = {}
	for i in range(len(lines)):
		if len(lines[i]) > 67:
			if lines[i][:lenATOM] == "ATOM ":
				chainID = lines[i][chainIDindex].rstrip()
				chainIDspacebefore = lines[i][chainIDindexMinusOne].rstrip()
				if len(chainIDspacebefore): # This is because some CHARMM sidechains have four letters, and that trips biopython
					pdb_is_possibly_problematic = 1
				
				if len(chainID)==0 or chainID=="X": # CHARMM SOMETIMES SAVES THE CHAINID AS 'X' IRRESPECTIVE OF SEGNAME
					pdb_is_possibly_problematic = 1
				#
			#
		#
	if pdb_is_possibly_problematic:
		return 0
	else:
		return 1
#
def read_pdb(fn,signed=0):
	raw_pdb_data = False
	if biopython:
		if check_pdb(fn):
			raw_pdb_data = read_pdb_biopython(fn,signed=signed)
		else:
			raw_pdb_data = read_pdb_inhouse(fn,signed=signed)
	else:
		raw_pdb_data = read_pdb_inhouse(fn,signed=signed)
	#
	matrix_material = [['model','chain','resid','R']]
	for model in list(raw_pdb_data.keys()):
		for chain in list(raw_pdb_data[model].keys()):
			for resid in list(raw_pdb_data[model][chain].keys()):
				R = False
				if 'R' in raw_pdb_data[model][chain][resid]:
					R = raw_pdb_data[model][chain][resid]['R']
				matrix_material.append([int(model),chain,int(resid),R])
	
	# Creating a matrix that can be queriable later
	pdb_matrix = np.array(matrix_material,dtype='O')
	return pdb_matrix
#

# Draw the mapping between phi,psi and Ramachandran number
def show_ramachandran_mapping(cmap=plt.get_cmap("Blues"),fn = "deme", stepsize=5,signed=0):
	PHI = []
	PSI = []
	RHO = []
	for phi in range(-180,181,stepsize):
		for psi in range(-180,181,stepsize):
			PHI.append(phi)
			PSI.append(psi)
			normalizedr = normalized_ramachandran_number(phi,psi,signed=signed)
			RHO.append(normalizedr)
	X=np.array(PHI)
	Y=np.array(PSI)
	Z=np.array(RHO)
	
	#color_bar_range = np.arange(0,1.01,0.01)
	color_bar_range = np.arange(rrange[0],rrange[-1]+0.005,0.01)
	
	if fn[-len(".eps"):] == ".eps":
		fn = fn[:-len(".eps")]
	
	cbfn = fn+"_colorbar.eps"
	fn = fn+".eps"
	
	print("#WRITING TO:",cbfn)
	make2Dfigure(np.ones(len(color_bar_range)),color_bar_range,color_bar_range,cmap=cmap, fn=cbfn, xscaling=colorbarXscaling,xtitle="Key",showeps=0)
	#
	print("#WRITING TO:",fn)
	make2Dfigure(X,Y,Z,fn,cmap=cmap,xscaling=1.0,xtitle="phi",ytitle="psi",xlabels=list(range(-180,181,90)),ylabels=list(range(-180,181,90)),showeps=0)
	#
	return 1
#

# From: https://stackoverflow.com/questions/7965743/how-can-i-set-the-aspect-ratio-in-matplotlib
def forceAspect(aspect,ax=False):
	if not ax: ax=plt.gca()
	#im = ax.get_images()
	#extent =  im[0].get_extent()
	extent = plt.axis()
	ax.set_aspect(abs((extent[1]-extent[0])/(extent[3]-extent[2]))/aspect)

# From: https://stackoverflow.com/questions/44970010/axes-class-set-explicitly-size-width-height-of-axes-in-given-units
def set_size(w,h, ax=None):
	""" w, h: width, height in inches """
	if not ax: ax=plt.gca()
	l = ax.figure.subplotpars.left
	r = ax.figure.subplotpars.right
	t = ax.figure.subplotpars.top
	b = ax.figure.subplotpars.bottom
	figw = float(w)/(r-l)
	figh = float(h)/(t-b)
	ax.figure.set_size_inches(figw, figh)
#

def write_image(fn_base):
	plt.savefig(fn+'.eps',dpi=200,bbox_inches='tight')
	plt.savefig(fn+'.png',dpi=200,bbox_inches='tight')
	if show: plt.show();

def draw_xyz(X,Y,Z, ylim=False, cmap='Greys', xlabel=False,ylabel=False,zlabel=False,title=False,vmin=None,vmax=None):
	
	aspect = 2.
	if len(set(X)) == 1:
		# Some structures have only one model, which is too thin, 
		# so we add another row with everything else being identical 
		# except that all new xs are skewed by 1
		X = list(X) + list(np.array(X)+1)
		Y = list(Y) + list(Y)
		Z = list(Z) + list(Z)
		# Also, the aspect ratio needs to be reset, since we are dealing with only one column
		aspect = .2
	#
	# Getting unique values for X
	setX = sorted(set(X))
	# Getting unique values for Y 
	setY = sorted(set(Y))
	
	# Code that offsets the values
	if 1: 
		# We want whole numbers to be situated at the middle of each column, not at the beginning and end
		# X
		# Getting the grid step size
		xsteps = []
		for i in range(1,len(setX)):
			xsteps.append(setX[i]-setX[i-1])
		xstep = np.median(xsteps)
		# Making the offset
		X = np.array(X)-xstep
		# Y
		# Getting the grid step size
		ysteps = []
		for i in range(1,len(setY)):
			ysteps.append(setY[i]-setY[i-1])
		ystep = np.median(ysteps)
		# Making the offset
		Y = np.array(Y)-ystep
		
		# Resetting the sorted unique values
		# Getting unique values for X
		setX = sorted(set(X))
		# Getting unique values for Y 
		setY = sorted(set(Y))
			
	
	#
	# A dictionary containing X values and their indices once ordered 
	X_to_ix = dict([[setX[ix],ix] for ix in range(len(setX))])
	# Creating a new array of indices instead of values
	Xix     =      [   X_to_ix[v] for  v in              X  ]
	
	# A dictionary containing X values and their indices once ordered 
	Y_to_ix = dict([[setY[ix],ix] for ix in range(len(setY))])
	# Creating a new array of indices instead of values
	Yix     =      [   Y_to_ix[v] for  v in              Y  ]
	
	# Creating an empty array with the right dimensions
	z_array = np.zeros((len(setY),len(setX))) * np.nan
	# Setting values of Z based on their position in the matrix
	z_array[Yix, Xix] = Z
	
	# Initiating the figure
	plt.clf()
	ax = plt.gca()
	# Drawing the main part of the figure
	
	im = plt.imshow(z_array,origin='lower',cmap=cmap,vmin=vmin,vmax=vmax,interpolation='nearest', extent=[min(X),max(X),min(Y),max(Y)])
	
	# create an axes on the right side of ax. The width of cax will be 5%
	# of ax and the padding between cax and ax will be fixed at 0.05 inch.
	cb = plt.colorbar(im,fraction=0.023, pad=0.04)
	[i.set_linewidth(1.5) for i in ax.spines.values()]
	
	# Setting labels
	if xlabel: plt.xlabel(xlabel, fontsize=15);
	if ylabel: plt.ylabel(ylabel, fontsize=15);
	if zlabel: cb.ax.set_title(zlabel,  rotation=0,fontsize=15);
	
	# Setting title
	if title: plt.title(title,fontsize=16)
	
	# limiting y if specified
	if ylim: plt.ylim(ylim);
	
	# Setting the aspect ratio
	forceAspect(aspect,ax=ax) #set_size(10,10)
	
	# Neatening things out
	plt.tight_layout()
	#
	# To see this graph and quit, uncomment the following:
	#plt.show(); exit();
#

# Grouping each data by 
def group_by(data,group_by="chain",columns_to_return=['model','resid','R']):
	# Getting column indices for each column name
	rx = {} # "rx" for Row indeX
	# Taking the first row and getting the column name and index
	for col in data[0,:]:
		rx[col] = list(data[0,:]).index(col)
	# 
	group_by_values = sorted(set(data[1:,rx[group_by]]))
	#
	grouped_data    = {}
	for filter_value in group_by_values:
		current_data = data[np.where(data[:,rx[group_by]] == filter_value)]
		grouped_data[filter_value] = []
		for return_column in columns_to_return:
			grouped_data[filter_value].append(current_data[:,rx[return_column]])
	#	
	return grouped_data
#

'''
N = 10
X = np.arange(N)*12
Y = np.arange(N)*-1.2
Z = np.arange(N)
draw_xyz_to_matrix(list(X),list(Y),list(Z))
plt.show()
'''	
if __name__ == "__main__":
	'''
	print("LOADING")
	# Set pdb name 
	pdbfn = './pdbs/nanosheet_birth_U7.pdb'
	# READ PDB in the form of a matrix with columns
	data = read_pdb(pdbfn)
	# <data> is a 2d array with four columns
	# ['model','chain','resid','R'] ... first row is a header, with values that follow
	
	# setting the name of the colormap
	cmap = "Chirality"
	
	# DRAWING A SINGLE GRAPH
	# Getting only those values for the particular chain 
	print("PLOTTING")
	grouped_data = group_by(data,group_by = 'chain', columns_to_return=['model','resid','R'])
	for chain in list(grouped_data.keys()):
		print('\t',chain)
		# Getting the X,Y,Z values for each entry
		models, residues, Rs = grouped_data[chain]
		
		# Finally, creating (but not showing) the graph 
		draw_xyz(X = models  ,      Y = residues  ,     Z = Rs
		   ,xlabel ='Frame #', ylabel ="Residue #",zlabel ='$\mathcal{R}$'
			 ,cmap = cmap    ,  title = cmap, vmin=0, vmax=1)
		# Now, we display the graph:
		#plt.show() # ... one can also use plt.savefig() to save to file
		plt.savefig('manuscript/automated_figures/example.pdf',dpi=200,bbox_inches="tight")
		print("Saved to:",'manuscript/automated_figures/example.pdf')
	#
	# DRAWING A SINGLE GRAPH
	# Getting only those values for the particular chain 
	print("PLOTTING HISTOGRAM")
	import numpy as np # for handling 2d arrays and calculating histograms
	pdbfn = './pdbs/1xqq.pdb'
	# READ PDB in the form of a matrix with columns
	data = read_pdb(pdbfn)
	# Getting only those values for the particular chain 
	grouped_data = group_by(data,group_by='chain', 
						columns_to_return=['model','resid','R'])
	for chain in list(grouped_data.keys()):
		# Getting the X,Y,Z values for each entry
		models, residues, Rs = grouped_data[chain]
		X = []; Y=[]; Z=[]; # Will set X=model, Y=R, Z=P(R)
		# Bundling the three lists into one 2d array
		new_data =  np.array(list(zip(models,residues,Rs)))
		# Getting all R values, model by model
		for m in sorted(set(new_data[:,0])): # column 0 is the model column
			# Getting all Rs for that model #
			current_rs = new_data[np.where(new_data[:,0]==m)][:,2] # column 2 contains R
			# Getting the histogram
			a,b = np.histogram(current_rs,bins=np.arange(0,1.01,0.01))
			max_count = float(np.max(a))
			for i in range(len(a)):
				X.append(m); Y.append((b[i]+b[i+1])/2.0); Z.append(a[i]/float(np.max(a)));
		
		# Finally, creating (but not showing) the graph 
		draw_xyz(X = X       ,      Y = Y  ,                Z = Z
		   ,xlabel ='Frame #', ylabel ="$\mathcal{R}$",zlabel ="$P'(\mathcal{R})$:"
			 ,cmap = 'Greys', ylim=[0,1])
		plt.yticks(np.arange(0,1.00001,0.2))
		# Now, we display the graph:
		plt.savefig('manuscript/automated_figures/example2.pdf',dpi=200,bbox_inches="tight")
		print("Saved to:",'manuscript/automated_figures/example.pdf')
		plt.show() # ... one can also use plt.savefig() to save to file
		
	# TRYING OUT VARIOUS CMAPS
	# Getting only those values for the particular chain 
	print("PLOTTING")
	grouped_data = group_by(data,group_by = 'chain', columns_to_return=['model','resid','R'])
	for chain in list(grouped_data.keys()):
		print('\t',chain)
		# Getting the X,Y,Z values for each entry
		models, residues, Rs = grouped_data[chain]
		for cmap in ['Greys','SecondaryStructure','Chirality']: #, 'Chirality_r', 'SecondaryStructureHard']:
			# Finally, creating (but not showing) the graph 
			draw_xyz(X = models  ,      Y = residues  ,     Z = Rs
			   ,xlabel ='Frame #', ylabel ="Residue #",zlabel ='$\mathcal{R}$'
				 ,cmap = cmap    ,  title = os.path.split(pdbfn)[-1][:-len('.pdb')]+' (CMAP: '+cmap+')'
				 ,vmin=0,vmax=1)
			# Now, we display the graph:
			#plt.show() # ... one can also use plt.savefig() to save to file
			FN = 'manuscript/automated_figures/example_%s.pdf' %(cmap)
			plt.savefig(FN,dpi=200,bbox_inches="tight")
			print("Saved to:",FN)
			plt.show()
		#
	#
	exit()
	'''
	if not "-pdb" in sys.argv:
		if "-h" in sys.argv or "-help" in sys.argv or "--help" in sys.argv:
			pass
		else:
			print("Must provide '-pdb' parameter. Exiting.")
			exit(0)
	show = False
	for i in range(len(sys.argv)):
		if sys.argv[i] == "-rmsd":
			showrmsd = 1
		if sys.argv[i] == "-show":
			show = True
		if sys.argv[i] == "-signed":
			print("Using the R number with range [-1,1]")
			signed = 1
			rrange = [-1,1]
		if sys.argv[i] == "-ss":
			colortype = "SecondaryStructure" # default: chirality
		if sys.argv[i] == "-h" or sys.argv[i] == "-help" or sys.argv[i] == "--help":
			print(helpme)
			exit(1)
		if sys.argv[i] == "-pdb":
			if len(sys.argv) <= i+1:
				print(helpme)
				print("MUST PROVIDE PDB NAME.")
				exit(0)
			else:
				pdbfn = str(sys.argv[i+1])
				print("# pdbfn set to:",pdbfn)
		elif sys.argv[i] == "-bins":
			if len(sys.argv) <= i+1:
				helpme
				print("When using '-bins', you must provide bin number. Exiting.")
				exit(0)
			else:
				if not sys.argv[i+1].isdigit():
					print(helpme)
					print("The -bin parameter must be a positive integer (provided: "+str(sys.argv[i+1])+") Exiting.")
					exit(0)
				else:
					bins = int(sys.argv[i+1])
					print("# bins set to:",bins)
					if bins == 0:
						print(helpme)
						print("Must have greater than 0 bins. Exiting.")
						exit(0)
	
	colormap_name = colortype
	if signed:
		colormap_name = colortype+'FourColor'
	print("Using color map name:",colormap_name)
	rcode_cmap = plt.get_cmap(colormap_name)
	#rcode_cmap = plt.get_cmap("deletemeSigned")
	
	pdbfn = os.path.abspath(pdbfn)
	pdbdir = os.path.dirname(pdbfn)
	pdbfilenames = []
	
	if os.path.isfile(pdbfn):
		# then this pathname leads to a FILE
		# ... so keep as is
		pdbfilenames = [pdbfn]
	elif os.path.isdir(pdbfn):
		pdbdir = pdbfn
		pdbfilenames = sorted(glob.glob(pdbdir+"/*.pdb"))
	else:
		print(helpme)
		exit("Either filename or directory expected. Exiting.")
	
	target_dir = pdbdir+"/reports/"
	#if len(pdbfilenames)>1:
	#	target_dir = pdbdir+"/report/"
	if not os.path.isdir(target_dir):
		os.makedirs(target_dir)
	NAME = os.path.basename(pdbfilenames[0])[:-len(".pdb")]
	target_base = target_dir.rstrip("/")+"/"+NAME
	
	#
	# To see how the (phi,psi) to Ramachandran number mapping occurs, set "if 0:" to "if 1:" below.
	if 0:
		phi_psi_to_ramachandran_number_filename = "phi_psi_to_r"
		if signed:
			phi_psi_to_ramachandran_number_filename+="_signed"
		if colortype == "SecondaryStructure":
			phi_psi_to_ramachandran_number_filename+="_ss"
		show_ramachandran_mapping(signed=signed, cmap = rcode_cmap, fn=phi_psi_to_ramachandran_number_filename,stepsize=5)
		exit()
	
	# JUST "CLEVERLY" ARRANGING THE FILENAMES, IF WE HAVE A SET OF FILENAMES RATHER THAN ONE
	# (e.g., pdbfilenames = [something2part1,something1part2,something1part1,something10part1]
	# pdbfilenames.sort() this list to: [something1part1,something1part2,something2part1,something10part1]
	REXP = re.compile( r'\d+' )
	def key_function( s ): return list(map(int, re.findall(REXP, s )))
	pdbfilenames.sort( key=key_function)
	
	print("# Parsing the PDB (structure) data")
	structure = np.array([])
	for pdbfn in pdbfilenames:
		# Check if the PDB has no subunit IDs, and then check if segnames exist (right most column)
		# and renaming the subunit IDs alphabetically and then numerically
		
		# READ PDB in the form of a matrix with columns ['model','chain','resid','R']
		latest_structure = read_pdb(pdbfn,signed)
		
		# Getting column indices for each column name
		rx = {} # "rx" for Row indeX
		for c in latest_structure[0,:]:
			rx[c] = list(latest_structure[0,:]).index(c)
		#
		sorted_models        = sorted(list(set(latest_structure[1:,rx['model']])))
		current_model_number = 0
		original_to_new_model_numbers = {}
		for actual_model_number in sorted_models:
			current_model_number                              += 1
			original_to_new_model_numbers[actual_model_number] = current_model_number
		#
		
		# Checking if we already have some structures loaded (then we have to offset the model numbers)
		if len(structure):
			#
			largest_model_number = max(list(structure[1:,rx['model']]))
			for m in list(original_to_new_model_numbers.keys()):
				original_to_new_model_numbers[m] = original_to_new_model_numbers[m] + largest_model_number
			#
		#
		# Resetting model numbers 
		new_model_numbers = [original_to_new_model_numbers[actual_model_number] for actual_model_number in latest_structure[1:,rx['model']]]
		latest_structure[1:,rx['model']] = copy.deepcopy(new_model_numbers)
		#	
		
		if len(structure):
			# Copying as structure
			structure = np.append(structure,copy.deepcopy(latest_structure), axis=0)
		else:
			# Adding the current model to structure
			structure =  copy.deepcopy(latest_structure)
	print("\t...done")
	
	# FIRST, GETTING THE DIFFERENT CHAIN IDs
	chains = sorted(set(structure[1:,rx['chain']]))
	
	# FINALLY, WE WILL GO THROUGH EACH CHAIN AND PRODUCE GRAPHS
	batchedfilenames = {}
	for chain in chains:
		filenames = []	
		print("CHAIN:",chain)
		
		# Getting only those values for the particular chain 
		current_chain = structure[np.where(structure[:,rx['chain']] == chain)]
		sorted_models = sorted(set(current_chain[1:,rx['model']]))
		
		models  =[]
		residues=[]
		Rs      =[]
		
		for model in sorted_models:
			current_model = current_chain[np.where(current_chain[:,rx['model']] == model)]
			#
			for resid in sorted(set(current_model[:,rx['resid']])):
				# The Ramachandran number
				R = current_model[np.where(current_model[:,rx['resid']] == resid)][:,rx['R']].mean() 
				# ... 'mean()' is meant for if we have a single residue displaying ambiguous positions
				
				models.append(model)
				residues.append(resid)
				Rs.append(R)
		#
		
		# You can apply a median filter many times over (so, dofilter can be 0 for "no", or 1,2,3,4, ...)			
		for i in range(dofilter):
			Rs = median_filter(Rs)
		#		
		
		if showrcode:
			X =models;Y=residues;Z=Rs;
			fn = target_base+"_chain_"+chain+".rcode"
			filenames.append(fn)
			cmap = 'SecondaryStructure' #rcode_cmap
			draw_xyz(X,Y,Z,cmap=cmap, xlabel='Frame #',ylabel='Residue #',zlabel='$\mathcal{R}$', title="Chain: '%s'"%chain, vmin=0, vmax=1)
			write_image(fn)
		# ----------------------------------
		xy_to_z = {}
		for x,y,z in zip(X,Y,Z):
			xy_to_z[(x,y)] = z
		
		# ----------------------------------
		# RMSD from reference time
		if len(set(X))>1:
			reference_index = 0
			reference_time = sorted(set(X))[0]
			xy_to_z_rmsd = {}
			for (x,y) in list(xy_to_z.keys()):
				xy_to_z_rmsd[(x,y)] = abs(xy_to_z[(x,y)]-xy_to_z[(reference_time,y)])
			
			X = []
			Y = []
			Z = []
			for (x,y) in list(xy_to_z_rmsd.keys()):
				z = xy_to_z_rmsd[(x,y)]
				X.append(x)
				Y.append(y)
				Z.append(z)
			
			if 0:#normalize
				if max(Z):
					for i in range(len(Z)):
						Z[i] = Z[i]/max(Z)
			
			fn = target_base+"_chain_"+chain+".rcode.rmsd"+str(reference_index)
			filenames.append(fn)
			draw_xyz(X,Y,Z,cmap=plt.get_cmap("Reds"), xlabel='Frame #',ylabel='Residue #',zlabel='RMSD$_\mathcal{R}$', title="Chain: '%s'"%chain)
			write_image(fn)		
		# ----------------------------------
		# Fluctuations from previous time
		if len(set(X)) > 1:
			x_sorted = sorted(set(X))
			xy_to_z_fluc = {}
			for (x,y) in list(xy_to_z.keys()):
				current_x_index = x_sorted.index(x)
				previous_x_index = current_x_index-1
				if previous_x_index < 0:
					previous_x_index = 0
				previous_x = x_sorted[previous_x_index]
				xy_to_z_fluc[(x,y)] = abs(xy_to_z[(x,y)]-xy_to_z[(previous_x,y)])
			
			X = []
			Y = []
			Z = []
			for (x,y) in list(xy_to_z_fluc.keys()):
				z = xy_to_z_fluc[(x,y)]
				X.append(x)
				Y.append(y)
				Z.append(z)
			if 1:#normalize
				if max(Z):
					for i in range(len(Z)):
						Z[i] = Z[i]/max(Z)
			
			fn = target_base+"_chain_"+chain+".rcode.rmsf"
			filenames.append(fn)
			draw_xyz(X,Y,Z,cmap=plt.get_cmap("Blues"), xlabel='Frame #',ylabel='Residue #',zlabel='RMSF$_\mathcal{R}$', title="Chain: '%s'"%chain)
			write_image(fn)
			
			
		# ----------------------------------
		if showhis:
			
			X = [] # copy.deepcopy(models)
			Y = [] # copy.deepcopy(residues)
			Z = [] # copy.deepcopy(Rs)
			
			for model in sorted_models:
				currentRs = []
				
				for current_model, R in zip(models,Rs):
					if model == current_model:
						currentRs.append(R)
				#
				if len(currentRs):
					step = 0.005
					bins = np.arange(rrange[0]-step/2,rrange[-1]+step,step)
					if rrange[0] < 0:
						step = 0.005*2
						bins = np.arange(rrange[0]+step/2,rrange[-1]+step,step)
					a,b = np.histogram(currentRs,bins=bins)
					for i in range(len(a)):
						X.append(model)
						Y.append(float(b[i]+b[i+1])/2.0)
						Z.append(float(a[i])/np.max(a))
			#
			for i in range(dofilter):
				Z = median_filter(Z)
			
			#
			fn = target_base+"_chain_"+chain+".rcode.his"
			filenames.append(fn)
			draw_xyz(X,Y,Z,cmap=plt.get_cmap("gray_r"), xlabel='Frame #',ylabel='$\mathcal{R}$',zlabel='$P(\mathcal{R})$', title="Chain: '%s'"%chain)
			write_image(fn)
		#
		batchedfilenames[chain] = copy.deepcopy(filenames)
	
	if 0: #do_vmd_etc:
		
		f = open("templates/template.tex","r")
		latexblock = f.read()
		f.close()
		
		USERMATERIAL  = r"\newcommand{\w}{0.15}"+"\n"
		USERMATERIAL += r"\newcommand{\h}{0.4}"+"\n"
		USERMATERIAL += r"\newcommand{\hc}{0.4}"+"\n"
		USERMATERIAL += r"\newcommand{\centerit}[1]{\noindent\textcolor{white}{.}\hfil#1\hfil\newline}"+"\n"
		
		
		for chain in sorted(batchedfilenames.keys()):
			#USERMATERIAL += r"\centerit{{\huge The ${\mathcal{R}}$eport for \texttt{\url{%s}.pdb}}}" % NAME +"\n"
			USERMATERIAL += r"{\large The ${\mathcal{R}}$eport for \texttt{\url{%s}.pdb, chain (ch):`%s'}" %(NAME,chain) +"\n"
			USERMATERIAL += r"\vfill"+"\n"
			filenames = batchedfilenames[chain]
			for i in range(len(filenames)/2):
				fn1 = filenames[i*2]
				fn2 = filenames[i*2+1]
				USERMATERIAL += r"\noindent"
				USERMATERIAL += r"\includegraphics[height=\h\textwidth]{%s}" % fn1[:-len('.eps')]+"\n"
				USERMATERIAL += r"\includegraphics[height=\hc\textwidth]{%s}" % fn2[:-len('.eps')]+"\n"
				USERMATERIAL += r"\newline"+"\n"
			USERMATERIAL += r"\vfill"+"\n\n~\n"
			if len(list(batchedfilenames.keys())) > 1:
				USERMATERIAL += r"\clearpage"+"\n"
		
		outputfilename = target_base+".tex"
		print("Writing to:",outputfilename)
		latexblock = latexblock.replace("USERMATERIAL",USERMATERIAL)
		f = open(outputfilename,"w")
		f.write(latexblock)
		f.close()
		
		os.system("pdflatex -shell-escape -output-directory="+os.path.dirname(outputfilename)+" "+outputfilename)
		print("OPENING:",outputfilename[:-len(".tex")]+".pdf")
		os.system("evince "+outputfilename[:-len(".tex")]+".pdf")
		os.system("rm "+outputfilename[:-len(".tex")]+".aux")
		os.system("rm "+outputfilename[:-len(".tex")]+".log")
		os.system("rm "+outputfilename[:-len(".tex")]+".out")
		os.system("rm "+outputfilename[:-len(".tex")]+"*converted-to.pdf")
	#
#
