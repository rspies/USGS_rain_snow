#Created on Thu Mar 21 16:12:17 2014
#@author: rspies
# Python 2.7
# This script reads in Arogonne temperature data and creates a txt file with days
# that meet freeze criteria -> for future comparison
# temperature data from sep11.wdm RRS

import os
import datetime
from dateutil import parser
import numpy

maindir = os.getcwd()[:-28]
tsnow = 31.5

################# create a list of days to use in the analysis ########################
ystart = 2002 # begin data grouping
yend = 2012 # end data grouping
start = datetime.datetime(ystart, 1, 1, 0, 0)
ticker = start
finish = datetime.datetime(yend, 9, 30, 23, 0)
date_list = []
while ticker <= finish:
    date_list.append(str(ticker)[:-9])
    ticker += datetime.timedelta(days=1)

################## Parse Argonne temperature file ################################    
print 'Processing data for ' + 'Argonne hourly temperature...'
fopen = open(maindir + 'data\\temperature\\argonne_temp_tdew.txt','r')
fnew = open(maindir + '\\data\\temperature\\argonne_tsnow_' + str(tsnow) + '.txt','w')
fnew.write('TSNOW parameter: ' + str(tsnow) + '\n')    
fnew.write('Date\t' + 'Temperature\t' + 'TSNOW\t' + 'Flag\n')
temp_lib = {}
badd = 0; badt = 0; err_dew = 0
for line in fopen:
    if line[:2] == '20': #ignores header
        udata = line.split('\t')
        date_check = parser.parse(udata[0])
        #print str(date_check)[:10]
        if date_check >= start and date_check <= finish:        
            temp = udata[1].rstrip()
            dewt = udata[2].rstrip()
            if temp == '':
                temp = 'na'
                badt += 1
            elif float(temp) < -30 or float(temp) > 120: # replace erroneous values with 'na'
                temp = 'na'
                badt += 1
            else:
                temp = float(temp)
            if dewt == '':
                dewt = 'na'
                badd += 1
            elif float(dewt) < -50 or float(dewt) > 120: # replace erroneous values with 'na'
                dewt = 'na'
                badd += 1
            else:
                dewt = float(dewt)
            if temp != 'na' and dewt != 'na':
                if dewt > temp:
                    print '### Dew > Temp ### -> ' + str(date_check)
                    print 'Dew: ' + str(dewt) + ' Temp: ' +str(temp)
                    err_dew += 1
                if temp <= (tsnow + 1):
                    tadj = (temp - dewt)*(0.12 + 0.008*temp)
                else:
                    tadj = 0.0
                #### tsnow can only increase (maximum of 1 degree F) ####
                if tadj > 1.0:
                    tadj = 1.0
                if tadj < 0.0:
                    tadj = 0.0
                snotmp = round((tsnow + tadj),1)
                ### rain / snow flag ###
                if temp >= snotmp:
                    rs_flag = 'Rain'
                else:
                    rs_flag = 'Snow'
                fnew.write(str(date_check) + '\t' + str(temp) + '\t' + str(snotmp) + '\t' + rs_flag + '\n')
            else:
                print 'Ignored: ' +str(date_check)
                fnew.write(str(date_check) + '\t' + 'na\t' + 'na\t' + 'na\n')
fopen.close()
print 'Bad data replaced with "na": ' + ' temp: ' + str(badt) + ' dew: ' + str(badd)
print 'Hours with Dew > Temp: ' + str(err_dew)
fnew.close()
print 'Complete!'