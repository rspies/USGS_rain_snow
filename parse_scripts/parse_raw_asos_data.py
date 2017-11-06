#Created on Wed Mar 26 09:45:17 2014
#@author: rspies
# Python 2.7
# This script reads in raw ASOS station data from the NCDC website
# http://www.ncdc.noaa.gov/data-access/land-based-station-data/land-based-datasets/automated-surface-observing-system-asos
# Output a station text file with temperature and precip type obs

import os
import numpy

os.chdir("..")
maindir = os.getcwd() + os.sep

# code numbers for rain and snow reports from info file
rain_reports = ['23','43','44','57','58','60','61','61','63','80','81','82','83','84']
snow_reports = ['24','70','71','72','73','74','75','75','77','45','46','47','48','85','86','87']
################## Parse each ground-gage file ################################    
all_wx = {}
print 'Processing raw ASOS data file...'
station_files = os.listdir(maindir + 'data\\asos\\ncdc_raw\\')
for station in station_files:
    count_fzra = 0
    if station [:1] == 'k': # look through each station file (e.g. klot)
        print 'Parsing ' + station + ' data...'
        fopen = open(maindir + 'data\\asos\\ncdc_raw\\' + station, 'r')
        fnew = open(maindir + 'data\\asos\\processed_temp_prec\\final\\' + station, 'w')
        line1 = fopen.readline()                                # read first line of file (to be skipped)
        line2 = fopen.readline()                                # read second line of file with column header info
        l2_mem = (line2.split())                                # split column header titles and save the list
        find_temp = l2_mem.index('Temp')                        # obtain the index of the 'Temp' column header
        find_wx = [i for i, x in enumerate(l2_mem) if x == 'Wx']# obtain the index of all weather code columns
        find_rm = l2_mem.index('Remarks')                       # obtain the index of the 'Remarks' column
        find_date = l2_mem.index('Date')                        # obtain the index of the Date column
        find_hrmn = l2_mem.index('HrMn')                        # obtain the index of the Hour/Minute column
        find_type = l2_mem.index('Type')                        # obtain the index of the report type column
        for lines in fopen:
            if lines[:1] == '7': #ignore blank lines
                each_line = lines.split(',')
                #if (float(each_line[find_temp]) * (9/5)) + 32 >= 31.5 and (float(each_line[find_temp]) * (9/5)) + 32 <= 31.9:
                #        print each_line[find_temp]
                if str(each_line[find_type])[:2] == 'FM' and 'METAR' in each_line[find_rm]: #ignore daily/monthly summaries, check that metar data available to compare to
                    for each_wx in find_wx:
                        if each_line[each_wx] != '  ' and (float(each_line[find_temp]) * (9/5)) + 32 >= 31.5 and (float(each_line[find_temp]) * (9/5)) + 32 <= 31.9:
                            if each_line[each_wx] in all_wx:    # create a dictionary of precip obs by temperature (between 31.5 and 31.9F)
                                all_wx[each_line[each_wx]].append(float(each_line[find_temp]))
                            else:
                                all_wx[each_line[each_wx]] = [float(each_line[find_temp])]
                        if each_line[each_wx] in rain_reports and 'RA' in each_line[find_rm]: # first check for any rain codes and confirm rain in remarks
                            fnew.write(each_line[find_date] + ' ' + each_line[find_hrmn] + '\t')
                            tempf = (float(each_line[find_temp]) * (9/5)) + 32
                            fnew.write(str("%.2f" % tempf) + '\t' + 'Rain\n')
                            break
                        if each_line[each_wx] in snow_reports and 'SN' in each_line[find_rm]: # if no rain check for any snow codes and confirm snow in remarks
                            fnew.write(each_line[find_date] + ' ' + each_line[find_hrmn] + '\t')
                            tempf = (float(each_line[find_temp]) * (9/5)) + 32
                            fnew.write(str("%.2f" % tempf) + '\t' + 'Snow\n')
                            break
                        if 'FZRA' in each_line[find_rm]:                     # lastly if no rain or snow check for freeze rain (only used for counting purposes)
                            count_fzra += 1
        fnew.close()
        fopen.close()
    print station + ': Freezing Rain Obs ' + str(count_fzra)
for key in all_wx:
    print str(key) + ' -> ' + str(len(all_wx[key])) + '  mean temp (C) ' + str(numpy.mean(all_wx[key]))
print 'Complete'