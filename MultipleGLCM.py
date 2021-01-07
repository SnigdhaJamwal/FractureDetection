import cv2
import numpy as np
from matplotlib import pyplot as plt
from xtract_features.glcms import *
#from filenameGenerator import generateFilenames
import pyrenn
import math

def glcmNN(f,n):
    
    train_data=np.empty([1,48])
    for i in range(0,n):
        img = cv2.imread(f+str(i)+".png",0)       
        feats = glcm(img)
        _all = feats.glcm_all().flatten()
        train_data=np.vstack((train_data,_all))
    train_data=np.delete(train_data,0,0)
    print(train_data.shape)
    return train_data

def trainGclmNN(train_data,f):
    fname,target_OP=generateFilenames(f)
    target_OP=np.array(target_OP)
    net=pyrenn.CreateNN([48,20,20,1])
    #target_OP=np.zeros((1,n))
    
    net=pyrenn.train_LM(train_data.transpose(),np.array(target_OP),net,k_max=500,E_stop=0.5,verbose=True)
    y = pyrenn.NNOut(train_data.transpose(),net)
    for i,j in zip(final_OP(y),target_OP.transpose()):
        print(i,j)
    accuracy(final_OP(y),target_OP.transpose())

    return net
def final_OP(y):
    final_y=[]
    for i in y:
        if math.isclose(i,1) or i>0.7:
            final_y.append([1])
        else:
            final_y.append([0])
    return final_y
def accuracy(y,exp_y):
    print("Total outputs=",len(y))
    tp=tn=fp=fn=0
    n=0
    for i,j in zip(y,exp_y):
        if i==j:
            n=n+1
        #print(i)
        #print(j)
        if j==0 and i[0]==0:
            tn=tn+1
        elif j==0 and i[0]==1:
            fp=fp+1
        elif j==1 and i[0]==0:
            fn=fn+1
        elif j==1 and i[0]==1:
            tp=tp+1
    print("Correct outputs",n)
    print("True positive",tp)
    print("True negative",tn)
    print("False positive",fp)
    print("False negative",fn)

    

#ytest = pyrenn.NNOut(Ptest,glcmNN("C:/MURA-v1.1/MURA-v1.1/train/XR_FOREARM/"))
#print(type(ytest))

#x=pyrenn.loadNN("C:/GLCM_LM.csv")