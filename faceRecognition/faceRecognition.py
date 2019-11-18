import cv2
import os
import paho.mqtt.client as mqtt
import numpy as np
from PIL import Image



# Global Variables
cam = cv2.VideoCapture(0)
detector = cv2.CascadeClassifier("haarcascade_frontalface_default.xml");
face_detected = 0
face_add = 0
face_id = 0

def on_connect(client, userdata, flags, rc):
    print("[faceRecognition]: Connected")
    client.subscribe("camera/addId")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    global face_detected
    global face_add
    global face_id 
    #print(msg.topic+" "+str(msg.payload))
    

    if str(msg.topic) == "camera/addId":
        face_id = str(msg.payload)
        face_add = 1
def initMqtt():
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect("localhost", 1883)
    client.loop_start()
#loop_stop(force=False)

# function to get the images and label data
def getImagesAndLabels(path):

    imagePaths = [os.path.join(path,f) for f in os.listdir(path)]
    faceSamples=[]
    ids = []

    for imagePath in imagePaths:

        PIL_img = Image.open(imagePath).convert('L') # convert it to grayscale
        img_numpy = np.array(PIL_img,'uint8')

        id = int(os.path.split(imagePath)[-1].split(".")[1])
        faces = detector.detectMultiScale(img_numpy)

        for (x,y,w,h) in faces:
            faceSamples.append(img_numpy[y:y+h,x:x+w])
            ids.append(id)

    return faceSamples,ids


def trainer():
    path = 'dataset'

    recognizer = cv2.face.LBPHFaceRecognizer_create()



    print ("\n [FaceRecognition] Training faces. It will take a few seconds. Wait ...")
    faces,ids = getImagesAndLabels(path)
    recognizer.train(faces, np.array(ids))

    # Save the model into trainer/trainer.yml
    recognizer.write('trainer/trainer.yml') # recognizer.save() worked on Mac, but not on Pi

    # Print the numer of faces trained and end program
    #print("\n [FaceRecognition] {0} faces trained. Exiting Program".format(len(np.unique(ids))))


def faceAddition(face_id):
    face_detector = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    # For each person, enter one numeric face id

    ## TODO: increament last id At last read last id from file

    #print("\n [FaceRecognition] Initializing face capture.")
    # Initialize individual sampling face count
    count = 0
    while(count<30):
        count += 1
        ret, img = cam.read()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_detector.detectMultiScale(gray, 1.3, 5)
        #cv2.imshow('image', img)
        for (x,y,w,h) in faces:

            cv2.rectangle(img, (x,y), (x+w,y+h), (255,0,0), 2)
            

            # Save the captured image into the datasets folder
            cv2.imwrite("dataset/User." + str(face_id) + '.' + str(count) + ".jpg", gray[y:y+h,x:x+w])
            print("[FaceRecognition]: Face capture count =   "  + str(count))
           # cv2.imshow('image', img)
        
        
        
       
        # Do a bit of cleanup
    
    trainer()

def faceDetection():
    global cam
    #print('[FaceRecognition]:  Face Detection ON')
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    try:
        recognizer.read('trainer/trainer.yml')
    except:
        return [0]
    cascadePath = "haarcascade_frontalface_default.xml"
    faceCascade = cv2.CascadeClassifier(cascadePath);

    font = cv2.FONT_HERSHEY_SIMPLEX

    #iniciate id counter
    id = 0

    # Define min window size to be recognized as a face
    minW = 0.1*cam.get(3)
    minH = 0.1*cam.get(4)
    counter = 0
    recognised_ids = []
    while counter<=20:
        counter+=1
        ret, img =cam.read()
        gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

        faces = faceCascade.detectMultiScale(
            gray,
            scaleFactor = 1.2,
            minNeighbors = 5,
            minSize = (int(minW), int(minH)),
           )

        for(x,y,w,h) in faces:

            cv2.rectangle(img, (x,y), (x+w,y+h), (0,255,0), 2)

            id, confidence = recognizer.predict(gray[y:y+h,x:x+w])

            # Check if confidence is less them 100 ==> "0" is perfect match
            if (confidence < 100):
                pass
               # id = names[id]
                #print("[FaceRecognition]:  Face id detected = " str(id))
            #    confidence = "  {0}%".format(round(100 - confidence))
            else:
                id = 0
            #    confidence = "  {0}%".format(round(100 - confidence))
            # storing list of recognised/unrecognised faces
            if not id in recognised_ids:
                recognised_ids.append(id)
           # cv2.putText(img, str(id), (x+5,y-5), font, 1, (255,255,255), 2)
           # cv2.putText(img, str(confidence), (x+5,y+h-5), font, 1, (255,255,0), 1)


        
        #cv2.imshow('camera',img)
    #print('[FaceRecognitinon]:  detection completed')
    return recognised_ids


if __name__ == "__main__":
    client = mqtt.Client()
    initMqtt()
    
    cam.set(3, 640) # set video width
    cam.set(4, 480) # set video height
    face_detected = 1
    while(1):
        if face_detected == 1:
            
            list_id = faceDetection()
            print ("[FaceRecognitinon]: Detected face ids : " + str(list_id))
            str_id = ' '.join(map(str, list_id))
        
            client.publish("camera/recognisedIds",str_id)
        if face_add == 1:
            faceAddition(face_id) 
            face_add = 0
    
    usleep(10000);
