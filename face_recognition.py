    #! python3
# face_recognition.py - detects faces in the captured stream and prints the ID of known users.

import cv2
import numpy as np
import os
import logging
import time
import math

class FaceRecognizer:

    def __init__(self):
        self.logger = logging.getLogger('Gesell.face_recognition.FaceRecognizer')
        self.logger.info('Initializing an instance of FaceRecognizer')
        self.recognizer = cv2.face.LBPHFaceRecognizer_create(15, 50)
        #self.recognizer = cv2.face.FisherFaceRecognizer_create(15, 3000)
        self.recognizer.read('trainer/trainer.yml')
        cascadePath = "haarcascade_frontalface_default.xml"
        self.faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + cascadePath);
        self.eyeCascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        #iniciate id counter
        id = 0
        # names related to ids: example ==>Dmitry: id=1,  etc
        self.names = ['None', 'Dmitry', 'Yaroslav', 'Anna', 'Agniya'] 

        # Initialize and start realtime video capture
        self.cam = cv2.VideoCapture(0)
        self.cam.set(3, 768) # set video widht
        self.cam.set(4, 768) # set video height

        # Define min window size to be recognized as a face
        self.minW = 0.1 * self.cam.get(3)
        self.minH = 0.1 * self.cam.get(4)

        self.detected_faces = set()

        self.users = {'Dmitry':{'focus': False, 'first': False, 'second': False, 'third': False},
                      'Anna':{'focus': False, 'first': False, 'second': False, 'third': False},
                      'Yaroslav':{'focus': False, 'first': False, 'second': False, 'third': False},
                      'Agniya':{'focus': False, 'first': False, 'second': False, 'third': False}}

        self.current_users = set()
        
        self.logger.info('FaceRecognizer has been initialized!')

    def  realtime_recognizer(self):
        total_recognitions = 0
        better = 0
        average_improvement = 0
        temp = 0
        while True:
            ret, img = self.cam.read()

            img = cv2.flip(img, 1)

            gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

            faces = self.faceCascade.detectMultiScale( 
                gray,
                scaleFactor = 1.3,
                minNeighbors = 5,
                minSize = (int(self.minW), int(self.minH)),
                )

            #if len(faces) == 0:
                #cv2.putText(gray, 'NO FACES DETECTED!!!', (100,30), self.font, 1.2, (0,0,255), 4)
                #cv2.imshow('camera', img)
              
            self.detected_faces = set() # The set is updated in real-time and consists of the users currently detected.

            for(x,y,w,h) in faces:
                cv2.rectangle(img, (x,y), (x+w,y+h), (0,255,0), 2)

                square = gray[y:y+h, x:x+w]
                square = cv2.resize(square, (200, 200))

                id, confidence = self.recognizer.predict(square)

                eyes_angle = self.eyes_angle(gray[y:y+h, x:x+w])

                if eyes_angle == None:
                    break

                gray = self.rotate_image(gray, eyes_angle)

                square = gray[y:y+h, x:x+w]
                square = cv2.resize(square, (200, 200))

                id, confidence2 = self.recognizer.predict(square)

                # Check if confidence is less than 100 ==> "0" is perfect match 
                if (confidence2 < 60):
                    """if abs(eyes_angle) >= 2:
                        total_recognitions += 1
                        if confidence2 < confidence:
                            better += 1
                        temp += (confidence - confidence2)"""
                    id = self.names[id]
                    #confidence2 = "  {0}%".format(round(100 - confidence2))
                    self.detected_faces.add(id)
                    #cv2.putText(img, str(id), (x+5,y-5), self.font, 1, (255,255,255), 2)
                    #print(f'Before: {100 - int(confidence)}%   After:  {confidence2}%')
                else:
                    id = "unknown"
                    #confidence2 = "  {0}%".format(round(100 - confidence2))
                    self.detected_faces.add('Unknown')
                    #cv2.putText(img, str(id), (x+5,y-5), self.font, 1, (0,0,255), 2)
                #cv2.putText(img, str(confidence2), (x+5,y+h-5), self.font, 1, (255,255,0), 1)
                #cv2.imshow('face', square)
                #cv2.imshow('camera', img)

            # Waits 2 seconds to capture the next frame. If the user presses 'ESC' the script is terminated.
            if len(faces) == 0:
                k = cv2.waitKey(2000) & 0xff
            else:
                k = cv2.waitKey(2000) & 0xff
            if k == 27:
                #print(f'Better confidence rate: {round((better / total_recognitions) * 100)}%. ')
                #print(f'Average confidence improvement: {round(temp / total_recognitions)}%.')
                self.cam.release()
                cv2.destroyAllWindows()
                self.logger.warning('The user pressed \'ESC\'. FaceRecognizer has been terminated.')
                break
            self.focus()

    def eyes_angle(self, gray):
        eyes = self.eyeCascade.detectMultiScale(
               gray,
               scaleFactor= 1.3,
               minNeighbors=5,
               minSize=(5, 5,)
               )
        if len(eyes) != 2:
            return None        
                
        coordinates = []
        
        for (ex, ey, ew, eh) in eyes:
            coordinates.append([(ex + ew) // 2, (ey + eh) // 2])
        angle = self.alignment(coordinates)    
        return angle

        
    def alignment(self, eyes):
        if eyes[0][0] < eyes[1][0]:
            left_eye, right_eye = eyes[0], eyes[1]
        else:
            left_eye, right_eye = eyes[1], eyes[0]
        tangens = abs(left_eye[1] - right_eye[1]) / abs(left_eye[0] - right_eye[0])
        angle = math.degrees(math.atan(tangens))
        if left_eye[1] > right_eye[1]:
            angle = angle*(-1)
        #print(left_eye[0], right_eye[0], angle)
        return angle

    def rotate_image(self, image, angle):
        image_center = tuple(np.array(image.shape[1::-1]) / 2)
        rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
        result = cv2.warpAffine(image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR)
        return result
        
    def focus(self):
        person = self.users['Dmitry']
        #print(person['focus'], person['first'], person['second'], person['third'])
        for user in self.users.keys():
            # If user is not in focus at the moment.
            if user not in self.detected_faces:
                if self.users[user]['third']:
                    self.users[user]['third'] = False
                elif self.users[user]['second']:
                    self.users[user]['second'] = False
                elif self.users[user]['first']:
                    self.users[user]['first'] = False
                elif self.users[user]['focus']:
                    self.current_users.remove(user)
                    self.users[user]['focus'] = False
                    self.logger.debug(f'User {user} is off the focus')
            # If user is in focus at the moment.
            else:
                if self.users[user]['focus'] == False:
                    self.current_users.add(user)
                    self.users[user]['focus'] = True
                    self.logger.debug(f'User {user} is using the mirror')
                self.users[user]['third'] = True
                self.users[user]['second'] = True
                self.users[user]['first'] = True
               

if __name__ == '__main__':
    recognizer = FaceRecognizer()
    recognizer.realtime_recognizer()


