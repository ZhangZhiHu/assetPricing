#-*-coding: utf-8 -*-
#author:tyhj

#import python packages
import numpy as np
import pandas as pd
import os
from shutil import copyfile

#import my utils
from zht.util.dfFilter import filterDf
from zht.util.pandasu import get_inter_frame

#import project elements
from params import sp,bdp,idp,tmpp


def get_nfc():
    '''
    non-financial stock codes
    :return:
    '''
    tbname='TRD_Co'
    df=pd.read_csv(os.path.join(sp,tbname+'.csv'))
    nf=df[df['Indcd']!=1]
    nf=nf.reset_index()
    nf=nf[['Stkcd']]
    nf.to_csv(os.path.join(tmpp,'nfc.csv'))



def _get_indicator1(name,tbname,fldname,timefld='Accper'):
    df=pd.read_csv(os.path.join(sp,tbname+'.csv'))
    df=df[df['Typrep']=='A']
    q='Accper endswith 12-31'
    df=filterDf(df,q)
    colnames=['Stkcd',timefld,fldname]
    df=df[colnames]
    subdfs=[]
    for stockId,x in list(df.groupby('Stkcd')):
        tmpdf=x[[timefld,fldname]]
        tmpdf=tmpdf.set_index(timefld)
        tmpdf.index=[ind[:-3] for ind in tmpdf.index]
        tmpdf.columns=[stockId]
        subdfs.append(tmpdf)

    table=pd.concat(subdfs,axis=1)
    table=table.sort_index(ascending=True)
    table.to_csv(os.path.join(tmpp,name+'.csv'))

def get_items1():
    items=[('operIncom','FS_Comins','B001101000','Accper'),
            ('operExp','FS_Comins','B001209000','Accper'),
            ('admExp','FS_Comins','B001210000','Accper'),
            ('finanExp','FS_Comins','B001211000','Accper'),
            ('totAsset','FS_Combas','A001000000','Accper'),
            ('totShe','FS_Combas','A003000000','Accper')
           ]
    for item in items:
        name,tbname,fldname,timefld=item
        _get_indicator1(name,tbname,fldname,timefld)
        print name

def readFromTmp(fn):
    df=pd.read_csv(os.path.join(tmpp,fn+'.csv'),index_col=0)
    return df

def get_op():
    operIncom=readFromTmp('operIncom')
    admExp=readFromTmp('admExp').fillna(method='ffill')
    finanExp=readFromTmp('finanExp').fillna(method='ffill')
    operExp=readFromTmp('operExp').fillna(method='ffill')

    op=operIncom-admExp-finanExp-operExp
    op.index=[str(int(ind[:4])+1)+'-06' for ind in op.index] #TODO:In june of year t,op comes from fiscal year ending in year t-1
    op.to_csv(os.path.join(tmpp,'op.csv'))


def get_inv():
    totAsset=readFromTmp('totAsset')
    inv=totAsset.pct_change()
    inv.index = [str(int(ind[:4]) + 1) + '-06' for ind in inv.index]#TODO:In june of year t,inv comes from fiscal year ending in year t-1
    inv.to_csv(os.path.join(tmpp,'inv.csv'))

def _get_indicator2(name,tbname,fldname,timefld='Trdmnt'):
    df = pd.read_csv(os.path.join(sp, tbname + '.csv'))
    q='Markettype in [1,4,16]'
    df=filterDf(df,q)
    colnames=['Stkcd',timefld,fldname]

    df = df[colnames]
    subdfs = []
    for stockId, x in list(df.groupby('Stkcd')):
        tmpdf = x[[timefld, fldname]]
        tmpdf = tmpdf.set_index(timefld)
        tmpdf.columns = [stockId]
        subdfs.append(tmpdf)

    table = pd.concat(subdfs, axis=1)
    table = table.sort_index(ascending=True)
    table.to_csv(os.path.join(tmpp,name+'.csv'))


def get_items2():
    items=[
        ('ret','TRD_Mnth','Mretwd','Trdmnt'),
        ('size','TRD_Mnth','Msmvosd','Trdmnt'),

    ]
    for item in items:
        name,tbname,fldname,timefld=item
        _get_indicator2(name,tbname,fldname,timefld)
        print name


def get_weight():
    size=readFromTmp('size')
    weight=size.shift(1)
    weight.to_csv(os.path.join(tmpp,'weight.csv'))


