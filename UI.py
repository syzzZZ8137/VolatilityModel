# -*- coding: utf-8 -*-
"""
Created on Tue Jan  9 14:27:27 2018

@author: shzb-200620
"""

from tkinter import *
import tkinter as tk
from tkinter import ttk
import tkinter.font as tkFont
import TimeSeriesInterpolator
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  
from matplotlib.figure import Figure  
import numpy as np
import pandas as pd
from mpl_toolkits.mplot3d import Axes3D

def pack(all_entry):
    
    benchmark = pd.DataFrame({'f_atm':[float(all_entry[4].get()),float(all_entry[5].get()),float(all_entry[6].get()),float(all_entry[7].get())], \
                          'days':[float(all_entry[0].get()),float(all_entry[1].get()),float(all_entry[2].get()),float(all_entry[3].get())], \
                          'alpha':[float(all_entry[8].get()),float(all_entry[9].get()),float(all_entry[10].get()),float(all_entry[11].get())],\
                          'f_ref':[float(all_entry[12].get()),float(all_entry[13].get()),float(all_entry[14].get()),float(all_entry[15].get())],\
                          'SSR':[float(all_entry[16].get()),float(all_entry[17].get()),float(all_entry[18].get()),float(all_entry[19].get())],\
                          'vol_ref':[float(all_entry[20].get()),float(all_entry[21].get()),float(all_entry[22].get()),float(all_entry[23].get())],\
                          'VCR':[float(all_entry[24].get()),float(all_entry[25].get()),float(all_entry[26].get()),float(all_entry[27].get())],\
                          'slope_ref':[float(all_entry[28].get()),float(all_entry[29].get()),float(all_entry[30].get()),float(all_entry[31].get())], \
                          'SCR':[float(all_entry[32].get()),float(all_entry[33].get()),float(all_entry[34].get()),float(all_entry[35].get())],\
                          'dn_cf':[float(all_entry[36].get()),float(all_entry[37].get()),float(all_entry[38].get()),float(all_entry[39].get())],\
                          'up_cf':[float(all_entry[40].get()),float(all_entry[41].get()),float(all_entry[42].get()),float(all_entry[43].get())], \
                          'put_curv':[float(all_entry[44].get()),float(all_entry[45].get()),float(all_entry[46].get()),float(all_entry[47].get())], \
                          'call_curv':[float(all_entry[48].get()),float(all_entry[49].get()),float(all_entry[50].get()),float(all_entry[51].get())],\
                          'dn_sm':[float(all_entry[52].get()),float(all_entry[53].get()),float(all_entry[54].get()),float(all_entry[55].get())],\
                          'up_sm':[float(all_entry[56].get()),float(all_entry[57].get()),float(all_entry[58].get()),float(all_entry[59].get())],\
                          'dn_slope':[float(all_entry[60].get()),float(all_entry[61].get()),float(all_entry[62].get()),float(all_entry[63].get())], \
                          'up_slope':[float(all_entry[64].get()),float(all_entry[65].get()),float(all_entry[66].get()),float(all_entry[67].get())]})
    
    return benchmark

def drawPic(all_entry):
    drawPic_2D(all_entry)
    drawPic_3D(all_entry)
    

def drawPic_2D(all_entry):
    
    #清空图像，以使得前后两次绘制的图像不会重叠  
    drawPic_2D.f.clf()  
    drawPic_2D.a=drawPic_2D.f.add_subplot(111)  
         
    #在[0,100]范围内随机生成sampleCount个数据点  
    benchmark = pack(all_entry)
    
    fatm1 = max(benchmark.loc[:,'f_atm'])
    fref1 = max(benchmark.loc[:,'f_ref'])
    fatm2 = min(benchmark.loc[:,'f_atm'])
    fref2 = min(benchmark.loc[:,'f_ref'])
    
    up = max(fatm1,fref1)*2
    down = min(fatm2,fref2)*0.5
    strike_lst = list(np.arange(down,up,(up-down)/100))
    
    res = pd.DataFrame()
    benchmark.index = [0,0,0,0]
    #print(benchmark)
    
    for eachtime in benchmark.loc[:,'days'].tolist():
        
        in_put = {'TimeToMaturity':eachtime,'strike':strike_lst}
        tmp = TimeSeriesInterpolator.time_interpolate(benchmark,in_put)
        tmp.set_index('strike',inplace=True)
        tmp.columns = ['vol_%ddays'%eachtime]
        res = pd.concat([res,tmp], axis=1, join_axes=[tmp.index])
    #print(res)
    legend=[]
    i = 0
    
    for each in res.columns:
        drawPic_2D.a.plot(res.index,res.loc[:,each],'-',linewidth=2,markersize=10)
        legend.append(each)
        i+=1
        
    drawPic_2D.a.grid(color='black',linestyle='--',linewidth=0.5)
    drawPic_2D.a.legend(legend,fontsize=8)
    
    drawPic_2D.canvas.show()

   
