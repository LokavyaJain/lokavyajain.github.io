#Creating the long form FFT file with the data for each of the bins 

#0. Initializing the dictionaries
#These are the columns to be included in each dictionary of each list
dictionarySkeleton = {"Animal Name": "", #all underscores etc. removed. Accounting for repeat measurements done in "measurement number"
                      "Data Group": "", #pre injury, 1 week, 1mA
                      "Location": "",#L1, S2, or nothing 
                      "Measurement Type": "", #stim or non-stim
                      "Measurement Number": "", #repeat measurements for an animal within each location
                      "Overall Measurement Number": "", #repeat measurements across each location
                      "Injury Type": "", #transection or contusion, even with pre injury 
                      "Frequency Bin": "", #ranges from 1 to x
                      "Area Under FFT": "" #area in each range 
}


#1.1
#First, a function that will take in a time series dataframe and produce a list with the area under x bins ranging from (x1,x2) 
#I will define the attributes for the whole file here so they can be quickly changed if needed: 
numberOfBins = 1
binsRange = (0, 0.1)
#Now, I will write the function
def FFTAreaProducer(dataFrame, numberOfBins: int, binsRange: tuple):
    originalDataFrame = dataFrame
    timeDataX = originalDataFrame['Time_s'].tolist()
    originalPressureDataY = originalDataFrame['Pressure_mmHg'].tolist()
    detrended = signal.detrend(originalDataFrame['Pressure_mmHg'], type = 'linear')
    detrendedPressureDataY = detrended.tolist()
    filteredPressureDataY = signal.savgol_filter(detrendedPressureDataY, window_length = 1000, polyorder = 2)

    sampleRate = 1000
    sampleDuration = len(filteredPressureDataY)/sampleRate
    N = len(filteredPressureDataY)
    yf = np.abs(np.fft.fft(filteredPressureDataY))
    xf = np.fft.fftfreq(N, 1/sampleRate)

    xfTemp = xf
    yfTemp = yf

    for x in range (0, len(xf)):
        if xf[x] >= binsRange[1]: 
            cutoffIndex = x
            break
        else:
            continue

    xInterp = np.linspace(start = binsRange[0], stop = xf[cutoffIndex], num = int((binsRange[1] - binsRange[0])*10000))
    xf = xf[0:cutoffIndex]
    yf = yf[0:cutoffIndex]
    for x in range (0, len(xInterp)):
        xInterp[x] = round(xInterp[x], 3)
    xInterp = np.sort(list(set(xInterp)))
    yInterp = np.interp(xInterp, xf, yf)

    rangeIndexList = []
    for x in range(0, numberOfBins):
        firstRangeValue = (x/numberOfBins)*xfTemp[cutoffIndex]
        secondRangeValue = ((x+1)/numberOfBins)*xfTemp[cutoffIndex]
        firstRangeValue = round(firstRangeValue, 3)
        secondRangeValue = round(secondRangeValue, 3)
        for x in range(0, len(xInterp)):
            if firstRangeValue == xInterp[x]:
                firstIndex = x
                break
            else:
                continue
        for x in range(0, len(xInterp)):
            if secondRangeValue == xInterp[x]:
                secondIndex = x
                break
            else:
                continue
        rangeTuple = (firstIndex, secondIndex)
        rangeIndexList.append(rangeTuple)


        
    areaList = []
    for x in range(0, len(rangeIndexList)):
        firstIndex = rangeIndexList[x][0]
        secondIndex = rangeIndexList[x][1]
        tempX = xInterp[firstIndex:secondIndex]
        tempY = yInterp[firstIndex:secondIndex]
        areaUnderGraph = integrate.trapezoid(tempY, tempX)
        areaList.append(areaUnderGraph)

    return areaList

