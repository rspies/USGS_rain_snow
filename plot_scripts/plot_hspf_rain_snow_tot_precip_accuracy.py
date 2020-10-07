#Created on Wed Mar 26 09:45:17 2014
#@author: rspies
# Python 2.7
# This script reads in the user created ASOS rain/snow phase with air temperature time series and 
# the HSPF equation calculation of rain/snow time series (ANL temperature). 
# Creates a bar graph showing the breakdown of temperature and total liquid precip accumulation by phase.

import os
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams['pdf.fonttype'] = 42    # need this to export editable text (edit in adobe) http://jonathansoma.com/lede/data-studio/matplotlib/exporting-from-matplotlib-to-open-in-adobe-illustrator/
matplotlib.rcParams['ps.fonttype'] = 42     # need this to export editable text (edit in adobe)
plt.rcParams['svg.fonttype'] = 'none'
import numpy as np
from dateutil import parser
import datetime
plt.ioff()

## set working dir
os.chdir("..")
maindir = os.getcwd() + os.sep

#################### input parameters ########################
min_temp = start_temp = 31.0    #31.5 # 31.0
max_temp = 35.0                 #35.0 #35.6 #33.5
temp_interval = 0.5             #1.0
cat_num = (max_temp - min_temp)/temp_interval
asos_name = {'KORD':"Chicago O'Hare",'KLOT':'Romeoville/Lewis University','KDPA':'DuPage Airport','KPWK':'Palwaukee'}
tsnow = 32.5                    # 32.5 32.0 31.5
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

################## Parse raw ASOS precip file from NCDC ################################    
kdpa = {}; kord = {}; kpwk = {}; klot = {}
print 'Processing raw ASOS data file...'

fopen = open(maindir + 'data\\asos\\ncdc_precip\\raw_precip_4_sites.txt', 'r')

line1 = fopen.readline()
line2 = fopen.readline()
l2_mem = (line2.split()) ### header line with column labels
# find indicies of desired variables
find_name = l2_mem.index('Name')
find_prec = l2_mem.index('Amt')
find_pr = l2_mem.index('Pr')
find_date = l2_mem.index('Date')
find_hrmn = l2_mem.index('HrMn')
find_type = l2_mem.index('Type')
for lines in fopen:
    each_line = lines.split(',')
    if str(each_line[find_type]) == 'FM-15' and str(each_line[find_pr]) == '01': #ignore daily/monthly summaries and only use hourly data
        prec = float(each_line[find_prec])
        if prec > 0.0 and prec < 300: # only use precip values greater than 0.0 and less than 300mm (~12in)        
            date_check = parser.parse(each_line[find_date] + each_line[find_hrmn])
            if date_check.minute >= 40:
                date_check += datetime.timedelta(hours = 1)
                date_check = date_check.replace(minute=0)
                if str(each_line[find_name])[:4] == 'CHIC':
                    if str(date_check) not in kord:
                        kord[str(date_check)] = prec
                    else:
                        print '!!!! Data already exists at this time (' + str(each_line[find_name])[:4] + ': ' + str(date_check) 
                if str(each_line[find_name])[:4] == 'DUPA':
                    if str(date_check) not in kdpa:
                        kdpa[str(date_check)] = prec
                    else:
                        print '!!!! Data already exists at this time (' + str(each_line[find_name])[:4] + ': ' + str(date_check) 
                if str(each_line[find_name])[:4] == 'LEWI':
                    if str(date_check) not in klot:
                        klot[str(date_check)] = prec
                    else:
                        print '!!!! Data already exists at this time (' + str(each_line[find_name])[:4] + ': ' + str(date_check) 
                if str(each_line[find_name])[:4] == 'PALW':
                    if str(date_check) not in kpwk:
                        kpwk[str(date_check)] = prec
                    else:
                        print '!!!! Data already exists at this time (' + str(each_line[find_name])[:4] + ': ' + str(date_check) 
        
fopen.close()
################# create a list of days to use in the analysis ########################
ystart = 2006 # begin data grouping
yend = 2013 # end data grouping
start = datetime.datetime(ystart, 1, 1, 0, 0)
finish = datetime.datetime(yend, 9, 30, 23, 0)

################## Parse each ASOS precip type file ################################    
print 'Processing rain/snow temperature file...'
station_files = os.listdir(maindir + 'data\\asos\\processed_temp_prec')
summary_open = open(summary_out + os.sep + 'prec_depth_ratio_stats_' + str(tsnow)+'tsnow_'+str(start_temp) + '-'+str(max_temp)+'.txt','w')
summary_open.write('TSNOW: ' + str(tsnow)+ '\n')
summary_open.write('Analysis period:' + str(start)+' - '+str(finish) + '\n')
summary_open.write('Temperature bounds: ' +str(start_temp) + ' - '+str(max_temp-0.1) + 'F\n')
summary_open.write('Site' + '\t' + 'HSPF rain/snow ratio' + '\t' + 'ASOS rain/snow ratio' + '\n')
for station in station_files:   
    ##### Call the appropriate dict of total precip ####
    if station == 'kord.txt':
        asos_tot_prcp = kord
    if station == 'kdpa.txt':
        asos_tot_prcp = kdpa
    if station == 'kpwk.txt':
        asos_tot_prcp = kpwk
    if station == 'klot.txt':
        asos_tot_prcp = klot
        
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
            date_check = datetime.datetime(yr,mo,dy,hr) + datetime.timedelta(hours = 1) # add hour because ASOS sites usually report at 53 minutes in hour
            date = str(date_check)            
            if date_check > finish: #datetime.datetime(2012,9,30,23):
                break
            elif date_check >= start and date_check <= finish:
                asos_date_rsflag[date] = str(type_event) 
        fopen.close()