def drawPic_3D(all_entry):
    
    #清空图像，以使得前后两次绘制的图像不会重叠  
    pass
#    drawPic_3D.f.clf()  
#    drawPic_3D.a = drawPic_3D.f.add_subplot(111)  
#    fig = plt.figure()
#    ax = Axes3D(fig)
#    X = np.arange(-4, 4, 0.25)
#    Y = np.arange(-4, 4, 0.25)
#    X, Y = np.meshgrid(X, Y)
#    R = np.sqrt(X**2 + Y**2)
#    Z = np.sin(R)
#    #drawPic_3D.a.plot(X,Y,Z)
#    # 具体函数方法可用 help(function) 查看，如：help(ax.plot_surface)
#    ax.plot_surface(X, Y, Z, rstride=1, cstride=1, cmap='rainbow')
#    #ax = plt.plot(X,Y)
#    
#    drawPic_3D.a.figure = ax.figure
#    drawPic_3D.canvas.show()
    
    


def cal():

    root = Tk()
    
    root.title("波动率曲线模型")  
    #root.resizable(0,0)  
    #root.geometry('1500x1000')
    button_font = tkFont.Font(size=12, weight=tkFont.BOLD)  
    button_bg = '#D5E0EE'  
    button_active_bg = '#E5E35B'
    label_font = tkFont.Font(size=10, weight=tkFont.BOLD)
    entry_font = tkFont.Font(size=9)
    
    label_lst = ['到期时间(天)','f_atm', 'alpha', 'f_ref', 'SSR',\
                 'vol_ref', 'VCR', 'slope_ref', 'SCR','dn_cf', 'up_cf', 'put_curv', 'call_curv',\
                 'dn_sm', 'up_sm', 'dn_slope', 'up_slope']
    
    label = Label(root,justify="left", text='BenchMark1', fg='blue',bg=button_bg, padx=10, pady=3,\
                      activebackground = button_active_bg,font=label_font)
    label.grid(row=0, column=1, columnspan=1, sticky=W+E, padx=10,  pady=5)
    
    
    label = Label(root,justify="left", text='BenchMark2', fg='blue',bg=button_bg, padx=10, pady=3,\
                      activebackground = button_active_bg,font=label_font)
    label.grid(row=0, column=2, columnspan=1, sticky=W+E, padx=10,  pady=5)
    
    
    label = Label(root,justify="left", text='BenchMark3', fg='blue',bg=button_bg, padx=10, pady=3,\
                      activebackground = button_active_bg,font=label_font)
    label.grid(row=0, column=3, columnspan=1, sticky=W+E, padx=10,  pady=5)
    
    label = Label(root,justify="left", text='BenchMark4', fg='blue',bg=button_bg, padx=10, pady=3,\
                      activebackground = button_active_bg,font=label_font)
    label.grid(row=0, column=4, columnspan=1, sticky=W+E, padx=10,  pady=5)
    
    label = Label(root,justify="left", text='2维波动率曲线', fg='blue',bg=button_bg, padx=10, pady=3,\
                      activebackground = button_active_bg,font=label_font)
    label.grid(row=0,column=5,rowspan=1,columnspan=4)
    
    label = Label(root,justify="left", text='3维波动率曲线', fg='blue',bg=button_bg, padx=10, pady=3,\
                      activebackground = button_active_bg,font=label_font)
    label.grid(row=10,column=5,rowspan=1,columnspan=4)
    
    i = 1
    for each in label_lst:
        
        label = Label(root,justify="left", text=each, fg='blue',bg=button_bg, padx=10, pady=3,\
                          activebackground = button_active_bg,font=label_font)
        label.grid(row=i, column=0, columnspan=1, sticky=W+E, padx=50,  pady=5)
        i+=1
    
    
    entry11 = Entry(root, justify="right", font=entry_font,width=10)
    entry11.grid(row=1, column=1, columnspan=1, sticky=W, padx=30,  pady=5)  
    entry11.insert(0,'1')
    
    entry12 = Entry(root, justify="right", font=entry_font,width=10)
    entry12.grid(row=1, column=2, columnspan=1, sticky=W, padx=30,  pady=5)  
    entry12.insert(0,'60')
    
    entry13 = Entry(root, justify="right", font=entry_font,width=10)
    entry13.grid(row=1, column=3, columnspan=1, sticky=W, padx=30,  pady=5)  
    entry13.insert(0,'120')
    
    entry14 = Entry(root, justify="right", font=entry_font,width=10)
    entry14.grid(row=1, column=4, columnspan=1, sticky=W, padx=30,  pady=5)  
    entry14.insert(0,'180')
    
    entry21 = Entry(root, justify="right", font=entry_font,width=10)
    entry21.grid(row=2, column=1, columnspan=1, sticky=W, padx=30,  pady=5)  
    entry21.insert(0,'2700')
    
    entry22 = Entry(root, justify="right", font=entry_font,width=10)
    entry22.grid(row=2, column=2, columnspan=1, sticky=W, padx=30,  pady=5)  
    entry22.insert(0,'2700')
    
    entry23 = Entry(root, justify="right", font=entry_font,width=10)
    entry23.grid(row=2, column=3, columnspan=1, sticky=W, padx=30,  pady=5)  
    entry23.insert(0,'2700')
    
    entry24 = Entry(root, justify="right", font=entry_font,width=10)
    entry24.grid(row=2, column=4, columnspan=1, sticky=W, padx=30,  pady=5)  
    entry24.insert(0,'2700')
    
    entry31 = Entry(root, justify="right", font=entry_font,width=10)
    entry31.grid(row=3, column=1, columnspan=1, sticky=W, padx=30,  pady=5)  
    entry31.insert(0,'0')
    
    entry32 = Entry(root, justify="right", font=entry_font,width=10)
    entry32.grid(row=3, column=2, columnspan=1, sticky=W, padx=30,  pady=5)  
    entry32.insert(0,'0')
    
    entry33 = Entry(root, justify="right", font=entry_font,width=10)
    entry33.grid(row=3, column=3, columnspan=1, sticky=W, padx=30,  pady=5)  
    entry33.insert(0,'0')
    
    entry34 = Entry(root, justify="right", font=entry_font,width=10)
    entry34.grid(row=3, column=4, columnspan=1, sticky=W, padx=30,  pady=5)  
    entry34.insert(0,'0')
    
    entry41 = Entry(root, justify="right", font=entry_font,width=10)
    entry41.grid(row=4, column=1, columnspan=1, sticky=W, padx=30,  pady=5)  
    entry41.insert(0,'2780')
    
    entry42 = Entry(root, justify="right", font=entry_font,width=10)
    entry42.grid(row=4, column=2, columnspan=1, sticky=W, padx=30,  pady=5)  
    entry42.insert(0,'2780')
    
    entry43 = Entry(root, justify="right", font=entry_font,width=10)
    entry43.grid(row=4, column=3, columnspan=1, sticky=W, padx=30,  pady=5)  
    entry43.insert(0,'2780')
    
    entry44 = Entry(root, justify="right", font=entry_font,width=10)
    entry44.grid(row=4, column=4, columnspan=1, sticky=W, padx=30,  pady=5)  
    entry44.insert(0,'2780')
    
    entry51 = Entry(root, justify="right", font=entry_font,width=10)
    entry51.grid(row=5, column=1, columnspan=1, sticky=W, padx=30,  pady=5)  
    entry51.insert(0,'50')
    
    entry52 = Entry(root, justify="right", font=entry_font,width=10)
    entry52.grid(row=5, column=2, columnspan=1, sticky=W, padx=30,  pady=5)  
    entry52.insert(0,'50')
    
    entry53 = Entry(root, justify="right", font=entry_font,width=10)
    entry53.grid(row=5, column=3, columnspan=1, sticky=W, padx=30,  pady=5)  
    entry53.insert(0,'50')
    
    entry54 = Entry(root, justify="right", font=entry_font,width=10)
    entry54.grid(row=5, column=4, columnspan=1, sticky=W, padx=30,  pady=5)  
    entry54.insert(0,'50')
    
    entry61 = Entry(root, justify="right", font=entry_font,width=10)
    entry61.grid(row=6, column=1, columnspan=1, sticky=W, padx=30,  pady=5)  
    entry61.insert(0,'0.125')
    
    entry62 = Entry(root, justify="right", font=entry_font,width=10)
    entry62.grid(row=6, column=2, columnspan=1, sticky=W, padx=30,  pady=5)  
    entry62.insert(0,'0.125')
    
    entry63 = Entry(root, justify="right", font=entry_font,width=10)
    entry63.grid(row=6, column=3, columnspan=1, sticky=W, padx=30,  pady=5)  
    entry63.insert(0,'0.125')
    
    entry64 = Entry(root, justify="right", font=entry_font,width=10)
    entry64.grid(row=6, column=4, columnspan=1, sticky=W, padx=30,  pady=5)  
    entry64.insert(0,'0.125')
    
    entry71 = Entry(root, justify="right", font=entry_font,width=10)
    entry71.grid(row=7, column=1, columnspan=1, sticky=W, padx=30,  pady=5)  
    entry71.insert(0,'0')
    
    entry72 = Entry(root, justify="right", font=entry_font,width=10)
    entry72.grid(row=7, column=2, columnspan=1, sticky=W, padx=30,  pady=5)  
    entry72.insert(0,'0')
    
    entry73 = Entry(root, justify="right", font=entry_font,width=10)
    entry73.grid(row=7, column=3, columnspan=1, sticky=W, padx=30,  pady=5)  
    entry73.insert(0,'0')
    
    entry74 = Entry(root, justify="right", font=entry_font,width=10)
    entry74.grid(row=7, column=4, columnspan=1, sticky=W, padx=30,  pady=5)  
    entry74.insert(0,'0')
    
    entry81 = Entry(root, justify="right", font=entry_font,width=10)
    entry81.grid(row=8, column=1, columnspan=1, sticky=W, padx=30,  pady=5)  
    entry81.insert(0,'0.38')
    
    entry82 = Entry(root, justify="right", font=entry_font,width=10)
    entry82.grid(row=8, column=2, columnspan=1, sticky=W, padx=30,  pady=5)  
    entry82.insert(0,'0.38')
    
    entry83 = Entry(root, justify="right", font=entry_font,width=10)
    entry83.grid(row=8, column=3, columnspan=1, sticky=W, padx=30,  pady=5)  
    entry83.insert(0,'0.38')
    
    entry84 = Entry(root, justify="right", font=entry_font,width=10)
    entry84.grid(row=8, column=4, columnspan=1, sticky=W, padx=30,  pady=5)  
    entry84.insert(0,'0.38')
    
    entry91 = Entry(root, justify="right", font=entry_font,width=10)
    entry91.grid(row=9, column=1, columnspan=1, sticky=W, padx=30,  pady=5)  
    entry91.insert(0,'0')
    
    entry92 = Entry(root, justify="right", font=entry_font,width=10)
    entry92.grid(row=9, column=2, columnspan=1, sticky=W, padx=30,  pady=5)  
    entry92.insert(0,'0')
    
    entry93 = Entry(root, justify="right", font=entry_font,width=10)
    entry93.grid(row=9, column=3, columnspan=1, sticky=W, padx=30,  pady=5)  
    entry93.insert(0,'0')
    
    entry94 = Entry(root, justify="right", font=entry_font,width=10)
    entry94.grid(row=9, column=4, columnspan=1, sticky=W, padx=30,  pady=5)  
    entry94.insert(0,'0')
    
    entry101 = Entry(root, justify="right", font=entry_font,width=10)
    entry101.grid(row=10, column=1, columnspan=1, sticky=W, padx=30,  pady=5)  
    entry101.insert(0,'-0.052')
    
    entry102 = Entry(root, justify="right", font=entry_font,width=10)
    entry102.grid(row=10, column=2, columnspan=1, sticky=W, padx=30,  pady=5)  
    entry102.insert(0,'-0.052')
    
    entry103 = Entry(root, justify="right", font=entry_font,width=10)
    entry103.grid(row=10, column=3, columnspan=1, sticky=W, padx=30,  pady=5)  
    entry103.insert(0,'-0.052')
    
    entry104 = Entry(root, justify="right", font=entry_font,width=10)
    entry104.grid(row=10, column=4, columnspan=1, sticky=W, padx=30,  pady=5)  
    entry104.insert(0,'-0.052')
    
    entry111 = Entry(root, justify="right", font=entry_font,width=10)
    entry111.grid(row=11, column=1, columnspan=1, sticky=W, padx=30,  pady=5)  
    entry111.insert(0,'0.055')
    
    entry112 = Entry(root, justify="right", font=entry_font,width=10)
    entry112.grid(row=11, column=2, columnspan=1, sticky=W, padx=30,  pady=5)  
    entry112.insert(0,'0.055')
    
    entry113 = Entry(root, justify="right", font=entry_font,width=10)
    entry113.grid(row=11, column=3, columnspan=1, sticky=W, padx=30,  pady=5)  
    entry113.insert(0,'0.055')
    
    entry114 = Entry(root, justify="right", font=entry_font,width=10)
    entry114.grid(row=11, column=4, columnspan=1, sticky=W, padx=30,  pady=5)  
    entry114.insert(0,'0.055')
    
    entry121 = Entry(root, justify="right", font=entry_font,width=10)
    entry121.grid(row=12, column=1, columnspan=1, sticky=W, padx=30,  pady=5)  
    entry121.insert(0,'2.1')
    
    entry122 = Entry(root, justify="right", font=entry_font,width=10)
    entry122.grid(row=12, column=2, columnspan=1, sticky=W, padx=30,  pady=5)  
    entry122.insert(0,'2.1')
    
    entry123 = Entry(root, justify="right", font=entry_font,width=10)
    entry123.grid(row=12, column=3, columnspan=1, sticky=W, padx=30,  pady=5)  
    entry123.insert(0,'2.1')
    
    entry124 = Entry(root, justify="right", font=entry_font,width=10)
    entry124.grid(row=12, column=4, columnspan=1, sticky=W, padx=30,  pady=5)  
    entry124.insert(0,'2.1')
    
    entry131 = Entry(root, justify="right", font=entry_font,width=10)
    entry131.grid(row=13, column=1, columnspan=1, sticky=W, padx=30,  pady=5)  
    entry131.insert(0,'-2.3')
    
    entry132 = Entry(root, justify="right", font=entry_font,width=10)
    entry132.grid(row=13, column=2, columnspan=1, sticky=W, padx=30,  pady=5)  
    entry132.insert(0,'-2.3')
    
    entry133 = Entry(root, justify="right", font=entry_font,width=10)
    entry133.grid(row=13, column=3, columnspan=1, sticky=W, padx=30,  pady=5)  
    entry133.insert(0,'-2.3')
    
    entry134 = Entry(root, justify="right", font=entry_font,width=10)
    entry134.grid(row=13, column=4, columnspan=1, sticky=W, padx=30,  pady=5)  
    entry134.insert(0,'-2.3')
    
    entry141 = Entry(root, justify="right", font=entry_font,width=10)
    entry141.grid(row=14, column=1, columnspan=1, sticky=W, padx=30,  pady=5)  
    entry141.insert(0,'1')
    
    entry142 = Entry(root, justify="right", font=entry_font,width=10)
    entry142.grid(row=14, column=2, columnspan=1, sticky=W, padx=30,  pady=5)  
    entry142.insert(0,'1')
    
    entry143 = Entry(root, justify="right", font=entry_font,width=10)
    entry143.grid(row=14, column=3, columnspan=1, sticky=W, padx=30,  pady=5)  
    entry143.insert(0,'1')
    
    entry144 = Entry(root, justify="right", font=entry_font,width=10)
    entry144.grid(row=14, column=4, columnspan=1, sticky=W, padx=30,  pady=5)  
    entry144.insert(0,'1')
    
    entry151 = Entry(root, justify="right", font=entry_font,width=10)
    entry151.grid(row=15, column=1, columnspan=1, sticky=W, padx=30,  pady=5)  
    entry151.insert(0,'1')
    
    entry152 = Entry(root, justify="right", font=entry_font,width=10)
    entry152.grid(row=15, column=2, columnspan=1, sticky=W, padx=30,  pady=5)  
    entry152.insert(0,'1')
    
    entry153 = Entry(root, justify="right", font=entry_font,width=10)
    entry153.grid(row=15, column=3, columnspan=1, sticky=W, padx=30,  pady=5)  
    entry153.insert(0,'1')
    
    entry154 = Entry(root, justify="right", font=entry_font,width=10)
    entry154.grid(row=15, column=4, columnspan=1, sticky=W, padx=30,  pady=5)  
    entry154.insert(0,'1')
    
    entry161 = Entry(root, justify="right", font=entry_font,width=10)
    entry161.grid(row=16, column=1, columnspan=1, sticky=W, padx=30,  pady=5)  
    entry161.insert(0,'0.001')
    
    entry162 = Entry(root, justify="right", font=entry_font,width=10)
    entry162.grid(row=16, column=2, columnspan=1, sticky=W, padx=30,  pady=5)  
    entry162.insert(0,'0.001')
    
    entry163 = Entry(root, justify="right", font=entry_font,width=10)
    entry163.grid(row=16, column=3, columnspan=1, sticky=W, padx=30,  pady=5)  
    entry163.insert(0,'0.001')
    
    entry164 = Entry(root, justify="right", font=entry_font,width=10)
    entry164.grid(row=16, column=4, columnspan=1, sticky=W, padx=30,  pady=5)  
    entry164.insert(0,'0.001')
    
    entry171 = Entry(root, justify="right", font=entry_font,width=10)
    entry171.grid(row=17, column=1, columnspan=1, sticky=W, padx=30,  pady=5)  
    entry171.insert(0,'0.001')
    
    entry172 = Entry(root, justify="right", font=entry_font,width=10)
    entry172.grid(row=17, column=2, columnspan=1, sticky=W, padx=30,  pady=5)  
    entry172.insert(0,'0.001')
    
    entry173 = Entry(root, justify="right", font=entry_font,width=10)
    entry173.grid(row=17, column=3, columnspan=1, sticky=W, padx=30,  pady=5)  
    entry173.insert(0,'0.001')
    
    entry174 = Entry(root, justify="right", font=entry_font,width=10)
    entry174.grid(row=17, column=4, columnspan=1, sticky=W, padx=30,  pady=5)  
    entry174.insert(0,'0.001')
    
    all_entry = [entry11,entry12,entry13,entry14,entry21,entry22,entry23,entry24,\
                 entry31,entry32,entry33,entry34,entry41,entry42,entry43,entry44,\
                 entry51,entry52,entry53,entry54,entry61,entry62,entry63,entry64,\
                 entry71,entry72,entry73,entry74,entry81,entry82,entry83,entry84,\
                 entry91,entry92,entry93,entry94,entry101,entry102,entry103,entry104,\
                 entry111,entry112,entry113,entry114,entry121,entry122,entry123,entry124,\
                 entry131,entry132,entry133,entry134,entry141,entry142,entry143,entry144,\
                 entry151,entry152,entry153,entry154,entry161,entry162,entry163,entry164,\
                 entry171,entry172,entry173,entry174]

    
    drawPic_2D.f = Figure(figsize=(6,4), dpi=100)
    drawPic_2D.canvas = FigureCanvasTkAgg(drawPic_2D.f, master=root)
    drawPic_2D.canvas.show()
    drawPic_2D.canvas.get_tk_widget().grid(row=1,column=5,rowspan=9,columnspan=4)
    
    drawPic_3D.f = Figure(figsize=(6,4), dpi=100)
    drawPic_3D.canvas = FigureCanvasTkAgg(drawPic_3D.f, master=root)
    drawPic_3D.canvas.show()
    drawPic_3D.canvas.get_tk_widget().grid(row=11,column=5,rowspan=9,columnspan=4)
    
    Button(root,text='输出',bg=button_bg, padx=50, pady=3,font=button_font,fg='green',\
           command=lambda : drawPic(all_entry), activebackground = button_active_bg).grid(row=18,column=1,rowspan=1,columnspan=4)
    #启动事件循环  
    
    root.mainloop()
    
if __name__ == '__main__':  
    cal()
    
    
