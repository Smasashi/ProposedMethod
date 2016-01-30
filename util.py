from math import *
import numpy as np


def func(x, a, b, c):
    return float(a)/float(x+b) + c


class Position(object):
    def __init__(self, floor, x, y, direction, point):
        self.Floor = floor
        self.X = x
        self.Y = y
        self.Direction = direction
        self.point = point

    def __repr__(self):
        return '(Point :%s  x :%s  y :%s)' % (self.point, self.X, self.Y)


class AreabyBSSID(object):
    def __init__(self):
        self.area_list = []

    def setarea(self, BSSID, poslist, varRSSI, posCnt, wifiCnt):
        self.area_list.append([BSSID, poslist, varRSSI, posCnt, wifiCnt])
        return None

    def get_posist(self, BSSID):
        for row in self.area_list:
            if BSSID == row[0]:
                return row[1]

    def get_detail(self, BSSID):
        for row in self.area_list:
            if BSSID == row[0]:
                return row

    def size(self):
        return len(self.area_list)

    def get_BSSID(self, index):
        return self.area_list[index][0]


def calc_wifi_dependence(bssid_prm, rssi_prm, now_wifi):
    maxrssi = -float("inf")
    numbssid = len(now_wifi)
    for row in now_wifi:
        if maxrssi < row[7]:
            maxrssi = row[7]
    if len(now_wifi) == 0:
        return 0.0

    '''
    dependence_bssid = (40.5/(float(len(now_wifi)) + 1.01) - 1.0)/60.0
    dependence_rssi = (197.5/(float(maxrssi) + 100.1) - 3.0)/60.0
    '''

    dependence_bssid = (bssid_prm[0] / (float(len(now_wifi)) + bssid_prm[1]) + bssid_prm[2])/40.0
    dependence_rssi = (rssi_prm[0] / (float(maxrssi) + rssi_prm[1]) + rssi_prm[2])/40.0

    print len(now_wifi), maxrssi

    rssi_sos = 18822.2
    bssid_sos = 18775.1

    dependence = (bssid_sos*(1.0-dependence_bssid) + (rssi_sos*(1.0-dependence_rssi)))/(bssid_sos + rssi_sos)

    if dependence > 1.0:
        dependence = 1.0
    elif dependence < 0.0:
        dependence = 0.0

    print dependence
    return dependence


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


def convert_resultant_vector(device_geo):
    roll = atan2(-device_geo[7], device_geo[9])
    pitch = atan2(device_geo[8], sqrt(device_geo[7] ** 2 + device_geo[9] ** 2))

    now_gm_ver = fabs(
        -cos(pitch) * sin(roll) * device_geo[4] + sin(pitch) * device_geo[5] + cos(
            pitch) * cos(roll) * device_geo[6])
    now_gm_whl = sqrt(device_geo[4] ** 2 + device_geo[5] ** 2 + device_geo[6] ** 2)
    now_gm_hor = sqrt(now_gm_whl ** 2 - now_gm_ver ** 2)

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
                pos = Position(row1[0], row1[1], row1[2], row1[3], None)
                isunique = True

                for row in list_where_in_bssid:
                    if row.X == pos.X and row.Y == pos.Y:
                        isunique = False
                        break

                if not isunique:
                    break

                list_where_in_bssid.append(Position(row1[0], row1[1], row1[2], row1[3], None))
                break

    return list(set(list_where_in_bssid))


def create_list_in_circle(pos, prev_PosList):
    poslist = []
    for prev_pos in prev_PosList:
        if sqrt((pos.X - prev_pos.X)**2 + (pos.Y - prev_pos.Y)**2) <= 3.0:
            poslist.append(prev_pos)
    return poslist


def dtw(vec1, vec2):
    import numpy as np
    d = np.zeros([len(vec1)+1, len(vec2)+1])
    d[:] = np.inf
    d[0, 0] = 0
    for i in range(1, d.shape[0]):
        for j in range(1, d.shape[1]):
            cost = (vec1[i-1][0]-vec2[j-1][0])**2 + (vec1[i-1][1]-vec2[j-1][1])**2 + (vec1[i-1][2]-vec2[j-1][1])**2
            d[i, j] = cost + min(d[i-1, j], d[i, j-1], d[i-1, j-1])
    return d[-1][-1]


def fit_rssi(data):
    ndata = np.array(data).T
    data_x = ndata[0]
    data_y = ndata[1]

    min_first_bias = 7.5
    min_x_bias = 101
    min_y_bias = -0.12

    min_point = float("inf")

    for i in xrange(10010, 12000, 100):
        for j in xrange(50, 40000, 100):
            for k in xrange(-1000, 0, 100):
                point = 0.0
                x_bias = float(i)/100.0
                y_bias = float(k)/100.0
                first_bias = float(j)/100.0
                isBreak = False

                for l in range(0, len(data_x)):
                    if data_x[l] + float(i)/100.0 == 0.0:
                        isBreak = True
                        break
                    point += (data_y[l] - func(data_x[l], first_bias, x_bias, y_bias))**2

                if isBreak:
                    break

                # print i, j, k, point

                if point < min_point:
                    min_point = point
                    min_x_bias = x_bias
                    min_y_bias = y_bias
                    min_first_bias = first_bias
                    #print "run"
                    #print first_bias, x_bias, y_bias
    return min_first_bias, min_x_bias, min_y_bias


def fit_bssid(data):
    ndata = np.array(data).T
    data_x = ndata[0]
    data_y = ndata[1]

    min_first_bias = 7.5
    min_x_bias = 101
    min_y_bias = -0.12

    min_point = float("inf")

    for i in xrange(1, 1000, 100):
        for j in xrange(50, 40000, 100):
            for k in xrange(-1000, 0, 100):
                point = 0.0
                x_bias = float(i)/100.0
                y_bias = float(k)/100.0
                first_bias = float(j)/100.0
                isBreak = False

                for l in range(0, len(data_x)):
                    if data_x[l] + float(i)/100.0 == 0.0:
                        isBreak = True
                        break
                    point += (data_y[l] - func(data_x[l], first_bias, x_bias, y_bias))**2

                if isBreak:
                    break

                #print i, j, k, point

                if point < min_point:
                    min_point = point
                    min_x_bias = x_bias
                    min_y_bias = y_bias
                    min_first_bias = first_bias
                    #print "run"
                    #print first_bias, x_bias, y_bias
    return min_first_bias, min_x_bias, min_y_bias
