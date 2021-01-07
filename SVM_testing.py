from joblib import load
import cv2
import os
from skimage.feature import hog
from ProcessImages import process_image
from svm_square_and_resize import make_square, resize_image
print('Import done.')

svm = load('../TrainedModels/svm_model_PI11_71.18%.csv')
#os.chdir('D:/CMS/final-year-project/Data/MURA-v1.1/MURA-v1.1/valid/XR_FOREARM/patient11214/study1_negative')
#folder = 'D:/CMS/final-year-project/App/FractureDetection/static/img/uploads/2020_02_13_21_35_46_269479_1/'

def testSVM(folder):
    os.chdir(folder)

    process_image(1,"image.png",folder,folder)
    make_square(folder+'1.png')
    resize_image(folder+'1.png')

    print('Image processed.')

    image = cv2.imread('1.png',0)
    color_features = image.flatten()
    hog_features = hog(image, block_norm = 'L2-Hys', pixels_per_cell=(16,16))
    hog_features = hog_features.reshape(1,-1)
    output = svm.predict(hog_features)
    prob = svm.predict_proba(hog_features)
    print(output)
    print(prob)
    return output,prob