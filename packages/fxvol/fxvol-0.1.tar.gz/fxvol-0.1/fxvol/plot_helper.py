import matplotlib.pyplot as plt

#plot one smile
def plotSmile(volSmile, smileAxisName, expiry):
    plt.subplots()
    plt.plot(volSmile['smileAxis'], volSmile['volatility'])
    plt.xlabel(smileAxisName)
    plt.ylabel('volatility')
    plt.title('smile '+ smileAxisName+' : expiry '+expiry)

#plot 2 smiles
def plot2Smile(newSmile, volSmile, smileAxisName, expiry):
    plt.plot(volSmile['smileAxis'], volSmile['volatility'], label="original curve")
    plt.plot(volSmile['smileAxis'], newSmile['volatility'], label="extrapolated")
    plt.xlabel(smileAxisName)
    plt.ylabel('volatility')
    plt.title('smile '+ smileAxisName+' : expiry '+expiry)
    plt.legend()
    plt.show()