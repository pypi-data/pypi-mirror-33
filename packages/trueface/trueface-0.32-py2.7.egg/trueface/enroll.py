import requests
import base64
import json
import time
import os
import numpy as np
import cv2
import argparse
import traceback
import sys


def get_features(image):
    """Get features from gpu server"""
    url = "http://54.80.111.222:18080/get-features"
    data = {
        "source":{"data":base64.b64encode(get_string_from_cv2(image))},
    }

    request = requests.post(url, data=json.dumps(data))

    print request.text
    try:
        return np.frombuffer(
            base64.decodestring(
                request.json()['encoding']), dtype=np.float32)
    except Exception:
        return None

def get_string_from_cv2(image):
    """Loads images and calls face encodings"""
    return cv2.imencode('.jpg', cv2.imread(image, 1))[1].tostring()


def main():
    data_folder = sys.argv[1]
    data_csv_to_save_to = sys.argv[2] + "/features.csv"
    label_csv_to_save_to = sys.argv[2] + "/labels.csv"

    print sys.argv[1]
    print sys.argv[2]

    for file in [data_csv_to_save_to, label_csv_to_save_to]:
        f = open(file, "w+")
        f.truncate()
        f.close()

    for identity in os.listdir(data_folder):
        if identity == '.DS_Store': continue

        for image in os.listdir(data_folder + identity):
            if image == '.DS_Store': continue
            try:

                raw = get_features(data_folder+identity+'/'+image)
                if raw is None:
                    continue
                raw = raw.reshape(1, -1)
                with open(data_csv_to_save_to, 'a') as abc:
                    np.savetxt(abc, raw, delimiter=",")

                with open(label_csv_to_save_to,'a') as fd:
                    fd.write(identity + '\n')
            except Exception as e:
                print traceback.format_exc()
                print e

