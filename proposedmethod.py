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


def geomagnetism_fingerprinting(correct_pos, poslist):
    now_geo = find_list_by_pos(correct_pos, curr_GeoList, bind_dir=True)

    local_now_geo = convert_resultant_vector(now_geo[0])

    estimation = []

    for pos in poslist:
        fp_geo = find_list_by_pos(pos, prev_GeoList, bind_dir=False)

        # print fp_geo
        for dir_idx in range(len(fp_geo)):
            local_fp_geo = convert_resultant_vector(fp_geo[dir_idx])

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


def wifi_fingerprinting(correct_pos, curr_WiFiList, prev_WiFiList, bssid_area):
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


def wifi_aided_magnetic_matching(correct_pos, curr_WiFiList, prev_WiFiList, bssid_area):
    wifians = wifi_fingerprinting(correct_pos, curr_WiFiList=curr_WiFiList, prev_WiFiList=prev_WiFiList,
                                  bssid_area=bssid_area)

    if wifians[0] == -1.0:
        return -1.0, -1.0

    now_geo = find_list_by_pos(correct_pos, curr_GeoList, bind_dir=True)
    local_now_geo = convert_resultant_vector(now_geo[0])

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

        local_prev_geo = convert_resultant_vector(p_geo[0])

        arr2.append(local_prev_geo)
        nowPoint = dtw(arr1, arr2)

        if minPoint > nowPoint:
            minPoint = nowPoint
            result = prev_pos.X, prev_pos.Y
            best_match = local_prev_geo

    estimation_profile.append(best_match)

    return result


def proposed_positioning(correct_pos, curr_WiFiList, prev_WiFiList, bssid_area):
    now_wifi = find_list_by_pos(correct_pos, curr_WiFiList, bind_dir=True)

    geo_result = proposed_geomagnetic_fingerprinting(correct_pos, curr_WiFiList=curr_WiFiList,
                                                     prev_WiFiList=prev_WiFiList, bssid_area=bssid_area)
    wifi_result = wifi_fingerprinting(correct_pos, curr_WiFiList=curr_WiFiList, prev_WiFiList=prev_WiFiList,
                                      bssid_area=bssid_area)

    wifi_dependance = calc_wifi_dependence(bssid_prm=bssid_prm, rssi_prm=rssi_prm, now_wifi=now_wifi)

    result = wifi_dependance * wifi_result[0] + (1.0 - wifi_dependance) * geo_result[0], wifi_dependance * wifi_result[
        1] + (1.0 - wifi_dependance) * geo_result[1]

    return result


def proposed_geomagnetic_fingerprinting(correct_pos, curr_WiFiList, prev_WiFiList, bssid_area):
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

            result = geomagnetism_fingerprinting(correct_pos, simple_bssid_pos[1])

            reciprocal = 1.0 / (float(simple_bssid_pos[3]))

            result_x += reciprocal * float(result[0])
            result_y += reciprocal * float(result[1])

            # geo_estimation.append((result, simple_bssid_pos[3]))

            sum_reciprocal += reciprocal
    else:
        result = geomagnetism_fingerprinting(correct_pos, bssid_area.get_posist("None"))

        result_x += (1.0 / float(bssid_area.get_detail("None")[3])) * float(result[0])
        result_y += (1.0 / float(bssid_area.get_detail("None")[3])) * float(result[1])

        # geo_estimation.append((geomagnetism_fingerprinting(correct_pos, bssid_area.get_posist("None")), bssid_area.get_detail("None")[3]))
        sum_reciprocal += 1.0 / float(bssid_area.get_detail("None")[3])

    if sum_reciprocal == 0.0:
        result = geomagnetism_fingerprinting(correct_pos, bssid_area.get_posist("None"))

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


