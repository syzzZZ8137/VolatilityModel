# -*- coding: utf-8 -*-
"""
Created on Thu May 24 15:14:42 2018

@author: Jax_GuoSen
"""

from tkinter import *
import tkinter as tk
from tkinter import ttk
import tkinter.font as tkFont
import TimeSeriesInterpolator
import VolatilityModelBase
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  
from matplotlib.figure import Figure  
import numpy as np
import pandas as pd
from mpl_toolkits.mplot3d import Axes3D
import GetDataMySQL
import os
import pandas as pd
import sys
import matplotlib.patches as mpatches
import ChangeParamData
import GetUnderling

#%%
def clear(entry):
    entry.delete(0, END)
#%%
def selection():
    global is_sell,is_buy,is_mid,var_lst,is_day
    is_sell = var2.get()
    is_buy = var1.get()
    is_mid = var3.get()
    is_day = []
    for i in range(len(var_lst)):
        is_day.append(var_lst[i].get())
    save(0)
    #print(is_day)
#%%买卖价差设置
def BAspread(df,param_list):
    para = param_list[param_list['Group']=='Volatility Settings']['DBparaname'].dropna().tolist()
    buy_sell_para = df.copy()
    for each in para:
        buy_sell_para[each] = df[each+'_offset']
        
    return buy_sell_para
#%%
def cal(db):
    #print(db)
    f_atm = float(F_atm.get())
    db['f_atm'] = f_atm #后接入数据库数据
    benchmark = db[['alpha','f_atm','f_ref','ssr','vol_ref','vcr',\
                         'slope_ref','scr','dn_cf','up_cf','call_curv',\
                         'dn_sm','up_sm','dn_slope','up_slope','put_curv','day']]
    
    
    benchmark.index = [0]*len(benchmark)

    strike_lst = VolatilityModelBase.VolatilityModelBase().create_strike_price_list( f_atm, int(x_n.get()), int(x_inc.get()))
    
    T_lst = (benchmark.loc[:,'day']).tolist()  #保证benchmark有
    T_lst.sort()
    
    #做调整，把勾选的date筛入
    benchmark_new = pd.DataFrame()
    T_lst_new = []
    #print(benchmark)
    for i in range(len(is_day)):
        if is_day[i] == 1:
            tmp = benchmark[benchmark['day']==float(T_lst[i])]
            benchmark_new = benchmark_new.append(tmp)
            T_lst_new.append(T_lst[i])
    
    benchmark = benchmark_new
    T_lst = T_lst_new

    interpoints = TimeSeriesInterpolator.benchmark_interpoints(strike_lst,benchmark)
    for eachtime in T_lst:
        IP = interpoints.loc[eachtime,'interpoints']
        for i in range(len(IP)):
            if IP.loc[i,'strike']<min(strike_lst) or IP.loc[i,'strike']>max(strike_lst):
                IP.drop(i,inplace=True)
    
    
    res = pd.DataFrame()
    res3D = pd.DataFrame()
    for eachtime in T_lst:
        in_put2 = {'TimeToMaturity':eachtime,'strike':strike_lst}
        tmp = TimeSeriesInterpolator.time_interpolate(benchmark,in_put2)
        
        tmp.set_index('strike',inplace=True)
        tmp.columns = ['vol_%ddays'%eachtime]
        res3D = pd.concat([res3D,tmp], axis=1, join_axes=[tmp.index])
        
        IP = interpoints.loc[eachtime,'interpoints'].copy()      #2D图至少保证曲线中有5个点插值点
        IP.set_index('strike',inplace=True)
        IP.columns = ['vol_%ddays'%eachtime]
        
        tmp = tmp.append(IP)
        tmp = tmp.sort_index()
        
        res = pd.concat([res,tmp], axis=1, join_axes=[tmp.index])
        
    
    
    return res,res3D,interpoints,strike_lst,T_lst,benchmark
    
