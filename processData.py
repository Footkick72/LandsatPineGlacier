from osgeo import gdal
import matplotlib.pyplot as plt
import numpy as np
import os

def processScene(name):
    path = "dataPineGlacier/" + name

    bluePath = path + "_SR_B2.TIF"
    greenPath = path + "_SR_B3.TIF"
    redPath = path + "_SR_B4.TIF"
    #shortWaveInfraredPath = path + "_SR_B6.TIF"

    blueData = gdal.Open(bluePath, gdal.GA_ReadOnly)
    blueBand = blueData.GetRasterBand(1).ReadAsArray()
    greenData = gdal.Open(greenPath, gdal.GA_ReadOnly)
    greenBand = greenData.GetRasterBand(1).ReadAsArray()
    redData = gdal.Open(redPath, gdal.GA_ReadOnly)
    redBand = redData.GetRasterBand(1).ReadAsArray()
    #shortWaveInfraredData = gdal.Open(shortWaveInfraredPath, gdal.GA_ReadOnly)
    #shortWaveInfraredBand = shortWaveInfraredData.GetRasterBand(1).ReadAsArray()

    blueNormalized = (blueBand + 1) * 0.0000275 - 0.2
    greenNormalized = (greenBand + 1) * 0.0000275 - 0.2
    redNormalized = (redBand + 1) * 0.0000275 - 0.2
    #shortWaveInfraredNormalized = (shortWaveInfraredBand + 1) * 0.00341802 + 149.0

    colorView = np.dstack((
                            (redNormalized + 0.2)/1.8000125,
                            (greenNormalized + 0.2)/1.8000125,
                            (blueNormalized + 0.2)/1.8000125
                        ))
    
    return colorView

def getCloudIndex(name):
    path = "dataPineGlacier/" + name + "_MTL.txt"
    f = open(path, "r")
    data = f.read()
    f.close()
    i = data.index("CLOUD_COVER = ") + 14
    clouds = float(data[i:i+5].strip())
    return clouds

def getDate(name):
    path = "dataPineGlacier/" + name + "_MTL.txt"
    f = open(path, "r")
    data = f.read()
    f.close()
    i = data.index("DATE_ACQUIRED = ") + 16
    date = data[i:i+10]
    return date

def getAxis(name):
    path = "dataPineGlacier/" + name + "_MTL.txt"
    f = open(path, "r")
    data = f.read()
    f.close()
    corners = [0,0,0,0]
    for i,corner in enumerate(["UL", "UR", "LL", "LR"]):
        coord = [0,0]
        for j,field in enumerate(["CORNER_" + corner + "_LAT_PRODUCT = ", "CORNER_" + corner + "_LON_PRODUCT = "]):
            k = data.index(field) + 24
            arg = data[k:k+9]
            coord[j] = arg
        corners[i] = coord
    xmin = min(c[0] for c in corners)
    xmax = max(c[0] for c in corners)
    ymin = min(c[1] for c in corners)
    ymax = max(c[1] for c in corners)
    return [xmin, xmax, ymin, ymax]

getDate("LC08_L2SR_002113_20141209_20201016_02_T2")
noiseThreshold = 25
scenes = set()
for file in os.listdir("dataPineGlacier/"):
    if "LC08" in file:
        name = file[:40]
        if getCloudIndex(name) < noiseThreshold:
            scenes.add(name)
print("Found %d non-cloudy scenes"%len(scenes))

for sceneName in scenes:
    img = processScene(sceneName)
    date = getDate(sceneName)
    plt.imshow(img)
    plt.title(date)
    plt.axis(False)
    plt.savefig("framesPineGlacier/" + date)
    plt.clf()
    plt.cla()


#path = "dataPineGlacier/" + sceneName
#bluePath = path + "_SR_B2.TIF"
#blue = gdal.Open("dataPineGlacier/" + sceneName + "_SR_B2.TIF", gdal.GA_ReadOnly)
# Note GetRasterBand() takes band no. starting from 1 not 0
#band = dataset.GetRasterBand(1)
#band = blue.GetRasterBand(1)
#arr = band.ReadAsArray()
#plt.imshow(arr)
#plt.show()
