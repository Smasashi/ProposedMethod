# -*- coding: UTF-8 -*-

import sqlite3
import sys
import math
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import matplotlib as mpl
import matplotlib.cm as cm
import numpy as np
from util import Position, BSSIDReliability, AreabyBSSID
from displayBSSID import display_bssid_distribution
from operator import itemgetter, attrgetter

_PENALTY_POINT = 500.0
_K = 3


def createposlist(cursor, sql):
    pos_search = cursor.execute(sql)

    poslist = []

    for row in pos_search:
        poslist.append(Position(row[0], row[1], row[2], row[3], None))

    return poslist


def create_sql_bind_rectangle(pos, R):
    bind = u"Floor=" + pos.floor + u" AND xcoordinate >= " + str(pos.x - R) + u" AND xcoordinate <= " + str(
        pos.x + R) + u" AND ycoordinate >= " + str(pos.y - R) + u" AND ycoordinate <= " + str(pos.y + R)
    return bind


def create_sql_bind_point(pos):
    bind = u" xcoordinate = " + str(pos.X) + u" AND ycoordinate = " + str(pos.Y) + u" AND floor = " + str(
        pos.Floor) + u" AND Direction = \"" + str(pos.Direction) + u"\""
    return bind


def calc_point_reliability(pos):
    pos_rectangle_bind = create_sql_bind_rectangle(pos, 3.0)

    search_around_point = prev_con.execute(u"SELECT * FROM PROCESSED_WiFi WHERE " + pos_rectangle_bind + u";")

    return None


def convert_resultant_vector(device_geo):
    now_roll = math.atan2(-device_geo[7], device_geo[9])
    now_pitch = math.atan2(device_geo[8], math.sqrt(device_geo[7] ** 2 + device_geo[8] ** 2))

    now_gm_ver = math.fabs(
        -math.cos(now_pitch) * math.sin(now_roll) * device_geo[4] + math.sin(now_pitch) * device_geo[5] + math.cos(
            now_pitch) * math.cos(now_roll) * device_geo[5])
    now_gm_whl = math.sqrt(device_geo[4] ** 2 + device_geo[5] ** 2 + device_geo[6] ** 2)
    now_gm_hor = math.sqrt(math.fabs(now_gm_whl ** 2 - now_gm_ver ** 2))

    return now_gm_hor, now_gm_ver, now_gm_whl


def find_list_by_pos(pos, List):
    list_in_pos = []

    for row in List:
        if pos.Floor == row[0] and pos.X == row[1] and pos.Y == row[2] and pos.Direction == row[3]:
            list_in_pos.append(row)
    return list_in_pos


def find_list_by_BSSID(sample, FP):
    list_where_in_bssid = []
    for row1 in FP:
        for row2 in sample:
            if row1[4] == row2[4]:
                list_where_in_bssid.append(Position(row1[0], row1[1], row1[2], row1[3], None))
                break

    return list(set(list_where_in_bssid))


def geomagnetism_fingerprinting(correct_pos, poslist):
    now_geo = find_list_by_pos(correct_pos, curr_GeoList)

    local_now_geo = convert_resultant_vector(now_geo[0])

    estimation = []

    for pos in poslist:
        fp_geo = find_list_by_pos(pos, prev_GeoList)

        local_fp_geo = convert_resultant_vector(fp_geo[0])

        point = (local_now_geo[0] - local_fp_geo[0]) ** 2 + (local_now_geo[1] - local_fp_geo[1]) ** 2 + \
                (local_now_geo[2] - local_fp_geo[2]) ** 2
        estimation.append(Position(pos.Floor, pos.X, pos.Y, pos.Direction, point))

    estimation = sorted(estimation, key=lambda x: x.point)

    if len(estimation) < _K:
        return -1.0, -1.0

    result_x = 0
    result_y = 0
    for i in range(0, _K):
        #print "(" + str(estimation
        # [i].X) + ":" + str(estimation[i].Y) + ":" + str(estimation[i].point) + ")"
        result_x += estimation[i].X
        result_y += estimation[i].Y

    return result_x / _K, result_y / _K