def cal_surface():
    global temp_db,buy_sell_para,temp_db_ref,buy_sell_para_ref
    #print(temp_db)
    res,res3D,interpoints,strike_lst,T_lst,benchmark = cal(temp_db)
    res_bs,res3D_bs,interpoints_bs,strike_lst,T_lst,benchmark_b = cal(buy_sell_para)
    
    res_ref,res3D_ref,interpoints_ref,strike_lst,T_lst,benchmark_ref = cal(temp_db_ref)
    res_ref_bs,res3D_ref_bs,interpoints_bs_ref,strike_lst,T_lst,benchmark_b_ref = cal(buy_sell_para_ref)
    
    res_b = res - res_bs
    res_s = res + res_bs
    res3D_b = res3D - res3D_bs
    res3D_s = res3D + res3D_bs
    
    res_ref_b = res_ref - res_ref_bs
    res_ref_s = res_ref + res_ref_bs
    res3D_ref_b = res3D_ref - res3D_ref_bs
    res3D_ref_s = res3D_ref + res3D_ref_bs
    #print(res_b)
    return res,res_b,res_s,res_ref,res_ref_b,res_ref_s,strike_lst,T_lst,benchmark['f_atm'].values[0],interpoints,interpoints_ref,res3D,res3D_b,\
res3D_s,res3D_ref,res3D_ref_b,res3D_ref_s

    
    

def drawPic(event):
    #%%
    global x_axischosen
    sig = x_axischosen.get()
    drawPic_2D(sig)
    drawPic_3D(sig)
    
def drawPic_2D(sig):
    
    
    res,res_b,res_s,res_ref,res_ref_b,res_ref_s,strike_lst,T_lst,f_atm,interpoints,interpoints_ref,res3D,res3D_b,\
res3D_s,res3D_ref,res3D_ref_b,res3D_ref_s = cal_surface()
    
    res_b = res_b.dropna()
    res_s = res_s.dropna()
    res_ref_b = res_ref_b.dropna()
    res_ref_s = res_ref_s.dropna()
    #print(1)
    #清空图像，以使得前后两次绘制的图像不会重叠 
    drawPic_2D.f.clf()  
    drawPic_2D.a=drawPic_2D.f.add_subplot(111) 
    
    legend=[]
    
    if sig == 'Log-Moneyness':
        res.index = np.log(res.index/f_atm)
        res_b.index = np.log(res_b.index/f_atm)
        res_s.index = np.log(res_s.index/f_atm)
        res_ref.index = np.log(res_ref.index/f_atm)
        res_ref_b.index = np.log(res_ref_b.index/f_atm)
        res_ref_s.index = np.log(res_ref_s.index/f_atm)
        for each in interpoints['interpoints'].tolist():
            each['strike'] = np.log(each['strike']/f_atm)
            
        for each in interpoints_ref['interpoints'].tolist():
            each['strike'] = np.log(each['strike']/f_atm)
        #for each in interpoints_b['interpoints'].tolist():
            #each['strike'] = np.log(each['strike']/f_atm)
        #for each in interpoints_s['interpoints'].tolist():
            #each['strike'] = np.log(each['strike']/f_atm)
        
        
        drawPic_2D.a.set_xlabel(sig)
        
    elif sig == 'Strike Price':
        drawPic_2D.a.set_xlabel(sig)
    else:
        pass
    
    cmap = ['blue','green','red','black','magenta','yellow','cyan']
    patch=[]
    i = 0
    #print(res)
    for each in res.columns:
        day = int(each[4:-4])
        legend.append(each)
        if is_mid == 1:
            drawPic_2D.a.plot(res.index,res.loc[:,each],'-o',linewidth=1,markersize=2,color = cmap[i])
            
            drawPic_2D.a.plot(res_ref.index,res_ref.loc[:,each],'--',linewidth=1,markersize=2,color = cmap[i])
            
            IP = interpoints.loc[day,'interpoints']
            
            IP1 = interpoints_ref.loc[day,'interpoints']
            
            drawPic_2D.a.scatter(IP['strike'],IP['vol'],300,color=cmap[i],marker = '|')
            
            drawPic_2D.a.scatter(IP1['strike'],IP1['vol'],300,color=cmap[i],marker = '|')
            
            
        if is_buy == 1:
            drawPic_2D.a.plot(res_b.index,res_b.loc[:,each],'-o',linewidth=1,markersize=2,color = cmap[i])
            
            drawPic_2D.a.plot(res_ref_b.index,res_ref_b.loc[:,each],'--',linewidth=1,markersize=2,color = cmap[i])
            
            #IP = interpoints_b.loc[day,'interpoints']
            
            #IP1 = interpoints_b_ref.loc[day,'interpoints']
            
            #drawPic_2D.a.scatter(IP['strike'],IP['vol'],300,color=cmap[i],marker = '|')
            
            #drawPic_2D.a.scatter(IP1['strike'],IP1['vol'],300,color=cmap[i],marker = '|')
            
        if is_sell == 1:
            drawPic_2D.a.plot(res_s.index,res_s.loc[:,each],'-o',linewidth=1,markersize=2,color = cmap[i])
            
            drawPic_2D.a.plot(res_ref_s.index,res_ref_s.loc[:,each],'--',linewidth=1,markersize=2,color = cmap[i])
            
            #IP = interpoints_s.loc[day,'interpoints']
            
            #IP1 = interpoints_s_ref.loc[day,'interpoints']
            
            #drawPic_2D.a.scatter(IP['strike'],IP['vol'],300,color=cmap[i],marker = '|')
            
            #drawPic_2D.a.scatter(IP1['strike'],IP1['vol'],300,color=cmap[i],marker = '|')
            
        patch.append(mpatches.Patch(color=cmap[i],label=each))
        i+=1
    
    
    drawPic_2D.a.grid(color='grey',linestyle='--',linewidth=0.5)
    drawPic_2D.a.legend(handles=patch,fontsize=8)
    
    drawPic_2D.a.set_ylabel('Volatility')
    
    drawPic_2D.a.set_yticklabels(['%.2f'%(x*100)+'%' for x in drawPic_2D.a.get_yticks()])  #改百分号

    drawPic_2D.canvas.show()
    #print(2)

