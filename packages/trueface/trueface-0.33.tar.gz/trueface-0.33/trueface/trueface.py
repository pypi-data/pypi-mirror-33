# coding: utf-8
"""identify demo"""
import cv2
import mxnet as mx
from mtcnn_detector import MtcnnDetector
from imutils.object_detection import non_max_suppression
import requests
import time
import pandas as pd
import base64
import json
import numpy as np
import dlib
import traceback
import random
import string
import mss
from requests_futures.sessions import FuturesSession
from art import text2art
import argparse
# import matplotlib.pyplot as plt
from pubnub.enums import PNStatusCategory
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
from imutils.video import WebcamVideoStream
from imutils.video import FileVideoStream
from termcolor import colored, cprint
import os


pnconfig = PNConfiguration()
 
pnconfig.subscribe_key = 'sub-c-8bd469de-0ec3-11e8-b857-da98488f5703'
pnconfig.publish_key = 'pub-c-e851be89-8ba0-4ed6-85bf-19a8ba08be80'
 
pubnub = PubNub(pnconfig)

# time.sleep(100)

ap = argparse.ArgumentParser(description="Trueface.ai Demo script")
# parser.add_argument('integers', metavar='N', type=int, nargs='+',
#                     help='an integer for the accumulator')

ap.add_argument("-pn", "--phone-number", default=False, 
                help="phone number to send sms alerts to")

ap.add_argument("-st", "--show-tracking", default=False, 
                help="whether to show the tracking box", action='store_true')

ap.add_argument("-fbu", "--frame-before-adding", default=20, 
                help="how many frames before it assigns an id to an unknown")

ap.add_argument("-mfd", "--minimum-face-detect", default=40, 
                help="minimum face size to detect")

ap.add_argument("-mfr", "--minimum-face-recognize", default=40, 
                help="minimum face size to recognize")

ap.add_argument("-sp", "--show-points", default=False, 
                help="the folder to use, the default is repo root", action='store_true')

ap.add_argument("-sc", "--show-chips", default=False, 
                help="whether to show face chips", action='store_true')

ap.add_argument("-t", "--threshold", default=0.3, 
                help="threshold to use") 

ap.add_argument("-dt", "--demo-type", default='camera', 
                help="screen or camera") 

ap.add_argument("-sro", "--show-roi-only", default=False, 
                help="screen or camera", action='store_true')

ap.add_argument("-ur", "--use-roi", default=False, 
                help="whether to use roi", action='store_true') 

ap.add_argument("-fdc", "--face-detect-confidence", default=.98, 
                help="minimum face size to recognize") 

ap.add_argument("-bu", "--blur-unknowns", default=False, 
                help="whether to blur unknowns", action='store_true') 

ap.add_argument("-r", "--resize", default=False, 
                help="whether to resize the stream", action='store_true') 

ap.add_argument("-fw", "--width", default=640, 
                help="width to resize it to") 

ap.add_argument("-fh", "--height", default=480, 
                help="height to resize it to") 

ap.add_argument("-s", "--source", default=0, 
                help="source to process") 

ap.add_argument("-tt", "--tracking-threshold", default=4, 
                help="tracking threshold to use")

ap.add_argument("-sd", "--send-data", default=4, 
                help="tracking threshold to use", action='store_true')

ap.add_argument("-ch", "--channel", default='naz', 
                help="channel to send on")

ap.add_argument("-uq", "--use-queue", default=False, 
                help="whether to queue frames", action='store_true')

ap.add_argument("-rv", "--record-video", default=False, 
                help="whether to record video", action='store_true')

ap.add_argument("-spd", "--spoof", default=False, 
                help="whether to preform spoof", action='store_true')

ap.add_argument("-f", "--features", default='', 
                help="whether to preform spoof")


ap.add_argument("-l", "--labels", default='', 
                help="whether to preform spoof")

args = vars(ap.parse_args())