###################### Parse Matching Argonne Data ############################        
        print 'Processing data for ' + 'Argonne hourly temperature and rain snow flag...'
        fopen = open(maindir + 'data\\temperature\\argonne_tsnow_' + str(tsnow) + '.txt','r')
        hspf_lib_arg_rain = {}; hspf_lib_arg_snow = {} # dictionary of HSPF rain/snow 
        asos_lib_arg_rain = {}; asos_lib_arg_snow = {} # dictionary of ASOS rain/snow 
        bad = 0
        for line in fopen:
            if line[:2] == '20': #ignores header
                udata = line.split('\t')
                date_check = parser.parse(udata[0])
                rs_flag = udata[3]
                if udata[1] != 'na':
                    temp = float(udata[1])
                    if str(date_check) in asos_date_rsflag and str(date_check) in asos_tot_prcp:  
                        #print str(date_check)
                        for key in categories:
                            if temp >= categories[key][0] and temp <= categories[key][1]:
                                key_in = key
            ############# populate rain/snow hspf dict with ASOS precip Depths ##########
                                if rs_flag.rstrip() == 'Rain':
                                    if key in hspf_lib_arg_rain:
                                        hspf_lib_arg_rain[key].append(asos_tot_prcp[str(date_check)])
                                    else:
                                        hspf_lib_arg_rain[key] = [asos_tot_prcp[str(date_check)]]
                                if rs_flag.rstrip() == 'Snow':
                                    if key in hspf_lib_arg_snow:
                                        hspf_lib_arg_snow[key].append(asos_tot_prcp[str(date_check)])
                                    else:
                                        hspf_lib_arg_snow[key] = [asos_tot_prcp[str(date_check)]]
            ############# populate rain/snow asos dict with ASOS precip Depths ##########
                                if asos_date_rsflag[str(date_check)] == 'Rain':    
                                    if key in asos_lib_arg_rain:
                                        asos_lib_arg_rain[key].append(asos_tot_prcp[str(date_check)])
                                    else:
                                        asos_lib_arg_rain[key] = [asos_tot_prcp[str(date_check)]]
                                if asos_date_rsflag[str(date_check)] == 'Snow':    
                                    if key in asos_lib_arg_snow:
                                        asos_lib_arg_snow[key].append(asos_tot_prcp[str(date_check)])
                                    else:
                                        asos_lib_arg_snow[key] = [asos_tot_prcp[str(date_check)]]
        fopen.close()
############### Calculate difference in rain/snow cats #######################  
        snow_hspf = {}; snow_asos= {}; rain_hspf ={}; rain_asos = {}
        total_rain_hspf = 0; total_rain_asos = 0
        total_snow_hspf = 0; total_snow_asos = 0
        #### calculate the sum of each category and replace empty categories with 0 precip ####
        for each in categories:
            if each in hspf_lib_arg_rain:
                hspf_rain = sum(hspf_lib_arg_rain[each])
            else:
                hspf_rain = 0
            if each in hspf_lib_arg_snow:
                hspf_snow = sum(hspf_lib_arg_snow[each])
            else:
                hspf_snow = 0
            if each in asos_lib_arg_rain:
                asos_rain = sum(asos_lib_arg_rain[each])
            else:
                asos_rain = 0
            if each in asos_lib_arg_snow:
                asos_snow = sum(asos_lib_arg_snow[each])
            else:
                asos_snow = 0
            rain_hspf[each] = hspf_rain/25.4 # convert mm to inches
            snow_hspf[each] = hspf_snow/25.4 # convert mm to inches
            rain_asos[each] = asos_rain/25.4 # convert mm to inches
            snow_asos[each] = asos_snow/25.4 # convert mm to inches
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
        ax1.set_ylabel('Precipitation Depth (inches)')
        ax1.set_xlabel('ANL Temperature (' + r'$^o$F)')
        ax1.set_title(asos_name[station[:-4].upper()] + ' (' + station[:-4].upper() + '):' + ' TSNOW=' + str(tsnow) + r'$^o$F' + '\n' + str(start.month) + '/' + str(start.day) + '/' + str(start.year) + ' - ' + str(finish.month) + '/' + str(finish.day) + '/' + str(finish.year))
        tick_num = np.arange(len(categories))
        ax1.set_xticks(tick_num+width)
        
        ############## Ratio difference text box ##################
        textstr = 'HSPF Rain/Snow Depth Ratio: ' + str("%.2f" % (float(total_rain_hspf)/total_snow_hspf)) + '\n' +\
            'ASOS Rain/Snow Depth Ratio: ' + str("%.2f" % (float(total_rain_asos)/total_snow_asos))
            
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
            plt.savefig(maindir + '\\figures\\rain_snow\\final\\SNOTMP_obs_plots\\' + station[:-4] + '_HSPF_vs_ASOS_tot_precip_' + str(tsnow)+'_'+str(ystart)+'_'+str(yend)+'.pdf', dpi=150, bbox_inches='tight')
            plt.savefig(maindir + '\\figures\\rain_snow\\final\\SNOTMP_obs_plots\\' + station[:-4] + '_HSPF_vs_ASOS_tot_precip_' + str(tsnow)+'_'+str(ystart)+'_'+str(yend)+'.svg', dpi=150, bbox_inches='tight')

summary_open.close()
#close('all') #closes all figure windows
print 'Complete'