def drawPic_3D(sig):
    
    res,res_b,res_s,res_ref,res_ref_b,res_ref_s,strike_lst,T_lst,f_atm,interpoints,interpoints_ref,res3D,res3D_b,\
res3D_s,res3D_ref,res3D_ref_b,res3D_ref_s = cal_surface()
    #print(res,res_b,res_s)
    #清空图像，以使得前后两次绘制的图像不会重叠  
    
    drawPic_3D.f.clf()  
    drawPic_3D.a = drawPic_3D.f.add_subplot(111,projection='3d')
    
    K = np.array(strike_lst)
    T = np.array(T_lst)
    
    if sig == 'Log-Moneyness':
        K = np.log(K/f_atm)
        drawPic_3D.a.set_xlabel(sig)
    elif sig == 'Strike Price':
        drawPic_3D.a.set_xlabel(sig)
    else:
        pass
    
    K, T= np.meshgrid(K, T)
    cmap = ['blue','green','red','black','magenta','yellow','cyan']
    # 具体函数方法可用 help(function) 查看，如：help(ax.plot_surface)
    if is_mid == 1:
        drawPic_3D.a.plot_wireframe(K, T, res3D.T,color='orange')
        drawPic_3D.a.plot_wireframe(K, T, res3D_ref.T,color='grey')
        for i in range(len(K)):
            drawPic_3D.a.plot(K[i],T[i],res3D.T.iloc[i,:],'-o',color=cmap[i],linewidth=1,markersize=2)
            drawPic_3D.a.plot(K[i],T[i],res3D_ref.T.iloc[i,:],'--',color=cmap[i],linewidth=1,markersize=2)
    if is_buy == 1:
        drawPic_3D.a.plot_wireframe(K, T, res3D_b.T,color='orange')
        drawPic_3D.a.plot_wireframe(K, T, res3D_ref_b.T,color='grey')
        for i in range(len(K)):
            drawPic_3D.a.plot(K[i],T[i],res3D_b.T.iloc[i,:],'-o',color=cmap[i],linewidth=1,markersize=2)
            drawPic_3D.a.plot(K[i],T[i],res3D_ref_b.T.iloc[i,:],'--',color=cmap[i],linewidth=1,markersize=2)
    if is_sell == 1:
        drawPic_3D.a.plot_wireframe(K, T, res3D_s.T,color='orange')
        drawPic_3D.a.plot_wireframe(K, T, res3D_ref_s.T,color='grey')
        for i in range(len(K)):
            drawPic_3D.a.plot(K[i],T[i],res3D_s.T.iloc[i,:],'-o',color=cmap[i],linewidth=1,markersize=2)
            drawPic_3D.a.plot(K[i],T[i],res3D_ref_s.T.iloc[i,:],'--',color=cmap[i],linewidth=1,markersize=2)
    
    #drawPic_3D.a.legend()
    drawPic_3D.a.set_ylabel('TimeToMaturity(days)') 
    drawPic_3D.a.set_zlabel('Volatility')
    #print(drawPic_3D.a.get_zticks())
    drawPic_3D.a.set_zticklabels(['%.2f'%(x*100)+'%' for x in drawPic_3D.a.get_zticks()[1:]])  #改百分号
    #drawPic_3D.f.colorbar(a,shrink=0.5,aspect=5)
    drawPic_3D.canvas.show()

