#-*-coding: utf-8 -*-
#author:tyhj
#main.py 2017/8/15 15:05

import os
import pandas as pd
import numpy as np
from itertools import combinations

from zht.util import mathu
from zht.util import pandasu
from zht.util.dfFilter import filterDf
from zht.util.statu import GRS_test

from tools import get_3dline,get_3dbar
from params import *


def get_indicatorId(name,param):
    '''

    Args:
        name:name of financial indicators
        param: an int number or a list of breakpoints such as [0.3,0.7]

    Returns:

    '''
    if not os.path.exists(indicatorIdPath):
        os.makedirs(indicatorIdPath)

    p=os.path.join(indicatorIdPath,'%s_%s.csv'%(name,param))
    if os.path.exists(p):
        ids=pd.read_csv(p,index_col=0)
        return ids
    else:
        df=pd.read_csv(os.path.join(tmpp,name+'.csv'),index_col=0)
        nfc=pd.read_csv(os.path.join(bdp,'nfc.csv'),index_col=0)['Stkcd'].values
        nfc=[str(n) for n in nfc]
        cols=[s for s in df.columns if s in nfc]
        df=df[cols]

        ids=pd.DataFrame(columns=df.columns)
        for month in df.index.tolist():
            sub = df.loc[month].to_frame()
            sub = sub.dropna()
            sub['id'] = mathu.getPortId(sub, param)
            ids.loc[month] = sub['id']
            print month
        ids.to_csv(p)
        return ids

def get_portId(vars,model):
    '''
    get the id for the intersection port

    Args:
        vars:a list or tuple like ['size','op']
        model:'2x2','2x3','2x4x4','2x2x2x2'

    Returns:

    '''
    if not len(vars)==len(model.split('x')):
        raise ValueError('vars do not match the model')

    p=os.path.join(portIdPath,'%s_%s.csv'%(model,'_'.join(vars)))
    # path = os.path.join(dp, 'portId_%s_%s.csv' % ('_'.join(vars), model))
    if os.path.exists(p):
        portId = pd.read_csv(p, index_col=0)
        return portId
    else:
        if model=='2x3':
            id1=get_indicatorId(vars[0],2)
            id2=get_indicatorId(vars[1],3)
            id1, id2 = pandasu.get_inter_frame([id1,id2])
            portId = id1 * 10 + id2
            portId.to_csv(p)
            return portId
        elif model=='2x2':
            id1=get_indicatorId(vars[0],2)
            id2=get_indicatorId(vars[1],2)
            id1, id2 = pandasu.get_inter_frame([id1,id2])
            portId = id1 * 10 + id2
            portId.to_csv(p)
            return portId
        elif model=='5x5':
            id1=get_indicatorId(vars[0],5)
            id2=get_indicatorId(vars[1],5)
            id1, id2 = pandasu.get_inter_frame([id1,id2])
            portId = id1 * 10 + id2
            portId.to_csv(p)
            return portId
        elif model=='2x4x4':
            id1=get_indicatorId(vars[0],2)
            id2=get_indicatorId(vars[1],4)
            id3=get_indicatorId(vars[2],4)
            id1,id2,id3=pandasu.get_inter_frame([id1,id2,id3])
            portId=id1*100+id2*10+id3
            portId.to_csv(p)
            return portId
        elif model=='2x2x2x2':
            id1=get_indicatorId(vars[0],2)
            id2=get_indicatorId(vars[1],2)
            id3=get_indicatorId(vars[2],2)
            id4=get_indicatorId(vars[3],2)
            id1,id2,id3,id4=pandasu.get_inter_frame([id1,id2,id3,id4])
            portId=id1*1000+id2*100+id3*10+id4
            portId.to_csv(p)
            return portId

