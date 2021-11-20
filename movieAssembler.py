import os
import PIL
import cv2

files = []
for file in os.listdir("framesPineGlacier/"):
    if file[0] != ".":
        year = int(file[0:4])
        month = int(file[5:7])
        day = int(file[8:10])
        files.append([file, year, month, day])

def compareValue(f1):
    return f1[1] * 1000**2 + f1[2] * 1000 + f1[3]

files.sort(key = compareValue)
for i,f in enumerate(files):
    files[i] = f[0]

frame = cv2.imread("framesPineGlacier/" + files[0])
height, width, layers = frame.shape

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
fourcc = 0
video = cv2.VideoWriter("pineGlacier.avi", fourcc, 2, (width,height))

for image in files:
    video.write(cv2.imread("framesPineGlacier/" + image))

cv2.destroyAllWindows()
video.release()
