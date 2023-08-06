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
from imutils.video import FileVideoStream

warnings.filterwarnings("ignore")

dir_path = os.path.dirname(os.path.realpath(__file__))

class Video(object):
    """TF Local Face Detector"""
    def __init__(self, ctx='cpu', min_face=50, accurate_landmark=False):
        self.detector = MtcnnDetector(
            model_folder=dir_path + '/model',
            ctx=mx.cpu() if ctx == 'cpu' else mx.gpu(), 
            num_worker=4, 
            minsize=min_face,
            accurate_landmark=accurate_landmark)
        self.faceTracker = []

    def track_face(face_to_track, image, face_label):
        """Initiates the tracking of a face"""
        x_face = int(face_to_track[0])
        y_face = int(face_to_track[1])
        w_face = int(int(face_to_track[2])-int(face_to_track[0]))
        h_face = int(int(face_to_track[3])-int(face_to_track[1]))

        tracker = dlib.correlation_tracker()
        tracker.start_track(image, 
                            dlib.rectangle(
                                int(x_face-10), 
                                int(y_face-20), 
                                int(x_face+w_face+10), 
                                int(y_face+h_face+20)))
        self.faceTrackers[face_label] = tracker

    def index_video(self, path):
        pass
