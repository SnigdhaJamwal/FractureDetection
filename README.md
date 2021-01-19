# FractureDetection

The aim of the project is to use Image Processing along with Supervised Learning algorithms to automate fracture detection in the forearm from X-ray images. The developed tool will be able to classify the untested digital X-rays through a web application where a user can upload digital X-ray images.
The given tool first segments the bone region of an X-ray image from its surrounding flesh region and other noise present in it and then generates the bone-contour which is used to extract the features of interest from the image and implement various existing algorithms trained on cleaned MURA (musculoskeletal radiographs) dataset on the processed image and give the final result based on a random forest approach.
