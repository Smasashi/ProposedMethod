# -*- coding: UTF-8 -*-

import matplotlib.pyplot as plt
import pandas as pd
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.cm as cm
import numpy as np
import math
from util import *

def display_bssid_distribution(bssid, fp_con):
    fingerprint_bssid_bind = ""

    for i in bssid:
        fingerprint_bssid_bind += "\"" + i + "\","

    pos_includes_bssid = fp_con.execute(
        u"SELECT DISTINCT Floor, xcoordinate, ycoordinate, Direction, avg_rssi, count FROM PROCESSED_WiFi WHERE BSSID IN(" + fingerprint_bssid_bind[
                                                                                                                             :-1] + u");")

    # pos_includes_bssid = prev_con.execute(u"SELECT DISTINCT Floor, xcoordinate, ycoordinate, Direction, avg_rssi FROM PROCESSED_WiFi;")

    # pos_includes_bssid = prev_con.execute(u"select bssid, count(bssid) as cnt, max(avg_rssi) as rssi from processed_wifi group by bssid order by cnt;")

    '''
    x_range = [0,101]
    y_range = [0, 51]

    x = []
    y = []
    t = [0] * (x_range[1] * y_range[1])

    for row in pos_includes_bssid:
        x.append(row[1])
        y.append(row[2])
        t.append(float(abs(row[4]))/100.0)

    df_sample = pd.DataFrame([x, y, t], index=list('xyt')).T

    fig, ax = plt.subplots()

    out = sns.regplot(x='x', y='y', data=df_sample, scatter=True, ax=ax, scatter_kws={'c': df_sample['t'], 'cmap': 'jet', 's': df_sample['t']})

    # print df_sample
    outpathc = out.get_children()[3]

    #plt.colorbar(mappable=outpathc)
    # sns.plt.axis("off")
    plt.show()

    '''

    x = []
    y = []
    t = []
    s = []

    for row in pos_includes_bssid:
        x.append(row[1])
        y.append(row[2])
        t.append((row[4]))
        s.append(row[5] * 10)

    cmap = plt.cm.get_cmap('Oranges')
    sc = plt.scatter(x, y, c=t, cmap=cmap, alpha=10, s=s)

    plt.colorbar(sc)
    plt.xlim(-10, 100)
    plt.xticks(())
    plt.ylim(-10, 50)
    plt.yticks(())

    plt.show()


def evaluation_mmr(method, method_name, delete_list ,curr_PosList, prev_PosList, fig_name, c_WiFiList, p_WiFiList):

    x = []
    for i in range(len(delete_list)):
        x.append(i*10)

    y = []
    for i in range(len(method)):
        y.append([])

    print delete_list

    bssid_area = configure_area_by_wifi(prev_WiFiList=p_WiFiList, prev_PosList=prev_PosList)

    for i in xrange(0, len(delete_list)):

        prev_WiFiList = delete_bssid_list(delete_list[i], WiFiList=p_WiFiList, bssid_area=bssid_area)
        curr_WiFiList = delete_bssid_list(delete_list[i], WiFiList=c_WiFiList, bssid_area=bssid_area)

        for j in xrange(0, len(method)):
            estimation_error = []
            error_cnt = 0
            for Cpos in curr_PosList:
                estimation = method[j](correct_pos=Cpos, curr_WiFiList=curr_WiFiList, prev_WiFiList=prev_WiFiList, bssid_area=bssid_area)
                # print str(Cpos.X) + ',' + str(Cpos.Y) + ',' + str(estimation[0]) + ',' + str(estimation[1])

                if round(estimation[0] - (-1.0)) == 0:
                    error_cnt += 1
                    # print "wrong "
                    continue

                # estimation_error.append(math.sqrt((Cpos.X - estimation[0]) ** 2 + (Cpos.Y - estimation[1]) ** 2))

            error_rate = float(error_cnt) / float(len(curr_PosList))

            print "error rate, " + str(error_rate)
            # print "mean error, " + str(np.mean(estimation_error))
            # print "median error, " + str(np.median(estimation_error))

            mpl.rcParams['font.family'] = 'Osaka'

            y[j].append(error_rate)

        '''
        plt.scatter(data_x, data_y)
        plt.xlabel(u"サンプルで得られたbssidの個数[個]")
        plt.ylabel(u"測位誤差[m]")
        '''

    for i in range(len(y) - 1):
        plt.plot(x, y[i], '-s')

    m_name = [method_name[0], method_name[1], method_name[2] + u"\n & " + method_name[3]]

    plt.legend(m_name, loc='lower right')
    plt.minorticks_on()
    plt.xlabel(u"BSSID削減率[%]")
    plt.ylabel(u"miss match rate[%]")

    plt.savefig(fig_name, transparent=True)



def evaluation(method, method_name, delete_list ,curr_PosList, prev_PosList, fig_name, c_WiFiList, p_WiFiList):

    f, ax = plt.subplots(len(delete_list), len(method), sharey=True, sharex=True)
    # f.set_label(u"[m]")

    print delete_list

    bssid_area = configure_area_by_wifi(prev_WiFiList=p_WiFiList, prev_PosList=prev_PosList)

    for i in xrange(0, len(delete_list)):

        prev_WiFiList = delete_bssid_list(delete_list[i], WiFiList=p_WiFiList, bssid_area=bssid_area)
        curr_WiFiList = delete_bssid_list(delete_list[i], WiFiList=c_WiFiList, bssid_area=bssid_area)

        for j in xrange(0, len(method)):
            estimation_error = []
            error_cnt = 0
            for Cpos in curr_PosList:
                estimation = method[j](correct_pos=Cpos, curr_WiFiList=curr_WiFiList, prev_WiFiList=prev_WiFiList, bssid_area=bssid_area)
                # print str(Cpos.X) + ',' + str(Cpos.Y) + ',' + str(estimation[0]) + ',' + str(estimation[1])

                if round(estimation[0] - (-1.0)) == 0:
                    error_cnt += 1
                    # print "wrong "
                    continue

                estimation_error.append(math.sqrt((Cpos.X - estimation[0]) ** 2 + (Cpos.Y - estimation[1]) ** 2))

            error_rate = float(error_cnt) / float(len(curr_PosList))

            print "error rate, " + str(error_rate)
            print "mean error, " + str(np.mean(estimation_error))
            print "median error, " + str(np.median(estimation_error))

            mpl.rcParams['font.family'] = 'Osaka'

            data = [estimation_error]

            ax[i, j].boxplot(data, sym='', whis=[5, 95], showmeans=True)
            ax[i, j].grid()
            ax[i, j].set_xlabel(method_name[j], fontsize=17)

            if j == 0:
                #ax[i,j].set_yticklabels(["bssid " + str(25*i) + "% cut"])
                ax[i, j].set_ylabel(u"bssid" + str(i*25) + u"% cut\npositioning error[m]", fontsize=17)

            textstr = 'miss match rate : %.2f' % error_rate
            props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
            ax[i, j].text(0.05, 1.00, textstr, fontsize=17, transform=ax[i, j].transAxes, verticalalignment='top', bbox=props)
            ax[i, j].tick_params(labelbottom='off')



            # print data

        '''
        plt.scatter(data_x, data_y)
        plt.xlabel(u"サンプルで得られたbssidの個数[個]")
        plt.ylabel(u"測位誤差[m]")
        '''

    plt.ylim([0, 45])

    plt.minorticks_on()

    f.set_size_inches(13, 16)

    plt.savefig(fig_name, transparent=True)