def get_rf():
    df = pd.read_csv(os.path.join(sp,'TRD_Nrrate.csv'))
    q = 'Nrr1 == NRI01'  # TODO:TBC=国债票面利率
    df = filterDf(df, q)
    colnames = ['Clsdt', 'Nrrmtdt']
    df = df.sort_values('Clsdt')

    df = df[colnames]
    df = df.set_index('Clsdt')

    dates = pd.date_range(df.index[0], df.index[-1], freq='D')
    dates = [d.strftime('%Y-%m-%d') for d in dates]

    newdf = pd.DataFrame(index=dates)
    newdf['Nrrmtdt'] = df['Nrrmtdt']
    newdf = newdf.fillna(method='ffill')
    newdf = newdf.reset_index()
    newdf['month'] = newdf['index'].apply(lambda x: '-'.join(x.split('-')[:-1]))

    avg = newdf.groupby('month').mean()
    avg = avg / 100
    del avg.index.name
    avg.columns = ['rf']
    avg.to_csv(os.path.join(tmpp,'rf.csv'))


def get_rm():
    name='rm'
    dbname=''
    tbname='TRD_Cnmont'
    fldname='Cmretwdos'
    timefld='Trdmnt'
    q=[]
    cols=[]

    df = pd.read_csv(os.path.join(sp, tbname + '.csv'))
    q = 'Markettype == 5'#综合A股市场
    df = filterDf(df, q)
    colnames = [timefld, fldname]

    df = df[colnames]

    df=df.set_index('Trdmnt')
    df=df.sort_index()
    del df.index.name
    df.columns=['rm']
    df.to_csv(os.path.join(tmpp,'rm.csv'))


def get_rp():
    rf=readFromTmp('rf')
    rm=readFromTmp('rm')

    rp=rm['rm']-rf['rf']

    rp=rp.to_frame()
    rp.columns=['rp']
    rp.to_csv(os.path.join(tmpp,'rp.csv'))


def get_mv():
    name='mv'
    tbname='TRD_Mnth'
    fldname='Mclsprc' #月收盘价
    timefld='Trdmnt'

    df = pd.read_csv(os.path.join(sp, tbname + '.csv'))
    q1 = 'Markettype in [1,4,16]'
    q2= 'Trdmnt endswith 12' #TODO: only need the data in December
    q=[q1,q2]
    df = filterDf(df, q)
    colnames = ['Stkcd', timefld, fldname]

    df = df[colnames]
    subdfs = []
    for stockId, x in list(df.groupby('Stkcd')):
        tmpdf = x[[timefld, fldname]]
        tmpdf = tmpdf.set_index(timefld)
        tmpdf.columns = [stockId]
        subdfs.append(tmpdf)

    table = pd.concat(subdfs, axis=1)
    table = table.sort_index(ascending=True)
    table.to_csv(os.path.join(tmpp,name+'.csv'))


def get_bv():
    name='bv'
    tbname='FI_T9'
    fldname='F091001A' #每股净资产
    timefld='Accper'

    df = pd.read_csv(os.path.join(sp, tbname + '.csv'))

    q1 = 'Typrep == A'
    q2 = 'Accper endswith 12-31'  # TODO: only need annual report
    q = [q1, q2]
    df = filterDf(df, q)
    colnames = ['Stkcd', timefld, fldname]

    df = df[colnames]
    subdfs = []
    for stockId, x in list(df.groupby('Stkcd')):
        tmpdf = x[[timefld, fldname]]
        tmpdf = tmpdf.set_index(timefld)
        tmpdf.columns = [stockId]
        subdfs.append(tmpdf)

    table = pd.concat(subdfs, axis=1)
    table.index=[ind[:-3] for ind in table.index]
    table = table.sort_index(ascending=True)
    table.to_csv(os.path.join(tmpp,name+'.csv'))


def get_btm():
    bv=readFromTmp('bv')
    mv=readFromTmp('mv')

    bv,mv=get_inter_frame([bv,mv])
    btm=bv/mv
    btm.index = [str(int(ind[:4]) + 1) + '-06' for ind in btm.index]
    btm.to_csv(os.path.join(tmpp,'btm.csv'))


def get_eret():
    '''
    monthly,stock excess ret

    Returns:

    '''
    ret = pd.read_csv(os.path.join(tmpp, 'ret.csv'), index_col=0)
    rf = pd.read_csv(os.path.join(tmpp, 'rf.csv'), index_col=0)
    eret = ret.sub(rf['rf'], axis=0)
    eret.to_csv(os.path.join(tmpp,'eret.csv'))
    return eret

def moveFiles():
    bdpFiles=['ret','weight','rf','rp','nfc','eret']
    idpFiles=['size','btm','inv','op']

    for bdpf in bdpFiles:
        src=os.path.join(tmpp,bdpf+'.csv')
        dst=os.path.join(bdp,bdpf+'.csv')
        if not os.path.exists(dst):
            copyfile(src,dst)

    for idpf in idpFiles:
        src=os.path.join(tmpp,idpf+'.csv')
        dst=os.path.join(idp,idpf+'.csv')
        if not os.path.exists(dst):
            copyfile(src,dst)