Art=text2art("Trueface.ai") # Return ascii text (default font) and default chr_ignore=True 
print(Art)


SESSION = FuturesSession()

account = "AC8d955524dddb7ba16f4f875773933e38"
token = "79fdf73dadac2ef478108311e0d20eca"

# bins =16
# lw = 3
# alpha = 0.5
# fig, ax = plt.subplots()
# ax.set_title('Histogram (RGB)')
# ax.set_xlabel('Bin')
# ax.set_ylabel('Frequency')
# lineR, = ax.plot(np.arange(bins), np.zeros((bins,)), c='r', lw=lw, alpha=alpha)
# lineG, = ax.plot(np.arange(bins), np.zeros((bins,)), c='g', lw=lw, alpha=alpha)
# lineB, = ax.plot(np.arange(bins), np.zeros((bins,)), c='b', lw=lw, alpha=alpha)
# ax.set_xlim(0, bins-1)
# ax.set_ylim(0, 1)
# plt.ion()
# plt.show()

dir_path = os.path.dirname(os.path.realpath(__file__))


detector = MtcnnDetector(
    model_folder=dir_path + '/model',
    ctx=mx.cpu(), 
    num_worker=4, 
    minsize=args['minimum_face_detect'], #minimum face size to be detected
    accurate_landmark=False) #setting this to false makes it slightly faster
    #setting it to true makes points slight more accurate

N = 8 #length of id to create
minFaceSizeToDetect = args['minimum_face_detect'] #minimun face size to detect
minFaceSizeToProcess = args['minimum_face_recognize'] #minimun face size to be processed by recognition and tracking
threshold = args['threshold'] #change threshold for similarity here

show_points = False
if args['show_points']:
    show_points = True

show_chips = False
if args['show_chips']:
    show_chips = True

source = args['source']

#"http://admin:sunesta210@192.168.4.15/cgi-bin/camera" 
#/"rtsp://192.168.2.4:554/11" # source of the stream

tracking_theshold = args['tracking_threshold']

show_tracking = False
if args['show_tracking']:
    show_tracking = True

send_sms = False
if args['phone_number']:
    send_sms = True
    number = args['phone_number']

demo_type = args['demo_type'] #input camera or screen
frames_before_adding_unknown = args['frame_before_adding']

face_detect_confidence = float(args['face_detect_confidence'])

use_roi = True if args['use_roi'] else False
show_roi_only = True if args['show_roi_only'] else False 
#if the demo type is screen make sure to set this to True, roi within frame has bug in screen mode

resize = False
if args['resize']:
    resize = True
    frame_height = int(eval(args['height']))
    frame_width = int(eval(args['width']))


if demo_type == 'screen':
    use_roi = True
    show_roi_only = True
#vcap = cv2.VideoCapture(source)

if args['use_queue']:
    vcap = FileVideoStream(source, queueSize=1000).start()
else:
    vcap = WebcamVideoStream(src=source).start()

print vcap.read().shape

if args['record_video']:
    out = cv2.VideoWriter(
        'test12.mov', 
        cv2.VideoWriter_fourcc('8', 'B', 'P', 'S'), 10, 
        (1280, 720))

#vcap = cv2.VideoCapture(source) #if set to rstp, uncomment line 294
#vcap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

fname = args['features']
flabels = args['labels']

logo = cv2.imread(dir_path+'/logo.png', cv2.IMREAD_UNCHANGED)
(wH, wW) = logo.shape[:2]
(B, G, R, A) = cv2.split(logo)
B = cv2.bitwise_and(B, B, mask=A)
G = cv2.bitwise_and(G, G, mask=A)
R = cv2.bitwise_and(R, R, mask=A)
logo = cv2.merge([B, G, R, A])

features = pd.read_csv(fname, header=None).as_matrix()
labels = pd.read_csv(flabels, header=None).as_matrix()
#print 'Collection:', labels