def get_portRet(vars,model):
    '''

    Args:
        vars: as params in function get_portId
        model:

    Returns:

    '''
    if not len(vars)==len(model.split('x')):
        raise ValueError('vars do not match the model')

    path=os.path.join(portRetPath,'%s_%s.csv'%(model,'_'.join(vars)))
    if os.path.exists(path):
        return pd.read_csv(path,index_col=0)
    else:
        portId=get_portId(vars,model).T
        ret=pd.read_csv(os.path.join(bdp,'ret.csv'),index_col=0)
        weight=pd.read_csv(os.path.join(bdp,'weight.csv'),index_col=0)

        ports=np.sort([p for p in portId.iloc[:,-1].unique() if not np.isnan(p)])

        portRet=pd.DataFrame()
        for month in portId.columns.tolist():
            year=month[:4]
            validmonths = [year + '-0' + str(i) for i in range(7, 10)]
            validmonths += [year + '-1' + str(i) for i in range(3)]
            validmonths += [str(int(year) + 1) + '-0' + str(i) for i in range(1, 7)]

            for port in ports:
                stocks=portId[portId[month]==port].index.tolist()
                for validmonth in validmonths:
                    if validmonth in ret.index.tolist():
                        try:#There may no intersection stocks between ret columns and stocks,especially at the start of the 1990s
                            tmp=pd.DataFrame()
                            tmp['ret']=ret.loc[validmonth,stocks]
                            tmp['weight']=weight.loc[validmonth,stocks]
                            tmp=tmp.dropna(axis=0,how='any')
                            pr=pandasu.mean_self(tmp,'ret','weight')
                            portRet.loc[validmonth,port]=pr
                        except KeyError:
                            portRet.loc[validmonth,port]=np.NaN
                    else:
                        portRet.loc[validmonth,port]=np.NaN
            print month
        portRet=portRet.dropna(axis=0,how='any')
        portRet.to_csv(path)

        return portRet

def cal_portRet():
    for var in ['btm','op','inv']:
        vars=['size',var]
        get_portRet(vars,'2x2')
        get_portRet(vars,'2x3')
        get_portRet(vars,'5x5')
        print var


    for vars in [['size', 'btm', 'op'], ['size', 'btm', 'inv'], ['size', 'op', 'inv']]:
        get_portRet(vars, '2x4x4')
        print vars

    vars = ['size', 'btm', 'op', 'inv']
    get_portRet(vars, '2x2x2x2')

def get_portEret(vars,model):
    path=os.path.join(portEretPath,'%s_%s.csv'%(model,'_'.join(vars)))
    portRet=get_portRet(vars,model)
    rf=pd.read_csv(os.path.join(bdp,'rf.csv'),index_col=0)
    portEret=portRet.sub(rf['rf'],axis=0)
    portEret=portEret.dropna(axis=0,how='any')
    portEret.to_csv(path)
    return portEret

def cal_portErets():
    for var in ['btm', 'op', 'inv']:
        vars = ['size', var]
        get_portEret(vars, '5x5')

    for vars in [['size', 'btm', 'op'], ['size', 'btm', 'inv'], ['size', 'op', 'inv']]:
        get_portEret(vars, '2x4x4')


#ff5 table1
def get_eret_fig():
    model='5x5'
    combs=combinations(['size','btm','op','inv'],2)
    for vars in combs:
        portEret=get_portEret(vars,model)
        lineFig=get_3dline(portEret,vars[0],vars[1])
        barFig=get_3dbar(portEret,vars[0],vars[1])
        lineFig.savefig(os.path.join(portEretFigPath,'%s_%s_0.png'%(model,'_'.join(vars))))
        barFig.savefig(os.path.join(portEretFigPath,'%s_%s_1.png'%(model,'_'.join(vars))))

def get_factorRet_2x3():
    model='2x3'
    vars=['size','btm','op','inv']
    factorName=['smb','hml','rmw','cma']
    dd={a:b for a,b in zip(vars,factorName)}

    #TODO:think about weighted average rather than equal weighted
    def func1(x):#factor return
        return (x[13]+x[23])/2-(x[11]+x[21])/2
    def func2(x):#smb
        return (x[11]+x[12]+x[13])/3-(x[21]+x[22]+x[23])/3

    smbs=pd.DataFrame()
    for var in ['btm','op','inv']:
        vars=['size',var]
        portRet=get_portRet(vars,model)

        portRet.columns=[int(float(col)) for col in portRet.columns]
        fr=portRet.apply(func1,axis=1)
        if var=='inv':
            fr=-fr
        fr=fr.to_frame()
        fr.columns=[dd[var]]
        fr.to_csv(os.path.join(factorRet,'%s_%s.csv'%(model,dd[var])))

        smbs[var]=portRet.apply(func2,axis=1)

    SMB=smbs.mean(axis=1)#average the smbs to get SMB
    SMB=SMB.to_frame()
    SMB.columns=['smb']
    SMB.to_csv(os.path.join(factorRet,'%s_%s.csv'%(model,dd['size'])))

