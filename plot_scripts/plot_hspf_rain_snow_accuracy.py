#Created on Wed Mar 26 09:45:17 2014
#@author: rspies
# Python 2.7
# This script reads in the user created ASOS rain/snow phase with air temperature time series and 
# the HSPF equation calculation of rain/snow time series (ANL temperature). 
# Creates a bar graph showing the breakdown of temperature and number of precip phase observations

import os
import matplotlib.pyplot as plt
import numpy as np
from dateutil import parser
import datetime
plt.ioff()

## set working dir
os.chdir("..")
maindir = os.getcwd() + os.sep

#################### input parameters ########################
min_temp = start_temp = 31.0 #31.5 #31.0
max_temp = 35.0 #35.6 #33.5 #35.0
temp_interval = 0.5 #1.0 #
cat_num = (max_temp - min_temp)/temp_interval
asos_name = {'KORD':'Chicago OHare','KLOT':'Romeoville/Lewis University','KDPA':'DuPage Airport','KPWK':'Palwaukee'}
tsnow = 32.5 # 32.5 32.0 31.5
plot_out = 'yes' # 'yes' or 'no' for saving the plot (can run for just stats output)
summary_out = maindir + '\\figures\\rain_snow\\final\\SNOTMP_obs_plots\\' 
################### Create temperature range categories ########################
categories = {}
cat_cnt = 1
while min_temp < max_temp:
    categories['cat'+str(cat_cnt)] = [min_temp,(min_temp + temp_interval)-0.1]
    cat_cnt +=1
    min_temp += temp_interval
print len(categories)
print categories

################## Parse Argonne temperature file ################################    
################# create a list of days to use in the analysis ########################
ystart = 2006 # begin data grouping
yend = 2013 # end data grouping
start = datetime.datetime(ystart, 1, 1, 0, 0)
finish = datetime.datetime(yend, 9, 30, 23, 0)

################## Parse each ASOS file ################################    
print 'Processing rain/snow temperature file...'
station_files = os.listdir(maindir + 'data\\asos\\processed_temp_prec')
summary_open = open(summary_out + os.sep + 'prec_count_ratio_stats_' + str(tsnow)+'tsnow_'+str(start_temp) + '-'+str(max_temp)+'.txt','w')
summary_open.write('TSNOW: ' + str(tsnow)+ '\n')
summary_open.write('Analysis period:' + str(start)+' - '+str(finish) + '\n')
summary_open.write('Temperature bounds: ' +str(start_temp) + ' - '+str(max_temp-0.1) + 'F\n')
summary_open.write('Site' + '\t' + 'HSPF rain/snow ratio' + '\t' + 'ASOS rain/snow ratio' + '\n')
for station in station_files:
    if station [:1] == 'k':
        asos_date_rsflag = {}
        print 'Parsing ' + station + ' data...'
        fopen = open(maindir + 'data\\asos\\processed_temp_prec\\' + station, 'r')
        for lines in fopen:
            each_line = lines.split('\t')
            type_event = each_line[2].rstrip()
            yr = int(each_line[0][:4])
            mo = int(each_line[0][4:6])
            dy = int(each_line[0][6:8])
            hr = int(each_line[0][9:11])
            mn = int(each_line[0][11:13])
            date_check = datetime.datetime(yr,mo,dy,hr) + datetime.timedelta(hours = 1) # add hour because ASOS sites usually report at ~xx:53 minutes in hour
            date = str(date_check)            
            if date_check > finish: #datetime.datetime(2012,9,30,23):
                break
            elif date_check >= start and date_check <= finish:
                asos_date_rsflag[date] = str(type_event) 
        fopen.close()
###################### Parse Matching Argonne Data ############################        
        print 'Processing data for ' + 'Argonne hourly temperature and rain snow flag...'
        fopen = open(maindir + 'data\\temperature\\argonne_tsnow_' + str(tsnow) + '.txt','r')
        hspf_lib_arg = {}
        asos_lib_arg = {} # dictionary of ASOS rain/snow with 
        bad = 0
        for line in fopen:
            if line[:2] == '20': #ignores header
                udata = line.split('\t')
                date_check = parser.parse(udata[0])
                rs_flag = udata[3]
                if udata[1] != 'na':
                    temp = float(udata[1])
                    if str(date_check) in asos_date_rsflag:        
                        for key in categories:
                            if temp >= categories[key][0] and temp <= categories[key][1]:
                                key_in = key
                                if key in hspf_lib_arg:
                                    hspf_lib_arg[key].append(rs_flag.rstrip())
                                else:
                                    hspf_lib_arg[key] = [rs_flag.rstrip()]
                                if key in asos_lib_arg:
                                    asos_lib_arg[key].append(asos_date_rsflag[str(date_check)])
                                else:
                                    asos_lib_arg[key] = [asos_date_rsflag[str(date_check)]]
                            
        fopen.close()
