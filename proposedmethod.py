# -*- coding: UTF-8 -*-

import sqlite3
import sys
import math
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib as mpl
import matplotlib.cm as cm
import numpy as np
import random
from util import *
from displayBSSID import *
from operator import *
from collections import deque

_PENALTY_POINT = 500.0
_K = 3
_queueLength = 20

estimation_profile = deque()
geomagnetism_profile = deque()
a = []


def geomagnetism_fingerprinting(correct_pos, poslist, israw):
    now_geo = find_list_by_pos(correct_pos, curr_GeoList, bind_dir=True)

    local_now_geo = convert_resultant_vector(now_geo[0], returnraw=israw)

    estimation = []

    for pos in poslist:

        if israw:
            fp_geo = find_list_by_pos(pos, prev_GeoList_forraw, bind_dir=False)
        else:
            fp_geo = find_list_by_pos(pos, prev_GeoList, bind_dir=False)

        # print fp_geo
        for dir_idx in range(len(fp_geo)):
            local_fp_geo = convert_resultant_vector(fp_geo[dir_idx], returnraw=israw)

            point = (local_now_geo[0] - local_fp_geo[0]) ** 2 + (local_now_geo[1] - local_fp_geo[1]) ** 2 + \
                    (local_now_geo[2] - local_fp_geo[2]) ** 2
            estimation.append(Position(pos.Floor, pos.X, pos.Y, fp_geo[dir_idx][3], point))

    estimation = sorted(estimation, key=lambda x: x.point)

    if len(estimation) < _K:
        return -1.0, -1.0

    # print estimation[:3]

    result_x = 0
    result_y = 0
    for i in range(0, _K):
        # print "(" + str(estimation
        # [i].X) + ":" + str(estimation[i].Y) + ":" + str(estimation[i].point) + ")"
        result_x += estimation[i].X
        result_y += estimation[i].Y

    return float(result_x) / float(_K), float(result_y) / float(_K)


def wifi_fingerprinting(correct_pos, curr_WiFiList, prev_WiFiList, bssid_area, israw):
    now_wifi = find_list_by_pos(correct_pos, curr_WiFiList, bind_dir=True)

    fp_wifi_poslist = find_list_by_BSSID(sample=now_wifi, FP=prev_WiFiList)

    estimation = []
    for pos in fp_wifi_poslist:
        fp_wifi = find_list_by_pos(Position(pos.Floor, pos.X, pos.Y, pos.Direction, None), prev_WiFiList, bind_dir=True)
        point = 0.0
        for sample in now_wifi:
            # print point
            for fingerprint_pos_wifi in fp_wifi:
                if sample[4] == fingerprint_pos_wifi[4]:
                    point += (float(sample[7]) - float(fingerprint_pos_wifi[7])) ** 2
                    break
            else:
                point += _PENALTY_POINT

        if point == 0.0:
            point = 0.0001

        estimation.append(Position(pos.Floor, pos.X, pos.Y, pos.Direction, point))

    estimation = sorted(estimation, key=lambda x: x.point)

    result_x = 0.0
    result_y = 0.0
    sum_weight = 0.0

    if len(estimation) < _K:
        return -1.0, -1.0

    for i in range(0, _K):
        result_x += (1.0 / float(estimation[i].point)) * estimation[i].X
        result_y += (1.0 / float(estimation[i].point)) * estimation[i].Y
        sum_weight += (1.0 / float(estimation[i].point))

    maxrssi = -float("inf")

    for row in now_wifi:
        if maxrssi < row[7]:
            maxrssi = row[7]

    result = float(result_x) / float(sum_weight), float(result_y) / float(sum_weight)
    error = math.sqrt((correct_pos.X - result[0]) ** 2 + (correct_pos.Y - result[1]) ** 2)

    data_bssid.append([len(now_wifi), error])
    data_rssi.append([maxrssi, error])

    return float(result_x) / sum_weight, float(result_y) / sum_weight

