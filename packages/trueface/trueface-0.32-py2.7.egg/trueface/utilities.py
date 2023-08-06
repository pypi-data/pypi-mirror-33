import cv2
import base64
import json
import random
import string

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    """generates an id string"""
    return ''.join(random.choice(chars) for _ in range(size))


def get_string_from_cv2(image, encode=False):
    """Gets a string from a cv2 image"""
    if encode:
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 50]
        return cv2.imencode('.jpg', image, encode_param)[1].tostring()
    return cv2.imencode('.jpg', image)[1].tostring()