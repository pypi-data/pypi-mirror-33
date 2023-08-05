import pandas as pd
import numpy as np
from .lee_extrapolation_helper import getLastPointsInLogMoneyness, computeExtraPoint, getFirstPointsInLogMoneyness, \
    computeExtraPointDelta, fromStrikeToLogMoneyness
from .plot_helper import plotSmile, plot2Smile


# import marketData from a file into, output : vol surface, expiry array and smile axis
def createAxisFromMd(name):
    vol = pd.read_excel(name)
    expiry = vol[vol.columns[0]]
    smileAxis = np.sort(vol.columns[1:])
    return vol, expiry, smileAxis


# return the smile for a given maturity of a vol surface
def getSmile(volatility, index):
    smileVol = pd.DataFrame()
    smileVol['smileAxis'] = volatility.columns[1:]
    smileVol['volatility'] = volatility.iloc[index][smileVol['smileAxis']].values
    return smileVol.sort_values(by='smileAxis', ascending=True)


# extract a smile from a vol surface for a given maturity
# output is the smile and the plot of it
def creatSmile(maturity, volatility, expiry, expiryList, smileAxisName):
    index = expiryList.index(maturity)
    if (index < 0):
        print("warning index is negative, we set up at the first expiry")
        index = 0
    elif (index >= expiry.size):
        print("warning index greater than the number of expiry, we set up to the last expiry. Max is : " + str(
            expiry.size - 1))
        index = expiry.size - 1

    smileVol = getSmile(volatility, index)
    plotSmile(smileVol, smileAxisName, maturity)
    return smileVol, expiry[index]

##compute the forward rate from the smile axis of the strike and logmoneyness surface
def getForwardRate(smileAxisStrike, smileAxisLogMoneyness):
    return smileAxisStrike[np.where(smileAxisLogMoneyness == 0)][0]

## compute the strike from the logmoneyness
def fromLogMoneynessToStrike(forward, logMoneyness):
    return forward * np.exp(logMoneyness)


def convertStrikeLogMoneyness(value, forward, smileAxisName):
    if (smileAxisName == "strike"):
        return fromStrikeToLogMoneyness(forward, value)
    return value

# return the extreme pillar of the smile
def getExtremePillar(volSmile):
    return volSmile.iloc[0]['smileAxis'], volSmile.iloc[-1]['smileAxis']


# add extra point to the smile
def addExtraPointToSmile(volSmile, extraPillar, extraVol, firstPillar, lastPillar):
    if (extraPillar > lastPillar):
        extraPoint = pd.DataFrame([[extraPillar, extraVol]], columns=volSmile.columns)
        return volSmile.append(extraPoint, ignore_index=True)
    elif (extraPillar < firstPillar):
        extraPoint = pd.DataFrame([[extraPillar, extraVol]], columns=volSmile.columns)
        return pd.concat([extraPoint, volSmile], ignore_index=True)

    return volSmile

# remove points in a symmetric way)
def removePoint(smileVol, nbPoints):
    return smileVol[nbPoints:-nbPoints]


