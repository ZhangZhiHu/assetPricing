#-*-coding: utf-8 -*-
#@author:tyhj
import pandas as pd
import numpy as np
import os
import tool
import param


def get_portfolio_constituents():
    rawdata_path=os.path.join(tool_old.dirpath, 'sorting_data')
    filenames_intersection=tool_old.get_intersection_filenames2(rawdata_path)
    sorting_types=os.listdir(rawdata_path)

    year_end_filenames=[fn for fn in filenames_intersection if fn.split('-')[1]=='12']

    for sorting_type in sorting_types:
        sorting_path=os.path.join(tool_old.dirpath, 'portfolio_constituent', sorting_type)
        if not os.path.exists(sorting_path):
            os.makedirs(sorting_path)

        for year_end_filename in year_end_filenames:
            df=pd.read_csv(os.path.join(rawdata_path,sorting_type,year_end_filename),index_col=0)
            portfolio_df=tool_old.get_portfolio(df, sorting_type, param.portfolio_number)
            portfolio_df.to_csv(os.path.join(sorting_path,year_end_filename))
            print sorting_type,year_end_filename


def sorting_independent():
    dir=os.path.join(tool.dirpath, 'sorting_data')
    sorting_types=os.listdir(dir)
    fns=os.listdir(os.path.join(dir,sorting_types[0]))
    # fns2=os.listdir(os.path.join(tool.dirpath,'month_return'))
    # fns=[fn for fn in fns1 if fn in fns2]

    newdir=os.path.join(tool.dirpath, 'combination')
    if not os.path.exists(newdir):
        os.makedirs(newdir)

    # rm=pd.read_csv(os.path.join(tool.dirpath,'rm.csv'),index_col=0)
    for fn in fns:
        dfs=[]
        for st in sorting_types:
            subdf=pd.read_csv(os.path.join(dir,st,fn),index_col=0)
            dfs.append(subdf)
        df=pd.concat(dfs,axis=1)

        # #add month_return
        # month_return=pd.read_csv(os.path.join(tool.dirpath,'month_return',fn),index_col=0)
        # df['month_return']=month_return['month_return']
        #
        # #add rm-rf
        # df['rmrf']=rm['rm']
        # df=df.dropna(axis=0)
        for st in sorting_types:
            df=tool.add_group_name(df,st,param.portfolio_number)
        df=df.sort_index()
        df.to_csv(os.path.join(newdir,fn))
        print fn

dir=os.path.join(tool.dirpath,'combination')
fns1=os.listdir(dir)
fns2=os.listdir(os.path.join(tool.dirpath,'month_return'))
fns=[fn for fn in fns1 if fn in fns2]