#%%单点计算
def vol_cal(days_cal,strike_cal,vol_mid,vol_buy,vol_sell):
    global temp_db,buy_sell_para
    
    T = float(days_cal.get())
    strike = [float(strike_cal.get())]
    
    db = temp_db.copy()
    db2 = buy_sell_para.copy()
    f_atm = float(F_atm.get())
    db['f_atm'] = f_atm #后接入数据库数据
    
    benchmark = db[['alpha','f_atm','f_ref','ssr','vol_ref','vcr',\
                         'slope_ref','scr','dn_cf','up_cf','call_curv',\
                         'dn_sm','up_sm','dn_slope','up_slope','put_curv','day']]
    benchmark2 = db2[['alpha','f_atm','f_ref','ssr','vol_ref','vcr',\
                         'slope_ref','scr','dn_cf','up_cf','call_curv',\
                         'dn_sm','up_sm','dn_slope','up_slope','put_curv','day']]
    
    benchmark.index = [0]*len(benchmark)
    benchmark2.index = [0]*len(benchmark2)
    
    
    
    in_put2 = {'TimeToMaturity':T,'strike':strike}
    res_mid = TimeSeriesInterpolator.time_interpolate(benchmark,in_put2)
    res_bs = TimeSeriesInterpolator.time_interpolate(benchmark2,in_put2)
    clear(vol_mid)
    clear(vol_buy)
    clear(vol_sell)
    volm = round(res_mid.loc[0,'vol']*100,3)
    volb = round((res_mid.loc[0,'vol']-res_bs.loc[0,'vol'])*100,3)
    vols = round((res_mid.loc[0,'vol']+res_bs.loc[0,'vol'])*100,3)
    vol_mid.insert(0,volm)
    vol_buy.insert(0,volb)
    vol_sell.insert(0,vols)
    
    if is_mid == 1:
        drawPic_3D.a.scatter(strike[0], T, volm/100, marker='o',s=200,color='red')
    if is_buy == 1:
        drawPic_3D.a.scatter(strike[0], T, volb/100, marker='o',s=200,color='red')
    if is_sell == 1:
        drawPic_3D.a.scatter(strike[0], T, vols/100, marker='o',s=200,color='red')

    
    

#%%

def submit():
    for contract in temp_db.index.tolist():
        exchange = contract.split('-')[0]
        index = contract.split('-')[1]
        days = contract.split('-')[2]
        for each in temp_db.columns.tolist():
            changevalue = str(temp_db.loc[contract,each])
            outputstr = ChangeParamData.Writeparamdata(each,changevalue,exchange=exchange,index=index,days=days)
            print(outputstr)

