# Create your views here.
from django.shortcuts import render
from django.forms.models import model_to_dict
from django.http.response import StreamingHttpResponse
import cv2
from imutils.video import VideoStream
import time # Provides time-related functions
import numpy as np
from keras.models import model_from_json
import operator
import sys, os
import tensorflow as tf
from . models import ATM
import time
from collections import Counter
from pynput.keyboard import Key, Listener
from django.http import HttpResponse



pred = []
#graph = tf.get_default_graph()
num = ""
cno = ""
pinno = ""

pred_palm = []
#graph = tf.get_default_graph()
palm = ""

 

class WebCam(object):
    def __del__(self):
        self.webcam.stop()

    def __init__(self):
        self.webcam = VideoStream(src=0).start()
        self.pred = []

    def get_frame(self):
        categories = {0: 'ZERO', 1: 'ONE',2: 'TWO',3: 'THREE',4: 'FOUR',5: 'FIVE',6: 'SIX',7: 'SEVEN',8: 'EIGHT',9: 'NINE' }
        # Loading the model
        json_file = open("security/model-bw.json", "r")
        model_json = json_file.read()
        json_file.close()
        loaded_model = model_from_json(model_json)
        # load weights into new model
        loaded_model.load_weights("security/model-bw.h5")
        

        frame = self.webcam.read()
        frame = cv2.flip(frame, 1)
    
        # Got this from collect-data.py
        # Coordinates of the ROI
        x1 = int(0.5*frame.shape[1])
        y1 = 10
        x2 = frame.shape[1]-10
        y2 = int(0.5*frame.shape[1])
        # Drawing the ROI
        # The increment/decrement by 1 is to compensate for the bounding box
        cv2.rectangle(frame, (x1-1, y1-1), (x2+1, y2+1), (255,0,0) ,1)
        # Extracting the ROI
        roi = frame[y1:y2, x1:x2]
        
        # Resizing the ROI so it can be fed to the model for prediction
        roi = cv2.resize(roi, (64, 64)) 
        roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        _, test_image = cv2.threshold(roi, 120, 255, cv2.THRESH_BINARY)
        
        # Batch of 1

        
        result = loaded_model.predict(test_image.reshape(1, 64, 64, 1))

        prediction = {'ZERO': result[0][0], 
                    'ONE': result[0][1], 
                    'TWO': result[0][2],
                    'THREE': result[0][3],
                    'FOUR': result[0][4],
                    'FIVE': result[0][5],
                    'SIX': result[0][6],
                    'SEVEN': result[0][7],
                    'EIGHT': result[0][8],
                    'NINE': result[0][9]
                    }
        # Sorting based on top prediction
        prediction = sorted(prediction.items(), key=operator.itemgetter(1), reverse=True)
        
        # Displaying the predictions
        cv2.putText(frame, prediction[0][0], (10, 120), cv2.FONT_HERSHEY_PLAIN, 1, (255,0,0), 1)

        print(prediction[0][0])

        
        global num, pred_palm
        num = str(prediction[0][0])
        print(type(num))

        scale_percent = 50

        width = int(frame.shape[1]*scale_percent/100)
        height = int(frame.shape[0]*scale_percent/100)
        dim=(width,height)

        frame = cv2.resize(frame,dim,interpolation=cv2.INTER_AREA)    
        ret, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()

    def show(self,key):
            print('\nYou Entered {0}'.format( key))



