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

def add_group_name(df,colname,group_number):
    new_df=df.sort_values(colname,ascending=True)
    number_middle=len(new_df)/group_number
    number_low = number_middle + (len(new_df) % group_number) / 2
    number_high = number_middle + len(new_df) % group_number - (len(new_df) % group_number / 2)

    stocklists={}
    stocklist_low=list(new_df[:number_low].index)
    stocklists[colname+'_low']=stocklist_low

    for j in range(group_number-2):
        start=number_low+j*number_middle
        end=number_low+(j+1)*number_middle
        stocklist_middle=list(new_df[start:end].index)
        stocklists[colname+'_'+str(j+2)]=stocklist_middle

    stocklist_high=list(new_df[-number_high:].index)
    stocklists[colname+'_high']=stocklist_high

    for portfolio_name in stocklists:
        new_df.loc[stocklists[portfolio_name],colname+'_group']=portfolio_name

    return new_df