def save(event):
    #update temp_db_ref
    global in_put,ExChosen,contractChosen,daysChosen,param_list,temp_db_ref,buy_sell_para_ref
    
    db_index = ExChosen.get()+'-'+contractChosen.get()+'-'+daysChosen.get()
    for each in in_put['DBparaname'].tolist():
        #print(each)
        sb = in_put[in_put['DBparaname']==each]['DataCurrSpin'].values[0]
        temp_db_ref.loc[db_index,each] = float(sb.get())

    buy_sell_para_ref = BAspread(temp_db_ref,param_list)
    drawPic(0)

def Set():
    global temp_db,temp_db_ref,buy_sell_para,buy_sell_para_ref
    temp_db = temp_db_ref.copy()
    buy_sell_para = buy_sell_para_ref.copy()
    drawPic(0)

def Revert():
    global temp_db,temp_db_ref,buy_sell_para,buy_sell_para_ref
    temp_db_ref = temp_db.copy()
    buy_sell_para_ref = buy_sell_para.copy()
    drawPic(0)
    
    #把spinbox中的值变回原来的
    global in_put
    #tmp = data[0]['data']
    tmp = temp_db[temp_db['day']==int(daysChosen.get())]
    
    for each in in_put['DBparaname'].tolist():
        True_value = tmp[each].values[0]
        sb = in_put[in_put['DBparaname']==each]['DataCurrSpin'].values[0]
        clear(sb)
        sb.insert(0,True_value)
    
def contact_day_to_params(event):
    #定义事件,该合约、天数---》参数更新
    global in_put,daysChosen,x_axischosen,temp_db,buy_sell_para,param_list,temp_db_ref
    #tmp = data[0]['data']
    if type(temp_db_ref) == type(0):
        #说明是第一次运行
        temp_db_ref = temp_db.copy()

    tmp = temp_db_ref[temp_db_ref['day']==int(daysChosen.get())]
    
    for each in in_put['DBparaname'].tolist():
        True_value = tmp[each].values[0]
        sb = in_put[in_put['DBparaname']==each]['DataCurrSpin'].values[0]
        clear(sb)
        sb.insert(0,True_value)
    
    buy_sell_para = BAspread(temp_db,param_list)
    
    x_axischosen['values'] = ['Strike Price','Log-Moneyness']
    

def contract_to_day(event):
    #定义事件,该合约--->更新天数
    global ExChosen,contractChosen,daysChosen,temp_db,labelbt6,var_lst,is_day,temp_db_ref
    temp_db_ref = 0
    data,bench_day = GetDataMySQL.getparamdata(exchange=ExChosen.get(),index=contractChosen.get(),model='wing')
    #print(bench_day)
    temp_db = GetDataMySQL.get_std_paramdata(exchange=ExChosen.get(),index=contractChosen.get(),model='wing')
    bench_day.sort()
    daysChosen['values'] =  bench_day   # 设置下拉列表的值
    daysChosen.current(0)
    contact_day_to_params(0)
    var_lst = []
    is_day = []
    
    former_labelbt6 = labelbt6.grid_slaves()
    for each in former_labelbt6:
        each.destroy()
        
    for i in range(len(bench_day)):
        var = tk.IntVar()
        checkbt = Checkbutton(labelbt6,text=str(bench_day[i]),\
                              variable=var, onvalue=1, offvalue=0,\
                              command=selection)
        checkbt.grid(row=15+i,column=2,rowspan=1,columnspan=1)
        var_lst.append(var)
        is_day.append(0)
    #print(var_lst)
    
def exchange_to_underlying(event):
    global ExChosen,contractChosen
    for each in GetUnderling.Getunderling()[1]:
        if ExChosen.get() == each['exchange']:
            contractChosen['values'] =  each['contract']  # 设置下拉列表的值
            break
    contractChosen.current(0)
    contract_to_day(0)
    
    