features = [x for x in features]
labels = [l[0] for l in labels]
unknown_counter = []
# initialize the HOG descriptor/person detector
# hog = cv2.HOGDescriptor()
# hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

last_time_sent = {}

def draw_label(image, point, label, 
               font=cv2.FONT_HERSHEY_SIMPLEX,
               font_scale=0.5, thickness=1):
    """Draw label on the video"""
    size = cv2.getTextSize(label, font, font_scale, thickness)[0]
    x_label, y_label = point
    cv2.rectangle(
        image, 
        (x_label, y_label - size[1]), 
        (x_label + size[0], y_label), 
        (0, 0, 0), 
        cv2.FILLED)
    cv2.putText(image, label, point, font, font_scale, (255, 255, 255), thickness)

def find_tracked_face(face, frame, draw, roi):
    """Matches detected faces to a tracked face"""
    matchedFid = None
    t2 = time.time()

    if (int(face[2]) - int(face[0])) > minFaceSizeToProcess:
        fidsToDelete = []
        for fid in faceTrackers:
            trackingQuality = faceTrackers[fid].update(frame)
            print 'Tracker quality:', trackingQuality
            if trackingQuality < tracking_theshold:
                fidsToDelete.append(fid)

        x = int(face[0])
        y = int(face[1])
        w = int(int(face[2])-int(face[0]))
        h = int(int(face[3])-int(face[1]))

        x_bar = x + 0.5 * w
        y_bar = y + 0.5 * h

        for fid in fidsToDelete:
            print "Removing fid " + str(fid) + " from list of trackers"
            faceTrackers.pop(fid, None)

        for fid in faceTrackers:
            trackingQuality = faceTrackers[fid].update(frame)
            # if trackingQuality < tracking_theshold:
            #     faceTrackers.pop(fid, None)
            #     continue
            tracked_position = faceTrackers[fid].get_position()

            t_x = int(tracked_position.left())
            t_y = int(tracked_position.top())
            t_w = int(tracked_position.width())
            t_h = int(tracked_position.height())

            t_x_bar = t_x + 0.5 * t_w
            t_y_bar = t_y + 0.5 * t_h
            if ((t_x <= x_bar <= (t_x + t_w)) and 
                    (t_y <= y_bar <= (t_y + t_h)) and 
                    (x <= t_x_bar <= (x + w)) and 
                    (y <= t_y_bar <= (y + h))):
                matchedFid = fid
                draw_label(draw, 
                           (int(roi[0]+face[0]), roi[1]+int(face[1])), 
                           'TrueFaceiD: %s' % (str(matchedFid)))
                publish_realtime(args['channel']+'-tracker-confidence', {"eon":{"tracker_confidence":trackingQuality}})
                if show_tracking:
                    cv2.rectangle(
                            draw, 
                            (int(roi[0]+t_x), roi[1]+int(t_y)), 
                            (int(roi[0]+t_x+t_w), roi[1]+int(t_y+t_h)), 
                            (255, 255, 255))
    trtime =  time.time() - t2
    print 'tracking inference time: ', trtime
    return frame, matchedFid, draw, str(matchedFid)

def get_string_from_cv2(image, encode=False):
    """Gets a string from a cv2 image"""
    if encode:
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 50]
        return cv2.imencode('.jpg', image, encode_param)[1].tostring()
    return cv2.imencode('.jpg', image)[1].tostring()


def get_features(image):
    """Get features from gpu server"""
    url = "http://54.80.111.222:18080/get-features"
    data = {
        "source":{"data":base64.b64encode(get_string_from_cv2(image))},
    }

    request = requests.post(url, data=json.dumps(data))

    print(request.text)
    try:
        return np.frombuffer(
            base64.decodestring(
                request.json()['encoding']), dtype=np.float32)
    except Exception as e:
        print e
        return None

