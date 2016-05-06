# coding=utf-8
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as tick
import numpy as np
from math import *
import matplotlib.font_manager
from matplotlib.font_manager import FontProperties
from matplotlib.backends.backend_pdf import PdfPages

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

# for Mac
font_path = '/Library/Fonts/Osaka.ttf'

fig, ax = plt.subplots()
# f.set_label(u"[m]")

ind = np.arange(4)
width = 0.20

#method_name = [u"Wi-Fi FP", u"WaMM", u"地磁気FP", u"提案手法"]
method_color = ['b', 'g', 'r', 'c']

# 許容誤差5m
#data = [[53.93258426966292, 43.82022471910113, 46.06741573033708, 62.92134831460674], [51.68539325842697, 44.9438202247191, 48.31460674157304, 62.92134831460674], [43.82022471910113, 35.95505617977528, 43.82022471910113, 51.68539325842697], [30.337078651685395, 28.08988764044944, 49.43820224719101, 48.31460674157304]]
# 許容誤差3m
#data = [[38.20224719101123, 35.95505617977528, 28.08988764044944, 42.69662921348314], [33.70786516853933, 32.58426966292135, 25.842696629213485, 39.325842696629216], [29.213483146067414, 24.719101123595504, 26.96629213483146, 35.95505617977528], [23.595505617977526, 24.719101123595504, 31.46067415730337, 28.08988764044944]]
# 許容誤差2m

# Other Route ver.
# 許容誤差5m
#data = [[48.31460674157304, 48.31460674157304, 43.82022471910113, 51.68539325842697], [47.19101123595505, 44.9438202247191, 42.69662921348314, 49.43820224719101], [37.07865168539326, 39.325842696629216, 43.82022471910113, 49.43820224719101], [22.47191011235955, 19.101123595505616, 39.325842696629216, 26.96629213483146]]
# 許容誤差3m
data = [[34.831460674157306, 37.07865168539326, 31.46067415730337, 39.325842696629216], [34.831460674157306, 37.07865168539326, 26.96629213483146, 39.325842696629216], [26.96629213483146, 29.213483146067414, 34.831460674157306, 33.70786516853933], [16.853932584269664, 14.606741573033707, 31.46067415730337, 24.719101123595504]]



data_t = np.array(data).transpose()

#mpl.rcParams['font.family'] = 'Osaka'

rects = []

for i in range(4):
    rect = ax.bar(ind+i*width, data_t[i], width=width, align='center', alpha=0.4, color=method_color[i])
    rects.append(rect)


def autolabel(rects):
    # attach some text labels
    for rect in rects:
        height = rect.get_height()
        ax.text(rect.get_x() + rect.get_width()/2., 1.05*height,
                '%d' % int(height),
                ha='center', va='bottom')


autolabel(rects[0])
autolabel(rects[1])
autolabel(rects[2])
autolabel(rects[3])

ax.set_xticks(ind + 1.5*width)
ax.set_xticklabels([0, 25, 50, 75])

ax.legend(rects, (u"Wi-Fi FP", u"WaMM", u"地磁気FP", u"提案手法"))

fig.set_size_inches(10, 6)

plt.grid()
plt.minorticks_on()

plt.ylim([0, 100])
plt.xlabel(u"BSSID削減率[%]", fontsize=18)
plt.ylabel(u"測位誤差が3m以下となる確率[%]", fontsize=18)

plt.savefig(u"Other_3m_convergence_evaluation", transparent=True)