############### Calculate difference in rain/snow cats #######################  
        snow_hspf = {}; snow_asos= {}; rain_hspf ={}; rain_asos = {}
        total_rain_hspf = 0; total_rain_asos = 0
        total_snow_hspf = 0; total_snow_asos = 0
        for each in categories:
            hspf_rain = hspf_lib_arg[each].count('Rain')
            hspf_snow = hspf_lib_arg[each].count('Snow')
            asos_rain = asos_lib_arg[each].count('Rain')
            asos_snow = asos_lib_arg[each].count('Snow')
            rain_hspf[each] = hspf_rain
            snow_hspf[each] = hspf_snow
            rain_asos[each] = asos_rain
            snow_asos[each] = asos_snow
            total_rain_hspf += hspf_rain
            total_rain_asos += asos_rain
            total_snow_hspf += hspf_snow
            total_snow_asos += asos_snow
        
###################### Create figure at each site ############################            
        fig = plt.figure(figsize=(8, 5))
        ax1 = fig.add_subplot(111)
        width = 0.2       # the width of the bars
        for cats in categories:
            if len(cats) == 4:
                loc = int(cats[-1:])-1
            elif len(cats) == 5:
                loc = int(cats[-2:])-1
            if loc == len(categories)-1: # only add first occurence to the legend (duplicates otherwise)
                ax1.bar(loc-width, snow_hspf[cats], width, color = 'blue', label = 'HSPF Snow', alpha = 0.35, hatch='//')
                ax1.bar(loc, snow_asos[cats], width, color = 'blue', label = 'ASOS Snow')
            else:
                ax1.bar(loc-width, snow_hspf[cats], width, color = 'blue', alpha=0.35, hatch='//')
                ax1.bar(loc, snow_asos[cats], width, color = 'blue')
        for cats in categories:
            if len(cats) == 4:
                loc = int(cats[-1:])-1
            elif len(cats) == 5:
                loc = int(cats[-2:])-1
            if loc == len(categories)-1:
                ax1.bar(loc+(width), rain_hspf[cats], width, color = 'red', label = 'HSPF Rain', alpha = 0.35, hatch='//')
                ax1.bar(loc+(width*2), rain_asos[cats], width, color = 'red', label = 'ASOS Rain')
            else:
                ax1.bar(loc+(width), rain_hspf[cats], width, color = 'red', alpha=0.35, hatch='//')
                ax1.bar(loc+(width*2), rain_asos[cats], width, color = 'red')
                
        ax1.set_xlim([width*-1,len(categories)-width*2]) # remove white space at end of bar plot
        ax1.set_ylabel('Number of ASOS and HSPF Rain-Snow Reports')
        ax1.set_xlabel('ANL Temperature (' + r'$^o$F)')
        ax1.set_title(asos_name[station[:-4].upper()] + ' (' + station[:-4].upper() + '):' + ' TSNOW=' + str(tsnow) + r'$^o$F' + '\n' + str(start.month) + '/' + str(start.day) + '/' + str(start.year) + ' - ' + str(finish.month) + '/' + str(finish.day) + '/' + str(finish.year))
        tick_num = np.arange(len(categories))
        ax1.set_xticks(tick_num+width)
        
        ############## Percent difference text box ##################
        #textstr = 'HSPF Rain Observations: ' + str(total_rain_hspf) + '\n' +\
        #    'ASOS Rain Observations: ' + str(total_rain_asos) + '\n' +\
        #    'HSPF Snow Observations: ' + str(total_snow_hspf) + '\n' +\
        #    'ASOS Snow Observations: ' + str(total_snow_asos)
        textstr = 'HSPF Rain/Snow Report Ratio: ' + str("%.2f" % (float(total_rain_hspf)/total_snow_hspf)) + '\n' +\
            'ASOS Rain/Snow Report Ratio: ' + str("%.2f" % (float(total_rain_asos)/total_snow_asos))
            
        summary_open.write(station[:-4] + '\t' + str("%.2f" % (float(total_rain_hspf)/total_snow_hspf)) + '\t' + str("%.2f" % (float(total_rain_asos)/total_snow_asos)) + '\n')
        # these are matplotlib.patch.Patch properties
        props = dict(boxstyle='round', facecolor = '0.8', alpha=0.5)
        
        # place a text box in upper left in axes coords
        ax1.text(0.20, 0.96, textstr, transform=ax1.transAxes, fontsize=11,
                 verticalalignment='top', bbox=props)
        
        tick_labels = []
        for key in range(1,len(categories)+1):
            tick_labels.append(str(categories['cat'+str(key)][0]) + ' - ' + str(categories['cat'+str(key)][1]))
        if len(categories) > 10:
            ax1.set_xticklabels(tick_labels,rotation=90)
        else:
            ax1.set_xticklabels(tick_labels,rotation=45)
        ax1.legend(loc='upper right',prop={'size':12})
        if plot_out == 'yes':
            plt.savefig(maindir + '\\figures\\rain_snow\\final\\SNOTMP_obs_plots\\' + station[:-4] + '_HSPF_vs_ASOS_' + str(tsnow)+'_'+str(ystart)+'_'+str(yend)+'.png', dpi=150, bbox_inches='tight')

summary_open.close()
#close('all') #closes all figure windows
print 'Complete'