import cv2
import time
import serial
import numpy as np
import picamera
from picamera.array import PiRGBArray#
from picamera import PiCamera
ser=serial.Serial('/dev/ttyAMA0',9600)
ser.write('s')
with picamera.PiCamera() as camera:
    with picamera.array.PiRGBArray(camera) as stream:
        camera.resolution=(640,480)
        camera.framerate=32
        #camera.start_preview()#
        while True:
            camera.capture(stream,'rgb',use_video_port=True)
            #print('stream',stream.array)
            img=stream.array
            img=cv2.flip(img,-1)
            img=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
            img=cv2.cvtColor(img,cv2.COLOR_RGB2GRAY)
            result=img.copy()
            img=cv2.resize(img,(640,480),interpolation=cv2.INTER_LINEAR)
            #img=cv2.Canny(img,50,150,apertureSize=3)#
            circles=cv2.HoughCircles(img,cv2.cv.CV_HOUGH_GRADIENT,1,500,\
                                     param1=100,param2=50,minRadius=10,\
                                     maxRadius=150)
            avgR=0
            avgX=0
            count=0
            stdR=100#
            stdX=320
            stdV=10#
            stdDir=0
            if circles is not None:
                circles=np.round(circles[0,:]).astype('int')
                print(circles)
                for (x,y,r) in circles:
                    cv2.circle(result,(x,y),r,(0,255,0),4)
                    avgR=avgR+r
                    avgX=avgX+x
                    count=count+1
            if count!=0:
                avgR=avgR/count
                avgX=avgX/count
                speed=stdV+(stdR-avgR)
                direction=stdDir+0.01(avgX-stdX)#
            else:
                print('no circle')
            
            cv2.imshow('result',result)#
            
            cv2.waitKey(1)
            stream.seek(0)
            stream.truncate()
            time.sleep(0.1)