#1.2 FFT peak producer 
#Modelled of function 1.1, it will take in a dataframe, and return a tuple with the x and y coordinates of the highest peak of the FFT
def FFTPeakProducer(dataFrame, binsRange: tuple):
    originalDataFrame = dataFrame
    timeDataX = originalDataFrame['Time_s'].tolist()
    originalPressureDataY = originalDataFrame['Pressure_mmHg'].tolist()
    detrended = signal.detrend(originalDataFrame['Pressure_mmHg'], type = 'linear')
    detrendedPressureDataY = detrended.tolist()
    filteredPressureDataY = signal.savgol_filter(detrendedPressureDataY, window_length = 1000, polyorder = 2)

    sampleRate = 1000
    sampleDuration = len(filteredPressureDataY)/sampleRate
    N = len(filteredPressureDataY)
    yf = np.abs(np.fft.fft(filteredPressureDataY))
    xf = np.fft.fftfreq(N, 1/sampleRate)

    xfTemp = xf
    yfTemp = yf

    for x in range (0, len(xf)):
        if xf[x] >= binsRange[1]: 
            cutoffIndex = x
            break
        else:
            continue

    xInterp = np.linspace(start = binsRange[0], stop = xf[cutoffIndex], num = int((binsRange[1] - binsRange[0])*10000))
    xf = xf[0:cutoffIndex]
    yf = yf[0:cutoffIndex]
    for x in range (0, len(xInterp)):
        xInterp[x] = round(xInterp[x], 3)
    xInterp = np.sort(list(set(xInterp)))
    yInterp = np.interp(xInterp, xf, yf)

    maxY = max(yInterp)
    yInterp = yInterp.tolist()
    maxIndex = yInterp.index(maxY)
    maxX = xInterp[maxIndex]

    return [maxX, maxY]


#2. 
#Then, a function that will handle the syntax issues with the naming of the original non-stim files (1wk vs wk1)
#It will parse through a file path and produce all the desired variables 
#It should work for both non-stim and stim files 
def filePathSyntaxHandler(filePath: str): 
    slashIndices = [x for x, character in enumerate(filePath) if character == "/"]
    startIndex = int(max(slashIndices)+1)
    fileName = filePath[startIndex:-4]

    if fileName[-2:] == "L1" or fileName[-2:] == "S2":
        nameStatus = "stim"
        underscoreIndices = [x for x, character in enumerate(fileName) if character == "_"]
        if underscoreIndices[0] == 0: 
            measurementNumber = 2 #this is the first statistic
            fileName = fileName[1:]
        elif underscoreIndices[0] == 3: 
            measurementNumber = 1
        else:
            print("Error with measurment number quantification")
        underscoreIndices = [x for x, character in enumerate(fileName) if character == "_"]
        animalName = fileName[0:underscoreIndices[0]] #second statistic 
        dataGroup = fileName[(underscoreIndices[0]+1):underscoreIndices[1]] #third statistic
        stimLocation = fileName[(underscoreIndices[1]+1):] #fourth statistic 
        if stimLocation == "S2":
            overallMeasurementNumber = measurementNumber + 2 #fifth statistic
        elif stimLocation == "L1":
            overallMeasurementNumber = measurementNumber
        else: 
            print("Error with OVERALL measurment number quantification")
        depthAndVolume = "2cm_1ml"
        timePoint = dataGroup
        measurementType = "stim"

    else: 
        nameStatus = "non-stim"
        underscoreIndices = [x for x, character in enumerate(fileName) if character == "_"]

        animalName = fileName[0:underscoreIndices[0]]
        depthAndVolume = fileName[(underscoreIndices[0]+1):underscoreIndices[2]]
        stimLocation = None
        measurementNumber = 1
        overallMeasurementNumber = 1
        dataGroup = fileName[underscoreIndices[3]+1:]
        timePoint = dataGroup
        measurementType = "non-stim"

    digit = int(animalName[-2:])
    if digit >= 88:
        injuryType = "Transection"
    elif digit < 88: 
        injuryType = "Contusion"
    else:
        print("Error with injury type identification")

    if len(timePoint) > 3: 
        if timePoint[3] == " ":
            timePoint = timePoint[0:-1]
        
    if timePoint == "1wk":
        dataGroup = "wk1"
    elif timePoint == "2wk":
        dataGroup = "wk2"
    elif timePoint == "3wk":
        dataGroup = "wk3"
    elif timePoint == "4wk":
        dataGroup = "wk4"
    elif timePoint == "5wk" or timePoint == "wk5":
        dataGroup = "wk6"
    elif timePoint == "6wk":
        dataGroup = "wk6"
    elif timePoint == "24hr" or timePoint == "24h" or timePoint == "0hr" or timePoint == "4hr":
        dataGroup = "24h"
    else:
        a = 0

    #print(animalName, dataGroup, depthAndVolume, stimLocation, measurementNumber, overallMeasurementNumber, injuryType)
    return animalName, dataGroup, depthAndVolume, stimLocation, measurementType, measurementNumber, overallMeasurementNumber, injuryType

