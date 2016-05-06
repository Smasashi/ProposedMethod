# coding=utf-8

import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.cm as cm
import numpy as np
import math
from util import *

mpl.use('Agg')


def display_bssid_distribution(prev_WiFiList, prev_PosList):

    poslist = copy.copy(prev_PosList)

    for pos in poslist:
        for row in prev_WiFiList:
            if pos.X == row[1] and pos.Y == row[2]:
                if pos.point is None:
                    pos.point = 1
                else:
                    pos.point += 1

    x = []
    y = []
    t = []
    s = []

    for pos in poslist:
        x.append(pos.X)
        y.append(pos.Y)
        t.append(pos.point)

    plt.figure(figsize=(14, 5.7))
    cmap = plt.cm.get_cmap('Oranges')
    sc = plt.scatter(x, y, c=t, cmap=cmap, s=30, marker='s')

    plt.colorbar(sc)
    plt.xlim(-10, 105)
    plt.xticks(())
    plt.ylim(-10, 50)
    plt.yticks(())

    plt.savefig(u"APnum_map", transparent=True)


def evaluation_mmr(method, method_name, delete_list, curr_PosList, prev_PosList, fig_name, c_WiFiList, p_WiFiList,
                   israw=True):
    x = []
    for i in range(len(delete_list)):
        x.append(i * 10)

    y = []
    for i in range(len(method)):
        y.append([])

    print delete_list

    delete_list = [[], [17, 90, 62, 33, 96, 2, 11, 77, 84, 89], [99, 27, 25, 6, 2, 66, 37, 50, 81, 91, 20, 96, 95, 7, 9, 65, 53, 43, 92, 78], [1, 16, 20, 90, 84, 40, 49, 10, 9, 3, 14, 6, 12, 59, 75, 30, 7, 29, 37, 97, 57, 5, 65, 27, 33, 88, 83, 34, 60, 51], [95, 80, 68, 96, 17, 64, 14, 67, 38, 41, 50, 85, 2, 15, 1, 11, 0, 21, 98, 84, 27, 8, 99, 91, 10, 83, 47, 12, 46, 39, 4, 97, 78, 55, 29, 82, 74, 28, 19, 57], [43, 49, 12, 24, 81, 64, 42, 52, 84, 6, 55, 98, 21, 27, 51, 34, 37, 90, 66, 48, 36, 87, 30, 93, 0, 16, 39, 7, 31, 8, 65, 88, 41, 20, 40, 13, 28, 74, 50, 96, 75, 94, 77, 44, 97, 25, 73, 3, 56, 72], [85, 38, 78, 12, 52, 82, 92, 22, 89, 45, 72, 29, 3, 66, 97, 83, 36, 91, 57, 15, 62, 94, 28, 68, 20, 59, 7, 86, 21, 55, 35, 54, 0, 77, 30, 88, 48, 2, 61, 81, 63, 84, 58, 6, 27, 11, 51, 16, 46, 99, 93, 80, 74, 98, 32, 40, 70, 9, 10, 4], [72, 20, 51, 86, 90, 95, 11, 46, 47, 93, 57, 22, 30, 26, 21, 7, 36, 84, 82, 89, 80, 56, 99, 1, 39, 17, 50, 45, 33, 54, 70, 27, 15, 98, 75, 8, 59, 37, 79, 38, 4, 71, 91, 3, 92, 25, 66, 12, 96, 83, 48, 6, 34, 49, 24, 65, 97, 41, 64, 58, 44, 60, 53, 67, 94, 40, 5, 29, 76, 18], [74, 2, 26, 48, 75, 97, 57, 0, 37, 4, 3, 25, 30, 92, 77, 21, 70, 28, 12, 81, 99, 50, 71, 58, 13, 44, 34, 89, 33, 35, 24, 66, 55, 62, 84, 52, 83, 42, 47, 91, 38, 18, 76, 60, 78, 72, 5, 53, 64, 7, 67, 6, 8, 82, 29, 19, 80, 56, 39, 88, 36, 65, 49, 86, 31, 16, 20, 10, 11, 51, 85, 68, 17, 96, 23, 22, 73, 43, 87, 79], [69, 76, 2, 4, 94, 33, 47, 18, 46, 80, 25, 62, 64, 6, 52, 38, 10, 75, 13, 45, 24, 83, 41, 82, 53, 35, 8, 96, 54, 95, 17, 92, 68, 49, 16, 37, 60, 3, 40, 43, 7, 22, 66, 56, 70, 67, 90, 11, 50, 98, 19, 12, 88, 71, 15, 81, 27, 93, 63, 32, 84, 59, 31, 36, 1, 42, 34, 51, 29, 44, 55, 14, 39, 28, 58, 26, 78, 99, 89, 79, 77, 9, 23, 21, 48, 5, 61, 72, 65, 91], [40, 73, 93, 16, 9, 33, 81, 57, 56, 4, 92, 97, 83, 99, 7, 94, 25, 19, 72, 6, 41, 27, 62, 89, 38, 44, 67, 50, 64, 22, 98, 31, 12, 78, 75, 61, 20, 37, 52, 69, 8, 79, 88, 66, 28, 65, 63, 77, 36, 42, 29, 45, 80, 39, 48, 47, 32, 84, 58, 15, 30, 82, 35, 49, 86, 55, 14, 96, 85, 91, 13, 10, 74, 70, 46, 11, 90, 34, 71, 5, 26, 21, 2, 43, 76, 95, 59, 24, 18, 54, 60, 0, 23, 17, 51, 68, 87, 3, 1, 53]]

    bssid_area = configure_area_by_wifi(prev_WiFiList=p_WiFiList, prev_PosList=prev_PosList)

    for i in xrange(0, len(delete_list)):

        prev_WiFiList = delete_bssid_list(delete_list[i], WiFiList=p_WiFiList, bssid_area=bssid_area)
        curr_WiFiList = delete_bssid_list(delete_list[i], WiFiList=c_WiFiList, bssid_area=bssid_area)

        for j in xrange(0, len(method)):
            estimation_error = []
            error_cnt = 0
            for Cpos in curr_PosList:
                estimation = method[j](correct_pos=Cpos, curr_WiFiList=curr_WiFiList, prev_WiFiList=prev_WiFiList,
                                       bssid_area=bssid_area, israw=israw)
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

            #mpl.rcParams['font.family'] = 'Osaka'

            y[j].append(error_rate*100)

        '''
        plt.scatter(data_x, data_y)
        plt.xlabel(u"サンプルで得られたbssidの個数[個]")
        plt.ylabel(u"測位誤差[m]")
        '''

    charcter = ['-s', '-^', '-o', '-D']
    m_size = [12, 12, 16, 11]
    l_width = [2, 2, 2, 5]

    plt.figure(figsize=(10, 5.3))

    for i in range(len(y)):
        plt.plot(x, y[i], charcter[i], linewidth=l_width[i], markersize=m_size[i])

    m_name = [method_name[0], method_name[1], method_name[2],  method_name[3]]

    plt.legend(m_name, loc='upper left', handlelength=2.5)
    plt.minorticks_on()
    plt.xlabel(u"BSSID削減率[%]", fontsize=18)
    plt.ylabel(u"測位失敗率[%]", fontsize=18)
    plt.grid()

    plt.savefig(fig_name, transparent=True)


