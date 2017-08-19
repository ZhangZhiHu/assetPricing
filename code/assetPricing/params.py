#-*-coding: utf-8 -*-
#author:tyhj
#params.py 2017/8/15 17:40
import os
'''
weight:tradable market value

capm:rp
ff3:rp,smb,hml
ff5:rp,smb,hml,rmw,cma

'''



#project directory
directory=r'D:\quantDb\researchTopics\assetPricing'

#source data path
sp=r'D:\quantDb\sourceData\gta\data\csv'

#paths
bdp=os.path.join(directory,'baseData')#base data
idp=os.path.join(directory,'indicator')#indicator repository
fdp=os.path.join(directory,'factor')#factor return time series
tmpp=os.path.join(directory,'tmp')#tmp data
indicatorIdPath=os.path.join(directory,'indicatorId')#used to store the port Id
portIdPath=os.path.join(directory,'portId')#used to store the Id of the intersection ports
portRetPath=os.path.join(directory,'portRet')#store the return of ports
portEretPath=os.path.join(directory,'portEret')#store the excess return
portEretFigPath=os.path.join(directory,'portEretFig')#fig of the excess return
factorRetPath=os.path.join(directory,'factorRet')#store the return of the factors
validatePath=os.path.join(directory,'validate')#store the validation results
regressPath=os.path.join(directory,'regress')#store the regression results
grsPath=os.path.join(directory,'GRS')


def initialize():
    #create neccessary directorys to store data
    for d in [directory,bdp,idp,fdp,tmpp,
              indicatorIdPath,portIdPath,portRetPath,
              portEretPath,portEretFigPath,
              factorRetPath,validatePath,
              regressPath,grsPath]:
        if not os.path.exists(d):
            os.makedirs(d)








