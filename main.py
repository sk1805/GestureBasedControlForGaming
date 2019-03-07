import speech_recognition as sr
import time
import signal
a = 0
import cv2
from threading import Thread
import numpy as np
import math
import sys
from directkeys import PressKey,ReleaseKey, W, A, S, D
import win32com.client as wincl
import tkinter as tk
from PIL import Image, ImageTk

speak = wincl.Dispatch("SAPI.SpVoice")

def pressEnter():
    pass

def straight():
    print("Straight")
    PressKey(W)
    ReleaseKey(A)
    ReleaseKey(D)
    ReleaseKey(S)

def brake():
    print("Breaking")
    PressKey(S)
    ReleaseKey(A)
    ReleaseKey(D)
    ReleaseKey(W)
    time.sleep(0.1)
    ReleaseKey(S)

def not_brake():
    print("Not Breaking")
    PressKey(W)
    ReleaseKey(A)
    ReleaseKey(D)
    ReleaseKey(S)
    time.sleep(0.1)
    ReleaseKey(W)

def left():
    print("Hard left")
    PressKey(A)
    ReleaseKey(W)
    ReleaseKey(S)
    ReleaseKey(D)

def right():
    print("Hard right")
    PressKey(D)
    ReleaseKey(W)
    ReleaseKey(A)
    ReleaseKey(S)

def reverse():
    print("Reverse")
    PressKey(S)
    ReleaseKey(A)
    ReleaseKey(W)
    ReleaseKey(D)

def forward_left():
    print("Turning left")
    PressKey(W)
    PressKey(A)
    ReleaseKey(D)
    ReleaseKey(S)
    time.sleep(0.05)
    ReleaseKey(A)


def forward_right():
    print("Turning right")
    PressKey(W)
    PressKey(D)
    ReleaseKey(A)
    ReleaseKey(S)
    time.sleep(0.05)
    ReleaseKey(D)

def reverse_left():
    print("Reverse left")
    PressKey(S)
    PressKey(A)
    ReleaseKey(W)
    ReleaseKey(D)


def reverse_right():
    print("Reverse right")
    PressKey(S)
    PressKey(D)
    ReleaseKey(W)
    ReleaseKey(A)

def releaseAllKeys():
    print("DidntDetectAnything")
    ReleaseKey(W)
    ReleaseKey(A)
    ReleaseKey(S)
    ReleaseKey(D)

cap = cv2.VideoCapture(0)
Dir="-->"

reverseMode = False
def setup():
    speak.Speak("Program starting in 5")
    time.sleep(1)
    speak.Speak("4")
    time.sleep(1)
    speak.Speak("3")
    time.sleep(1)
    speak.Speak("2")
    time.sleep(1)
    speak.Speak("1")
    time.sleep(1)

def isKeyword(str):
    print(str)
    str.lower()
    words = str.split()
    for w in words:
        if w == "reverse":
            reverseMode = True
            print("Reverse Mode ON")
            speak.Speak("Reverse Mode On")
            return False
            #time.sleep(3)
        elif w == "forward":
            reverseMode = False
            print("Reverse Mode OFF")
            speak.Speak("Reverse Mode Off")
            return False
            # time.sleep(3)
        elif w == "pause":
            global a
            a = 1
            return False
        elif w == "resume":
            global a
            a = 0
            return False
        elif w == "stop":
            global a
            a = -1
            return True
        elif w == "help":
            window = tk.Tk()
            window.title("Instructions for Gesture Driving")
            window.geometry("1000x1000")
            window.configure(background='white')
            pic = "ss3.png"
            img1 = ImageTk.PhotoImage(Image.open(pic))
            row = tk.Frame(window)
            l= tk.Label(row,image=img1)
            l.pack()
            row.pack()
            def close_window ():
                window.destroy()
            frame = tk.Frame(window)
            frame.pack()
            button = tk.Button(frame, text = "Close Window", command = close_window)
            button.pack()
            window.mainloop()
        elif w == "restart":
            pressEnter()