def evaluation_geo(method, method_name, delete_list, curr_PosList, prev_PosList, fig_name, c_WiFiList, p_WiFiList):
    tf = [True, False]
    raworprocessed = [u"無加工地磁気データを利用", u"加工地磁気データを利用"]

    delete_list = [[], [96, 54, 27, 31, 23, 19, 22, 83, 3, 86, 51, 68, 12, 92, 46, 29, 70, 52, 44, 73, 81, 98, 90, 18, 59], [1, 66, 61, 31, 99, 25, 27, 86, 23, 15, 28, 40, 14, 24, 30, 68, 62, 50, 48, 45, 0, 7, 2, 16, 9, 59, 57, 21, 34, 78, 74, 53, 33, 41, 81, 71, 19, 92, 94, 69, 10, 44, 55, 18, 32, 79, 73, 77, 47, 36], [42, 62, 53, 49, 64, 15, 5, 84, 79, 39, 45, 40, 81, 35, 67, 28, 74, 46, 90, 68, 2, 9, 44, 29, 13, 55, 99, 0, 82, 32, 75, 87, 31, 97, 34, 24, 25, 54, 18, 4, 98, 1, 19, 94, 85, 8, 3, 6, 33, 12, 60, 27, 58, 38, 78, 16, 63, 51, 73, 71, 86, 50, 95, 61, 10, 93, 20, 7, 48, 80, 88, 22, 37, 14, 92], [64, 12, 18, 80, 13, 29, 57, 19, 42, 90, 40, 44, 84, 22, 53, 25, 5, 83, 87, 41, 33, 30, 51, 20, 70, 8, 14, 59, 24, 76, 82, 60, 3, 27, 71, 99, 73, 47, 88, 91, 92, 79, 98, 63, 56, 78, 69, 16, 93, 7, 0, 38, 34, 61, 26, 74, 9, 36, 86, 1, 28, 32, 52, 2, 66, 58, 54, 77, 62, 72, 10, 65, 15, 48, 67, 43, 6, 37, 95, 85, 89, 17, 45, 4, 94, 81, 75, 97, 46, 49, 35, 96, 39, 11, 50, 21, 55, 23, 31, 68]]

    f, ax = plt.subplots(len(delete_list), len(tf), sharey=True, sharex=True)
    # f.set_label(u"[m]")

    print delete_list

    bssid_area = configure_area_by_wifi(prev_WiFiList=p_WiFiList, prev_PosList=prev_PosList)

    for i in xrange(0, len(delete_list)):

        prev_WiFiList = delete_bssid_list(delete_list[i], WiFiList=p_WiFiList, bssid_area=bssid_area)
        curr_WiFiList = delete_bssid_list(delete_list[i], WiFiList=c_WiFiList, bssid_area=bssid_area)

        for j in xrange(0, len(tf)):
            estimation_error = []
            error_cnt = 0
            for Cpos in curr_PosList:
                estimation = method(correct_pos=Cpos, curr_WiFiList=curr_WiFiList, prev_WiFiList=prev_WiFiList,
                                    bssid_area=bssid_area, israw=tf[j])
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
            # ax[i, j].set_xlabel(raworprocessed[j], fontsize=17)

            if j == 0:
                # ax[i,j].set_yticklabels(["bssid " + str(25*i) + "% cut"])
                ax[i, j].set_ylabel(u"BSSID" + str(i * 25) + u"%削減時の\n測位誤差[m]", fontsize=17)

            if i == 0:
                ax[i, j].set_title(raworprocessed[j], fontsize=17)

            # textstr = 'miss match rate : %.2f' % error_rate
            # props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
            # ax[i, j].text(0.05, 1.00, textstr, fontsize=17, transform=ax[i, j].transAxes, verticalalignment='top', bbox=props)
            ax[i, j].tick_params(labelbottom='off')

    plt.minorticks_on()

    f.set_size_inches(13, 16)

    plt.savefig(fig_name, transparent=True)