#3.
#Then, creating a function that will take in a non-stim folder name as an input and produce a list with the fft area for each bin using 
#the FFT area function. 
windowSize = 60000
def nonStimFFTStatsProducer(csvFilePath: str, windowSize: int):
    #Now, I will get the data for the area
    originalDataFrame = pd.read_csv(csvFilePath)
    dataFrameLength = (len(originalDataFrame))
    numberOfWindows = int(np.floor(dataFrameLength/windowSize))
    #this one will have to window the dataframes and handle the multiple windows using function 1
    windowedDataFrames = []
    for x in range (0, numberOfWindows):
        index1 = x*windowSize
        index2 = (x+1)*windowSize
        cutDf = originalDataFrame.iloc[index1:index2]
        windowedDataFrames.append(cutDf)
    allBinAreas = []
    allWindowedPeaksList = []
    for x in range (0, len(windowedDataFrames)):
        dataFrame = windowedDataFrames[x]
        areaList = FFTAreaProducer(dataFrame, numberOfBins, binsRange)
        allBinAreas.append(areaList)
        peakList = FFTPeakProducer(dataFrame, binsRange)
        allWindowedPeaksList.append(peakList)
        
    averagedAreaList = [np.mean(x) for x in list(zip(*allBinAreas))] #this will average all the bins 
    averagedPeakList = [np.mean(x) for x in list(zip(*allWindowedPeaksList))] #this will average all the peaks

    return (averagedAreaList, averagedPeakList)


#4.
#A dictionary that produces a handful of dictionaries
def dictionaryProducer(filePath: str):
    fileDetails = filePathSyntaxHandler(filePath)
    if fileDetails[2] != "2cm_1ml":
        return "Error"
    if fileDetails[4] == 'stim':
        dataFrame = pd.read_csv(filePath)
        areaList = FFTAreaProducer(dataFrame, numberOfBins, binsRange)
        peakCoordinates = FFTPeakProducer(dataFrame, binsRange)
        dictList = [] #This is a list that holds the x dictionaries for the x number of bins 
        for x in range (0, len(areaList)):
            areaDict = {"Animal Name": fileDetails[0], #all underscores etc. removed. Accounting for repeat measurements done in "measurement number"
                      "Data Group": fileDetails[1], #pre injury, 1 week, 1mA
                      "Location": fileDetails[3],#L1, S2, or nothing 
                      "Measurement Type": fileDetails[4], #stim or non-stim
                      "Measurement Number": fileDetails[5],#repeat measurements for an animal within each location
                      "Overall Measurement Number": fileDetails[6], #repeat measurements across each location
                      "Injury Type": fileDetails[7], #transection or contusion, even with pre injury 
                      "Frequency Bin": (int(x)+1), #ranges from 1 to x
                      "Area Under FFT": areaList[x]#area in each range
                       }
            dictList.append(areaDict)
        peakDict = {"Animal Name": fileDetails[0], #all underscores etc. removed. Accounting for repeat measurements done in "measurement number"
                      "Data Group": fileDetails[1], #pre injury, 1 week, 1mA
                      "Location": fileDetails[3],#L1, S2, or nothing 
                      "Measurement Type": fileDetails[4], #stim or non-stim
                      "Measurement Number": fileDetails[5],#repeat measurements for an animal within each location
                      "Overall Measurement Number": fileDetails[6], #repeat measurements across each location
                      "Injury Type": fileDetails[7], #transection or contusion, even with pre injury 
                      "Peak Frequency": peakCoordinates[0], 
                      "Peak Power": peakCoordinates[1]
                    }
        return dictList, peakDict
        gc.collect()
    elif fileDetails[4] == 'non-stim': 
        tupleToUnpack = nonStimFFTStatsProducer(filePath, windowSize)
        areaList = tupleToUnpack[0]
        peakCoordinates = tupleToUnpack[1]
        dictList = [] #This is a list that holds the x dictionaries for the x number of bins 
        for x in range (0, len(areaList)):
            areaDict = {"Animal Name": fileDetails[0], #all underscores etc. removed. Accounting for repeat measurements done in "measurement number"
                      "Data Group": fileDetails[1], #pre injury, 1 week, 1mA
                      "Location": fileDetails[3],#L1, S2, or nothing 
                      "Measurement Type": fileDetails[4], #stim or non-stim
                      "Measurement Number": fileDetails[5],#repeat measurements for an animal within each location
                      "Overall Measurement Number": fileDetails[6], #repeat measurements across each location
                      "Injury Type": fileDetails[7], #transection or contusion, even with pre injury 
                      "Frequency Bin": (int(x)+1), #ranges from 1 to x
                      "Area Under FFT": areaList[x]#area in each range
                       }
            dictList.append(areaDict)
        peakDict = {"Animal Name": fileDetails[0], #all underscores etc. removed. Accounting for repeat measurements done in "measurement number"
                      "Data Group": fileDetails[1], #pre injury, 1 week, 1mA
                      "Location": fileDetails[3],#L1, S2, or nothing 
                      "Measurement Type": fileDetails[4], #stim or non-stim
                      "Measurement Number": fileDetails[5],#repeat measurements for an animal within each location
                      "Overall Measurement Number": fileDetails[6], #repeat measurements across each location
                      "Injury Type": fileDetails[7], #transection or contusion, even with pre injury 
                      "Peak Frequency": peakCoordinates[0], 
                      "Peak Power": peakCoordinates[1]
                    }
        return dictList, peakDict
        gc.collect()
    else: 
        raise ValueError("In dictionary producer function, expected either non-stim or stim measurementType")