def post_image(label, confidence, image):
    '''posts an image to be processed'''
    payload = {
        "name": label,
        "number":number,
        "confidence":confidence,
        "image":base64.b64encode(get_string_from_cv2(image)),
        "message":"ADT demo"
    }
    request = SESSION.put(
        'https://marriott-service-dot-chuispdetector.appspot.com/', data=json.dumps(payload))

    return request

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
    faceTrackers[face_label] = tracker

# timestamp = time.time()
# delay = 0.05
def get_roi(frame, roi):
    if use_roi:
        if roi is None:
            roi = cv2.selectROI("Image", frame, False, False)
            roi = roi
            cv2.destroyWindow("Image")
        else:
            frame = frame[int(roi[1]):int(roi[1]+roi[3]), int(roi[0]):int(roi[0]+roi[2])]
    return frame, roi


def blur_face(total_boxes, draw):
    face = total_boxes[f]
    x = int(face[0])
    y = int(face[1])
    w = int(int(face[2])-int(face[0]))+5
    h = int(int(face[3])-int(face[1]))+5
    face = draw[roi_copy[1]+y:roi_copy[1]+y+h,roi_copy[0]+x:roi_copy[0]+x+w]
    sub_face = cv2.GaussianBlur(face,(173, 173), 70)
    draw[y:y+h,x:x+w] = sub_face
    return draw

def detect_pedestrians():
    # detect people in the image
    (rects, weights) = hog.detectMultiScale(draw, winStride=(4, 4),
        padding=(8, 8), scale=1.05)
 
    # draw the original bounding boxes
    rects = np.array([[x, y, x + w, y + h] for (x, y, w, h) in rects])
    pick = non_max_suppression(rects, probs=None, overlapThresh=0.65)
    for (xA, yA, xB, yB) in pick:
        cv2.rectangle(draw, (xA, yA), (xB, yB), (0, 255, 0), 2)

faces = []
id_array = []
faceTrackers = {}
unknown_faces = []
unknown_labels = []

def process_face(raw, draw, total_boxes, f, frame, roi_copy):
# # print raw
    sim_list = []
    del sim_list[:]
    label_index = 0

    t1 = time.time()
    #check the chip against every face
    for i, face in enumerate(features):
        _sim = np.dot(face, raw.T)
        sim_list.append(_sim)

    max_f = np.max(sim_list)
    fr_time = time.time() - t1
    print 'local inference took: ', fr_time

    #publish_realtime('c3-spline2', {"eon":{"FR":time.time() - t1}})


    publish_realtime(args['channel']+'-confidence', {"eon":{"confidence":(max_f*100)}})

    print 'detected similarity:', max_f
    if max_f > threshold:
        #label is the index of the max in face id array
        label = labels[sim_list.index(max_f)]
        track_face(total_boxes[f], frame, label)
        if send_sms:
            post_image(label, max_f, chip)
            last_time_sent[label] = time.time()
    else:
        u_sim_list = []
        max_u = 0

        if not unknown_faces:
            u_label = "%s" % ''.join(
                random.choice(
                    string.ascii_uppercase + string.digits) \
                    for _ in range(N)).upper()
            unknown_labels.append(u_label)
            unknown_faces.append(raw)
            label = 'unknown'
            draw_label(draw, 
               (int(roi_copy[0]+total_boxes[f][0]), 
                int(roi_copy[1]+total_boxes[f][1])), 
               'TrueFaceiD: %s' % (str(label)))
            return

        #get sim over previously seen faces
        for i, face in enumerate(unknown_faces):
            _sim = np.dot(face, raw.T)
            u_sim_list.append(_sim)

        max_u = np.max(u_sim_list)
        #if seen before get label, otherwise generate one
        if max_u > threshold:
            u_label = unknown_labels[u_sim_list.index(max_u)]
        else:
            u_label = "%s" % ''.join(
                random.choice(
                    string.ascii_uppercase + string.digits) \
                    for _ in range(N)).upper()
            unknown_labels.append(u_label)
            unknown_faces.append(raw)

        #checks if face occured long enough to add to in memory collection
        if unknown_labels.count(u_label) > frames_before_adding_unknown:
            label = u_label
            labels.append(u_label)
            features.append(raw)
            track_face(total_boxes[f], frame, u_label)
        else:
            unknown_labels.append(u_label)
            unknown_faces.append(raw)
            label = 'unknown'
            if args['blur_unknowns']:
                draw = blur_face(total_boxes, draw)

    draw_label(draw, 
               (int(roi_copy[0]+total_boxes[f][0]), 
                int(roi_copy[1]+total_boxes[f][1])), 
               'TrueFaceiD: %s' % (str(label)))

    return draw, label

