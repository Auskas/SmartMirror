#! python3
# facerecognition.py

import cv2
import os
import math
import numpy as np

def eyes_angle(gray):
    eyes = eyeCascade.detectMultiScale(
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
    angle = alignment(coordinates)    
    return angle

        
def alignment(eyes):
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

def rotate_image(image, angle):
    image_center = tuple(np.array(image.shape[1::-1]) / 2)
    rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
    result = cv2.warpAffine(image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR)
    return result


cam = cv2.VideoCapture(0)
#cam.set(4, 640) # set video width
#cam.set(4, 640) # set video height

face_detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
eyeCascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

# For each person, enter one numeric face id
face_id = input('\n enter user id end press  ==>  ')

print("\n [INFO] Initializing face capture. Look the camera and wait ...")
# Initialize individual sampling face count
count = 0

while True:
    #input('Press \'Enter\' to take a snapshot')
    ret, img = cam.read()
    
    img = cv2.flip(img, 1)
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    faces = face_detector.detectMultiScale(gray, 1.3, 5)

    for (x,y,w,h) in faces:

        angle = eyes_angle(gray[y:y+h, x:x+w])

        if angle == None:
            break

        gray = rotate_image(gray, angle)

        square = gray[y:y+h, x:x+w]
        square = cv2.resize(square, (200, 200))

        #cv2.rectangle(img, (x,y), (x+w,y+h), (255,0,0), 2)     
        count += 1

        # Save the captured image into the datasets folder
        cv2.imwrite("dataset/User." + str(face_id) + '.' + str(count) + ".jpg", square)

    cv2.imshow('image', img)
    k = cv2.waitKey(100) & 0xff # Press 'ESC' for exiting video
    if k == 27:
        break
    if count >= 15: # Takes 10 face sample and stops video
        break



# Do a bit of cleanup
print("\n [INFO] Exiting Program and cleanup stuff")
cam.release()
cv2.destroyAllWindows()
