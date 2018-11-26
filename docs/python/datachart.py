import re
from pyecharts import Bar,Line,Overlap,Grid
with open('1.txt','r') as f:
    content=[]
    time=[]
    gscn=[]
    rate=[]
    headroom=[]
    for line in f.readlines():
        row=' '.join(line.split())
        row_after = row.strip().split(" ")
        content.append(row_after)
    del content[0:2]
    new_cont=content
    new_cont.pop()
    for i in range(len(new_cont)):
        time.append(new_cont[i][0])
        gscn.append(new_cont[i][1])
        rate.append(new_cont[i][2])
        headroom.append(new_cont[i][3])




line1 = Line()

line1.add("headroom", time, headroom,yaxis_min=1000,
        yaxis_interval=1000, yaxis_max=3000,xaxis_rotate=45,is_datazoom_show=True,xaxis_label_textsize=10,legend_top="top")

line2 = Line()
line2.add("rate", time, rate, yaxis_formatter="%",xaxis_rotate=45,xaxis_label_textsize=10,legend_top="top")

overlap = Overlap(width=1200, height=700)
overlap.add(line1)
overlap.add(line2, yaxis_index=1, is_add_yaxis=True)
overlap.render()