#%%
global temp_db,param_list,is_buy,is_sell,is_mid
#创建一个临时数据库，dataframe,临时存储数据，不存入真正的数据库
is_buy = 0
is_sell = 0
is_mid = 0

rootpath = os.getcwd()
param_list = pd.read_csv(rootpath+'/Volatility_UI.csv',sep=';')
button_bg = '#D5E0EE'  
button_active_bg = '#E5E35B'
#button_font = tkFont.Font(size=12, weight=tkFont.BOLD)

root = Tk()
root.title('国信期货波动率曲面管理')


#%%参数部分
title = param_list['Group'].drop_duplicates().tolist()
title_labelframe = {}

for each in title:
    label = LabelFrame(root,text = each)
    label.grid(row=0,column=param_list[param_list['Group']==each]['column'].tolist()[0],sticky=N+W,padx=10,pady=5)
    title_labelframe.update({each:label})
    #print(title_labelframe)


#排版
in_put = []
for i in range(len(param_list)):
    labelframe = LabelFrame(title_labelframe[param_list.loc[i,'Group']], text=param_list.loc[i,'LabelName'])
    labelframe.grid(row=int(param_list.loc[i,'row']),
                    column=int(param_list.loc[i,'column']),sticky=N+W, padx=10,  pady=5)
    
    if param_list.loc[i,'DataType'] == 'SpinBox':
        sb = Spinbox(labelframe,
             from_ = param_list.loc[i,'DataDownBound'],
             to = param_list.loc[i,'DataUpBound'],
             increment = param_list.loc[i,'Step'],
             command = lambda :save(0))
        sb.grid(row=int(param_list.loc[i,'row']+1),
                column=int(param_list.loc[i,'column']),sticky=N+W, padx=10,  pady=5)
        sb.bind('<Return>',save)
        
        in_put.append([param_list.loc[i,'DBparaname'],sb])  #作为input
        
    elif param_list.loc[i,'DataType'] == 'Label':
        lb = Label(labelframe,
                   text = param_list.loc[i,'DataCurr'])
        lb.grid(row=int(param_list.loc[i,'row']+1),
                column=int(param_list.loc[i,'column']),sticky=N+W, padx=10,  pady=5)
    
    else:
        pass
        
    
in_put = pd.DataFrame(in_put,columns = ['DBparaname','DataCurrSpin'])


#%%下拉框选合约-天数部分
label = LabelFrame(title_labelframe['Wing Model Setting'], text='Selection')
label.grid(row=1,column=1,rowspan=6,sticky=N+W, padx=10,  pady=5)

labelframe1 = LabelFrame(label, text='Exchange')
labelframe1.grid(row=2,column=1,sticky=N+W, padx=10,  pady=5)
ExChosen = ttk.Combobox(labelframe1, width=12)
ExChosen['values'] =  GetUnderling.Getunderling()[0]['exchange'].tolist()  # 设置下拉列表的值
ExChosen.grid(column=1, row=3)      # 设置其在界面中出现的位置  column代表列   row 代表行
ExChosen.bind("<<ComboboxSelected>>",exchange_to_underlying)

labelframe2 = LabelFrame(label, text='Underlying')
labelframe2.grid(row=3,column=1,sticky=N+W, padx=10,  pady=5)
contractChosen = ttk.Combobox(labelframe2, width=12)
contractChosen.grid(column=1, row=4)      # 设置其在界面中出现的位置  column代表列   row 代表行
contractChosen.bind("<<ComboboxSelected>>",contract_to_day)

labelframe3 = LabelFrame(label, text='TimeToMaturity')
labelframe3.grid(row=5,column=1,sticky=N+W, padx=10,  pady=5)
daysChosen = ttk.Combobox(labelframe3, width=12)
daysChosen.grid(column=1, row=6)      # 设置其在界面中出现的位置  column代表列   row 代表行
daysChosen.bind("<<ComboboxSelected>>",contact_day_to_params)