class PiCam(object):
    def __del__(self):
        self.webcam.stop()

    def __init__(self):
        self.webcam = VideoStream(src=0).start()
        self.pred = []

    def get_frame(self):
        categories = {'left': 'left', 'right': 'right'}
        # Loading the model
        json_file = open("security/model_palm-bw.json", "r")
        model_json = json_file.read()
        json_file.close()
        loaded_model = model_from_json(model_json)
        # load weights into new model
        loaded_model.load_weights("security/model_palm-bw.h5")
        

        frame = self.webcam.read()
        frame = cv2.flip(frame, 1)
    
        # Got this from collect-data.py
        # Coordinates of the ROI
        x1 = int(0.5*frame.shape[1])
        y1 = 10
        x2 = frame.shape[1]-10
        y2 = int(0.5*frame.shape[1])
        # Drawing the ROI
        # The increment/decrement by 1 is to compensate for the bounding box
        cv2.rectangle(frame, (x1-1, y1-1), (x2+1, y2+1), (255,0,0) ,1)
        # Extracting the ROI
        roi = frame[y1:y2, x1:x2]
        
        # Resizing the ROI so it can be fed to the model for prediction
        roi = cv2.resize(roi, (64, 64)) 
        roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        _, test_image = cv2.threshold(roi, 120, 255, cv2.THRESH_BINARY)
        
        # Batch of 1

        
        result = loaded_model.predict(test_image.reshape(1, 64, 64, 1))

        prediction = {'LEFT': result[0][0], 
                    'RIGHT': result[0][1], 
                    }
        # Sorting based on top prediction
        prediction = sorted(prediction.items(), key=operator.itemgetter(1), reverse=True)
        
        # Displaying the predictions
        cv2.putText(frame, prediction[0][0], (10, 120), cv2.FONT_HERSHEY_PLAIN, 1, (255,0,0), 1)

        print(prediction[0][0])

        
        global palm, pred
        palm = str(prediction[0][0])
        print(type(palm))

        scale_percent = 50

        width = int(frame.shape[1]*scale_percent/100)
        height = int(frame.shape[0]*scale_percent/100)
        dim=(width,height)

        frame = cv2.resize(frame,dim,interpolation=cv2.INTER_AREA)    
        ret, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()

    def show(self,key):
            print('\nYou Entered {0}'.format( key))




def gen(camera):
    while True:
        frame = camera.get_frame()
        yield(b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

def webcam_feed(request):
    return StreamingHttpResponse(gen(WebCam()), content_type='multipart/x-mixed-replace; boundary=frame')

def picam_feed(request):
    return StreamingHttpResponse(gen(PiCam()), content_type='multipart/x-mixed-replace; boundary=frame')

# Create your views here.
def home(request):
    return render(request,'homepage.html')


def procedure(request):
    return render(request,'procedure.html')

def palm_verification(request):
    return render(request,'palm.html')


def cardno(request):
    i=0
    if request.method == 'POST':
        cardno=request.POST.get('cdno')
        global cno
        cno = cardno
        cards = ATM.objects.values('cardno')
        names = ATM.objects.values('name')
        while i < len(cards):
            i = i+1
            if cards[i-1].get("cardno") == cardno:
                print('True')
                cardno=str(cardno)
                name=ATM.objects.filter(cardno=cardno).values_list('name', flat=True)
                global pinno
                pinno=ATM.objects.filter(cardno=cardno).values_list('pin', flat=True)
                pinno=str(pinno)
                name=str(name)
                a,name,b = name.split("'")
                a,pinno,b= pinno.split("'")
                print(name)
                print(pinno)

                return render(request,'welcome.html')
            else:
                print('False')
                return render(request,'error1.html')
    return render(request,'cardno.html')

def pin(request):
    global pred
    print(pred)
    pins = ""
    for preds in pred:
        if preds == 'ZERO':
            pins = pins + '0'
        elif preds == 'ONE':
            pins = pins + '1'
        elif preds == 'TWO':
            pins = pins + '2'
        elif preds == 'THREE':
            pins = pins + '3'
        elif preds == 'FOUR':
            pins = pins + '4'
        elif preds == 'FIVE':
            pins = pins + '5'
        elif preds == 'SIX':
            pins = pins + '6'
        elif preds == 'SEVEN':
            pins = pins + '7'
        elif preds == 'EIGHT':
            pins = pins + '8'
        else:
            pins = pins + '9'
    pins = pins[-4:]
    print(pins)
    global pinno
    print(pinno)
    if pinno == pins:
        return render(request,'palm.html')
    else:
        return render(request,'error2.html')

def enter(request):
    if request.method == 'POST':
        val=request.POST.get('enter')
        global pred, num
        pred.append(num)
        print(pred)
        return render(request,'procedure.html')

def enter2(request):
    if request.method == 'POST':
        val=request.POST.get('enter2')
        global pred_palm, palm
        pred_palm.append(palm)
        print(pred_palm)
        return render(request,'palm.html')

def palm(request):
    global pred_palm
    print(pred_palm)
    if pred_palm[0] == 'LEFT':
        return render(request,'success.html')
    else:
        return render(request,'error3.html')
        





