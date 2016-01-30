# -*- coding: UTF-8 -*-

import matplotlib.pyplot as plt
import pandas as pd
import matplotlib as mpl
import matplotlib.cm as cm
import numpy as np
import math

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


def evaluation(method, method_name, curr_PosList):
    print len(method)

    f, ax = plt.subplots(1,len(method), sharey=True)
    f.set_label(U"測位誤差[m]")
    plt.ylabel(u"測位誤差[m]")

    for i in xrange(0, len(method)):
        estimation_error = []
        error_cnt = 0
        for Cpos in curr_PosList:
            wifi_estimation = method[i](Cpos)
            print (Cpos.X, Cpos.Y), wifi_estimation

            if round(wifi_estimation[0] - (-1.0)) == 0:
                error_cnt += 1
                print "wrong "
                continue

            estimation_error.append(math.sqrt((Cpos.X - wifi_estimation[0]) ** 2 + (Cpos.Y - wifi_estimation[1]) ** 2))

        error_rate = float(error_cnt) / float(len(curr_PosList))

        print "error rate:" + str(error_rate)
        print "mean error:" + str(np.mean(estimation_error))
        print "median error:" + str(np.median(estimation_error))

        mpl.rcParams['font.family'] = 'Osaka'

        data = [estimation_error]

        ax[i].boxplot(data, sym='', whis=[5,95], showmeans=True)
        ax[i].grid()
        ax[i].set_xlabel(method_name[i])

        textstr = 'miss match rate : %.2f' % error_rate
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        ax[i].text(0.05, 0.95, textstr, fontsize=14, transform=ax[i].transAxes, verticalalignment='top', bbox=props)



        # print data

        '''
        plt.scatter(data_x, data_y)
        plt.xlabel(u"サンプルで得られたbssidの個数[個]")
        plt.ylabel(u"測位誤差[m]")
        '''
    # plt.ylim([0, 30])
    plt.minorticks_on()

    plt.show()
