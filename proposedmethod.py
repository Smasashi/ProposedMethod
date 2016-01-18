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
from operator import itemgetter, attrgetter

_PENALTY_POINT = 500.0
_K = 3


class bssid_reliability(object):
    def __init__(self, bssid, point):
        bssid = bssid
        point = point

    def __repr__(self):
        return '(bssid: %s -- point: %s)' % (self.bssid, self.point)


class Position(object):
    def __init__(self, floor, x, y, direction, point):
        self.Floor = floor
        self.X = x
        self.Y = y
        self.Direction = direction
        self.point = point

    def __repr__(self):
        return '(Point :%s  x :%s  y :%s)' % (self.point, self.X, self.Y)


class area(object):
    def __init__(self, spot, wifi_dependance):
        self.spots = [spot]
        self.wifi_dependance = wifi_dependance


def createposlist(cursor, sql):
    pos_search = cursor.execute(sql)

    poslist = []

    for row in pos_search:
        poslist.append(Position(row[0], row[1], row[2], row[3], None))

    return poslist


def create_sql_bind_rectangle(pos, R):
    bind = u"Floor=" + pos.floor + u" AND xcoordinate >= " + str(pos.x - R) + u" AND xcoordinate <= " + str(pos.x + R) + u" AND ycoordinate >= " + str(pos.y - R) + u" AND ycoordinate <= " + str(pos.y + R)
    return bind


def create_sql_bind_point(pos):
    bind = u" xcoordinate = " + str(pos.X) + u" AND ycoordinate = " + str(pos.Y) + u" AND floor = " + str(pos.Floor) + u" AND Direction = \"" + str(pos.Direction) + u"\""
    return bind


def calc_point_reliability(pos):

    pos_rectangle_bind = create_sql_bind_rectangle(pos, 3.0)

    search_around_point = prev_con.execute(u"SELECT * FROM PROCESSED_WiFi WHERE " + pos_rectangle_bind + u";")

    return None


def geomagnetism_fingerprinting(correct_pos, estimated_area):
    now_geo_bind = create_sql_bind_point(correct_pos)
    now_geo_cur = prev_con.execute(u"SELECT * FROM PROCESSED_GEO WHERE " + now_geo_bind + u";")
    now_geo = now_geo_cur.fetchall()

    now_roll = math.atan2(-now_geo[0][0], now_geo[0][2])
    # now_pitch = math.atan2(-r)

    # for pos in estimated_area:




def wifi_fingerprinting(correct_pos):

    now_wifi_bind = create_sql_bind_point(correct_pos)
    print now_wifi_bind
    now_wifi_cur = curr_con.execute(u"SELECT * FROM PROCESSED_WiFi WHERE " + now_wifi_bind + u";")
    now_wifi = now_wifi_cur.fetchall()

    fingerprint_wifi_bind = u""
    for row in now_wifi:
        fingerprint_wifi_bind += "\"" + str(row[4]) + "\","

    wifi_fingerprint_pos_list_cur = prev_con.execute(u"SELECT DISTINCT Floor, xcoordinate, ycoordinate, Direction FROM PROCESSED_WiFi WHERE BSSID IN(" + fingerprint_wifi_bind[:-1] + u");")
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
        u"SELECT DISTINCT Floor, xcoordinate, ycoordinate, Direction, avg_rssi, count FROM PROCESSED_WiFi WHERE BSSID IN(" + fingerprint_bssid_bind[:-1] + u");")

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
    curr_con = sqlite3.connect(curr_db_name)

    prev_PosList = createposlist(sqlite3.connect(prev_db_name).cursor(),
                                 u"SELECT DISTINCT Floor, xcoordinate, ycoordinate, direction FROM PROCESSED_WiFi;")
    curr_PosList = createposlist(sqlite3.connect(curr_db_name).cursor(),
                                 u"SELECT DISTINCT Floor, xcoordinate, ycoordinate, direction FROM PROCESSED_WiFi;")

    display_bssid_distribution(["10:6f:3f:d9:8e:ad"])



    # for Cpos in range(len(curr_PosList)):
    #     print wifi_fingerprinting(curr_PosList[Cpos])
