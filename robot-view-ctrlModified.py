import diff_drive
import ach
import sys
import time
from ctypes import *
import socket
import cv2.cv as cv
import cv2
import numpy as np
import pygame


# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)


pygame.init()
 
# Loop until the user clicks the close button.
done = False
 
# Used to manage how fast the screen updates
clock = pygame.time.Clock()
 
# Current position
x_coord = 10
y_coord = 10


# Count the joysticks the computer has
joystick_count = pygame.joystick.get_count()
if joystick_count == 0:
    # No joysticks!
    print("Error, I didn't find any joysticks.")
else:
    # Use joystick #0 and initialize it
    my_joystick = pygame.joystick.Joystick(0)
    my_joystick.init()

dd = diff_drive
ref = dd.H_REF()
tim = dd.H_TIME()

ROBOT_DIFF_DRIVE_CHAN   = 'robot-diff-drive'
ROBOT_CHAN_VIEW   = 'robot-vid-chan'
ROBOT_TIME_CHAN  = 'robot-time'
# CV setup 
cv.NamedWindow("wctrl", cv.CV_WINDOW_AUTOSIZE)
#capture = cv.CaptureFromCAM(0)
#capture = cv2.VideoCapture(0)

# added
##sock.connect((MCAST_GRP, MCAST_PORT))
newx = 320
newy = 240

nx = 320
ny = 240

r = ach.Channel(ROBOT_DIFF_DRIVE_CHAN)
r.flush()
v = ach.Channel(ROBOT_CHAN_VIEW)
v.flush()
t = ach.Channel(ROBOT_TIME_CHAN)
t.flush()
MaximumSpead = 3
i=0
ref.ref[0]=0
ref.ref[1]=0

while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
    if joystick_count != 0:
 
        left = my_joystick.get_axis(3)
	print "left = ",left
        right = my_joystick.get_axis(1)

    img = np.zeros((newx,newy,3), np.uint8)
    c_image = img.copy()
    vid = cv2.resize(c_image,(newx,newy))
    [status, framesize] = v.get(vid, wait=False, last=True)
    if status == ach.ACH_OK or status == ach.ACH_MISSED_FRAME or status == ach.ACH_STALE_FRAMES:
        vid2 = cv2.resize(vid,(nx,ny))
        img = cv2.cvtColor(vid2,cv2.COLOR_BGR2RGB)
        cv2.imshow("wctrl", img)
        cv2.waitKey(10)
    else:
        raise ach.AchException( v.result_string(status) )


    [status, framesize] = t.get(tim, wait=False, last=True)
    if status == ach.ACH_OK or status == ach.ACH_MISSED_FRAME or status == ach.ACH_STALE_FRAMES:
        pass
        #print 'Sim Time = ', tim.sim[0]
    else:

        raise ach.AchException( v.result_string(status) )
    if -left>0 and -left <=1 and ref.ref[0] <=MaximumSpead: 
	ref.ref[0] = ref.ref[0]+.01
    if -left<0 and -left >=-1 and ref.ref[0] >=-MaximumSpead: 
	ref.ref[0] = ref.ref[0]-.01
    if -right>0 and -right <=1 and ref.ref[1] <=MaximumSpead: 
	ref.ref[1] = ref.ref[1]+.01
    if -right<0 and -right >=-1 and ref.ref[1] >=-MaximumSpead: 
	ref.ref[1] = ref.ref[1]-.01
    print "ref.ref[0] = ",ref.ref[0]
    print "ref.ref[1] = ",ref.ref[1]
    print "right = ", -right
    print "left = ", -left

#    ref.ref[1] = -right

    print 'Sim Time = ', tim.sim[0]
    
    # Sets reference to robot
    r.put(ref);
