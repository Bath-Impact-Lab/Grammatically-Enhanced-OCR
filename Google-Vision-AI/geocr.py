import cv2
import imutils
import json
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import requests
import time
import os
from base64 import b64encode
from IPython.display import Image
from pylab import rcParams


rcParams['figure.figsize'] = 10, 20

def makeImageData(imgpath):
    img_req = None
    with open(imgpath, 'rb') as f:
        ctxt = b64encode(f.read()).decode()
        img_req = {
            'image': {
                'content': ctxt
            },
            'features': [{
                'type': 'DOCUMENT_TEXT_DETECTION',
                'maxResults': 1
            }]
        }
    return json.dumps({"requests": img_req}).encode()


def requestOCR(url, api_key, imgpath):
    imgdata = makeImageData(imgpath)
    response = requests.post(url,
                             data=imgdata,
                             params={'key': api_key},
                             headers={'Content-Type': 'application/json'})
    return response

def gen_cord(result):
    cord_df = pd.DataFrame(result['boundingPoly']['vertices'])
    x_min, y_min = np.min(cord_df["x"]), np.min(cord_df["y"])
    x_max, y_max = np.max(cord_df["x"]), np.max(cord_df["y"])
    return result["description"], x_max, x_min, y_max, y_min



