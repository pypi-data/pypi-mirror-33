#!/usr/bin/env python -W ignore::DeprecationWarning
import cv2
#import mxnet as mx
#from mtcnn_detector import MtcnnDetector
from imutils.object_detection import non_max_suppression
import os
#from utilities import get_string_from_cv2
import base64
import warnings
import io, sys
import json
import numpy as np
import requests

warnings.filterwarnings("ignore")

dir_path = os.path.dirname(os.path.realpath(__file__))

class API(object):
    """TF Server API Wrapper"""
    def __init__(self, url, auth_token):
        self.url = url
        self.auth_token = auth_token
        self.headers = {
            "Content-Type":"application/json",
            "x-auth":auth_token
        }


    def get_features(self, image):
        """get features from api"""
        url = self.url + "/enroll"
        data = {
            "image":{"data":base64.b64encode(open(image).read())},
        }

        request = requests.post(
            url, data=json.dumps(data), headers=self.headers)

        print request.json()
        

    def match(self):
        """perform match"""
        pass

    def identify(self):
        """perform identify"""
        pass

    def upload_collection(self):
        """TF Server API Wrapper"""
        pass

    def get_collection(self):
        """TF Server API Wrapper"""
        pass

    def update_collection(self):
        """TF Server API Wrapper"""
        pass