u'''
wifi-aided mmでは常にprocessed geoを使用する.
'''

def wifi_aided_magnetic_matching(correct_pos, curr_WiFiList, prev_WiFiList, bssid_area, israw):
    wifians = wifi_fingerprinting(correct_pos, curr_WiFiList=curr_WiFiList, prev_WiFiList=prev_WiFiList,
                                  bssid_area=bssid_area, israw=israw)

    if wifians[0] == -1.0:
        return -1.0, -1.0

    now_geo = find_list_by_pos(correct_pos, curr_GeoList, bind_dir=True)
    local_now_geo = convert_resultant_vector(now_geo[0], returnraw=False)

    if len(estimation_profile) >= _queueLength:
        estimation_profile.popleft()

    if len(geomagnetism_profile) >= _queueLength:
        geomagnetism_profile.popleft()

    estimation_profile.append(local_now_geo)

    estposlist = create_list_in_circle(Position(None, wifians[0], wifians[1], None, None), prev_PosList)

    minPoint = float('inf')
    best_match = [1.0, 1.0, 1.0]
    result = -1.0, -1.0

    arr1 = list(estimation_profile)

    # print wifians
    # print estposlist

    for prev_pos in estposlist:
        arr2 = list(geomagnetism_profile)

        p_geo = find_list_by_pos(prev_pos, prev_GeoList, bind_dir=True)

        local_prev_geo = convert_resultant_vector(p_geo[0], returnraw=False)

        arr2.append(local_prev_geo)
        nowPoint = dtw(arr1, arr2)

        if minPoint > nowPoint:
            minPoint = nowPoint
            result = prev_pos.X, prev_pos.Y
            best_match = local_prev_geo

    estimation_profile.append(best_match)

    return result


def proposed_positioning(correct_pos, curr_WiFiList, prev_WiFiList, bssid_area, israw):
    now_wifi = find_list_by_pos(correct_pos, curr_WiFiList, bind_dir=True)

    geo_result = proposed_geomagnetic_fingerprinting(correct_pos, curr_WiFiList=curr_WiFiList,
                                                     prev_WiFiList=prev_WiFiList, bssid_area=bssid_area, israw=israw)
    wifi_result = wifi_fingerprinting(correct_pos, curr_WiFiList=curr_WiFiList, prev_WiFiList=prev_WiFiList,
                                      bssid_area=bssid_area, israw=israw)

    wifi_dependance = calc_wifi_dependence(bssid_prm=bssid_prm, rssi_prm=rssi_prm, now_wifi=now_wifi)

    result = wifi_dependance * wifi_result[0] + (1.0 - wifi_dependance) * geo_result[0], wifi_dependance * wifi_result[
        1] + (1.0 - wifi_dependance) * geo_result[1]

    return result


def proposed_geomagnetic_fingerprinting(correct_pos, curr_WiFiList, prev_WiFiList, bssid_area, israw):
    now_wifi = find_list_by_pos(correct_pos, curr_WiFiList, bind_dir=True)

    # geo_estimation = []

    sum_reciprocal = 0.0

    result_x = 0.0
    result_y = 0.0

    if not len(now_wifi) == 0:
        for row in now_wifi:
            simple_bssid_pos = bssid_area.get_detail(row[4])

            if simple_bssid_pos is None:
                continue

            result = geomagnetism_fingerprinting(correct_pos, simple_bssid_pos[1], israw=israw)

            reciprocal = 1.0 / (float(simple_bssid_pos[3]))

            result_x += reciprocal * float(result[0])
            result_y += reciprocal * float(result[1])

            # geo_estimation.append((result, simple_bssid_pos[3]))

            sum_reciprocal += reciprocal
    else:
        result = geomagnetism_fingerprinting(correct_pos, bssid_area.get_posist("None"), israw=israw)

        result_x += (1.0 / float(bssid_area.get_detail("None")[3])) * float(result[0])
        result_y += (1.0 / float(bssid_area.get_detail("None")[3])) * float(result[1])

        # geo_estimation.append((geomagnetism_fingerprinting(correct_pos, bssid_area.get_posist("None")), bssid_area.get_detail("None")[3]))
        sum_reciprocal += 1.0 / float(bssid_area.get_detail("None")[3])

    if sum_reciprocal == 0.0:
        result = geomagnetism_fingerprinting(correct_pos, bssid_area.get_posist("None"), israw=israw)

        result_x += (1.0 / float(bssid_area.get_detail("None")[3])) * float(result[0])
        result_y += (1.0 / float(bssid_area.get_detail("None")[3])) * float(result[1])

        # geo_estimation.append((geomagnetism_fingerprinting(correct_pos, bssid_area.get_posist("None")), bssid_area.get_detail("None")[3]))
        sum_reciprocal += 1.0 / float(bssid_area.get_detail("None")[3])

    # print result_x, result_y

    # print geo_estimation
    return result_x / sum_reciprocal, result_y / sum_reciprocal