## add points to the smile and plot it
def addPointsAndPlot(NumberOfPoints, fileName, maturity, factor,expiryList, aod, smileAxisName,   forward=1.0, expendRight=1.1,
                     expendLeft=0.9):
    #### creat your surface
    volSurface, expiry, smileAxis = createAxisFromMd(fileName)
    index = expiryList.index(maturity)
    ###take the smaile accroding to the maturity
    smileVol = pd.DataFrame()
    smileVol['smileAxis'] = volSurface.columns[1:]
    smileVol['volatility'] = volSurface.iloc[index][smileVol['smileAxis']].values
    expiryVal = expiry[index] - aod
    ##get extremePillar
    firstPillar, lastPillar = getExtremePillar(smileVol)
    ##add extra point log linear (symmetric right/left)
    pointRight = np.logspace(1, 1.25, NumberOfPoints + 1, endpoint=False)
    pointLeft = -np.logspace(1, 1.25, NumberOfPoints + 1, endpoint=False)
    if (smileAxisName == "strike"):
        pointRight = np.linspace(lastPillar, expendRight * lastPillar, NumberOfPoints + 1, endpoint=False)
        pointLeft = np.linspace(firstPillar, expendLeft * firstPillar, NumberOfPoints + 1, endpoint=False)

    pillarRightStart, volRightStart, pillarRightEnd, volRightEnd = getLastPointsInLogMoneyness(smileVol, smileAxisName,
                                                                                               forward)
    pillarLeftStart, volLeftStart, pillarLeftEnd, volLeftEnd = getFirstPointsInLogMoneyness(smileVol, smileAxisName,
                                                                                            forward)
    for i in np.arange(NumberOfPoints + 1):
        extraVol = computeExtraPoint(pillarRightStart, volRightStart, pillarRightEnd, volRightEnd,
                                     convertStrikeLogMoneyness(pointRight[i], forward, smileAxisName), factor,
                                     expiryVal)
        smileVol = addExtraPointToSmile(smileVol, pointRight[i], extraVol, firstPillar, lastPillar)
        extraVol = computeExtraPoint(pillarLeftStart, volLeftStart, pillarLeftEnd, volLeftEnd,
                                     convertStrikeLogMoneyness(pointLeft[i], forward, smileAxisName), factor, expiryVal)
        smileVol = addExtraPointToSmile(smileVol, pointLeft[i], extraVol, firstPillar, lastPillar)
    plotSmile(smileVol, smileAxisName, maturity)


# remove points in the smile and build it
def removePointsAndPlot(nbPoints, fileName, maturity, factor, expiryList,aod, smileAxisName, forward=1.0):
    #### creat your surface
    volSurface, expiry, smileAxis = createAxisFromMd(fileName)
    index = expiryList.index(maturity)
    ###take the smaile accroding to the maturity
    smileVol = pd.DataFrame()
    smileVol['smileAxis'] = volSurface.columns[1:]
    smileVol['volatility'] = volSurface.iloc[index][smileVol['smileAxis']].values
    expiryVal = expiry[index] - aod
    ##get extremePillar
    newVol = removePoint(smileVol, nbPoints)
    firstPillar, lastPillar = getExtremePillar(newVol)
    pillarRightStart, volRightStart, pillarRightEnd, volRightEnd = getLastPointsInLogMoneyness(newVol, smileAxisName,
                                                                                               forward)
    pillarLeftStart, volLeftStart, pillarLeftEnd, volLeftEnd = getFirstPointsInLogMoneyness(newVol, smileAxisName,
                                                                                            forward)
    for i in np.arange(nbPoints):
        pointRight = smileVol.iloc[-i - 1]['smileAxis']
        extraVol = computeExtraPoint(pillarRightStart, volRightStart, pillarRightEnd, volRightEnd,
                                     convertStrikeLogMoneyness(pointRight, forward, smileAxisName), factor, expiryVal)
        newVol = addExtraPointToSmile(newVol, pointRight, extraVol, firstPillar, lastPillar)
        pointLeft = smileVol.iloc[i]['smileAxis']
        extraVol = computeExtraPoint(pillarLeftStart, volLeftStart, pillarLeftEnd, volLeftEnd,
                                     convertStrikeLogMoneyness(pointLeft, forward, smileAxisName), factor, expiryVal)
        newVol = addExtraPointToSmile(newVol, pointLeft, extraVol, firstPillar, lastPillar)
    newVol = newVol.sort_values(by=['smileAxis'], ascending=True)
    plot2Smile(newVol, smileVol, smileAxisName, maturity)


