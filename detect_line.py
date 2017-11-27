import cv2
import picamera
import picamera.array
import math
import numpy as np
#import zmq
import time
import serial
ser = serial.Serial('/dev/ttyAMA0',9600)
ser.write('s')

# For OpenCV2 image display
IMAGE_WINDOW_NAME = 'YellowBarTracker'
CONTROL_WINDOW_NAME = 'Control'
MASK_WINDOW_NAME = 'Mask'

# For socket communication
port = '5556'
#context = zmq.Context()
#socket = context.socket(zmq.PUB)

# Setting the initial mask threshold 
iLowH = 10
iHighH = 140

iLowS = 0
iHighS = 255

iLowV = 0
iHighV = 255

# Require by cv2.createTrackbar. we have nothing to do with nothing method
def nothing(var):
    pass

def connect():
    print('Getting data from camera...')
    socket.bind('tcp://*:%s' % port)
    
# Create trackbars for easier adjustment of the HSV threshold
def make_hsv_adjustment():
    pass
    #cv2.namedWindow(CONTROL_WINDOW_NAME)
    #cv2.createTrackbar('LowH', CONTROL_WINDOW_NAME, iLowH, 255, nothing); #Hue (0 - 179)
    #cv2.createTrackbar('HighH', CONTROL_WINDOW_NAME, iHighH, 255, nothing);

    #cv2.createTrackbar('LowS', CONTROL_WINDOW_NAME, iLowS, 255, nothing); #Saturation (0 - 255)
    #cv2.createTrackbar('HighS', CONTROL_WINDOW_NAME, iHighS, 255, nothing);

    #cv2.createTrackbar('LowV', CONTROL_WINDOW_NAME, iLowV, 255, nothing); #Value (0 - 255)
    #cv2.createTrackbar('HighV', CONTROL_WINDOW_NAME, iHighV, 255, nothing);
    
def track(image):

    '''Accepts BGR image as Numpy array
       Returns: (x,y) coordinates of centroid if found
                (-1,-1) if no centroid was found
                None if user hit ESC
    '''

    # Blur the image to reduce noise
    blur = cv2.GaussianBlur(image, (5,5),0)

    # Convert BGR to HSV
    hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)
    
    # Get the treshold from the trackbars
    #iLowH = cv2.getTrackbarPos('LowH', CONTROL_WINDOW_NAME)
    #iHighH = cv2.getTrackbarPos('HighH', CONTROL_WINDOW_NAME)
    #iLowS = cv2.getTrackbarPos('LowS', CONTROL_WINDOW_NAME)
    #iHighS = cv2.getTrackbarPos('HighS', CONTROL_WINDOW_NAME)
    #iLowV = cv2.getTrackbarPos('LowV', CONTROL_WINDOW_NAME)
    #iHighV = cv2.getTrackbarPos('HighV', CONTROL_WINDOW_NAME)

    # Threshold the HSV image for only green colors
    lower_yellow = np.array([iLowH,iLowS,iLowV])
    upper_yellow = np.array([iHighH,iHighS,iHighV])
    #lower_yellow=np.array([0,43,46])
    #upper_yellow=np.array([180,255,255])

    # Threshold the HSV image to get only yellow colors
    mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
    mask=cv2.bitwise_not(mask,mask)
    #cv2.imshow(MASK_WINDOW_NAME, mask)

    # Blur the mask
    bmask = cv2.GaussianBlur(mask, (5,5),0)

    # Take the moments to get the centroid
    moments = cv2.moments(bmask)
    m00 = moments['m00']
    centroid_x, centroid_y, radius = None, None, None
    if m00 != 0:
        centroid_x = int(moments['m10']/m00)
        centroid_y = int(moments['m01']/m00)
        #print 'centroid_x',centroid_x
        #print 'centroid_y',centroid_y
        radius = int(math.sqrt(m00 / 255 / 3.14159265358979323846))

    # Assume no centroid
    ball = (-1,-1, 0)

    # Use centroid if it exists
    if centroid_x != None and centroid_y != None and radius != None:

        ball = (centroid_x, centroid_y, radius)

        # Put red circle in at centroid in image
        cv2.circle(image, (centroid_x, centroid_y), 4, (255,0,0)) # center
        cv2.circle(image, (centroid_x, centroid_y), radius, (0,255,0))

    # Display full-color image
    #cv2.imshow(IMAGE_WINDOW_NAME, image)

    # Force image display, setting centroid to None on ESC key input
    #if cv2.waitKey(1) & 0xFF == 27:
    #    ball = None

    # Return coordinates of ball
    return ball

if __name__ == '__main__':
    #connect()
    #make_hsv_adjustment();
    with picamera.PiCamera() as camera:
        with picamera.array.PiRGBArray(camera) as stream:
            camera.resolution = (320, 240)

            while True:
                camera.capture(stream, 'bgr', use_video_port=True)
                # stream.array now contains the image data in BGR order
                image = stream.array
                image=cv2.flip(image,-1)
                ball = track(image)
                cx=ball[0]
                
                if not ball:
                    break
                if cv2.waitKey(1) & 0xFF == 27:
                    break

                #msg = '%d %d %d' % ball
                #print(msg)
                print(int((cx-160)/2+100))
                msg=chr(int((160-cx)/2+80))
                if cx==-1:
                    #ser.write('s')
                    print('no line')
                else:
                    ser.write(msg)
                #socket.send(msg)

                # reset the stream before the next capture
                stream.seek(0)
                stream.truncate()
                
                time.sleep(0.05);

            #cv2.destroyAllWindows()
