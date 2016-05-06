# coding=utf-8
import csv
import numpy as np
import sys
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import pylab as pl
import scipy
import math
from scipy.optimize import *

data = []
data_x = []
data_y = []


def func(x, a, b, c):
    return float(a)/float(x+b) + c

with open('bssid.csv', 'r') as f:
    reader = csv.reader(f)
    header = next(reader)

    for row in reader:
        data.append([float(row[0]), float(row[1])])
        data_x.append(float(row[0]))
        data_y.append(float(row[1]))

xdata = np.array(data_x)
ydata = np.array(data_y)
parameter_initial = np.array([0.0, 0.0, 0.0])

x = np.linspace(-100, -40, 100)
# x =  pl.linspace(0, 50, 500)
y = []
'''
min_first_bias = 7.5
min_x_bias = 101
min_y_bias = -0.12
'''

min_first_bias = 7.5
min_x_bias = 101
min_y_bias = -0.12

min_point = float("inf")

print np.array([data_x, data_y]).transpose()


'''
for i in xrange(1, 1000, 100):
    for j in xrange(50, 20000, 100):
        for k in xrange(-1000, 0, 100):
'''

for i in xrange(10010, 12000, 100):
    for j in xrange(50, 20000, 100):
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

            print i, j, k, point

            if point < min_point:
                min_point = point
                min_x_bias = x_bias
                min_y_bias = y_bias
                min_first_bias = first_bias
                print "run"
                print first_bias, x_bias, y_bias

print min_first_bias, min_x_bias, min_y_bias, min_point

for i in range(0, len(x)):
    y.append(func(x[i], min_first_bias, min_x_bias, min_y_bias))

#print func(min(data_x), min_first_bias, min_x_bias, min_y_bias)
#print func(max(data_x), min_first_bias, min_x_bias, min_y_bias)

#mpl.rcParams['font.family'] = 'Osaka'

s=data.index

plt.figure(figsize=(10, 7))

fig, ax1 = plt.subplots()

ax1.scatter(data_x, data_y, s=50)
ax1.set_xlabel(u"観測最大RSSI[dB]")
ax1.set_ylabel(u"測位誤差[m]")
ax1.set_ylim(0, 60)
ax1.set_xlim(-100, -40)

ax1.plot(x, y, color='r', label=u"観測最大RSSIに関する誤差特性")

'''
ax2 = ax1.twinx()
ax2.set_ylabel(u"観測最大RSSIに関する誤差特性のパラメータ値", color='r')
ax2.set_ylim(0, 60)
ax2.set_xlim(-100, -40)
'''


plt.legend()

plt.rcParams['font.size'] = 15
plt.savefig('rssi_scatter.eps', transparent=True)