def add_logo_to_frame(draw):
    (h, w) = draw.shape[:2]
    draw = np.dstack([draw, np.ones((h, w), dtype="uint8") * 255])
    overlay = np.zeros((h, w, 4), dtype="uint8")
    overlay[h - wH - 10:h - 10, w - wW - 10:w - 10] = logo
    cv2.addWeighted(overlay, 1, draw, 1.0, 0, draw)
    return draw


def x_uncomplete():
    #this is was the start of an attempt to measure some variables to improve latency on rtsp and grab frames quicker
    # print vcap.get(cv2.CAP_PROP_POS_FRAMES)
    # print vcap.get(cv2.CAP_PROP_FRAME_COUNT)
    # print vcap.get(cv2.CAP_PROP_POS_MSEC)
    pass

def get_frame():
    last_time = time.time()
    if demo_type == 'camera':
        frame = vcap.read()
        if resize:
            frame = cv2.resize(frame, (frame_width, frame_height))
        draw = frame.copy()
    elif demo_type == 'screen':
        with mss.mss() as sct:
            frame = np.array(sct.grab(sct.monitors[1]))
            frame = cv2.resize(frame, (frame.shape[1]/2, frame.shape[0]/2), interpolation = cv2.INTER_AREA)
            draw = frame.copy()
            frame = frame[...,0:3]
    return frame, draw


def process_roi(frame, draw, roi):
    if use_roi:
        if roi == (0,0,0,0):
            #get roi
            roi = cv2.selectROI("Select ROI", frame, False, False)
            cv2.destroyWindow("Select ROI")
            return frame, draw, roi, roi
        else:
            #slice frame
            frame = frame[int(roi[1]):int(roi[1]+roi[3]), int(roi[0]):int(roi[0]+roi[2])]

        if not show_roi_only:
            #draw roi region on full frame
            cv2.rectangle(
                    draw, 
                    (int(roi[0]), int(roi[1])), 
                    (int(roi[0]+roi[2]), int(roi[1]+roi[3])), 
                    (255, 255, 255))
    #a copy of of roi we can safely overwrite
    roi_copy = roi
    #if configuration wants to show roi only
    if show_roi_only:
        draw = frame
        #set roi position to zero to correct bounding box locations
        #the roi copy allows us to set correct bounding boxes witgout overwriting roi variable 
        roi_copy = (0,0,0,0)
    return frame, draw, roi, roi_copy

def draw_face_box(draw, roi_copy, total_boxes, f):
    cv2.rectangle(
        draw, 
        (int(roi_copy[0]+total_boxes[f][0]), roi_copy[1]+int(total_boxes[f][1])), 
        (int(roi_copy[0]+total_boxes[f][2]), roi_copy[1]+int(total_boxes[f][3])), 
        (255, 255, 255))
    return draw

def my_publish_callback(channel, message):
    #print channel
    #print message
    pass

def publish_realtime(channel, data):
    if args['send_data']:
        pubnub.publish().channel(channel).message(data).async(my_publish_callback)


def get_ip():
    request = requests.get('https://api.ipify.org?format=json')
    return request.json()

def get_latlong(ip):
    url = "http://freegeoip.net/json/" + ip
    request = requests.get(url)
    return request.json()

