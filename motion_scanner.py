# import the necessary packages
import argparse
import datetime
import imutils
import time
import cv2
import sys
import numpy
import tensorflow as tf
from classify_image import maybe_download_and_extract, ImageClassifier


maybe_download_and_extract()

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", help="path to the video file")
ap.add_argument("-a", "--min-area", type=int, default=1024, help="minimum area size")
args = vars(ap.parse_args())

# if the video argument is None, then we are reading from webcam
if args.get("video", None) is None:
    camera = cv2.VideoCapture(0)
    time.sleep(0.25)

# otherwise, we are reading from a video file
else:
    camera = cv2.VideoCapture(args["video"])

if not camera.isOpened():
    print("Could not open camera")
    sys.exit()

# initialize the first frame in the video stream
alpha = 0.2
kernel = (31, 31)
firstFrame = None
lastState = "Unoccupied"
tracker = cv2.Tracker_create("TLD")

surf = cv2.xfeatures2d.SURF_create()
fgbg = cv2.createBackgroundSubtractorKNN()
#fgbg = cv2.createBackgroundSubtractorMOG2()

# loop over the frames of the video
#with ImageClassifier() as classify_image:

ic = ImageClassifier()
ic.__enter__()
classify_image = lambda image_data: ic.inference(image_data)
while True:
    # grab the current frame and initialize the occupied/unoccupied
    # text
    (grabbed, frame) = camera.read()
    text = "Unoccupied"

    # if the frame could not be grabbed, then we have reached the end
    # of the video
    if not grabbed:
        break

    # resize the frame, convert it to grayscale, and blur it
    frame = imutils.resize(frame, width=800)
    detect_frame = frame.copy()

    if firstFrame is None:
        firstFrame = frame.copy()

    fgmask = fgbg.apply(frame)
    fgmask = cv2.morphologyEx(fgmask, cv2.MORPH_OPEN, kernel)

    '''
    apply fgmask to frame
    then use surf to detect blobs and extract key points on masked image
    then find contours on grey frame and filter contours by wether they container key point
    find cerents of contours cv2.moments(cnts)
    '''
    #(kps, descs) = surf.detectAndCompute(gray, None)
    '''
    #frame = cv2.bitwise_and(frame, frame, mask=fgmask)
    #frame = cv2.cvtColor(fgmask, cv2.COLOR_GRAY2BGR)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    #thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]
    #thresh = cv2.threshold(fgmask, 25, 255, cv2.THRESH_BINARY)[1]


    # on thresholded image
    thresh = gray.copy()
    #thresh = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)[1]
    #thresh = cv2.erode(thresh, None, iterations=3)
    #thresh = cv2.dilate(thresh, None, iterations=8)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
    image, cnts, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)
    kp, des = surf.detectAndCompute(gray, None) #keypoints of objects
    frame = cv2.drawKeypoints(frame, kp, None, (255,0,0), 4)
    '''
    image, cnts, hierarchy = cv2.findContours(fgmask, cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)

    # loop over the contours
    for c in cnts:
        # if the contour is too small, ignore it
        #print("contour:", c)
        if cv2.contourArea(c) < args["min_area"]:
            continue

        #compute center
        #M = cv2.moments(c)
    	#cX = int(M["m10"] / M["m00"])
    	#cY = int(M["m01"] / M["m00"])

        # compute the bounding box for the contour, draw it on the frame,
        # and update the text
        (x, y, w, h) = cv2.boundingRect(c)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        text = "Occupied"

        #cv2.drawContours(frame, [c], -1, (0, 255, 0), 2)
        image_data = cv2.cvtColor(detect_frame[y:y+h,x:x+w], cv2.COLOR_BGR2RGB)
        #print("classifying:", x, y)
        top_k = classify_image(image_data)
        top_item = top_k[0]
        if top_item[1] > .1:
            label = "{1:.2%} {0}".format(*top_item)
            cv2.putText(frame, label, (x, y+20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 1)
        else:
            print("not sure but:", top_item)
        '''

        if not len(trackedObjects):
            image_data = cv2.cvtColor(frame[y:y+h,x:x+w], cv2.COLOR_BGR2RGB)
            top_k = classify_image(image_data)
            print("predictions:")
            print(top_k)
            trackedObjects.append(c)
        '''


    if lastState != text:
        lastState = text
        print("New State:", text)
    '''
    if text == "Occupied":
        top_k = classify_image(detect_frame)
        top_item = top_k[0]
        if top_item[1] > .8:
            text += " by " + top_item[0]
    '''

    # draw the text and timestamp on the frame
    #cv2.putText(frame, "Room Status: {}".format(text), (10, 20),
    #    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    cv2.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),
        (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

    # show the frame and record if the user presses a key
    cv2.imshow("Security Feed", frame)
    #cv2.imshow("Thresh", thresh)
    #cv2.imshow("Frame Delta", frameDelta)

    key = cv2.waitKey(10) & 0xFF

    # if the `q` key is pressed, break from the lop
    if key == ord("q"):
        break

# cleanup the camera and close any open windows
camera.release()
cv2.destroyAllWindows()
