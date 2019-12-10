#! python3
# gestures.py - module for detecting gestures to perform gestures' control of the mirror.
# If five fingers are detected the self.command string gets the value 'VoiceControl'.
# 'VoiceControl is then used to mute the speakers in order to allow voice control of the mirror.

import cv2
import numpy as np
import math
import logging
import time

class Gestures:

    def __init__(self):
        self.logger = logging.getLogger('Gesell.gestures.Gestures')
        self.camera = cv2.VideoCapture(0)
        self.camera.set(10,200)
        ret, self.frame = self.camera.read()
        self.shape = self.frame.shape
        self.cap_region_x_begin=0.35  # start point/total width
        self.cap_region_y_end=0.55  # start point/total width
        self.threshold = 60  #  BINARY threshold
        self.blurValue = 41  # GaussianBlur parameter 
        self.bgSubThreshold = 50
        self.learningRate = 0
        self.bgModel = cv2.createBackgroundSubtractorMOG2(0, self.bgSubThreshold)
        self.command = 'None' # Variable contains detected gesture commands.
        self.logger.debug('An instance of Gestures has been created.')

    def removeBG(self, frame):
        fgmask = self.bgModel.apply(frame,learningRate=self.learningRate)
        kernel = np.ones((3, 3), np.uint8)
        fgmask = cv2.erode(fgmask, kernel, iterations=1)
        res = cv2.bitwise_and(frame, frame, mask=fgmask)
        return res

    def calculateFingers(self, res, drawing):  # -> finished bool, cnt: finger count
        #  convexity defect
        hull = cv2.convexHull(res, returnPoints=False)
        if len(hull) > 3:
            defects = cv2.convexityDefects(res, hull)
            if type(defects) != type(None):  # avoid crashing.   (BUG not found)

                cnt = 0
                for i in range(defects.shape[0]):  # calculate the angle
                    s, e, f, d = defects[i][0]
                    start = tuple(res[s][0])
                    end = tuple(res[e][0])
                    far = tuple(res[f][0])
                    a = math.sqrt((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2)
                    b = math.sqrt((far[0] - start[0]) ** 2 + (far[1] - start[1]) ** 2)
                    c = math.sqrt((end[0] - far[0]) ** 2 + (end[1] - far[1]) ** 2)
                    angle = math.acos((b ** 2 + c ** 2 - a ** 2) / (2 * b * c))  # cosine theorem
                    if angle <= math.pi / 2:  # angle less than 90 degree, treat as fingers
                        cnt += 1
                        cv2.circle(drawing, far, 8, [211, 84, 0], -1)
                return True, cnt
        return False, 0

    def mainloop(self):
        """ Calling gesture detection algorithm in a endless loop. 
        First checks if there is a gesture in the top left corner,
        second, checks if there is a gesture in the top right corner."""
        while self.camera.isOpened():
            self.detection(0, int(self.cap_region_x_begin * self.shape[1]))
            self.detection(int((1 - self.cap_region_x_begin) * self.shape[1]), self.shape[1])

    def detection(self, begin, end):
        """ The algorithm for detecting a hand in ROI and counting the number of fingers.
        If there are five fingers detected in either ROI, assigns self.command 'VoiceControl' value."""
        #print(begin, end)
        ret, frame = self.camera.read()
        frame = cv2.bilateralFilter(frame, 5, 50, 100)  # smoothing filter
        frame = cv2.flip(frame, 1)  # flip the frame horizontally
        
        cv2.rectangle(frame, (begin, 0),
                             (end, int(self.cap_region_y_end * frame.shape[0])), 
                             (255, 0, 0), 2)

        #cv2.imshow('original', frame)
        #  Main operation
        img= self.removeBG(frame)
        img = img[0:int(self.cap_region_y_end * frame.shape[0]),
                    begin:end]  # clip the ROI
        # convert the image into binary image
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (self.blurValue, self.blurValue), 0)
        ret, thresh = cv2.threshold(blur, self.threshold, 255, cv2.THRESH_BINARY)
        # get the coutours
        contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        length = len(contours)
        maxArea = -1
        if length > 0:
            for i in range(length):  # find the biggest contour (according to area)
                temp = contours[i]
                area = cv2.contourArea(temp)
                if area > maxArea:
                    maxArea = area
                    ci = i
            res = contours[ci]
            hull = cv2.convexHull(res)
            drawing = np.zeros(img.shape, np.uint8)
            cv2.drawContours(drawing, [res], 0, (0, 255, 0), 2)
            cv2.drawContours(drawing, [hull], 0, (0, 0, 255), 3)

            isFinishCal,cnt = self.calculateFingers(res,drawing)
            # If found five fingers.
            if cnt == 4:
                if self.command == 'None':
                    self.command = 'VoiceControl'
                    #self.logger.debug('Five fingers detected.')
                    cv2.waitKey(30)
                    #time.sleep(0.05)
                else:
                    cv2.waitKey(30)
                    #time.sleep(0.05)
            else:
                if self.command != 'None':
                    self.command = 'None'
                    #self.logger.debug('The gesture is out of the focus')
                #time.sleep(0.05) 
                cv2.waitKey(30)    
            cv2.imshow('output', drawing)
        #print(self.command)
        cv2.waitKey(30)
        #time.sleep(0.05)

        

if __name__ == '__main__':
    g = Gestures()
    g.mainloop()
