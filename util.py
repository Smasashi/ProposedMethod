class BSSIDReliability(object):
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


class AreabyBSSID(object):
    def __init__(self):
        self.list = []

    def setarea(self, bssid, reliability, poslist):
        list.append([bssid, reliability, poslist])

    def getposlist(self, bssid):
        for row in list:
            if bssid == row[0]:
                return row[2], row[3]

