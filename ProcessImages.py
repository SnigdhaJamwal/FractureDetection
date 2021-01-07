import numpy as np 
import cv2 #this is the main openCV class, the python binding file should be in /pythonXX/Lib/site-packages
from matplotlib import pyplot as plt
from skimage.morphology import disk
import bisect
import skimage.feature
from numba import jit
import skimage
import os
import skimage.io

def imadjust(src, tol=1, vin=[0,255], vout=(0,255)):
    # src : input one-layer image (numpy array)
    # tol : tolerance, from 0 to 100.
    # vin  : src image bounds
    # vout : dst image bounds
    # return : output img

    assert len(src.shape) == 2 ,'Input image should be 2-dims'

    tol = max(0, min(100, tol))

    if tol > 0:
        # Compute in and out limits
        # Histogram
        hist = np.histogram(src,bins=list(range(0,256)),range=(0,256))[0]

        # Cumulative histogram
        cum = hist.copy()
        for i in range(0, 255):
            cum[i-1] 
            hist[i]
            cum[i] = cum[i - 1] + hist[i]

        # Compute bounds
        total = src.shape[0] * src.shape[1]
        low_bound = total * tol / 100
        upp_bound = total * (100 - tol) / 100
        vin[0] = bisect.bisect_left(cum, low_bound)
        vin[1] = bisect.bisect_left(cum, upp_bound)

    # Stretching
    scale = (vout[1] - vout[0]) / (vin[1] - vin[0])
    vs = src-vin[0]
    vs[src<vin[0]]=0
    vd = vs*scale+0.5 + vout[0]
    vd[vd>vout[1]] = vout[1]
    dst = vd

    return dst
    
def process_image(n,f,dir_open,dir_save):
    #os.chdir(dir_open)    
    img = cv2.imread(f,0) #import image
    imgadj=imadjust(img)
    
    imgadj_erode=cv2.erode(imgadj,disk(3))
    imgadj_dilate=cv2.dilate(imgadj,disk(3))
    diff=imgadj_dilate-imgadj_erode    
    imgadj_diff=imgadj-diff
    img_sobel=cv2.Sobel(imgadj_diff,cv2.CV_8U,1,0,ksize=3)+ cv2.Sobel(imgadj_diff,cv2.CV_8U,0,1,ksize=3)
    
    os.chdir(dir_save)    
    cv2.imwrite(str(n)+".png",img_sobel)

dir="C:/ProcessedImages"
    