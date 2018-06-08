# -*- coding: utf-8 -*-
"""
Created on Wed May 30 10:25:34 2018

@author: Harrison
"""
import PyMySQLwrite
#%% 更改model_params表中的数据，选定合约和参数名
def Writeparamdata(changeitem,changevalue,exchange='',index='',days=''):
    
    if exchange==''and index=='' and days=='':  #判断是否有合约限制 输出可执行MySQL语句
        strall="UPDATE futurexdb.model_params SET paramvalue='"+ changevalue + "' where accountid=20 and paramname="+"'"\
        +changeitem+"'"
    else:                           
        modelinstance=exchange+'-'+index+'-'+days
        strall="UPDATE futurexdb.model_params SET paramvalue='"+ changevalue + "' where accountid=20 and modelinstance ='"\
        +modelinstance +"' and " +'paramname='+"'"+changeitem+"'"
    
    data=PyMySQLwrite.MySQLexecute1(strall)                  #调用函数执行MySQL语句
    
    if exchange==''and index=='' and days=='':  #输出结果整合
        outputstr='本次更改全部时间：'+changeitem+' 值至：'+changevalue+' 受到影响的行数: '+str(data)
    else:
        outputstr='本次更改：'+modelinstance+' '+changeitem+' 值至：'+changevalue+' 受到影响的行数: '+str(data)
    #print(outputstr)                            #print结果 
    return outputstr                            #返回结果
#%%使用方法
#a=Writeparamdata('alpha','0')                       #替换所有合约的ALpha值
#b=Writeparamdata('alpha','0','DCE','C','1')         #替换DCE-C-1合约的ALpha值