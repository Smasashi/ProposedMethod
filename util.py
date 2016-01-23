class BSSIDReliability(object):
    def __init__(self, BSSID, point):
        BSSID = BSSID
        point = point

    def __repr__(self):
        return '(BSSID: %s -- point: %s)' % (self.BSSID, self.point)


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