def evaluation(method, method_name, delete_list, curr_PosList, prev_PosList, fig_name, c_WiFiList, p_WiFiList,
               israw=True):
    f, ax = plt.subplots(len(delete_list), len(method), sharey=True, sharex=True)
    # f.set_label(u"[m]")

    meany = [[], [], [], []]
    mediany = [[], [], [], []]

    delete_list = [[], [69, 32, 56, 39, 71, 24, 43, 12, 87, 54, 46, 4, 61, 89, 2, 53, 45, 74, 60, 95, 7, 28, 99, 42, 19], [29, 99, 64, 66, 39, 85, 2, 32, 86, 10, 62, 70, 49, 18, 50, 80, 40, 97, 57, 19, 3, 63, 0, 8, 20, 89, 15, 54, 68, 35, 56, 30, 44, 81, 6, 17, 48, 24, 5, 42, 46, 55, 52, 94, 88, 33, 1, 74, 34, 58], [44, 21, 20, 79, 48, 3, 93, 57, 89, 49, 6, 88, 40, 73, 87, 46, 78, 84, 4, 75, 58, 43, 27, 5, 33, 96, 80, 97, 69, 0, 11, 35, 86, 83, 76, 37, 28, 8, 17, 2, 94, 38, 41, 24, 36, 54, 42, 55, 92, 65, 95, 59, 7, 12, 31, 29, 56, 99, 25, 26, 16, 13, 14, 66, 60, 98, 45, 47, 51, 9, 32, 18, 72, 30, 61]]

    print delete_list

    bssid_area = configure_area_by_wifi(prev_WiFiList=p_WiFiList, prev_PosList=prev_PosList)

    for i in xrange(0, len(delete_list)):

        prev_WiFiList = delete_bssid_list(delete_list[i], WiFiList=p_WiFiList, bssid_area=bssid_area)
        curr_WiFiList = delete_bssid_list(delete_list[i], WiFiList=c_WiFiList, bssid_area=bssid_area)

        for j in xrange(0, len(method)):
            estimation_error = []
            error_cnt = 0
            for Cpos in curr_PosList:
                estimation = method[j](correct_pos=Cpos, curr_WiFiList=curr_WiFiList, prev_WiFiList=prev_WiFiList,
                                       bssid_area=bssid_area, israw=israw)
                # print str(Cpos.X) + ',' + str(Cpos.Y) + ',' + str(estimation[0]) + ',' + str(estimation[1])

                if round(estimation[0] - (-1.0)) == 0:
                    error_cnt += 1
                    # print "wrong "
                    continue

                estimation_error.append(math.sqrt((Cpos.X - estimation[0]) ** 2 + (Cpos.Y - estimation[1]) ** 2))

            error_rate = float(error_cnt) / float(len(curr_PosList))

            print "-" + method_name[j] + " delete rate:" + str(i*25)
            print "error rate, " + str(error_rate)
            print "mean error, " + str(np.mean(estimation_error))
            meany[j].append(np.mean(estimation_error))
            mediany[j].append(np.median(estimation_error))
            print "median error, " + str(np.median(estimation_error))

            # mpl.rcParams['font.family'] = 'Osaka'

            data = [estimation_error]

            ax[i, j].boxplot(data, sym='', whis=[5, 95], showmeans=True)
            ax[i, j].grid()

            if j == 0:
                # ax[i,j].set_yticklabels(["bssid " + str(25*i) + "% cut"])
                ax[i, j].set_ylabel(u"BSSID" + str(i * 25) + u"%削減時の\n測位誤差[m]", fontsize=18)

            if i == 0:
                ax[i, j].set_title(method_name[j], fontsize=18)

            textstr = u'測位失敗率:%.2f' % error_rate
            props = dict(boxstyle='round', facecolor='wheat', alpha=0.2)
            ax[i, j].text(0.05, 0.95, textstr, fontsize=18, transform=ax[i, j].transAxes, verticalalignment='top',
                          bbox=props)
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

    plt.savefig("Other_route_box", transparent=True)
    #print meany
    #print mediany


