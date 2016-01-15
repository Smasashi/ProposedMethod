# -*- coding: UTF-8 -*-

import sqlite3
import sys
import math
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
from operator import itemgetter, attrgetter

_PENALTY_POINT = 500.0
_K = 3


class Position(object):
    def __init__(self, floor, x, y, direction, bssid, freq, ave_rssi, dif_rssi, cnt, h_geo, v_geo, w_geo, point):
        self.Floor = floor
        self.X = x
        self.Y = y
        self.Direction = direction
        self.point = point
        self.bssid = [bssid]
        self.frequency = [freq]
        self.ave_rssi = [ave_rssi]
        self.dif_rssi = [dif_rssi]
        self.cnt = [cnt]
        self.h_geo = h_geo
        self.v_geo = v_geo
        self.w_geo = w_geo
        self.point = point


    def __repr__(self):
        return '(Point :%s  x :%s  y :%s)' % (self.point, self.X, self.Y)

def import_database(database_name):
    con = sqlite3.connect(database_name)
    wifi = con.cursor()
    geo = con.cursor()
    grvty = con.cursor()
    wifi.execute(u"SELECT * FROM CONDUCTED_WiFi")
    geo.execute(u"SELECT * FROM CONDUCTED_GEO")
    grvty.execute(u"SELECT * FROM CONDUCTED_GRAVITY")
    TmpList = []
    c = -1
    pos_tuple = (-1, -1, -1, -1)
    for row in wifi:
        if not (row[0] == pos_tuple[0] and row[1] == pos_tuple[1] and row[2] == pos_tuple[2] and row[3] == pos_tuple[3]):
            pos_tuple = (row[0], row[1], row[2], row[3])
            TmpList.append(Position(row[0], row[1], row[2], row[3], row[4], row[6], row[7], row[8], row[9], None, None, None, None))
            c += 1
        else:
            TmpList[c].bssid.append(row[4])
            TmpList[c].frequency.append(row[6])
            TmpList[c].ave_rssi.append(row[7])
            TmpList[c].dif_rssi.append(row[8])
            TmpList[c].cnt.append(row[9])

    return TmpList


def createposlist(cursor, sql):
    pos_search = cursor.execute(sql)

    poslist = []

    for row in pos_search:
        poslist.append(Position(row[0], row[1], row[2], row[3], None))

    return poslist


def wifi_fingerprinting(Finger):
    now_wifi_bind = u" xcoordinate = " + str(ans_pos.X) + u" AND ycoordinate = " + str(
        ans_pos.Y) + u" AND floor = " + str(ans_pos.Floor) + u" AND Direction = \"" + str(ans_pos.Direction) + u"\""
    print now_wifi_bind
    now_wifi = prev_con.execute(u"SELECT * FROM PROCESSED_WiFi WHERE" + now_wifi_bind + u";")

    print u"SELECT * FROM PROCESSED_WiFi WHERE" + now_wifi_bind + u";"

    fingerprint_wifi_bind = u""
    for row in now_wifi.fetchall():
        fingerprint_wifi_bind += "\"" + str(row[4]) + "\","
    #print fingerprint_wifi_bind[:-1]

    wifi_fingerprint_pos_list = curr_con.execute(
        u"SELECT DISTINCT Floor, xcoordinate, ycoordinate, Direction FROM PROCESSED_WiFi WHERE BSSID IN(" +
        fingerprint_wifi_bind[:-1] + u");")
    #print wifi_fingerprint_pos_list.rowcount
    estimation = []
    for fp in wifi_fingerprint_pos_list:
        #now_wifi = prev_con.execute(u"SELECT * FROM PROCESSED_WiFi WHERE" + now_wifi_bind + u";")
        now_wifi.scroll(0)
        fingerprint_pos_bind = u" xcoordinate = " + str(fp[1]) + u" AND ycoordinate = " + str(fp[2]) + u" AND floor = "\
                               + str(fp[0]) + u" AND Direction = \"" + str(fp[3]) + u"\""
        point = 0.0
        for sample in now_wifi:
            wifi_fingerprint = curr_con.execute(u"SELECT * FROM PROCESSED_WiFi WHERE" + fingerprint_pos_bind + u";")
            #print point
            for fingerprint_pos_wifi in wifi_fingerprint:
                if sample[4] == fingerprint_pos_wifi[4]:
                    point += math.pow(sample[7] - fingerprint_pos_wifi[7], 2)
            else:
                point += _PENALTY_POINT
        estimation.append(Position(fp[0], fp[1], fp[2], fp[3], point))

    print sorted(estimation, key=lambda x: x.point)


    result_x = 0
    result_y = 0

    if len(estimation) < 3:
        return 0.0, 0.0

    for i in range(0, _K):
        result_x += estimation[i].X
        result_y += estimation[i].Y

    return result_x / _K, result_y / _K


def wifi_aided_magnetic_mathcing(ans_pos):
    wifi_fingerprinting(ans_pos=ans_pos)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print '#error '
        exit()

    prev_PosList = []
    curr_PosList = []

    prev_db_name = sys.argv[1]
    curr_db_name = sys.argv[2]

    prev_list = import_database(prev_db_name)
    curr_list = import_database(curr_db_name)

    prev_PosList = createposlist(sqlite3.connect(prev_db_name).cursor(),
                                 u"SELECT DISTINCT Floor, xcoordinate, ycoordinate, direction FROM PROCESSED_WiFi;")
    curr_PosList = createposlist(sqlite3.connect(curr_db_name).cursor(),
                                 u"SELECT DISTINCT Floor, xcoordinate, ycoordinate, direction FROM PROCESSED_WiFi;")

    for Cpos in range(len(curr_PosList)):
        print wifi_fingerprinting(curr_PosList[Cpos])
