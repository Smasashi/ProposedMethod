import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import matplotlib as mpl
import matplotlib.cm as cm
import numpy as np

def display_bssid_distribution(bssid, fp_con):
    fingerprint_bssid_bind = ""

    for i in bssid:
        fingerprint_bssid_bind += "\"" + i + "\","

    pos_includes_bssid = fp_con.execute(
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