def evaluation_convergence(method, method_name, delete_list, curr_PosList, prev_PosList, fig_name, c_WiFiList, p_WiFiList,
               israw=True):
    f, ax = plt.subplots(len(delete_list), 1, sharey=True, sharex=False)
    # f.set_label(u"[m]")

    convergence_data = []

    meany = [[], [], [], []]
    mediany = [[], [], [], []]
    ind = np.arange(len(delete_list))
    method_name = [u"Wi-Fi FP", u"WaMM", u"地磁気FP", u"提案手法"]

    delete_list = [[], [69, 32, 56, 39, 71, 24, 43, 12, 87, 54, 46, 4, 61, 89, 2, 53, 45, 74, 60, 95, 7, 28, 99, 42, 19], [29, 99, 64, 66, 39, 85, 2, 32, 86, 10, 62, 70, 49, 18, 50, 80, 40, 97, 57, 19, 3, 63, 0, 8, 20, 89, 15, 54, 68, 35, 56, 30, 44, 81, 6, 17, 48, 24, 5, 42, 46, 55, 52, 94, 88, 33, 1, 74, 34, 58], [44, 21, 20, 79, 48, 3, 93, 57, 89, 49, 6, 88, 40, 73, 87, 46, 78, 84, 4, 75, 58, 43, 27, 5, 33, 96, 80, 97, 69, 0, 11, 35, 86, 83, 76, 37, 28, 8, 17, 2, 94, 38, 41, 24, 36, 54, 42, 55, 92, 65, 95, 59, 7, 12, 31, 29, 56, 99, 25, 26, 16, 13, 14, 66, 60, 98, 45, 47, 51, 9, 32, 18, 72, 30, 61]]

    print delete_list

    bssid_area = configure_area_by_wifi(prev_WiFiList=p_WiFiList, prev_PosList=prev_PosList)

    for i in xrange(0, len(delete_list)):

        data = []

        prev_WiFiList = delete_bssid_list(delete_list[i], WiFiList=p_WiFiList, bssid_area=bssid_area)
        curr_WiFiList = delete_bssid_list(delete_list[i], WiFiList=c_WiFiList, bssid_area=bssid_area)

        for j in xrange(0, len(method)):
            estimation_error = []
            convergence = 0
            error_cnt = 0
            for Cpos in curr_PosList:
                estimation = method[j](correct_pos=Cpos, curr_WiFiList=curr_WiFiList, prev_WiFiList=prev_WiFiList,
                                       bssid_area=bssid_area, israw=israw)
                # print str(Cpos.X) + ',' + str(Cpos.Y) + ',' + str(estimation[0]) + ',' + str(estimation[1])

                if round(estimation[0] - (-1.0)) == 0:
                    error_cnt += 1
                    # print "wrong "
                    continue

                error = math.sqrt((Cpos.X - estimation[0]) ** 2 + (Cpos.Y - estimation[1]) ** 2)
                estimation_error.append(error)

                if error <= 3.0:
                    convergence += 1

            error_rate = float(error_cnt) / float(len(curr_PosList))
            probability = convergence / float(len(curr_PosList))

            print u"-" + method_name[j] + u" delete rate:" + str(i*25)
            print u"error rate, " + str(error_rate)
            print u"mean error, " + str(np.mean(estimation_error))
            meany[j].append(np.mean(estimation_error))
            mediany[j].append(np.median(estimation_error))
            print u"median error, " + str(np.median(estimation_error))
            print u"convergence probability, " + str(probability)

            data.append(probability * 100)

        convergence_data.append(data)

        mpl.rcParams['font.family'] = 'Osaka'
        ax[i].barh(ind, data, align='center', alpha=0.4, tick_label=method_name)

        ax[i].set_yticks(ind, method_name)
        ax[i].set_xlabel(u"bssid "+ str(i * 25) + u"% cut   3m convergence probablity[%]")

        ax[i].grid()

    f.set_size_inches(8, 16)

    plt.minorticks_on()

    print convergence_data

    plt.savefig(u"other_route", transparent=True)
    #print meany
    #print mediany