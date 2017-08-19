#-*-coding: utf-8 -*-
#author:tyhj
#getFactor.py 2017/8/17 10:55
import pandas as pd
import numpy as np
import os

from zht.data.resset import ressetApi
from zht.data.gta import gtaApi
from zht.util import pandasu

from params import *

#momentum
def get_carhart4():
    '''
    carhart momentum factor is constructed as the equal-weighted
    average of firms with the highest 30 percent eleven-month returns
    lagged one month minus the equal-weight average of firms with the
    lowest 30 percent eleven-month returns lagged one month.

    reference:
        On persistence in mutual fund performance,Carhart 1997
    '''
    mom=ressetApi.getMomentum()
    carhartMom=mom['MomFac_11M_Eq']
    carhartMom.to_csv(os.path.join(factorRetPath,'carhartMom.csv'))

def get_liqSen():
    '''
    calculate the marketwide liquidity indicator (lt) and stocks' sensitivity respect to
    'lt',adjusted for exposures to fama french three factors.

    "Liquidity Risk and Expected Stock Returns",by Lubos Pastor,2003

    Returns:

    '''
    mktRet=gtaApi.get_mktRetD()
    ret=gtaApi.get_stockRetD()
    # the volume is measured in millions of dollars as in the paper,
    # here we use million Chinese Yuan
    vol=gtaApi.get_stockVolD()/1000000

    close=gtaApi.get_stockCloseD()

    mktRet,ret,vol=pandasu.get_inter_index([mktRet,ret,vol])
    excessRet=ret.sub(mktRet.iloc[:,0],axis=0)
    sign=np.sign(excessRet)

    monthStarts,monthEnds=pandasu.getMonthStartAndEnd(mktRet)
    monthStarts=monthStarts[1:-1]
    monthEnds=monthEnds[1:-1]

    def _get_validStocks(monthEnd):
        '''
        Stocks with share prices less than $5 and greater than $1000
        at the end of the previous month are filtered out.

        Args:
            monthEnd:

        Returns:

        '''
        closeprice=close.loc[monthEnd,:]
        stocks=closeprice[(5.0<closeprice) & (closeprice<1000.0)].index.tolist()
        return stocks

    gammait=pd.DataFrame()
    for start,end in zip(monthStarts,monthEnds):
        validStocks=_get_validStocks(end)

        retsub=ret.loc[start:end,validStocks]
        volsub=vol.loc[start:end,validStocks]

        excessRetsub=excessRet.loc[start:end,validStocks]
        signsub=sign.loc[start:end,validStocks]

        for stock in validStocks:
            regdf=pd.DataFrame()
            regdf['y']=excessRetsub[stock].shift(-1)#the dependable variable is
            regdf['x1']=retsub[stock]
            regdf['x2']=signsub[stock]*volsub[stock]
            regdf=regdf.dropna(axis=0,how='any')
            if regdf.shape[0]>10:
                #the threshold in the pastor's paper is 15.Since it will filter out a lot of samples,we lower our threshold.
                slope,t,r2,resid=pandasu.reg(regdf)
                gammait.loc[start[:-3],stock]=slope[2]
        print start[:-3]

    gammait=pd.read_csv(os.path.join(idp,'liq.csv'),index_col=0)
    gammait=pandasu.winsorize(gammait,axis=0)
    # TODO:there are some extremely outliers to be filtered out
    # gammait.to_csv(os.path.join(idp,'liq.csv'))

    gammat = gammait.mean(axis=1)

    deltaGammat=pd.Series()
    m1=0
    mts=pd.Series()
    months=gammait.index.tolist()
    delta=gammait-gammait.shift(1)
    for i in range(1,len(months)):
        #months[i] denotes t,and months[i-1] denotes t-1
        tickers=delta.loc[months[i]].dropna().index.tolist()
        date=[m for m in monthEnds if m.startswith(months[i-1])][0]#the end of the month t-1
        if i==1:
            m1=vol.loc[date,tickers].sum()
        #mt is the total value at the end of month t-1 of the stocks included
        #in the average in montht,and month 1 corresponds to the first month.
        mt=vol.loc[date,tickers].sum()
        mts[months[i]]=mt
        deltaGammat[months[i]]=mt/m1*delta.loc[months[i]].mean()
        print months[i]

    regdf=pd.DataFrame()
    regdf['y']=deltaGammat
    regdf['x1']=deltaGammat.shift(1)
    regdf['x2']=mts.shift(1)/m1*gammat.shift(1)
    regdf=regdf.dropna(axis=0,how='any')
    slope,t,r2,resid=pandasu.reg(regdf)
    mut=pd.Series(resid,index=regdf.index)
    lt=mut*1000000#adjust the magnitude of the data,which do not affect the result

    lt=lt.fillna(method='ffill')#there are several NaNs,fill them
    lt.to_csv(os.path.join(idp,'liquidity.csv'))

    eret=pd.read_csv(os.path.join(tmpp,'eret.csv'),index_col=0)
    smb=pd.read_csv(os.path.join(factorRetPath,'2x3_smb.csv'),index_col=0)
    hml=pd.read_csv(os.path.join(factorRetPath,'2x3_hml.csv'),index_col=0)
    rp=pd.read_csv(os.path.join(bdp,'rp.csv'),index_col=0)
    #liquidity sensitivity
    liqSen=pd.DataFrame()

    for count,col in enumerate(eret.columns):
        regdf=pd.DataFrame()
        regdf['y']=eret[col]
        regdf['x1']=lt
        regdf['x2']=smb['smb']
        regdf['x3']=hml['hml']
        regdf['x4']=rp['rp']
        for i in range(60,regdf.shape[0]):
            sub=regdf.iloc[i-60:i,:]
            sub=sub.dropna(axis=0,how='any')
            if sub.shape[0]>36:
                slope,t,r2,resid=pandasu.reg(sub)
                liqSen.loc[regdf.index[i],col]=slope[1]
        print count
        #TODO:using rolling method.
        # pd.rolling_apply(regdf,window=300,func=func,min_periods=150)
        # model=regdf.rolling(window=300,min_periods=150).apply(func)
    liqSen.to_csv(os.path.join(idp,'liqSen.csv'))