def get_factorRet_2x2():
    model='2x2'
    vars=['size','btm','op','inv']
    factorName=['smb','hml','rmw','cma']
    dd={a:b for a,b in zip(vars,factorName)}

    #TODO:think about weighted average rather than equal weighted
    def func1(x):#factor return
        return (x[12]+x[22])/2-(x[11]+x[21])/2
    def func2(x):#smb
        return (x[11]+x[12])/2-(x[21]+x[22])/2

    smbs=pd.DataFrame()
    for var in ['btm','op','inv']:
        vars=['size',var]
        portRet=get_portRet(vars,model)

        portRet.columns=[int(float(col)) for col in portRet.columns]
        fr=portRet.apply(func1,axis=1)
        if var=='inv':
            fr=-fr
        fr=fr.to_frame()
        fr.columns=[dd[var]]
        fr.to_csv(os.path.join(factorRet,'%s_%s.csv'%(model,dd[var])))

        smbs[var]=portRet.apply(func2,axis=1)

    SMB=smbs.mean(axis=1)#average the smbs to get SMB
    SMB=SMB.to_frame()
    SMB.columns=['smb']
    SMB.to_csv(os.path.join(factorRet,'%s_%s.csv'%(model,dd['size'])))

def get_factorRet_2x2x2x2():
    model = '2x2x2x2'
    vars = ['size', 'btm', 'op', 'inv']
    factorName = ['smb', 'hml', 'rmw', 'cma']
    dd = {a: b for a, b in zip(vars, factorName)}

    portRet=get_portRet(vars,model)
    portRet.columns=[int(float(col)) for col in portRet.columns]

    pns=portRet.columns.tolist()
    pns=sorted(pns)

    for var in vars:
        ind=vars.index(var)
        subport1=[p for p in pns if str(p)[ind]=='1']
        subport2=[p for p in pns if str(p)[ind]=='2']

        ret1=portRet[subport1].mean(axis=1)
        ret2=portRet[subport2].mean(axis=1)

        fr=ret2-ret1
        if var in ['size','inv']:
            fr=-fr
        fr=fr.to_frame()
        fr.columns=[dd[var]]
        fr.to_csv(os.path.join(factorRet,'%s_%s.csv'%(model,dd[var])))

def _validate_ff5_factorRet():
    tbname='STK_MKT_FivefacMonth'
    df=pd.read_csv(os.path.join(sp,tbname+'.csv'))
    q='MarkettypeID == P9709'
    df=filterDf(df,q)
    df=df.set_index('TradingMonth')

    typeDict={1:'2x3',2:'2x2',3:'2x2x2x2'}

    for k,v in typeDict.iteritems():
        smb=df[df['Portfolios']==k]['SMB1'].to_frame()
        smb['mysmb']=pd.read_csv(os.path.join(factorRetPath,'%s_smb.csv'%v),index_col=0)['smb']

        hml=df[df['Portfolios']==k]['HML1'].to_frame()
        hml['myhml']=pd.read_csv(os.path.join(factorRetPath,'%s_hml.csv'%v),index_col=0)['hml']

        rmw=df[df['Portfolios']==k]['RMW1'].to_frame()
        rmw['myrmw']=pd.read_csv(os.path.join(factorRetPath,'%s_rmw.csv'%v),index_col=0)['rmw']

        cma=df[df['Portfolios']==k]['CMA1'].to_frame()
        cma['mycma']=pd.read_csv(os.path.join(factorRetPath,'%s_cma.csv'%v),index_col=0)['cma']

        rp=df[df['Portfolios']==k]['RiskPremium1'].to_frame()
        rp['myrp']=pd.read_csv(os.path.join(bdp,'rp.csv'),index_col=0)['rp']

        direc=os.path.join(validatePath,'%s'%v)
        if not os.path.exists(direc):
            os.makedirs(direc)

        smb.dropna(axis=0).cumsum().plot().get_figure().savefig(os.path.join(direc,'smb.png'))
        hml.dropna(axis=0).cumsum().plot().get_figure().savefig(os.path.join(direc,'hml.png'))
        rmw.dropna(axis=0).cumsum().plot().get_figure().savefig(os.path.join(direc,'rmw.png'))
        cma.dropna(axis=0).cumsum().plot().get_figure().savefig(os.path.join(direc,'cma.png'))
        rp.dropna(axis=0).cumsum().plot().get_figure().savefig(os.path.join(direc,'rp.png'))

