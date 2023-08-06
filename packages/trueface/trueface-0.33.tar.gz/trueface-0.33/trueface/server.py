# coding: utf-8
"""identify demo"""
# import mxnet as mx
# from mtcnn_detector import MtcnnDetector
# from imutils.object_detection import non_max_suppression
import time
import base64
import json
import traceback
import random
import string
import mss
import argparse
import docker
import os
from utilities import id_generator


def start_container(image_name, api_key, secret, port):
    """starts a trueface image"""
    client = docker.from_env()
    try:
        client.images.get(image_name)
    except docker.errors.ImageNotFound:
        print 'image not found, attempting to pull...'
        client.images.pull(image_name)
    container = client.containers.run(image_name, ports={'8085/tcp': int(port)}, detach=True, tty=True, stdin_open=True)
    container.rename("truefaceServer_%s" % id_generator())
    container.exec_run(['sh', '-c', "echo '{\"api_key\":\"%s\",\"secret\":\"%s\"}'  > creds.json" % (api_key, secret)])
    container.exec_run(['pm2', 'start', 'api'])
    print container.id

def main():
    ap = argparse.ArgumentParser(description="Trueface.ai Server Management")
    ap.add_argument("-sc", "--start-server", default=False, 
                    help="phone number to send sms alerts to", action='store_true')
    ap.add_argument("-i", "--image-name", default=False, 
                    help="the image name you'd like to start")
    ap.add_argument("-a", "--api-key", default=False, 
                    help="your api key")
    ap.add_argument("-s", "--secret", default=False, 
                    help="your secret")
    ap.add_argument("-p", "--port", default=False, 
                    help="port to expose the container on")

    args = vars(ap.parse_args())

    if args['start_server']:
        start_container(args["image_name"], args['api_key'], args['secret'], args['port'])
