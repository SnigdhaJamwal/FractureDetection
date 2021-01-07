import os, io
from google.cloud import vision
from google.cloud.vision import types
import pandas as pd

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r"service-account-token.json"

client = vision.ImageAnnotatorClient()

pathname = "D:/App/FractureDetection/static/img/uploads"
filename = "3.jpg"

def is_xray(path):

    # return True
    
    # Remember to set it back to usual before final deployment
    
    try:
        with io.open(path,'rb') as imagefile:
            content = imagefile.read()
            
    except Exception as e:
        print(str(e))
        return False
    
    try:
        image = vision.types.Image(content = content)
        response = client.label_detection(image = image)
        labels = response.label_annotations

        df = pd.DataFrame(columns=['description','score','topicality'])
        for label in labels:
            df = df.append(
                dict(
                    description=label.description,
                    score=label.score,
                    topicality=label.topicality
                ), ignore_index = True
            )
        print(df)
        required_labels = ['X-ray','Medical radiography','Radiography','Radiology','Joint']

        for label in required_labels:
            if df['description'].str.contains(label).any():
                print(label,'found!')
                return True
        else:
            print('Label not found.')
            return False
    except Exception as e:
        return True
    