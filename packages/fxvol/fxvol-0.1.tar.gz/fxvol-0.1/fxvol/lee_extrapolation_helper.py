import numpy as np

# compute extra points (Lee log moneyness)
def computeExtraPoint(pillarStart, volStart, pillarEnd, volEnd, extraPillar, factor, expiry):
    slope = (volEnd - volStart) / (np.sqrt(np.abs(pillarEnd) / expiry) - (np.sqrt(np.abs(pillarStart) / expiry)))
    return factor * slope * (np.sqrt(np.abs(extraPillar) / expiry) - np.sqrt(np.abs(pillarEnd) / expiry)) + volEnd

# compute extra points (Lee log moneyness)
def computeExtraPointDelta(pillarStart, volStart, pillarEnd, volEnd, extraPillar, factor, expiry):
    if extraPillar >= 0.5:
        deltaEnd = deltaAdjustmentLargeDelta(pillarEnd, expiry)
        deltaStart = deltaAdjustmentLargeDelta(pillarStart, expiry)
        deltaExtra = deltaAdjustmentLargeDelta(extraPillar, expiry)
    else:
        deltaEnd = deltaAdjustmentSmallDelta(pillarEnd, expiry)
        deltaStart = deltaAdjustmentSmallDelta(pillarStart, expiry)
        deltaExtra = deltaAdjustmentSmallDelta(extraPillar, expiry)

    slope = (volEnd - volStart) / (deltaEnd - deltaStart)
    return factor * slope * (deltaExtra - deltaEnd) + volEnd

def deltaAdjustmentLargeDelta(delta, expiry):
    if((1 - delta)<=0):
        print(
            "error 1-delta is negative : " + str(1 - delta) + " delta is : " + str(delta) + " for the expiry : " + str(
                expiry))
    return (1 - np.log((1 - delta) / (delta))) / (3.0 * np.sqrt(expiry))


## compute the logmoneyness from the strike
def fromStrikeToLogMoneyness(forward, strike):
    return np.log(strike / forward)


def deltaAdjustmentSmallDelta(delta, expiry):
    if ((1 - delta) <= 0):
        print("error 1-delta is negative : " + str(1 - delta)+" delta is : "+str(delta)+" for the expiry : "+str(expiry))
    return (-1 + np.log((delta) / (1 - delta))) / (np.sqrt(expiry))

# get last points in order to compute the slope in the right wings
def getLastPointsInLogMoneyness(volSmile, smileAxisName, forward):
    pillarRightStart = volSmile.iloc[-2]['smileAxis']
    pillarRightEnd = volSmile.iloc[-1]['smileAxis']
    if (smileAxisName == "strike"):
        pillarRightStart = fromStrikeToLogMoneyness(forward, pillarRightStart)
        pillarRightEnd = fromStrikeToLogMoneyness(forward, pillarRightEnd)

    return pillarRightStart, volSmile.iloc[-2]['volatility'], pillarRightEnd, volSmile.iloc[-1]['volatility']

# get last points in order to compute the slope in the left wings
def getFirstPointsInLogMoneyness(volSmile, smileAxisName, forward):
    pillarLeftStart = volSmile.iloc[1]['smileAxis']
    pillarLeftEnd = volSmile.iloc[0]['smileAxis']
    if (smileAxisName == "strike"):
        pillarLeftStart = fromStrikeToLogMoneyness(forward, pillarLeftStart)
        pillarLeftEnd = fromStrikeToLogMoneyness(forward, pillarLeftEnd)

    return pillarLeftStart, volSmile.iloc[1]['volatility'], pillarLeftEnd, volSmile.iloc[0]['volatility']