def wifi_fingerprinting(correct_pos):
    now_wifi = find_list_by_pos(correct_pos, curr_WiFiList)

    fp_wifi_poslist = find_list_by_BSSID(now_wifi, prev_WiFiList)

    estimation = []
    for pos in fp_wifi_poslist:
        fp_wifi = find_list_by_pos(Position(pos.Floor, pos.X, pos.Y, pos.Direction, None), prev_WiFiList)
        point = 0.0
        for sample in now_wifi:
            # print point
            for fingerprint_pos_wifi in fp_wifi:
                if sample[4] == fingerprint_pos_wifi[4]:
                    point += (sample[7] - fingerprint_pos_wifi[7]) ** 2
                    break
            else:
                point += _PENALTY_POINT
        estimation.append(Position(pos.Floor, pos.X, pos.Y, pos.Direction, point))
    estimation = sorted(estimation, key=lambda x: x.point)

    result_x = 0
    result_y = 0

    if len(estimation) < 3:
        return -1.0, -1.0

    for i in range(0, _K):
        result_x += estimation[i].X
        result_y += estimation[i].Y

    return result_x / _K, result_y / _K


def proposed_positioning(correct_pos):
    now_wifi = find_list_by_pos(correct_pos, curr_WiFiList)

    geo_estimation = []

    if not len(now_wifi) == 0 :
        for row in now_wifi:
            simple_bssid_pos = bssid_area.get_detail(row[4])

            if simple_bssid_pos is None:
                continue

            geo_estimation.append((geomagnetism_fingerprinting(correct_pos, simple_bssid_pos[1]), simple_bssid_pos[3]))
    else:
        geo_estimation.append((geomagnetism_fingerprinting(correct_pos, bssid_area.get_posist("None")), bssid_area.get_detail("None")[3]))

    print geo_estimation


def configure_area_by_wifi():
    area = AreabyBSSID()

    bssid_list = []
    for row in prev_WiFiList:
        bssid_list.append(row[4])
    bssid_list_uniq = list(set(bssid_list))

    None_wifi_poslist = []

    for row1 in prev_PosList:
        for row2 in curr_WiFiList:
            if row1.Floor == row2[0] and row1.X == row2[1] and row1.Y == row2[2] and row1.Direction == row2[3]:
                break
        else:
            None_wifi_poslist.append(row1)

    area.setarea("None", None_wifi_poslist, -1.0, len(None_wifi_poslist), -1.0)

    for bssid in bssid_list_uniq:
        pos_cnt = 0
        poslist = []
        rssilist = []
        wifi_receive_cnt = 0
        for row in prev_WiFiList:
            if bssid == row[4]:
                pos_cnt += 1
                poslist.append(Position(row[0], row[1], row[2], row[3], None))
                rssilist.append(row[7])
                wifi_receive_cnt += row[9]
        area.setarea(bssid, poslist, np.var(rssilist), pos_cnt, wifi_receive_cnt)
    return area


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
    prev_WiFiList = prev_con.execute(u"SELECT * FROM PROCESSED_WiFi").fetchall()
    prev_GeoList = prev_con.execute(u"SELECT * FROM posture_estimation").fetchall()

    curr_con = sqlite3.connect(curr_db_name)
    curr_PosList = createposlist(sqlite3.connect(curr_db_name).cursor(),
                                 u"SELECT DISTINCT Floor, xcoordinate, ycoordinate, direction FROM PROCESSED_GEO;")
    curr_WiFiList = curr_con.execute(u"SELECT * FROM PROCESSED_WiFi").fetchall()
    curr_GeoList = curr_con.execute(u"SELECT * FROM posture_estimation").fetchall()

    bssid_area = configure_area_by_wifi()

    estimation_error = []
    error_cnt = 0
    '''
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

    for Cpos in curr_PosList:
        print (Cpos.X ,Cpos.Y), proposed_positioning(Cpos)