def regress():
    factors=['rp','smb','hml','rmw','cma']
    combs=[]
    for i in range(1,len(factors)+1):
        combs+=list(combinations(factors,i))

    fns=os.listdir(portEretPath)

    grsData=[]
    for model in ['2x3','2x2','2x2x2x2']:
        for fn in fns:
            port=fn[:-4]
            dv=pd.read_csv(os.path.join(portEretPath,fn),index_col=0) #dependent variable

            for comb in combs:
                iv = pd.DataFrame()#independent variables
                for factor in comb:
                    if factor=='rp':
                        iv['rp'] = pd.read_csv(os.path.join(bdp, 'rp.csv'), index_col=0)['rp']
                    else:
                        iv[factor]=pd.read_csv(os.path.join(factorRetPath,'%s_%s.csv'%(model,factor)),index_col=0)[factor]

                dv=dv.dropna(axis=0,how='any')
                iv=iv.dropna(axis=0,how='any')

                dv,iv=pandasu.get_inter_index([dv,iv])

                SLOPE = pd.DataFrame(columns=['constant'] + iv.columns.tolist())
                T = pd.DataFrame(columns=['constant'] + iv.columns.tolist())
                R2 = pd.DataFrame(columns=['r2'])
                RESID = pd.DataFrame()

                for col in dv.columns.tolist():
                    df = pd.DataFrame()
                    df[col] = dv[col]
                    df[iv.columns.tolist()] = iv
                    if df.shape[0] > iv.shape[1] + 1:  # make sure that the number of samples is larger than the number of factors plus one.
                        slope, t, r2, resid = pandasu.reg(df)
                        SLOPE.loc[col] = slope
                        T.loc[col] = t
                        R2.loc[col] = r2
                        RESID[col] = pd.Series(resid, index=df.index)

                #directory
                direc = os.path.join(regressPath, model, port,str(len(comb))+'_'+'_'.join(comb))
                if not os.path.exists(direc):
                    os.makedirs(direc)

                SLOPE.to_csv(os.path.join(direc,'slope.csv'))
                T.to_csv(os.path.join(direc,'t.csv'))
                R2.to_csv(os.path.join(direc,'r2.csv'))
                RESID.to_csv(os.path.join(direc,'resid.csv'))

                RESID=RESID.as_matrix()
                alpha=np.mat(SLOPE['constant']).T
                factor=iv.as_matrix()
                GRS,pvalue=GRS_test(factor,RESID,alpha)


                grsData.append([model,fn,comb,GRS,pvalue])
                print model,fn,comb,GRS,pvalue

    grsDf=pd.DataFrame(grsData,columns=['model','fn','comb','GRS','pvalue'])
    grsDf.to_csv(os.path.join(grsPath,'grsDf.csv'))

    print 'regress finished!'

def factor_correlation():
    fns=os.listdir(factorRetPath)
    df=pd.DataFrame()
    for fn in fns:
        factor=pd.read_csv(os.path.join(factorRetPath,fn),index_col=0).iloc[:,0]
        df[fn[:-4]]=factor
    corr=df.corr()
    corr.to_csv(os.path.join(directory,'factorCorr.csv'))