folderPath = '/Volumes/KINGSTON/ContusionAnimal_Project/All Raw Data with Stim for FFT Analysis'
allFiles = os.listdir(folderPath)
dictionaries = [dictionaryProducer(folderPath+"/"+x) for x in allFiles if x[0] != "."]

peakDictionaries = [] 
fftDictionaries = []
for x in range (0, len(dictionaries)):
    overAllTuple = dictionaries[x]
    if overAllTuple != "Error": 
        bins = overAllTuple[0]
        peaks = overAllTuple[1]
        fftDictionaries = fftDictionaries + bins
        peakDictionaries.append(peaks)
    else:
        continue

#First, for the FFT bin dictionaries
csvDataFrame = pd.DataFrame(fftDictionaries)
csvDataFrame.to_csv('/Users/lokavyajain/Desktop/Lab_Volunteering/tSCS Data/Analyzed Spreadsheets/All FFT Areas 1 Bins 0.1 Range.csv', index = False)

#Then, for the peak dictionaries 
csvDataFrame = pd.DataFrame(peakDictionaries)
csvDataFrame.to_csv('/Users/lokavyajain/Desktop/Lab_Volunteering/tSCS Data/Analyzed Spreadsheets/All FFT Peaks 1 Bins 0.1 Range.csv', index = False)









#Then, plotting it all: 

 ### Now, visualizing the data that was produced onto a series of violin plots with means and confidence intervals 


csvFilePath = '/Users/lokavyajain/Desktop/Lab_Volunteering/tSCS Data/Analyzed Spreadsheets/All FFT Peaks 5 Bins 0.5 Range.csv'
df = pd.read_csv(csvFilePath)
df = df[df["Data Group"] != '8mA']

plt.figure(figsize = (15, 7))

df = df[df["Measurement Number"] == 1]
#df = df[df["Injury Type"] == "Contusion"]
df = df[(df["Injury Type"] == "Transection") | ((df["Injury Type"] == "Contusion") & (df["Data Group"] == "pre"))]

metric = "Peak Power" 

hue_order = ["pre", "24h", "wk1", "wk2", "wk3", "wk4", "wk6", "0.5mA", "1mA", "1.5mA", "2mA", "2.5mA", "3mA", "4mA", "5mA", "6mA", "7mA"]
ax = plt.gca()

ax = sns.violinplot(data=df, x="Data Group", y=metric, hue="Data Group", 
                 hue_order=hue_order, 
                 order=hue_order, 
                 inner=None, 
                 alpha=0.25)

ax = sns.stripplot(data=df, x='Data Group', y=metric, hue='Data Group', size=5, jitter=True, alpha = 0.5, marker = 'X')


#Now, plotting the statistical differences
# Define comparisons and p-values

comparisons = []
pValues = []

text = (""" contrast    estimate    SE  df t.ratio p.value
 0.5mA - wk1  -166866 36100 217  -4.620  0.0009
 0.5mA - wk3  -168703 36100 217  -4.671  0.0007
 1.5mA - wk1  -184589 36100 217  -5.111  0.0001
 1.5mA - wk3  -186426 36100 217  -5.162  0.0001
 1mA - wk1    -169827 36100 217  -4.702  0.0006
 1mA - wk3    -171664 36100 217  -4.753  0.0005
 2.5mA - wk1  -161750 36500 217  -4.431  0.0019
 2.5mA - wk3  -163587 36500 217  -4.482  0.0016
 3mA - wk1    -138691 36500 217  -3.800  0.0235
 3mA - wk3    -140529 36500 217  -3.850  0.0196
 5mA - wk3    -131259 36500 217  -3.596  0.0488
 6mA - wk1    -142948 36500 217  -3.916  0.0153
 6mA - wk3    -144785 36500 217  -3.967  0.0127
 7mA - wk1    -136732 36900 217  -3.703  0.0333
 7mA - wk3    -138570 36900 217  -3.753  0.0279""")

