# coding=utf-8
import matplotlib as mpl
import matplotlib.pyplot as plt
from math import *

mpl.use('Agg')

#name = ["using raw geomagnetism mean error", "using raw geomagnetism median error",
#"using processed geomagnetism mean error", "using processed geomagnetism median error"]

#method mean comparison
#y = [[7.2475851423911646, 7.893040551285015, 8.9301944946379255, 11.226374567953185], [5.9574510712679265, 7.8078397335249869, 7.997463848136098, 10.571461213803353], [8.8475408231523609, 8.6648445597914403, 9.2849842821090789, 9.5703690875131571], [6.9080415897430871, 7.414259944895365, 8.5360392937949872, 10.760854564310369]]

#method median comparison
y = [[2.8714787227491931, 3.0707813563293485, 3.2612962909541992, 4.8270989709215248], [3.0, 3.0, 4.0, 5.0], [5.6366488405980482, 5.0442486501405188, 6.7464763623217445, 5.0110987927909694], [3.4801021696368521, 3.5668629492037822, 4.4532104320516845, 5.2832590413241212]]

#geo median & mean comparison
#y = [[8.85, 7.54, 8.67, 9.67, 26.0], [5.63, 4.38, 5.43, 7.03, 25.67], [11.54, 10.14, 10.95, 11.01, 26.0], [7.60, 7.50, 8.08, 8.67, 24.69]]

# mpl.rcParams['font.family'] = 'Osaka'


#method comp
x = [0, 25, 50, 75]
m_size = [12, 12, 16, 12]
l_width = [2, 2, 2, 5]
character = ['-s', '-^', '-o', '-D']
name = [u"Wi-Fi FP", u"WaMM", u"地磁気FP", u"提案手法"]


#geo comp
#x = [0, 25, 50, 75, 100]
#m_size = [12, 12, 12, 12]
#l_width = [2, 2, 2, 2]
#character = ['-rs', '--rs', '-b^', '--b^']
#plt.xlim([0, 100])
#name = [u"無加工地磁気データ 平均値", u"無加工地磁気データ 中央値", u"加工地磁気データ 平均値", u"加工地磁気データ 中央値"]

plt.figure(figsize=(10, 5.3))

for i in range(len(y)):
    plt.plot(x, y[i], character[i], linewidth=l_width[i], markersize=m_size[i])

plt.xlabel(u"BSSID削減率[%]", fontsize=18)
plt.ylabel(u"測位誤差[m]", fontsize=18)

plt.minorticks_on()
plt.grid(which='both')
plt.legend(name, loc='upper left', handlelength=2.5)

plt.xlim([0, 75])


plt.savefig(u"method_comp_median", transparent=True)
#plt.savefig(u"geo_prm", transparent=True)