def suhas():
    while True:
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print("Say something")
            audio = r.adjust_for_ambient_noise(source)
            audio = r.listen(source)
            try:
                flag = isKeyword(r.recognize_google(audio))
                if(flag):
                    speak.Speak("Program Shutting Down")
                    break
            except sr.UnknownValueError:
                print("Some exception")
            except sr.RequestError as e:
                print("Some other exception")

process = Thread(target=suhas)
process.start()
lower=np.array([0,20,150]) #HSV ranges for skin color
upper=np.array([20,255,255])
setup()
while(1):
    global a
    if(a == -1):
        break
    if(a == 1):
        continue
    _,img=cap.read()
    im=img
    img=img[250:400,200:500] #Define RegionOfInterest
    im=cv2.rectangle(im,(500,250),(200,400),(0,255,0),2)



    converted=cv2.cvtColor(img,cv2.COLOR_BGR2HSV) #convert BGR image to HSV image
    skinMask=cv2.inRange(converted,lower,upper)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    skinMask=cv2.morphologyEx(skinMask,cv2.MORPH_CLOSE,kernel)
    skinMask = cv2.dilate(skinMask, kernel, iterations = 4)
    skinMask = cv2.GaussianBlur(skinMask, (7,7), 0)
    skin=cv2.bitwise_and(img,img,mask=skinMask)
    im2,contours,hierarchy=cv2.findContours(skinMask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)#fit contours to hand regions

    try:

        cnt=max(contours,key=lambda x:cv2.contourArea(x))
        for ind,ct in enumerate(contours):#Iterate over all contours in frame
            M=cv2.moments(contours[ind])
            area=int(M["m00"])
            if area in range(7000,13000):#Ignore other contours that are not of hands
                m1=cv2.moments(contours[0])
                m2=cv2.moments(contours[1])
                x1=int(m1["m10"]/m1["m00"])
                y1=int(m1["m01"]/m1["m00"])
                x2=int(m2["m10"]/m2["m00"])
                y2=int(m2["m01"]/m2["m00"])
                slope=math.tan(((y2-y1)/(x2-x1)))*100#convert the slope into %
                slope=round(slope,2)

                if slope>0:
                    Dir="<--"
                else:
                    Dir="-->"

                distance=math.sqrt(((x2-x1)**2) + ((y2-y1)**2))
                distance=round((distance/300)*100,2)#convert distance from 0 - 300 into %

                if(distance>100):#limit distance to 100
                    distance=100
                if slope>100:#limit angle to 100
                    slope=100
                elif slope< -100:
                    slope=-100

                cv2.line(im,(x1,y1),(x2,y2),(100,255,0),5)#plot line between centres of two hands
                cv2.putText(im,"Turning:"+Dir+str(slope)+"deg",(50,50),cv2.FONT_HERSHEY_SIMPLEX,0.5,(255,255,255),2)
                cv2.putText(im,"Acceleration:"+(str(distance)),(50,150),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,255,0),2)
                # print("xAxis")
                # print("yAxis")
                #               xAxis(slope)#set xAxis on Joystick to the slope %
                #               yAxis(distance)#set yAxis on Joystick to speed %

                if(not reverseMode):
                    if slope > 80 or slope < -80:
                        pass
                    elif slope > 65:
                        left()
                    elif slope<-65:
                        right()
                    elif slope>15:#limit angle to 100
                        forward_left()
                    elif slope< -15:
                        forward_right()
                    elif(distance>30):
                        straight()
                else:
                    if slope > 65:
                        right()
                    elif slope<-65:
                        left()
                    elif slope>15:#limit angle to 100
                        reverse_right()
                    elif slope< -15:
                        reverse_left()
                    elif(distance>30):
                        reverse()

            else:
                if area>13000 and len(contours)==1:#If area is of two hands joined
                    cv2.putText(im,"BRAKE",(50,50),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),4)
                    if(not reverseMode):
                        brake()
                    else:
                        not_brake()

    except ValueError:#If hands are out of the frame
#       reCentre()
        releaseAllKeys()
        pass

    except:
        pass

    cv2.imshow('main cam',im)
    cv2.imshow('segment',skin)
    # print(a)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cv2.destroyAllWindows()
process.join()
