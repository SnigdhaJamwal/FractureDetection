
from joblib import load
import cv2
import os
from skimage.feature import hog
from ProcessImages import process_image
from svm_square_and_resize import make_square, resize_image
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import pandas as pd
import matplotlib.pyplot as plt
import pyrenn
from MultipleGLCM import glcmNN,final_OP,accuracy
import numpy as np
import io
from sklearn.metrics import accuracy_score
from sklearn.svm import SVC

def outputNetwork(f):
    img=cv2.imread(f+"image.png",0)
    process_image(0,f+"image.png",f,f)
    make_square(f+"/0.png")
    resize_image(f+"/0.png")
    features_list=[]
    img = cv2.imread(f+"/0.png",0)
    image_features =hog(img, block_norm='L2-Hys', pixels_per_cell=(16, 16))
    features_list.append(image_features)
    feature_matrix=np.array(features_list)
    ss = StandardScaler()
# run this on our feature matrix
    fracture_stand = ss.fit_transform(feature_matrix)

    pca = PCA(n_components=500)
    # use fit_transform to run PCA on our standardized matrix
    fracture_pca = ss.fit_transform(fracture_stand)

# look at new shape
#print('PCA matrix shape is: ', fracture_pca.shape)
    X = pd.DataFrame(fracture_pca) 
    svm= load("C:/TrainedModels/svm_model_PI12_68.36%.csv")
    y_pred = svm.predict(X) 
    svm_prob=svm.predict_proba(X)[0]
    print(type(svm_prob))

    valid_data=glcmNN(f,1)
    net=pyrenn.loadNN("C:/TrainedModels/glcm_model_1.csv")
    y = pyrenn.NNOut(valid_data.transpose(),net)
    final=0

    glcmOutput = final_OP(y)[0][0]
    SVMOutput = y_pred[0]
    glcm_prob = [0.0, 0.0]

    if glcmOutput == 1:
        glcm_prob = [0.25, 0.75]
    else:
        glcm_prob = [0.75, 0.25]

    '''
    for i,j in zip(final_OP(y),y_pred):
        if i[0]==j==0:
            final=0
        elif i[0]==j==1:
            final=0
        elif j==1:
            final=1
        elif i[0]==0:
            final=0
        
        else:
            final=0
    '''
    
    print("GCLM output:",glcmOutput)
    print("SVM output:",SVMOutput)
    print("GCLM prob:",glcm_prob)
    print("SVM prob:",svm_prob)

    final_prob = [(svm_prob[0]+glcm_prob[0])/2, (svm_prob[1]+glcm_prob[1])/2]
    print('Final prob: ',final_prob)
    if final_prob[0] > 0.5:
        final = 0
    else:
        final = 1

    return final, final_prob[1]

    

