#Created on Wed Mar 26 09:45:17 2014
#@author: rspies
# Python 2.7
# This script reads in the user created rain/snow ASOS temperature file
# Creates a bar graph showing the breakdown of temperature and precip type

import os
import matplotlib.pyplot as plt
import numpy as np
from dateutil import parser
import datetime
import my_plot_module
import module_parse_txt
plt.ioff()

os.chdir("..")
maindir = os.getcwd() + os.sep
min_temp = start_temp = 23.0 #23.0 (use for % plot) #25.0 (use for bar plot)
max_temp = 36.0 #36.0 #35.6
temp_interval = 0.5 #0.5 #1.0
cat_num = (max_temp - min_temp)/temp_interval
temp_source = 'asos' # choices: ['asos', 'argonne'] -> selects the temp source for the bar chart
bar_plot = 'yes' # choices: ['yes', 'no'] -> this creates the bar chart
percent_plot = 'no' # choices: ['yes', 'no'] -> 'yes' automatically adds plots for argonne and asos temps
asos_name = {'KORD':'Chicago OHare','KLOT':'Romeoville/Lewis University','KDPA':'DuPage Airport','KPWK':'Palwaukee'}
if percent_plot == 'yes' and bar_plot == 'no':
    temp_source = ['asos', 'argonne']

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
yend = 2011 # end data grouping
start = datetime.datetime(ystart, 1, 1, 0, 0)
finish = datetime.datetime(yend, 9, 30, 23, 0)

if temp_source == 'argonne' or percent_plot == 'yes':
    print 'Processing data for ' + 'Argonne hourly temperature...'
    fopen = open(maindir + 'data\\temperature\\argonne.txt','r')
    temp_lib_arg = {}
    bad = 0
    for line in fopen:
        if line[:2] == '20': #ignores header
            udata = line.split('\t')
            date_check = parser.parse(udata[0])
            if date_check >= start and date_check <= finish:        
                temp = udata[1].rstrip()
                if temp == '':
                    temp = 'na'
                    bad += 1
                elif float(temp) < -30 or float(temp) > 120: # replace erroneous values with 'na'
                    temp = 'na'
                    bad += 1
                else:
                    temp = float(temp)
                key = str(date_check)
                temp_lib_arg[key]=temp                 
    fopen.close()
    print 'Bad data replaced with "na": ' + str(bad)
    

################## Parse each ground-gage file ################################    
print 'Processing rain/snow temperature file...'
station_files = os.listdir(maindir + 'data\\asos\\processed_temp_prec')
for station in station_files:
    if station [:1] == 'k':
        rain = {}
        snow = {}
        print 'Parsing ' + station + ' data...'
        fopen = open(maindir + 'data\\asos\\processed_temp_prec\\' + station, 'r')
        for lines in fopen:
            each_line = lines.split('\t')
            type_event = each_line[2].rstrip()
            temp = float(each_line[1])
            for key in categories:
                if temp >= categories[key][0] and temp <= categories[key][1]:
                    key_in = key

                    if type_event == 'Rain':
                        if key_in in rain:
                            rain[key_in].append(temp)
                        else:
                            rain[key_in] = [temp]
                    if type_event == 'Snow':
                        if key_in in snow:
                            snow[key_in].append(temp)
                        else:
                            snow[key_in] = [temp]                
        fopen.close()
#################### Pair Argonne Temperature with ASOS weather obs ############            
    if temp_source == 'argonne' or percent_plot == 'yes':
        print 'Processing rain/snow temperature file...'
        raina = {}
        snowa = {}
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
            temp = float(temp_lib_arg[date])
            for key in categories:
                if temp >= categories[key][0] and temp <= categories[key][1]:
                    key_in = key

                    if type_event == 'Rain':
                        if key_in in raina:
                            raina[key_in].append(temp)
                        else:
                            raina[key_in] = [temp]
                    if type_event == 'Snow':
                        if key_in in snowa:
                            snowa[key_in].append(temp)
                        else:
                            snowa[key_in] = [temp]                
        fopen.close()
        if temp_source == 'argonne':
            rain = {}; snow = {} #empty the contents of the dictionary from asos temp
            rain = raina; snow = snowa #replace with argonne temp match data