lines = text.splitlines()

for x in range (1, len(lines)):
    line = lines[x]
    spaces = [index for index, char in enumerate(line) if char == " "]
    dashes = [index for index, char in enumerate(line) if char == "-"]
    firstTerm = str(line[1:spaces[1]])
    secondTerm = str(line[(spaces[2]+1):spaces[3]])
    pValue = (line[(spaces[-1]+1):])
    try: 
        pValue = float(pValue)
    except: 
        pValue = float(0.0001)
    tuple = (firstTerm, secondTerm)
    comparisons.append(tuple)
    pValues.append(pValue)

# Create the annotator
annotator = Annotator(ax, pairs=comparisons, data=df, x="Data Group", y="Peak Frequency", order=hue_order)


# Configure style
annotator.configure(test=None, text_format='star', verbose=2,
                    line_height=0.01,
                    fontsize=7,
                    color='black',
                    use_fixed_offset=True)

# Set your custom p-values separately
annotator.set_pvalues(pValues)

try: 
    ax = ssns.pointplot(data=df, x='Data Group', y=metric, hue = "Data Group",
              color = "black",
              estimator='mean',
              errorbar=('ci', 95),
              linestyle='none',
              capsize=0.2)     # disables line connecting points
#             dodge=True)     # helps if using 'hue')

except: 
    annotator.annotate()


#ax = sns.boxplot(data = df, x = "Data Group", y = "Peak Power", hue = "Data Group", hue_order = hue_order, order = hue_order)

ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)

plt.title(label = "5 Bins with a range of 0-0.5Hz")


plt.savefig("/Users/lokavyajain/Desktop/tempICORDPDF.pdf", format = "pdf", bbox_inches='tight')




import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from statannotations.Annotator import Annotator

# ---- STEP 1: Load your main dataset ----
df = pd.read_csv('/Users/lokavyajain/Desktop/Lab_Volunteering/tSCS Data/Analyzed Spreadsheets/All FFT Areas 1 Bins 0.1 Range.csv')

# ---- STEP 2: Load pairwise comparison results from R ----
pw_df = pd.read_csv('/Users/lokavyajain/Desktop/Lab_Volunteering/R LME Stats Tests/All FFT Areas 1 Bins 0.1 Range pw_df.csv')

# ---- STEP 3: Create comparison pairs automatically ----
# pw_df will have columns like "contrast", "estimate", "p.value", etc.
# In some versions, "contrast" may look like "wk1 - wk2", so we need to split them:
pw_df[["group1", "group2"]] = pw_df["contrast"].str.split(" - ", expand=True)

# Filter to only significant results (p < 0.05)
sig_pw = pw_df[pw_df["p.value"] <= 0.05]

# Create list of tuples for statannotations, e.g. [('wk1', 'wk2'), ('wk1', 'wk3')]
pairs = list(sig_pw[["group1", "group2"]].itertuples(index=False, name=None))

# ---- STEP 4: Plot violin plot ----
plt.figure(figsize=(15, 7))
hue_order = ["pre", "24h", "wk1", "wk2", "wk3", "wk4", "wk6", "0.5mA", "1mA", "1.5mA", "2mA", "2.5mA", "3mA", "4mA", "5mA", "6mA", "7mA"]
ax = plt.gca()

ax = sns.boxplot(data=df, x="Data Group", y="Area Under FFT", hue="Data Group", 
                 hue_order=hue_order, 
                 order=hue_order)

#ax = sns.stripplot(data=df, x='Data Group', y="Area Under FFT", hue='Data Group', size=5, jitter=True, alpha = 0.5, marker = 'X')

ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)


# Create the annotator
annotator = Annotator(ax, pairs, data=df, x="Data Group", y="Area Under FFT", order=hue_order)


# Configure style
annotator.configure(test=None, text_format='star', verbose=2,
                    line_height=0.01,
                    fontsize=7,
                    color='black',
                    use_fixed_offset=True)


annotator.set_pvalues(sig_pw["p.value"].tolist())
annotator.annotate()


# ---- STEP 5: Add significance annotations ----



plt.title("Area Under FFT in Bin 1 (0-0.1Hz)")
plt.tight_layout()


plt.savefig("/Users/lokavyajain/Desktop/tempICORD.pdf", format = "pdf", bbox_inches='tight')






