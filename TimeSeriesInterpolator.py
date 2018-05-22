# -*- coding: utf-8 -*-
"""
Created on Mon May 21 10:22:27 2018

@author: Jax_GuoSen
"""
import Wing
import pandas as pd
import matplotlib.pyplot as plt

def get_curve(X_lst,Tdays,benchmark):
    WingModel = Wing.Wing()
    para = benchmark[benchmark['days']==Tdays]
    tmp = WingModel.volatility_curve(X_lst,Tdays,para.loc[0,'alpha'],\
                                para.loc[0,'f_atm'],para.loc[0,'f_ref'],para.loc[0,'SSR'],\
                                para.loc[0,'vol_ref'],para.loc[0,'VCR'],para.loc[0,'slope_ref'],\
                                para.loc[0,'SCR'],para.loc[0,'dn_cf'],para.loc[0,'up_cf'],\
                                para.loc[0,'put_curv'],para.loc[0,'call_curv'],\
                                para.loc[0,'dn_sm'],para.loc[0,'up_sm'],\
                                para.loc[0,'dn_slope'],para.loc[0,'up_slope'])  #得到曲线
    return tmp
    

def time_interpolate(benchmark,in_put):
    
    X_lst = in_put['strike']
    res = [X_lst]  #保存结果
    bench_time = benchmark.loc[:,'days'].tolist()
    #异常情况1
    if len(set(benchmark['days'].tolist()))<len(benchmark):
        print('输入有误！请确认是否输入两组相同时间的参照波动率')
        return 0
    #异常情况2
    if len(bench_time) == 0:
        print('请输入至少一组参照波动率参数！')
        return 1
    
    
    #情况1，左端点左
    if in_put['TimeToMaturity']<=bench_time[0]:
        
        tmp = get_curve(X_lst,bench_time[0],benchmark)
        res.append(tmp['theo'])
        #print(1)
    
    #情况2，右端点右
    elif in_put['TimeToMaturity']>=bench_time[-1]:
        
        tmp = get_curve(X_lst,bench_time[-1],benchmark)
        res.append(tmp['theo'])
        #print(2)
    
    #情况3，中间
    else:
        for i in range(len(bench_time)-1):
            if in_put['TimeToMaturity']<bench_time[i+1]:
                tmp1 = get_curve(X_lst,bench_time[i],benchmark)['theo']
                tmp2 = get_curve(X_lst,bench_time[i+1],benchmark)['theo']
                weight1 = (bench_time[i+1]-in_put['TimeToMaturity'])/(bench_time[i+1]-bench_time[i])
                weight2 = (in_put['TimeToMaturity']-bench_time[i])/(bench_time[i+1]-bench_time[i])
                
                tmp1 = [x*weight1 for x in tmp1]
                tmp2 = [x*weight2 for x in tmp2]
                tmp =[tmp1[i]+tmp2[i] for i in range(min(len(tmp1),len(tmp2)))]
                res.append(tmp)
                #print(3+i)
                break
    
    res = pd.DataFrame(res,index=['strike','vol']).T
    return res
    



'''
f_atm, X_n, X_inc
X_list,
days, alpha, f_atm, f_ref, SSR,
vol_ref, VCR, slope_ref, SCR,
dn_cf, up_cf, put_curv, call_curv,
dn_sm, up_sm, dn_slope, up_slope
'''

if __name__ == '__main__':
    
    in_put = {'TimeToMaturity':130,'strike':list(range(2000,4000,50))}  #输入希望球的 vol(K,T)
    
    bench_time = [60,120,180]  #输入benchmark的时间，从小到大
    
    benchmark = pd.DataFrame(columns=['f_atm',\
                                  'days', 'alpha', 'f_ref', 'SSR',\
                                  'vol_ref', 'VCR', 'slope_ref', 'SCR',\
                                  'dn_cf', 'up_cf', 'put_curv', 'call_curv',\
                                  'dn_sm', 'up_sm', 'dn_slope', 'up_slope'])
    
    benchmark1 = pd.DataFrame({'f_atm':[2700], \
                          'days':[bench_time[0]], 'alpha':[1], 'f_ref':[2780], 'SSR':[50],\
                          'vol_ref':[0.125], 'VCR':[0], 'slope_ref':[0.38], 'SCR':[0],\
                          'dn_cf':[-0.052], 'up_cf':[0.055], 'put_curv':[2.1], 'call_curv':[-2.3],\
                          'dn_sm':[1], 'up_sm':[1], 'dn_slope':[0.001], 'up_slope':[0.001]})
    
    benchmark2 = pd.DataFrame({'f_atm':[2700], \
                          'days':[bench_time[1]], 'alpha':[2], 'f_ref':[2780], 'SSR':[50],\
                          'vol_ref':[0.125], 'VCR':[0], 'slope_ref':[0.38], 'SCR':[0],\
                          'dn_cf':[-0.052], 'up_cf':[0.055], 'put_curv':[2.1], 'call_curv':[-2.3],\
                          'dn_sm':[1], 'up_sm':[1], 'dn_slope':[0.001], 'up_slope':[0.001]})
    
    benchmark3 = pd.DataFrame({'f_atm':[2700], \
                          'days':[bench_time[2]], 'alpha':[-1], 'f_ref':[2780], 'SSR':[50],\
                          'vol_ref':[0.125], 'VCR':[0], 'slope_ref':[0.38], 'SCR':[0],\
                          'dn_cf':[-0.052], 'up_cf':[0.055], 'put_curv':[2.1], 'call_curv':[-2.3],\
                          'dn_sm':[1], 'up_sm':[1], 'dn_slope':[0.001], 'up_slope':[0.001]})
    
    benchmark = benchmark.append(benchmark1)
    benchmark = benchmark.append(benchmark2)
    benchmark = benchmark.append(benchmark3)
    
    out_put = time_interpolate(benchmark,in_put)
    out_put.set_index('strike',inplace=True)
    out_put.plot(kind='line',linewidth=2,color='b',grid=True)
    