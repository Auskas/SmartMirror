#!/usr/bin/python3
# gestures_recognizer.py - finger detection and tracking using opencv and a trained CNN model.

from tensorflow.keras.models import load_model
import numpy as np
import cv2
import os, copy
import logging

class GesturesRecognizer:

    def __init__(self):
        self.logger = logging.getLogger('Gesell.gestures_recognizer.GesturesRecognizer')

        if __name__ == '__main__': # Creates a logger if the module is called directly.
            ch = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            ch.setFormatter(formatter)
            self.logger.setLevel(logging.DEBUG)
            self.logger.addHandler(ch)
            #import alsaaudio
            #m = alsaaudio.Mixer()
            #audio_volume = int(m.getvolume()[0])

        if os.path.isfile('hand_histogram.npy'):
            try:
                self.hand_hist = np.load('hand_histogram.npy')
                self.logger.info('Skin histogram has been loaded.')
            except Exception as error:
                self.logger.error('Canniot load skin histogram.')
        else:
            self.hand_hist = None
            self.logger.warning('Hand histogram file has not been found.')
        
        try:
            self.model = load_model(f'Working_models{os.sep}Model_without_optimizer_32x32_3conv-32-64-128_2dense-128.h5')
            self.logger.info('The CNN has been loaded.')
        except Exception as error:
            self.logger.error(f'Cannot load the CNN: {error}')

        self.LABELS = ['Five', 'Four', 'Inverted L', 'Peace', 'Pointing finger', 'None', 'Sign of the horns', 'Thumb up']
        self.LABEL = ''
        self.cam = cv2.VideoCapture(0)
        self.logger.debug(f'Brightness {self.cam.get(10)}')
        self.logger.debug(f'Contrast {self.cam.get(11)}')
        self.cam.set(10, -5.0) # Sets the brightness of the camera.
        self.cam.set(11, 150) # Sets the contrast of the camera.
        self.tips = []
        self.exposure_time = 0 # Increases by one every frame the tip of a finger is detected.
        #ret, image = cam.read()
        self.ROI_SIZE = 250
        self.IMG_SIZE = 32
        # Frame per second rate - the number of frames analyzed per second.
        self.FPS = 20
        self.TIP_TEXT = 'The tip of the finger is being tracked'
        ret, self.frame = self.cam.read()
        self.begin_X, self.begin_Y = int(self.frame.shape[1] - self.ROI_SIZE), 0
        self.end_X, self.end_Y = self.frame.shape[1], self.ROI_SIZE
        self.finger_tip = None # the coordinates of the pointing finger tip.
        self.diff = 0
        self.command = 'None'
        self.max_contour_found = None

    def draw_rectangle(self, frame):
        # Get the number of rows and columns in the frame.
        # The underscore means that I don't care about that variable (it is the dimension of the frame in that particular case).
        rows, cols, _ = frame.shape

        self.hand_rect_one_x = np.array(
            [6 * rows / 20, 6 * rows / 20, 6 * rows / 20, 10 * rows/ 20, 10 *rows / 20, 10 *rows / 20,
            14 * rows / 20, 14 * rows / 20, 14 * rows / 20], dtype=np.uint32)
        
        self.hand_rect_one_y = np.array(
            [9 * cols / 20, 10 * cols / 20, 11 * cols / 20, 9 * cols/ 20, 10 *cols / 20, 11 *cols / 20,
            9 * cols / 20, 10 * cols / 20, 11 * cols / 20], dtype=np.uint32)
        
        self.hand_rect_two_x, self.hand_rect_two_y = self.hand_rect_one_x + 10, self.hand_rect_one_y + 10
        
        self.number_of_rectangles = self.hand_rect_one_x.size
        
        for i in range(self.number_of_rectangles):
            cv2.rectangle(frame, (self.hand_rect_one_y[i], self.hand_rect_one_x[i]),
                            (self.hand_rect_two_y[i], self.hand_rect_two_x[i]),
                            (0, 255, 0), 1)
        return frame

    def set_hand_hist(self, frame):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        roi = np.zeros([90, 10, 3], dtype=hsv.dtype)

        for i in range(self.number_of_rectangles):
            roi[i * 10: i * 10 + 10, 0: 10] = hsv[self.hand_rect_one_x[i]: self.hand_rect_one_x[i] + 10,
                                                  self.hand_rect_one_y[i]: self.hand_rect_one_y[i] + 10]
        self.hand_hist = cv2.calcHist([roi], [0, 1], None, [180, 256], [0, 180, 0, 256])
        cv2.normalize(self.hand_hist, self.hand_hist, 0, 255, cv2.NORM_MINMAX)
        np.save('hand_histogram', self.hand_hist)

    def draw_final(self, frame):
        contours = self.contours(frame)
        if contours is not None and len(contours) > 0:
            self.max_contour_found = self.max_contour(contours)
            self.hull_found = self.hull(self.max_contour_found)
            self.centroid_found = self.centroid(self.max_contour_found)
            self.defects_found = self.defects(self.max_contour_found)

            if self.centroid_found is not None and self.defects_found is not None and len(self.defects_found)> 0:
                self.farthest_point_found = self.farthest_point(self.defects_found, self.max_contour_found, self.centroid_found)

                # Checks if the point is in the bottom of the frame - that cannot be True.
                # The tip of the finger should occupy the upper two thirds of the frame.
                if self.farthest_point_found is not None and self.farthest_point_found[1] < frame.shape[0] * 2 / 3:
                    self.finger_tip = self.farthest_point_found
                else:
                    self.finger_tip = None
            else:
                self.finger_tip = None
        else:
            self.max_counter_found = None
            self.hull_found = None
            self.centroid_found = None
            self.defects_found = None
            self.finger_tip = None


    def apply_hist_mask(self, frame):
        # The input frame is converted to HSV (Hue, Saturation, Value)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        # Highlights a hand by applying the histogram to the input frame.
        dst = cv2.calcBackProject([hsv], [0,1], self.hand_hist, [0, 180, 0, 256], 1)

        disc = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11))
        cv2.filter2D(dst, -1, disc, dst)

        ret, thresh = cv2.threshold(dst, 0, 250, cv2.THRESH_BINARY)
        thresh = cv2.merge((thresh, thresh, thresh))

        cv2.GaussianBlur(dst, (3,3), 0, dst)

        self.res = cv2.bitwise_and(frame, thresh)
        #cv2.imshow('Skin texture', self.res)
        return self.res

    def contours(self, frame):
        contours = cv2.findContours(frame, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[0]
        return contours

    def max_contour(self, contours):
        max_i = 0
        max_area = 0
        for i in range(len(contours)):
            contour = contours[i]
            area = cv2.contourArea(contour)
            if area > max_area:
                max_area, max_i = area, i
        return contours[max_i]

    def hull(self, contour):
        hull = cv2.convexHull(contour)
        return hull

    def defects(self, contour):
        hull = cv2.convexHull(contour, returnPoints=False)
        if hull is not None and len(hull > 3) and len(contour) > 3:
            defects = cv2.convexityDefects(contour, hull)
            return defects
        else:
            return None

    def centroid(self, contour):
        moments = cv2.moments(contour)
        if moments['m00'] != 0:
            cx = int(moments['m10']/moments['m00'])
            cy = int(moments['m01']/moments['m00'])
            return (cx,cy)
        else:
            return None

    def farthest_point(self, defects, contour, centroid):
        s = defects[:,0][:,0]
        cx, cy = centroid

        x = np.array(contour[s][:,0][:,0], dtype=np.float)
        y = np.array(contour[s][:,0][:,1], dtype=np.float)
        		
        xp = cv2.pow(cv2.subtract(x, cx), 2)
        yp = cv2.pow(cv2.subtract(y, cy), 2)
        dist = cv2.sqrt(cv2.add(xp, yp))

        dist_max_i = np.argmax(dist)

        if dist_max_i < len(s):
            farthest_defect = s[dist_max_i]
            farthest_point = tuple(contour[farthest_defect][0])
            return farthest_point
        else:
            return None

    def get_histogram(self):
        # If a hand snapshot is not taken the script waits for the user to put their hand into the ROI and press Spacebar.
        while True:
            ret, frame = self.cam.read()
            roi = frame[self.begin_Y:self.end_Y, self.begin_X:self.end_X]
            init_roi = roi.copy()
            self.draw_rectangle(roi)
            text = 'Cover all the green boxes with your hand and press Spacebar'
            cv2.putText(frame, text, (10,30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0) , 2)
            cv2.imshow('ROI', color_roi)        
            cv2.imshow('Camera feed', frame)
            k = cv2.waitKey(30) & 0xff
            if k == 27:
                cam.release()
                cv2.destroyAllWindows()
                break
            elif k == 32:
                self.set_hand_hist(init_roi)


    def tracker(self):
        while True:
            ret, frame = self.cam.read()
            frame = cv2.flip(frame, 1)
            roi = frame[self.begin_Y:self.end_Y, self.begin_X:self.end_X]
            cv2.rectangle(frame, (frame.shape[1] - self.ROI_SIZE, 0),
                         (frame.shape[1], self.ROI_SIZE), 
                         (255, 0, 0), 2)
            color_roi = roi.copy()
            roi = self.apply_hist_mask(roi)
            roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            ret, roi = cv2.threshold(roi, 0, 255, cv2.THRESH_BINARY)
            preprocessed = roi.copy()

            # Calls the function to find the contour, hull, centre of a hand and the tip of the pointing finger.
            self.draw_final(roi)

            roi = cv2.resize(roi, (self.IMG_SIZE, self.IMG_SIZE))
            roi = roi / 255.0

            roi = roi.reshape(-1, self.IMG_SIZE, self.IMG_SIZE, 1)

            prediction = self.model.predict(roi)
            i = prediction.argmax(axis=-1)[0]

            if i != 5:
                self.LABEL = self.LABELS[i]
            else:
                self.LABEL = ''

            if i == 0:
                self.command = 'VoiceControl'
            else:
                self.command = 'None'

            if prediction[0][i] * 100 > 70:
                text = f'{self.LABELS[i]} {prediction[0][i]*100:.2f}%'
                color = (0, 0, 255)
            else:
                text = 'Unknown'
                color = (0, 0, 255)
            cv2.putText(frame, text, (10,30), cv2.FONT_HERSHEY_SIMPLEX, 1, color , 4)

            # Displays the contour with the maximum area - presumably a hand.
            if self.max_contour_found is not None:
                cv2.drawContours(color_roi, [self.max_contour_found], -1, (0, 255, 0), 10)
            # Displays the centre of the contour.
            if self.centroid_found is not None:
                cv2.circle(color_roi, self.centroid_found, 10, [255, 0, 0], -1)
            # Displays the hull of the max contour.
            if self.hull_found is not None:
                cv2.drawContours(color_roi, [self.hull_found], -1, (255, 0, 0), 3)

            # If the CNN detects a pointing finger or a thumb up the last 15 checkpoint of the tip are displayed and saved.
            if i == 4:

                self.exposure_time += 1
                if self.defects_found is not None and len(self.defects_found) > 0:
                    for i in range(self.defects_found.shape[0]):
                        s, e, f, d = self.defects_found[i, 0]
                        start = tuple(self.max_contour_found[s][0])
                        end = tuple(self.max_contour_found[e][0])
                        far = tuple(self.max_contour_found[f][0])
                        #cv2.circle(color_roi, start, 5, [255, 0, 255], -1)

                    # In order to avoid wrong tracking of the tip while the user is moving their hand to the ROI,
                    # the script waits for (exposure_time * FPS miliseconds) before starts tracking the tip.
                    if self.exposure_time > 20:
                        cv2.putText(frame, self.TIP_TEXT, (10,60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255) , 2)
                        #cv2.putText(frame, f'Audio volume: {self.audio_volume}%', (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255) , 2)
                        
                        # Very first coordinate of tracking.
                        if len(self.tips) == 0 and self.finger_tip != None:
                            self.tips.append(self.finger_tip)
                            continue
                        
                        # If it is at least second detected coordinate and it is not far away from the previous one.
                        elif (
                            self.finger_tip != None
                            and len(self.tips) > 0
                            and abs(self.finger_tip[1] - self.tips[len(self.tips) - 1][1]) < 20
                            and abs(self.finger_tip[0] - self.tips[len(self.tips) - 1][0]) < 25
                            ):
                            self.tips.append(self.finger_tip)

                            if len(self.tips) > 15:
                                self.tips.pop(0)

                            for tip in self.tips:
                                cv2.circle(color_roi, tip, 5, [0, 0, 255], -1)
                                coordinates = (frame.shape[1] - self.ROI_SIZE + tip[0], tip[1])
                                cv2.circle(frame, coordinates, 5, [0, 0, 255], -1)

                            # Changes audio volume when the finger moves either to the left or to the right.
                            # The tip coordinates are in the following format (x,y)
                            self.diff = self.tips[len(self.tips) - 1][0] - self.tips[len(self.tips) - 2][0]

                        # Something went wrong: either the finger is moved too fast or an artefact is detected as the finger.
                        else:
                            self.diff = 0
                            self.tips = []
            else:
                self.exposure_time = 0
                self.diff = 0
                self.tips = []

            k = cv2.waitKey(int(1000 / self.FPS)) & 0xff
            if k == 27:
                self.cam.release()
                cv2.destroyAllWindows()
                break
            frame_original = cv2.resize(frame, (960, 720))
            cv2.imshow('ROI', color_roi)
            cv2.imshow('Preprocessed ROI', preprocessed)
            cv2.imshow('Camera feed', frame)

if __name__ == '__main__':
    import alsaaudio
    gestures_recognizer = GesturesRecognizer()
    gestures_recognizer.tracker()




        

