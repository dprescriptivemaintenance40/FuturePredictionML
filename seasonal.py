# from typing import final
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.ar_model import AutoReg
import numpy as np
import datetime

print("========= Welcome to Dynamic Prescriptive Maintenance =========")
print("===== Copyright © DPM AI Analytics ====")
print ("Process is started please wait")

series = pd.read_csv('Input/FilledValues.csv')


series.set_index('Date')
series.index=pd.to_datetime(series.index, unit='D',origin=min(series['Date']))
result=seasonal_decompose(series['ValueNew'], model='additive', period=365,extrapolate_trend='freq')
resultFinal = pd.concat([result.observed, result.seasonal,result.trend,result.resid],axis=1)
resultFinal.index.name  = "Date"
resultFinal['resses'] =result.seasonal+result.resid
resultFinal['datemonth']  = resultFinal.index.strftime("%m/%d")
datemonth = pd.DataFrame(columns = ['datemonth','average'])
datemonth['datemonth'] = resultFinal['datemonth']
dtmean=resultFinal.groupby(['datemonth'])['resses'].mean()
#print(dtmean)
#plt.show()

Training = resultFinal['ValueNew'].copy()
model = AutoReg(Training, lags=3)
model_fit = model.fit()
predictedValue = model_fit.predict(len(resultFinal), len(resultFinal)+800)
#predictedValue["finalvalue"]=0
#predictedValue['datemonth']  = predictedValue.iloc[:, [0]].strftime("%m/%d")
panda1 = pd.DataFrame({'Date':predictedValue.index, 'ValuePredicted':predictedValue.values})
panda1["datemonth"]= panda1["Date"].dt.strftime("%m/%d")

finalDf = pd.merge(pd.DataFrame(panda1), pd.DataFrame(dtmean), left_on=['datemonth'], 
              right_on= ['datemonth'], how='left')
finalDf["ValueNew"] = finalDf["ValuePredicted"] + finalDf["resses"]
finalDf.set_index('Date', inplace=True)

bigdata = pd.concat([resultFinal,finalDf])
# print(bigdata)
# bigdata.to_csv("FinalOutPut.csv")
#ax = resultFinal.plot()
#finalDf.plot(ax=ax)
cond =  bigdata.index >= '2019-06-10' 
colorsarr = np.where(cond, 'red', 'green')
print(colorsarr)
plt.plot(bigdata.index,bigdata["ValueNew"])
plt.show()
bigdata.to_csv("Output/FinalOutPut.csv")
print (" Process is end, check Output folder for output")