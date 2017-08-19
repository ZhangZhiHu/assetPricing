#-*-coding: utf-8 -*-
#@author:tyhj

import os
import pandas as pd

def bk_to_mkt():
    dir=r'C:\fama_macbeth\data\PB'
    newdir=r'c:\fama_macbeth\data\book_to_mkt'
    if not os.path.exists(newdir):
        os.makedirs(newdir)

    fns=os.listdir(dir)
    for fn in fns:
        path=os.path.join(dir,fn)
        df=pd.read_csv(path,index_col=0)
        df=1/df
        del df.index.name
        df.to_csv(os.path.join(newdir,fn))
        # print fn

def delete_invalid_index():
    dir=r'c:\fama_macbeth\data'
    factornames=os.listdir(dir)
    for factorname in factornames:
        fns=os.listdir(os.path.join(dir,factorname))
        for fn in fns:
            df=pd.read_csv(os.path.join(dir,factorname,fn),index_col=0)
            a=len(df)
            invalid_codes=[code for code in df.index if code.startswith('T')]
            df=df.drop(invalid_codes)
            b=len(df)
            df.to_csv(os.path.join(dir,factorname,fn))
            print factorname,fn

def change_name():
    dir=r'C:\fama_macbeth\data\book_to_mkt'
    fns=os.listdir(dir)
    for fn in fns:
        df=pd.read_csv(os.path.join(dir,fn),index_col=0)
        df.columns=['book_to_mkt']
        df.to_csv(os.path.join(dir,fn))
        # print fn

#market return
def get_rm():
    from WindPy import *
    w.start()

    wdata=w.wsd("000300.SH", "close", "2004-12-20", "2016-12-31", "Period=M")
    dates=[t.strftime('%Y-%m-%d') for t in wdata.Times]

    df=pd.DataFrame(wdata.Data[0],index=dates,columns=['close'])
    # df.to_csv(r'C:\fama_macbeth\independent_variables\hs300.csv')

    df1=df.pct_change()
    df1.to_csv(r'C:\fama_macbeth\independent_variables\rm.csv')

def dropna():
    dir = os.path.join(tool.dirpath, 'sorting_data')
    sorting_types = os.listdir(dir)
    for st in sorting_types:
        fns = os.listdir(os.path.join(dir, st))
        for fn in fns:
            df = pd.read_csv(os.path.join(dir, st, fn), index_col=0)
            df = df.dropna(axis=0)
            df.to_csv(os.path.join(dir, st, fn))
            # print st, fn


def change_date_format():
    df=pd.read_csv(r'C:\fama_macbeth\rm.csv',index_col=0)

    new_index=[]
    for i in range(len(df)):
        d=df.index[i]
        year,month,day=[int(m) for m in d.split('/')]
        import datetime
        date=datetime.datetime(year,month,day).strftime('%Y-%m-%d')
        new_index.append(date)
    df.index=new_index
    df.to_csv(r'c:\fama_macbeth\rm.csv')