###################### Create figure at each site ############################            
    if bar_plot == 'yes':
        fig = plt.figure()
        ax1 = fig.add_subplot(111)
        width = 0.35       # the width of the bars
        for cats in snow:
            if len(cats) == 4:
                loc = int(cats[-1:])-1
            elif len(cats) == 5:
                loc = int(cats[-2:])-1
            if loc == len(categories)-1: # only add first occurence to the legend (duplicates otherwise)
                ax1.bar(loc, len(snow[cats]), width, color = 'blue', label = 'Snow')
            else:
                 ax1.bar(loc, len(snow[cats]), width, color = 'blue')
        for cats in rain:
            if len(cats) == 4:
                loc = int(cats[-1:])-1
            elif len(cats) == 5:
                loc = int(cats[-2:])-1
            if loc == len(categories)-1:
                ax1.bar(loc+width, len(rain[cats]), width, color = 'red', label = 'Rain')
            else:
                ax1.bar(loc+width, len(rain[cats]), width, color = 'red')
        ax1.set_xlim([0,len(categories)-width]) # remove white space at end of bar plot
        ax1.set_ylabel('Number of Hourly Observations')
        
        if temp_source == 'asos':
            ax1.set_title(station[:-4].upper() + ': ' + asos_name[station[:-4].upper()] + ' ASOS\n' + str(start.month) + '/' + str(start.day) + '/' + str(start.year) + ' - ' + str(finish.month) + '/' + str(finish.day) + '/' + str(finish.year))
            ax1.set_xlabel('Temperature (' + r'$^o$F)')
        elif temp_source == 'argonne':
            ax1.set_title(station[:-4].upper() + ': ' + asos_name[station[:-4].upper()] + ' ASOS Precipitation Phase Observations &\n' + 'ANL Temperature Data (' + str(start.month) + '/' + str(start.day) + '/' + str(start.year) + ' - ' + str(finish.month) + '/' + str(finish.day) + '/' + str(finish.year) + ')',fontsize=14)
            ax1.set_xlabel('ANL Temperature (' + r'$^o$F)')
        tick_num = np.arange(len(categories))
        ax1.set_xticks(tick_num+width)
        tick_labels = []
        for key in range(1,len(categories)+1):
            tick_labels.append(str(categories['cat'+str(key)][0]) + ' - ' + str(categories['cat'+str(key)][1]))
        if len(categories) > 10:
            ax1.set_xticklabels(tick_labels,rotation=90)
        else:
            ax1.set_xticklabels(tick_labels,rotation=45)
        ax1.legend(loc='upper right')
        if temp_source == 'asos':
            plt.savefig(maindir + '\\figures\\rain_snow\\final\\' + station[:-4] + str(temp_interval)+'.png', dpi=150, bbox_inches='tight')
        if temp_source == 'argonne':
            plt.savefig(maindir + '\\figures\\rain_snow\\final\\' + station[:-4] + 'argonne_temp.png', dpi=150, bbox_inches='tight')
    else:
        print 'User chose not to plot bar chart'
######################### add rain/snow percent plot ##########################    
    if percent_plot == 'yes':
        print 'Creating precip percentage plot...'
        fig = plt.figure()
        ax2 = fig.add_subplot(111)
        rpcnt = []; spcnt = []; x=[]
        module_parse_txt.pcnt_rain_snow(rain,snow,categories,rpcnt,spcnt,x)
        x_new, y_new, solve = my_plot_module.curve_fit(x,rpcnt)
        print 'rain % solve temp = ' + str(round(solve[-2],2))
        ax2.plot(x,rpcnt,color='red',marker = 'o', ls = '')
        ax2.plot(x_new,y_new,color='red', lw = 1.5,label='Rain - ASOS')
        x_new, y_new, solve = my_plot_module.curve_fit(x,spcnt)
        print 'snow % solve temp = ' + str(round(solve[-2],2))
        ax2.plot(x,spcnt,color='blue',marker = 'o',ls = '')
        ax2.plot(x_new,y_new,color='blue', lw = 1.5, label='Snow - ASOS')        
        rpcnt = []; spcnt = []; x=[]        
        module_parse_txt.pcnt_rain_snow(raina,snowa,categories,rpcnt,spcnt,x)
        x_new, y_new, solve = my_plot_module.curve_fit(x,rpcnt)
        print 'raina % solve temp = ' + str(round(solve[-2],2))
        ax2.plot(x,rpcnt,color='red',marker = 'o', ls = '',mec = 'red',mfc='none')
        ax2.plot(x_new,y_new,color='red', lw = 1.5, ls = '--',label='Rain - Argonne')
        x_new, y_new, solve = my_plot_module.curve_fit(x,spcnt)
        print 'snowa % solve temp = ' + str(round(solve[-2],2))        
        ax2.plot(x,spcnt,color='blue',marker = 'o', ls = '',mec = 'blue',mfc='none')
        ax2.plot(x_new,y_new,color='blue', lw = 1.5, ls = '--', label='Snow - Argonne')         
        
        ax2.set_ylabel('Percent of ASOS Precipitation Observions')
        ax2.set_xlabel('Temperature (' + r'$^o$F)')
        ax2.set_ylim(0,100)
        # set limits below to ignore edge effects of poly trend line
        ax2.set_xlim(start_temp + 6,max_temp - 1)
        ax2.grid(True)
        ax2.set_title(asos_name[station[:-4].upper()] + ' (' + station[:-4].upper() + ')'+ '\n' + str(start.month) + '/' + str(start.day) + '/' + str(start.year) + ' - ' + str(finish.month) + '/' + str(finish.day) + '/' + str(finish.year))
        ax2.legend(loc='center left')   
        plt.savefig(maindir + '\\figures\\rain_snow\\final\\' + station[:-4] + '_r-s_percent.png', dpi=150, bbox_inches='tight')

#close('all') #closes all figure windows
print 'Complete'
