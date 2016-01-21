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
    now_roll = math.atan2(-device_geo[0], device_geo[2])
    now_pitch = math.atan2(device_geo[1], math.sqrt(device_geo[0] ** 2 + device_geo[2] ** 2))

    now_gm_ver = math.fabs(
        -math.cos(now_pitch) * math.sin(now_roll) * device_geo[0] + math.sin(now_pitch) * device_geo[1] + math.cos(
            now_pitch) * math.cos(now_roll) * device_geo[1])
    now_gm_whl = math.sqrt(device_geo[0] ** 2 + device_geo[1] ** 2 + device_geo[2] ** 2)
    now_gm_hor = math.sqrt(math.fabs(now_gm_whl ** 2 - now_gm_ver ** 2))

    return now_gm_hor, now_gm_ver, now_gm_whl


def geomagnetism_fingerprinting(correct_pos, poslist):
    now_geo_bind = create_sql_bind_point(correct_pos)
    now_geo_cur = curr_con.execute(u"SELECT * FROM PROCESSED_GEO WHERE " + now_geo_bind + u";")
    now_geo = now_geo_cur.fetchall()

    local_now_geo = convert_resultant_vector(now_geo[0])

    estimation = []

    for pos in poslist:
        fp_geo_bind = create_sql_bind_point(pos)
        fp_geo_cur = prev_con.execute(u"SELECT * FROM PROCESSED_GEO WHERE" + fp_geo_bind + u";")
        fp_geo = fp_geo_cur.fetchall()

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
        print "(" + str(estimation[i].X) + ":" + str(estimation[i].Y) + ":" + str(estimation[i].point) + ")"
        result_x += estimation[i].X
        result_y += estimation[i].Y

    return result_x / _K, result_y / _K


def wifi_fingerprinting(correct_pos):
    now_wifi_bind = create_sql_bind_point(correct_pos)
    print now_wifi_bind
    now_wifi_cur = curr_con.execute(u"SELECT * FROM PROCESSED_WiFi WHERE " + now_wifi_bind + u";")
    now_wifi = now_wifi_cur.fetchall()

    fingerprint_wifi_bind = u""
    for row in now_wifi:
        fingerprint_wifi_bind += "\"" + str(row[4]) + "\","

    wifi_fingerprint_pos_list_cur = prev_con.execute(
        u"SELECT DISTINCT Floor, xcoordinate, ycoordinate, Direction FROM PROCESSED_WiFi WHERE BSSID IN(" + fingerprint_wifi_bind[
                                                                                                            :-1] + u");")
    wifi_fingerprint_pos_list = wifi_fingerprint_pos_list_cur.fetchall()

    estimation = []
    for fp in wifi_fingerprint_pos_list:
        fingerprint_pos_bind = create_sql_bind_point(Position(fp[0], fp[1], fp[2], fp[3], None))
        point = 0.0
        for sample in now_wifi:
            wifi_fingerprint = prev_con.execute(u"SELECT * FROM PROCESSED_WiFi WHERE" + fingerprint_pos_bind + u";")
            # print point
            for fingerprint_pos_wifi in wifi_fingerprint:
                if sample[4] == fingerprint_pos_wifi[4]:
                    point += (sample[7] - fingerprint_pos_wifi[7]) ** 2
                    break
            else:
                point += _PENALTY_POINT
        estimation.append(Position(fp[0], fp[1], fp[2], fp[3], point))
    estimation = sorted(estimation, key=lambda x: x.point)

    result_x = 0
    result_y = 0

    if len(estimation) < 3:
        return -1.0, -1.0

    for i in range(0, _K):
        result_x += estimation[i].X
        result_y += estimation[i].Y

    return result_x / _K, result_y / _K


def wifi_aided_magnetic_mathcing(correct_pos):
    wifi_fingerprinting(correct_pos=correct_pos)


def area_division_by_bssid():
    return


def display_bssid_distribution(bssid):
    fingerprint_bssid_bind = ""

    for i in bssid:
        fingerprint_bssid_bind += "\"" + i + "\","

    pos_includes_bssid = prev_con.execute(
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
                                 u"SELECT DISTINCT Floor, xcoordinate, ycoordinate, direction FROM PROCESSED_WiFi;")
    prev_WiFiList = prev_con.execute(u"SELECT * FROM PROCESSED_WiFi").fetchall()
    prev_GeoList = prev_con.execute(u"SELECT * FROM posture_estimation").fetchall()

    curr_con = sqlite3.connect(curr_db_name)
    curr_PosList = createposlist(sqlite3.connect(curr_db_name).cursor(),
                                 u"SELECT DISTINCT Floor, xcoordinate, ycoordinate, direction FROM PROCESSED_WiFi;")
    curr_WiFiList = curr_con.execute(u"SELECT * FROM PROCESSED_WiFi").fetchall()
    curr_GeoList = curr_con.execute(u"SELECT * FROM posture_estimation").fetchall()

    for Cpos in curr_PosList:
    #    print wifi_fingerprinting(curr_PosList[Cpos])
        print geomagnetism_fingerprinting(Cpos, prev_PosList)