### create point for delta
def addPointsAndPlotDelta(NumberOfPoints, fileName, maturity, factor, expiryList,aod, smileAxisName, forward=1.0, expendRight=1.1,
                          expendLeft=0.1):
    #### creat your surface
    volSurface, expiry, smileAxis = createAxisFromMd(fileName)
    index = expiryList.index(maturity)
    ###take the smaile accroding to the maturity
    smileVol = pd.DataFrame()
    smileVol['smileAxis'] = volSurface.columns[1:]
    smileVol['volatility'] = volSurface.iloc[index][smileVol['smileAxis']].values
    smileVol = smileVol.sort_values(by="smileAxis", ascending=True)
    expiryVal = expiry[index] - aod
    ##get extremePillar
    firstPillar, lastPillar = getExtremePillar(smileVol)
    ##add extra point log linear (symmetric right/left)
    pointRight = np.linspace(lastPillar, expendRight * lastPillar   , NumberOfPoints + 1, endpoint=True)
    pointLeft = np.linspace(firstPillar, expendLeft * firstPillar, NumberOfPoints + 1, endpoint=True)
    pillarRightStart, volRightStart, pillarRightEnd, volRightEnd = getLastPointsInLogMoneyness(smileVol, smileAxisName,
                                                                                               forward)
    pillarLeftStart, volLeftStart, pillarLeftEnd, volLeftEnd = getFirstPointsInLogMoneyness(smileVol, smileAxisName,
                                                                                            forward)
    for i in np.arange(NumberOfPoints + 1):
        extraVol = computeExtraPointDelta(pillarRightStart, volRightStart, pillarRightEnd, volRightEnd, pointRight[i],
                                          factor, expiryVal)
        smileVol = addExtraPointToSmile(smileVol, pointRight[i], extraVol, firstPillar, lastPillar)
        extraVol = computeExtraPointDelta(pillarLeftStart, volLeftStart, pillarLeftEnd, volLeftEnd, pointLeft[i],
                                          factor, expiryVal)
        smileVol = addExtraPointToSmile(smileVol, pointLeft[i], extraVol, firstPillar, lastPillar)
    plotSmile(smileVol, smileAxisName, maturity)

# remove points in the smile and build it
def removePointsAndPlotDelta(nbPoints, fileName, maturity, factor, expiryList,aod, smileAxisName, forward=1.0):
    #### creat your surface
    volSurface, expiry, smileAxis = createAxisFromMd(fileName)
    index = expiryList.index(maturity)
    ###take the smaile accroding to the maturity
    smileVol = pd.DataFrame()
    smileVol['smileAxis'] = volSurface.columns[1:]
    smileVol['volatility'] = volSurface.iloc[index][smileVol['smileAxis']].values
    smileVol = smileVol.sort_values(by="smileAxis", ascending=True)
    expiryVal = expiry[index] - aod
    ##get extremePillar
    newVol = removePoint(smileVol, nbPoints)
    firstPillar, lastPillar = getExtremePillar(newVol)
    pillarRightStart, volRightStart, pillarRightEnd, volRightEnd = getLastPointsInLogMoneyness(newVol, smileAxisName,
                                                                                               forward)
    pillarLeftStart, volLeftStart, pillarLeftEnd, volLeftEnd = getFirstPointsInLogMoneyness(newVol, smileAxisName,
                                                                                            forward)
    for i in np.arange(nbPoints):
        pointRight = smileVol.iloc[-i - 1]['smileAxis']
        extraVol = computeExtraPointDelta(pillarRightStart, volRightStart, pillarRightEnd, volRightEnd, pointRight,
                                          factor, expiryVal)
        newVol = addExtraPointToSmile(newVol, pointRight, extraVol, firstPillar, lastPillar)
        pointLeft = smileVol.iloc[i]['smileAxis']
        extraVol = computeExtraPointDelta(pillarLeftStart, volLeftStart, pillarLeftEnd, volLeftEnd, pointLeft, factor,
                                          expiryVal)
        newVol = addExtraPointToSmile(newVol, pointLeft, extraVol, firstPillar, lastPillar)
    newVol = newVol.sort_values(by=['smileAxis'], ascending=True)
    plot2Smile(newVol, smileVol, smileAxisName, maturity)