labelframe4 = LabelFrame(label,text = 'X_axis')
labelframe4.grid(row=7,column=1,sticky=N+W,padx=10,pady=5)
x_axischosen = ttk.Combobox(labelframe4, width=12)
x_axischosen.grid(column=1, row=8)
x_axischosen.bind("<<ComboboxSelected>>",drawPic)



#%%
window = tk.Toplevel(root)
nb = ttk.Notebook(window)
nb.pack(expand=1, fill="both")

labelplot = LabelFrame(nb,text = 'Volatility Curve/Surface')
labelplot.pack(expand=1, fill="both")

drawPic_2D.f = Figure(figsize=(6,4), dpi=100)
drawPic_2D.canvas = FigureCanvasTkAgg(drawPic_2D.f, master=labelplot)
drawPic_2D.canvas.show()
drawPic_2D.canvas.get_tk_widget().pack(expand=1, fill="both")

drawPic_3D.f = Figure(figsize=(6,4), dpi=100)
drawPic_3D.canvas = FigureCanvasTkAgg(drawPic_3D.f, master=labelplot)
drawPic_3D.canvas.show()
drawPic_3D.canvas.get_tk_widget().pack(expand=1, fill="both")

labelframe = LabelFrame(title_labelframe['Wing Model Setting'], text='X_inc')
labelframe.grid(row=8,column=1,sticky=N+W, padx=10,  pady=5)
x_inc = Spinbox(labelframe,from_ = 0,to = 100000,increment = 1,command = lambda :save(0))
clear(x_inc)
x_inc.insert(0,25)
x_inc.grid(row=8,column=1,sticky=N+W, padx=10,  pady=5)
x_inc.bind('<Return>',drawPic)

labelframe = LabelFrame(title_labelframe['Wing Model Setting'], text='X_n')
labelframe.grid(row=8,column=2,sticky=N+W, padx=10,  pady=5)
x_n = Spinbox(labelframe,from_ = 0,to = 100000,increment = 1,command = lambda :save(0))
clear(x_n)
x_n.insert(0,30)
x_n.grid(row=8,column=2,sticky=N+W, padx=10,  pady=5)
x_n.bind('<Return>',drawPic)

labelframe = LabelFrame(title_labelframe['Wing Model Setting'], text='f_atm')
labelframe.grid(row=1,column=2,sticky=N+W, padx=10,  pady=5)
F_atm = Spinbox(labelframe,from_ = 0,to = 100000,increment = 1,command = lambda :save(0))
clear(F_atm)
F_atm.insert(0,2850)
F_atm.grid(row=2,column=2,sticky=N+W, padx=10,  pady=5)
F_atm.bind('<Return>',drawPic)

labelbt = LabelFrame(title_labelframe['Wing Model Setting'],text = 'Button')
labelbt.grid(row=9,column=1,columnspan=2,sticky=N+W,padx=10,pady=5)


labelbt3 = LabelFrame(labelbt,text = 'Adjust')
labelbt3.grid(row=18,column=1,rowspan=1,columnspan=2,sticky=N+W,padx=10,pady=5)
bt = Button(labelbt3,text='Set',bg=button_bg, padx=50, pady=3,fg='green',\
           command=lambda : Set(),activebackground = button_active_bg,\
           font = tkFont.Font(size=12, weight=tkFont.BOLD))
bt.grid(row=19,column=1,rowspan=1)
bt = Button(labelbt3,text='Revert',bg=button_bg, padx=50, pady=3,fg='green',\
           command=lambda : Revert(),activebackground = button_active_bg,\
           font = tkFont.Font(size=12, weight=tkFont.BOLD))
bt.grid(row=19,column=2,rowspan=1)


labelbt4 = LabelFrame(labelbt,text = 'Submit(To Database)')
labelbt4.grid(row=20,column=1,rowspan=1,columnspan=2,sticky=N+W,padx=10,pady=5)
bt = Button(labelbt4,text='Submit(To Database)',bg=button_bg, padx=50, pady=3,fg='green',\
           command=lambda : submit(),activebackground = button_active_bg,\
           font = tkFont.Font(size=12, weight=tkFont.BOLD))
