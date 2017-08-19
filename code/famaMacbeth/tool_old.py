#-*-coding: utf-8 -*-
#@author:tyhj
import pandas as pd
import numpy as np
import os

def get_dirpath():
    cwd=os.getcwd()
    dirpath=os.path.split(cwd)[0]
    return dirpath

dirpath=get_dirpath()

def winsorize(df,factor):
    sub_df = df[[factor]]
    sub_df[sub_df > np.percentile(sub_df, 95)] = np.percentile(sub_df, 95)
    sub_df[sub_df < np.percentile(sub_df, 5)] = np.percentile(sub_df, 5)
    return sub_df

def get_intersection_filenames2(dirpath):
    '''
    there are several subdirectorys in dirpath,return the intersection
    '''
    factornames = os.listdir(dirpath)
    filenames_intersection=[]
    for i,fn in enumerate(factornames):
        filenames=os.listdir(os.path.join(dirpath,fn))
        if i == 0:
            filenames_intersection=filenames
        else:
            filenames_intersection=[d for d in filenames_intersection if d in filenames]
    return filenames_intersection


def get_portfolio(df,colname,portfolio_number):
    new_df=df.sort_values(colname,ascending=True)
    number_middle=len(new_df)/portfolio_number
    number_low = number_middle + (len(new_df) % portfolio_number) / 2
    number_high = number_middle + len(new_df) % portfolio_number - (len(new_df) % portfolio_number / 2)

    stocklists={}
    stocklist_low=list(new_df[:number_low].index)
    stocklists[colname+'_low']=stocklist_low

    for j in range(portfolio_number-2):
        start=number_low+j*number_middle
        end=number_low+(j+1)*number_middle
        stocklist_middle=list(new_df[start:end].index)
        stocklists[colname+'_'+str(j+2)]=stocklist_middle

    stocklist_high=list(new_df[-number_high:].index)
    stocklists[colname+'_high']=stocklist_high

    for portfolio_name in stocklists:
        new_df.loc[stocklists[portfolio_name],'portfolio_name']=portfolio_name

    new_df=new_df[['portfolio_name']]
    return new_df