'''
def delete_random_bssid_percent(percent):
    bssidnum = bssid_area.size()
    randomlist = random.sample(xrange(0, bssidnum), int(bssidnum*(float(percent)/100.0)))
    delete_bssid_list = []

    for idx in randomlist:
        delete_bssid_list.append(bssid_area.get_BSSID(idx))

    curr_idx_list = []
    for dl_bssid in delete_bssid_list:
        for curr_wifi_idx in range(len(curr_WiFiList)):
            if curr_WiFiList[curr_wifi_idx][4] == dl_bssid:
                curr_idx_list.append(curr_wifi_idx)

    curr_idx_inverse_list = sorted(curr_idx_list, reverse=True)

    for i in curr_idx_inverse_list:
        del curr_WiFiList[i]

    prev_idx_list = []
    for dl_bssid in delete_bssid_list:
        for prev_wifi_idx in range(len(prev_WiFiList)):
            if prev_WiFiList[prev_wifi_idx][4] == dl_bssid:
                prev_idx_list.append(prev_wifi_idx)

    prev_idx_inverse_list = sorted(prev_idx_list, reverse=True)
    for i in prev_idx_inverse_list:
        del prev_WiFiList[i]
'''


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print '#error '
        exit()

    prev_PosList = []
    curr_PosList = []

    prev_db_name = sys.argv[1]
    curr_db_name = sys.argv[2]

    prev_con = sqlite3.connect(prev_db_name)
    prev_PosList = createposlist(sqlite3.connect(prev_db_name).cursor(),
                                 u"SELECT DISTINCT Floor, xcoordinate, ycoordinate, direction FROM PROCESSED_GEO;")
    p_WiFiList = prev_con.execute(u"SELECT * FROM PROCESSED_WiFi").fetchall()
    prev_GeoList = prev_con.execute(u"SELECT * FROM posture_estimation").fetchall()

    prev_GeoList_forraw = insert_other_direction(prev_GeoList)

    curr_con = sqlite3.connect(curr_db_name)
    curr_PosList = createposlist(sqlite3.connect(curr_db_name).cursor(),
                                 u"SELECT DISTINCT Floor, xcoordinate, ycoordinate, direction FROM PROCESSED_GEO;")
    c_WiFiList = curr_con.execute(u"SELECT * FROM PROCESSED_WiFi").fetchall()
    curr_GeoList = curr_con.execute(u"SELECT * FROM posture_estimation").fetchall()

    '''
    estimation_error = []
    error_cnt = 0
    for Cpos in curr_PosList:
        wifi_estimation = wifi_fingerprinting(Cpos)
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
    '''

    data_bssid = []
    data_rssi = []

    bssid_prm = [41.5, 1.01, -1.0]
    rssi_prm = [235.5, 100.1, -5.0]

    list_0cut = []

    # delete_random_bssid_list(list_0cut)

    geo = 'raw'
    percent = 0

    # delete_random_bssid_percent(percent)

    fig_name = geo + 'bssid' + str(percent) + 'cut' + '.png'

    # for Cpos in curr_PosList:
    #     wifi_fingerprinting(Cpos)

    # bssid_prm = fit_bssid(data_bssid)
    # rssi_prm = fit_rssi(data_rssi)

    # print bssid_area.size()

    print bssid_prm
    print rssi_prm

    bssidnum = 96
    delete_list_11 = []
    delete_list_5 = []
    delete_list_4 = []
    for i in [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]:
        delete_list_11.append(random.sample(xrange(0, bssidnum), int(bssidnum * (float(i) / 100.0))))

    for i in [0, 25, 50, 75, 100]:
        delete_list_5.append(random.sample(xrange(0, bssidnum), int(bssidnum * (float(i) / 100.0))))

    for i in [0, 25, 50, 75]:
        delete_list_4.append(random.sample(xrange(0, bssidnum), int(bssidnum * (float(i) / 100.0))))

    # evaluation([proposed_geomagnetic_fingerprinting], [u"proposed geomagnetic fingerprinting"], curr_PosList)
    # display_bssid_distribution(prev_WiFiList=p_WiFiList, prev_PosList=prev_PosList)

    '''
    evaluation_mmr(method=[wifi_fingerprinting, wifi_aided_magnetic_matching, proposed_geomagnetic_fingerprinting,
                           proposed_positioning],
                   method_name=[u"Wi-Fi FP", u"WaMM", u"地磁気FP", u"提案手法"],
                   delete_list=delete_list_11,
                   curr_PosList=curr_PosList,
                   prev_PosList=prev_PosList,
                   fig_name="error_rate_all",
                   c_WiFiList=c_WiFiList,
                   p_WiFiList=p_WiFiList
                   )

    '''
    '''
    evaluation_geo(method=proposed_geomagnetic_fingerprinting,
                   method_name=u"proposed geomagnetism FP",
                   delete_list=delete_list_5,
                   curr_PosList=curr_PosList,
                   prev_PosList=prev_PosList,
                   fig_name="geo_comparison",
                   c_WiFiList=c_WiFiList,
                   p_WiFiList=p_WiFiList,
                   )
    '''
    evaluation(method=[wifi_fingerprinting,  wifi_aided_magnetic_matching, proposed_geomagnetic_fingerprinting,
                       proposed_positioning],
               method_name=[u"Wi-Fi FP", u"WaMM", u"地磁気FP", u"提案手法"],
               delete_list=delete_list_4,
               curr_PosList=curr_PosList,
               prev_PosList=prev_PosList,
               fig_name=fig_name,
               c_WiFiList=c_WiFiList,
               p_WiFiList=p_WiFiList
               )
    '''
    evaluation_convergence(method=[wifi_fingerprinting,  wifi_aided_magnetic_matching,
                                   proposed_geomagnetic_fingerprinting,proposed_positioning],
                           method_name=[u"Wi-Fi FP", u"WaMM", u"地磁気FP", u"提案手法"],
                           delete_list=delete_list_4,
                           curr_PosList=curr_PosList,
                           prev_PosList=prev_PosList,
                           fig_name=u"convergence evaluation",
                           c_WiFiList=c_WiFiList,
                           p_WiFiList=p_WiFiList
               )
    '''
    # evaluation([wifi_fingerprinting, proposed_geomagnetic_fingerprinting, wifi_aided_magnetic_matching, proposed_positioning], ["wifi fingerprinting","proposed geomagnetic fingerprinting" ,"wifi aided magnetic matching", "proposed positioning method"], curr_PosList)
    # evaluation([wifi_fingerprinting, proposed_geomagnetic_fingerprinting, proposed_positioning], ["wifi fingerprinting","proposed geomagnetic fingerprinting" , "proposed positioning method"], curr_PosList)