bt.grid(row=21,column=1,rowspan=1,columnspan=2)

var1 = tk.IntVar()
var2 = tk.IntVar()
var3 = tk.IntVar()

labelbt5 = LabelFrame(labelbt, text='Display Offset')
labelbt5.grid(row=14,column=1,sticky=N+W,padx=10,pady=5)

checkbt1 = Checkbutton(labelbt5,text='Buy',\
                       variable=var1, onvalue=1, offvalue=0,\
                       command=selection)
checkbt1.grid(row=15,column=1,rowspan=1,columnspan=1)

checkbt2 = Checkbutton(labelbt5,text='Sell',\
                       variable=var2, onvalue=1, offvalue=0,\
                       command=selection)
checkbt2.grid(row=16,column=1,rowspan=1,columnspan=1)

checkbt3 = Checkbutton(labelbt5,text='Mid',\
                       variable=var3, onvalue=1, offvalue=0,\
                       command=selection)
checkbt3.grid(row=17,column=1,rowspan=1,columnspan=1)

global labelbt6
#Display Benchmarks 根据数据库中有多少个days数据产生
labelbt6 = LabelFrame(labelbt, text='Display Benchmarks')
labelbt6.grid(row=14,column=2,sticky=N+W,padx=10,pady=5)

labelbt7 = LabelFrame(title_labelframe['Wing Model Setting'],text = 'Single Point Calculate')
labelbt7.grid(row=22,column=1,rowspan=1,columnspan=2,sticky=N+W,padx=10,pady=5)

labelframe = LabelFrame(labelbt7, text='Days To Maturity')
labelframe.grid(row=23,column=1,sticky=N+W, padx=10,  pady=5)
days_cal = Spinbox(labelframe,from_ = 0,to = 100000,increment = 1)
clear(days_cal)
days_cal.insert(0,100)
days_cal.grid(row=24,column=1,sticky=N+W, padx=10,  pady=5)

labelframe = LabelFrame(labelbt7, text='Strike Price')
labelframe.grid(row=23,column=2,sticky=N+W, padx=10,  pady=5)
strike_cal = Spinbox(labelframe,from_ = 0,to = 100000,increment = 1)
clear(strike_cal)
strike_cal.insert(0,2850)
strike_cal.grid(row=24,column=2,sticky=N+W, padx=10,  pady=5)

labelframe = LabelFrame(labelbt7, text='Result: Volatility(%)')
labelframe.grid(row=26,column=1,columnspan=2,sticky=N+W, padx=10,  pady=5)

l1 = LabelFrame(labelframe, text='Mid Vol')
l1.grid(row=27,column=1,sticky=N+W, padx=10,  pady=5)
vol_mid = Entry(l1,justify="right")
clear(vol_mid)
vol_mid.grid(row=27,column=1,sticky=N+W, padx=10,  pady=5)

l2 = LabelFrame(labelframe, text='Buy Vol')
l2.grid(row=27,column=2,sticky=N+W, padx=10,  pady=5)
vol_buy = Entry(l2,justify="right")
clear(vol_buy)
vol_buy.grid(row=27,column=2,sticky=N+W, padx=10,  pady=5)

l3 = LabelFrame(labelframe, text='Sell Vol')
l3.grid(row=28,column=2,sticky=N+W, padx=10,  pady=5)
vol_sell = Entry(l3,justify="right")
clear(vol_sell)
vol_sell.grid(row=28,column=2,sticky=N+W, padx=10,  pady=5)

bt = Button(labelbt7,text='Calculate',bg=button_bg, padx=50, pady=3,fg='green',\
           command=lambda : vol_cal(days_cal,strike_cal,vol_mid,vol_buy,vol_sell),activebackground = button_active_bg,\
           font = tkFont.Font(size=12, weight=tkFont.BOLD))
bt.grid(row=25,column=1,columnspan=2,sticky=N+W, padx=10,  pady=5)



root.mainloop()