unique_faces = []
def count_unique(raw):
    if not unique_faces:
        unique_faces.append(raw)
        print 'first face'

    sim_list = []
    for i, face in enumerate(unique_faces):
        _sim = np.dot(face, raw.T)
        sim_list.append(_sim)
    max_f = np.max(sim_list)
    if max_f < (threshold - 0.15):#+0.1):
        print 'unique_face'
        unique_faces.append(raw)
    print 'total unique seen faces', len(unique_faces)
    return len(unique_faces)


def variance_of_laplacian(image):
    return cv2.Laplacian(image, cv2.CV_64F).var()



def get_user_info(image):
    return cv2.Laplacian(image, cv2.CV_64F).var()


def check_if_blurry(chip, draw):
    gray = cv2.cvtColor(chip, cv2.COLOR_BGR2GRAY)
    fm = variance_of_laplacian(gray)
    text = "Not Blurry"
 
    # if the focus measure is less than the supplied threshold,
    # then the image should be considered "blurry"
    if fm < 150:
        text = "Blurry"
 
    # show the image
    cv2.putText(draw, "{}: {:.2f}".format(text, fm), (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 3)


# def detect_age(img):
#     # predict ages and genders of the detected faces
#     cv2.resize(img, dsize=(64, 64))
#     results = model.predict(faces)
#     predicted_genders = results[0]
#     ages = np.arange(0, 101).reshape(101, 1)
#     predicted_ages = results[1].dot(ages).flatten()

#     # draw results
#     for i, d in enumerate(detected):
#         label = "{}, {}".format(int(predicted_ages[i]),
#                                 "F" if predicted_genders[i][0] > 0.5 else "M")
#         draw_label(img, (d.left(), d.top()), label)
SPRESULT = None
sp_in_progress = False
def sp_detect(sess, resp):
    global sp_in_progress
    global SPRESULT
    if resp.json()['data']['class'] == 'Fake' and resp.json()['data']['score'] > 0.25:
        result = 'FAKE'
        cprint('Face is %s' % result, 'white', 'on_red')
    else:
        result = 'REAL'
        cprint('Face is %s' % result, 'white', 'on_green')
    SPRESULT = result
    sp_in_progress = False


def call_spoof(image):
    global sp_in_progress
    if not sp_in_progress:
        sp_in_progress = True
        headers = {
          "x-api-key":"N0pYcPtwXm8ZOwDKs6rDp72j7RmwuDGL5NjZXFVJ",
          "Content-Type":"application/json",
        }
        sp_url = "https://api.trueface.ai/v1/spdetect"

        data = {
          "img":base64.b64encode(get_string_from_cv2(image)),
        }
        SESSION.post(sp_url, data=json.dumps(data), headers=headers, background_callback=sp_detect)






def main():
    roi = (0,0,0,0)
    latlon = None
    try:
        ip = get_ip()['ip']
        latlon = get_latlong(ip)
    except Exception:
        pass
    framesp = 0
    while(True): 
        try:
            last_time = time.time()
            frame, draw = get_frame()
            if frame is None:
                continue
            frame, draw, roi, roi_copy = process_roi(frame, draw, roi)
            framesp += 1
            publish_realtime(args['channel']+'-chip', {"frames":framesp})

            if latlon:
                publish_realtime(args['channel']+'-map-single', [{"latlng":[latlon['latitude'], latlon['longitude']]}])

            t1 = time.time()
            results = detector.detect_face(frame)
            fdtime = time.time() - t1
            print 'face detection time: ', fdtime
            #this converts the frame shape to add alpha values so we can add a transparent logo
            draw = add_logo_to_frame(draw)
            #if no detect results, show the frame and continue with the loop
            if results is None:
                cv2.imshow("Trueface.ai - press q to quit", draw)
                if args['record_video']:
                    out.write(draw)
                if cv2.waitKey(33) == ord('q'):
                    break
                continue

            total_boxes = results[0]
            points = results[1]
            #get image chips
            chips = detector.extract_image_chips(frame, points, 112, 0.37)
            total_faces = 0
            #loop over every chip
            for f, chip in enumerate(chips):
                publish_realtime(args['channel']+'-face_detect_confidence', {"eon":{"face_detect_confidence":(total_boxes[f][-1]*100)}})
                print 'face width: %spx' % (int(total_boxes[f][2]) - int(total_boxes[f][0]))
                #draw red box here to show detector but low confidence

                if total_boxes[f][-1] > face_detect_confidence:
                    #draw rectangle
                    total_faces += 1
                    draw_face_box(draw, roi_copy, total_boxes, f)
                    publish_realtime(args['channel']+'-face_width', {"eon":{"face_width":(int(total_boxes[f][2]) - int(total_boxes[f][0]))}})


                    #draw 5 points on the face
                    if show_points:
                        for i in range(5):
                            cv2.circle(draw, (points[f][i], points[f][i + 5]), 1, (255, 0, 0), 2)

                    frame, matchID, draw, label = find_tracked_face(total_boxes[f], frame, draw, roi_copy)

                    #if the tracker didn't find anyone, run face recognition
                    if ((int(total_boxes[f][2]) - int(total_boxes[f][0])) > minFaceSizeToProcess and 
                            matchID is None):
                        t1 = time.time()
                        #age = detect_age(chip)
                        raw = get_features(chip)
                        print 'calling the server for face features took: ', time.time() - t1
                        if raw is None:
                            continue
                        raw = raw.reshape(1, -1)
                        ufaces = count_unique(raw)
                        publish_realtime(args['channel']+'-chip', {"unique_faces":ufaces})

                        draw, label = process_face(raw, draw, total_boxes, f, frame, roi_copy)

                    chip = np.dstack(
                        [chip, np.ones((chip.shape[0], chip.shape[0]), dtype="uint8") * 255])
                    
                    #check_if_blurry(chip, draw)
                    
                    if (f*chip.shape[0] + chip.shape[0]) < draw.shape[1] and show_chips:
                        draw[0:0+chip.shape[0], f*chip.shape[0]:f*chip.shape[0]+chip.shape[1]] = chip

                    #chip = cv2.resize(chip, dsize=(56, 56), interpolation=cv2.INTER_CUBIC)
                    #print len(base64.b64encode(get_string_from_cv2(chip, True)))

                    publish_realtime(args['channel']+'-chip', {"chip":base64.b64encode(get_string_from_cv2(chip, True)), "label":label,"frame":framesp})
            print('fps: {0}'.format(1 / (time.time()-last_time)))

            #pubnub.publish().channel("c3-spline2").message({"eon":{"fps":1 / (time.time()-last_time), "total_faces":total_faces,"fdtime":fdtime}}).async(my_publish_callback)
            publish_realtime(args['channel']+"-c3-spline2", {"eon":{"fps":1 / (time.time()-last_time), "total_faces":total_faces,"fdtime":fdtime}})

            if args['spoof']:
                if framesp % 10:
                    frame = cv2.resize(frame, (320, 240))
                    call_spoof(frame)
                    cv2.putText(draw, "Last Spoof Result: {}".format(SPRESULT),
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            if args['use_queue']:
                cv2.putText(draw, "Queue Size: {}".format(vcap.Q.qsize()),
                (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            if args['record_video']:
                out.write(draw)

            cv2.imshow('Trueface.ai - press q to quit', draw)

        except Exception as e:
            print traceback.format_exc()
            print e
            # if isinstance(source, str):
            #     if args['use_queue']:
            #         vcap = FileVideoStream(source, queueSize=1000).start()
            #     else:
            #         vcap = WebcamVideoStream(src=source).start()

        if cv2.waitKey(33) == ord('q'):
            break

if __name__ == '__main__':
    main()    

