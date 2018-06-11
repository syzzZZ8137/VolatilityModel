# -*- coding: utf-8 -*-
"""
Created on Wed Jun  6 16:35:05 2018

@author: Harrison
"""

import pymysqlread
import PyMySQLreadZH
import pandas as pd
#%%
def Getunderling():
    #%% 
    strall='SELECT * FROM futurexdb.model_params where accountid=20 and model= '+"'wing' "
    data=pymysqlread.dbconn(strall)                             #读取函数pymysqlread
    #%%
    days = data.modelinstance.drop_duplicates().tolist()
    Totaltable=[]
    for i in range(len(days)):
        bb=days[i].split('-')[0]             
        Totaltable.append(bb)
    Totaltable = list(set(Totaltable))
    Outputexchage=pd.DataFrame(columns=['exchange','ZHname'])
    for i in range(len(Totaltable)):
        Outputexchage.loc[i,'exchange']=Totaltable[i]
        Outputexchage.loc[i,'ZHname']=PyMySQLreadZH.readexchangeZH(Totaltable[i])
        
    aa = pd.DataFrame(columns=Totaltable)
    for i in range(aa.shape[1]):
        j=0
        for ii in range(len(days)):
            if days[ii].split('-')[0]==aa.columns[i]:
                aa.loc[j,aa.columns[i]]=days[ii].split('-')[1]
                j=j+1
    Totaltable1=[]
    for i in range(aa.shape[1]):
        contractname=aa.iloc[:,i].drop_duplicates().dropna().tolist()
        exchangename=aa.columns[i]
        contractZH=[]
        for ii in range(len(contractname)):
            contractZH.append(PyMySQLreadZH.readcontructZH(exchangename,contractname[ii]))
        Totaltable1.append({'contract':contractname,'ZHname':contractZH,'exchange':exchangename})
    return Outputexchage,Totaltable1
#%%使用方法
if __name__ == '__main__':
    z,q=Getunderling()
    a=z.shape[0]              #交易所个数    
    b=z.exchange[0]           #获取第一个交易所名字
    c=z.ZHname[0]             #获取第一个交易所中文名字
    d=len(q[0]['contract'])   #第一个交易所合约个数    
    e=q[0]['contract'][0]     #获取第一个交易所第一个合约名字
    f=q[0]['ZHname'][0]       #获取第一个交易所第一个合约中文名字


    
