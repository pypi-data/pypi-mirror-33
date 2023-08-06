#!/usr/bin/env python -W ignore::DeprecationWarning
import cv2
import mxnet as mx
from mtcnn_detector import MtcnnDetector
from imutils.object_detection import non_max_suppression
import os
from utilities import get_string_from_cv2
import base64
import warnings
import io, sys
import json
import numpy as np

warnings.filterwarnings("ignore")

dir_path = os.path.dirname(os.path.realpath(__file__))

class Detector(object):
    """TF Local Face Detector"""
    def __init__(self, ctx='cpu', min_face=50, accurate_landmark=False):
        self.detector = MtcnnDetector(
            model_folder=dir_path + '/model',
            ctx=mx.cpu() if ctx == 'cpu' else mx.gpu(), 
            num_worker=4, 
            minsize=min_face,
            accurate_landmark=accurate_landmark)

    def get_image(self, _bin, b64):
        if b64:
            _bin = base64.b64decode(_bin)
            _bin = np.fromstring(_bin, np.uint8)
            image = cv2.imdecode(_bin, cv2.IMREAD_COLOR)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            return image
        return cv2.imread(_bin)


    def find_faces(self, 
                   img, 
                   return_chips=False, 
                   chip_size=112, 
                   padding=0.37, 
                   b64=False,
                   binary=False):
        """finds all faces and returns chips"""
        if not binary:
            img = self.get_image(img, b64)
        results = self.detector.detect_face(img)
        if results is None:
            return None
        total_boxes = results[0]
        points = results[1]
        faces = []
        for i, box in enumerate(total_boxes):
            faces.append({
                "bounding_box":box.tolist(),
                "points":points[i].tolist(),
                "chip":None
            })
        if return_chips:
            chips = self.detector.extract_image_chips(img, points, chip_size, padding)
            for i, chip in enumerate(chips):
                faces[i]['chip'] = base64.b64encode(get_string_from_cv2(chip))
        return json.dumps(faces)

    def return_biggest_face(self, array):
        """finds the biggest face"""
        sizes = []
        for face in array:
            size = int(face[2]) - int(face[0])
            sizes.append(size)
        maxFace = np.max(sizes)
        return sizes.index(maxFace)

    def find_biggest_face(self, img, return_chips=False, chip_size=112, padding=0.37, b64=False):
        """finds the biggest face"""
        img = self.get_image(img, b64)
        results = self.detector.detect_face(img)
        if results is None:
            return None
        total_boxes = results[0]
        points = results[1]
        faces = []
        f_index = self.return_biggest_face(total_boxes)
        faces.append({
            "bounding_box":total_boxes[f_index].tolist(),
            "points":points[f_index].tolist(),
        })
        if return_chips:
            faces[0]['chip'] = base64.b64encode(get_string_from_cv2(
                self.detector.extract_image_chips(img, points, chip_size, padding)[f_index]))

        return json.dumps(faces)
