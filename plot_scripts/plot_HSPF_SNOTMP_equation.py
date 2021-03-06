#Created on Mon May 12 13:30:52 2014
#@author: rspies
# Python 2.7
# This script creates a plot of the SNOTMP variable in HSPF.
# SNOTMP is a function of the TSNOW parameter, input temperature, and input
# dewpoint data.

import os
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams['pdf.fonttype'] = 42    # need this to export editable text (edit in adobe) http://jonathansoma.com/lede/data-studio/matplotlib/exporting-from-matplotlib-to-open-in-adobe-illustrator/
matplotlib.rcParams['ps.fonttype'] = 42     # need this to export editable text (edit in adobe)
plt.rcParams['svg.fonttype'] = 'none'
from matplotlib import cm
from matplotlib import ticker
import numpy as np
plt.ioff()
os.chdir("..")
maindir = os.getcwd() + os.sep


### User input data ###
TSNOW = 32.0
temp_max = 36
temp_min = 28
dd_min = 0
dd_max = 5
dd_int = dd_max/((float(temp_max) - temp_min)*10)
#dd,temp = np.mgrid[dd_min:dd_max:0.2,temp_min:temp_max:0.1] #
ddy,ddx = np.mgrid[dd_min:dd_max:dd_int,dd_min:dd_max:dd_int]
tempy,tempx = np.mgrid[temp_min:temp_max:0.1,temp_min:temp_max:0.1]
# temperature matrix -> changes in y direction
temp = np.flipud(tempy) # need to flip matrix upside down to arrange from low to high (bottom to top)
dd = ddx # dew point depression matrix -> changes in x direction

snotmp = TSNOW + (dd * (0.12 + 0.008*temp)) # SNOTMP Equation from HSPF manual
final_snotmp = snotmp.clip(max=(TSNOW+1)) # set limit to SNOTMP value (TSNOW + 1)

fig = plt.figure()
ax1 = fig.add_subplot(111)
cmap=cm.coolwarm
image = ax1.imshow(final_snotmp, cmap=cmap,extent=[dd_min,dd_max,temp_min,temp_max],interpolation='none')
cbar = fig.colorbar(image,shrink=0.6,format='%.1f')
tick_locator = ticker.MaxNLocator(nbins=11,min_n_ticks=11)
cbar.locator = tick_locator
cbar.update_ticks()

#### color bar properties ###
text = 'SNOTMP Temperature (' + r'$^o$F)'
cbar.ax.set_ylabel(text, rotation=270,labelpad=20)

#### axis and title properties ###
ax1.set_xlabel('Dewpoint Depression (' + r'$^o$F)' + '\n' + '(Air Temperature - Dewpoint Temperature)')
ax1.set_ylabel('Air Temperature (' + r'$^o$F)')
ax1.set_title('SNOTMP Distribution\n (TSNOW = ' + str(TSNOW) + r'$^o$F)')
plt.savefig(maindir + '\\figures\\rain_snow\\final\\' + 'HSPF_SNOTMP_distribution_' + str(TSNOW) + '_final.pdf', dpi=150, bbox_inches='tight')
plt.savefig(maindir + '\\figures\\rain_snow\\final\\' + 'HSPF_SNOTMP_distribution_' + str(TSNOW) + '_final.svg', dpi=150, bbox_inches='tight')
print 'Completed!!!'