def insert_other_direction():
    other_data = []
    for row in prev_GeoList:
        for dir_num in [90, 180, 270]:
            rotate_deg = (math.pi / 2.0) * float(dir_num / 90)
            rotate_geo = [row[4] * cos(rotate_deg) - row[5] * sin(rotate_deg),
                          row[4] * sin(rotate_deg) + row[5] * cos(rotate_deg), row[6]]
            other_data.append(
                [row[0], row[1], row[2], rotate_direction(row[3], dir_num), rotate_geo[0], rotate_geo[1], rotate_geo[2],
                 row[7], row[8], row[9]])
    prev_GeoList.extend(other_data)


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

    insert_other_direction()

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
    '''
    list_10cut = [11, 43, 105, 88, 69, 54, 33, 14, 57, 38]
    list_20cut = [105, 30, 83, 100, 56, 64, 10, 6, 47, 62, 2, 67, 81, 4, 12, 32, 92, 72, 91, 24, 26]
    list_25cut = [74, 55, 88, 36, 52, 92, 20, 35, 38, 70, 4, 98, 8, 86, 41, 82, 61, 32, 58, 12, 85, 22, 107, 90, 65, 30, 99]
    list_30cut = [100, 37, 32, 21, 17, 7, 80, 90, 75, 46, 14, 66, 8, 68, 52, 101, 5, 25, 45, 61, 72, 65, 62, 6, 93, 77, 74, 107, 16, 82, 88, 96]
    list_40cut = [78, 77, 69, 107, 92, 103, 96, 84, 56, 34, 47, 15, 53, 39, 24, 94, 16, 28, 49, 40, 14, 65, 21, 51, 59, 98, 6, 73, 97, 67, 88, 31, 80, 25, 90, 105, 57, 29, 99, 64, 41, 74, 7]
    list_50cut = [105, 1, 96, 33, 47, 53, 25, 37, 66, 55, 50, 72, 86, 32, 11, 24, 44, 9, 20, 59, 22, 68, 81, 45, 7, 29, 101, 89, 28, 10, 52, 58, 19, 30, 79, 8, 49, 42, 85, 91, 63, 82, 75, 2, 16, 27, 78, 51, 83, 15, 67, 54, 73, 60]
    list_60cut = [10, 50, 4, 2, 98, 78, 7, 51, 26, 12, 92, 31, 104, 53, 63, 77, 75, 64, 107, 42, 61, 88, 15, 66, 96, 40, 16, 60, 44, 83, 33, 103, 3, 29, 20, 52, 0, 48, 13, 68, 70, 106, 80, 46, 39, 41, 79, 1, 9, 84, 18, 35, 45, 27, 8, 81, 47, 21, 49, 86, 85, 5, 72, 73]
    list_70cut = [30, 10, 106, 1, 90, 12, 79, 45, 61, 66, 105, 85, 55, 46, 96, 99, 6, 40, 49, 71, 57, 87, 33, 68, 9, 95, 62, 34, 7, 86, 58, 94, 27, 64, 24, 89, 44, 37, 102, 3, 75, 80, 8, 53, 25, 28, 70, 23, 48, 59, 72, 2, 56, 36, 31, 35, 83, 77, 50, 22, 101, 67, 92, 13, 93, 29, 15, 26, 74, 54, 73, 47, 41, 103, 14]
    list_75cut = [56, 94, 55, 85, 83, 58, 51, 73, 40, 14, 96, 66, 19, 8, 48, 35, 67, 28, 72, 84, 6, 76, 61, 106, 78, 100, 0, 93, 103, 107, 65, 31, 13, 18, 4, 68, 47, 88, 50, 92, 71, 64, 49, 16, 53, 23, 11, 74, 25, 36, 87, 45, 95, 29, 39, 57, 101, 33, 102, 20, 60, 105, 32, 34, 41, 98, 99, 9, 79, 77, 89, 90, 2, 81, 7, 86, 69, 63, 17, 1, 91]
    list_80cut = [33, 12, 2, 52, 31, 85, 0, 60, 48, 103, 54, 41, 107, 23, 40, 74, 73, 80, 57, 32, 50, 45, 53, 39, 3, 42, 69, 16, 62, 61, 56, 86, 64, 100, 26, 34, 90, 38, 68, 21, 49, 18, 44, 29, 17, 11, 77, 78, 95, 79, 14, 20, 72, 91, 83, 88, 102, 105, 22, 24, 27, 25, 75, 13, 37, 97, 99, 43, 55, 9, 96, 89, 66, 101, 7, 94, 67, 46, 15, 65, 6, 58, 63, 98, 76, 87]
    list_90cut = [81, 16, 85, 77, 42, 99, 25, 35, 38, 87, 47, 66, 4, 55, 61, 63, 36, 11, 62, 56, 41, 20, 49, 37, 69, 96, 83, 92, 95, 6, 91, 50, 24, 19, 70, 93, 45, 104, 22, 71, 74, 26, 9, 89, 97, 33, 44, 59, 105, 34, 100, 67, 21, 78, 94, 86, 13, 14, 64, 88, 73, 10, 48, 15, 75, 103, 0, 101, 76, 12, 30, 57, 29, 54, 102, 28, 5, 58, 60, 82, 40, 1, 8, 106, 2, 31, 107, 65, 3, 43, 23, 17, 32, 27, 79, 72, 68]
    list_100cut = [10, 22, 102, 24, 76, 73, 97, 58, 32, 88, 17, 9, 51, 5, 104, 87, 99, 106, 60, 2, 78, 50, 95, 90, 62, 72, 65, 34, 12, 19, 16, 18, 15, 100, 61, 69, 42, 64, 71, 77, 31, 89, 66, 75, 33, 70, 25, 74, 53, 37, 57, 40, 11, 84, 67, 94, 29, 26, 6, 79, 96, 7, 55, 83, 39, 63, 81, 52, 8, 47, 105, 27, 3, 13, 20, 41, 0, 54, 92, 68, 107, 48, 82, 28, 59, 4, 44, 23, 35, 101, 85, 38, 91, 1, 49, 45, 93, 80, 36, 14, 21, 98, 103, 46, 30, 86, 56, 43]
    # 108 APs
    '''

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

    bssidnum = 100
    delete_list = []
    for i in [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]:
        delete_list.append(random.sample(xrange(0, bssidnum), int(bssidnum * (float(i) / 100.0))))

    # evaluation([proposed_geomagnetic_fingerprinting], [u"proposed geomagnetic fingerprinting"], curr_PosList)

    evaluation_mmr(method=[wifi_fingerprinting, wifi_aided_magnetic_matching, proposed_geomagnetic_fingerprinting,
                           proposed_positioning],
                   method_name=[u"Wi-Fi FP", u"Existing method", u"proposed geomagnetism FP", u"proposed method"],
                   delete_list=delete_list,
                   curr_PosList=curr_PosList,
                   prev_PosList=prev_PosList,
                   fig_name="error_rate",
                   c_WiFiList=c_WiFiList,
                   p_WiFiList=p_WiFiList
                   )

    '''
    evaluation(method=[wifi_fingerprinting,  wifi_aided_magnetic_matching, proposed_geomagnetic_fingerprinting,
                       proposed_positioning],
               method_name=["Wi-Fi FP","Existing method", "proposed geomagnetism FP", "proposed method"],
               delete_list=delete_list,
               curr_PosList=curr_PosList,
               prev_PosList=prev_PosList,
               fig_name=fig_name,
               c_WiFiList=c_WiFiList,
               p_WiFiList=p_WiFiList
               )
    '''

    # evaluation([wifi_fingerprinting, proposed_geomagnetic_fingerprinting, wifi_aided_magnetic_matching, proposed_positioning], ["wifi fingerprinting","proposed geomagnetic fingerprinting" ,"wifi aided magnetic matching", "proposed positioning method"], curr_PosList)
    # evaluation([wifi_fingerprinting, proposed_geomagnetic_fingerprinting, proposed_positioning], ["wifi fingerprinting","proposed geomagnetic fingerprinting" , "proposed positioning method"], curr_PosList)
