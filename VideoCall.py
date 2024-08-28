import imutils as imutils
import numpy
import pygame
from pygame.locals import *
import cv2
import numpy as np
import sys

camera = cv2.VideoCapture(0)
pygame.init()
pygame.display.set_caption("OpenCV camera stream on Pygame")
screen = pygame.display.set_mode((1280, 720))

try:
    while True:

        ret, frame = camera.read()
        frame = cv2.resize(frame, (960, 360))
        screen.fill([0, 0, 0])

        frame = np.array(frame)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = np.rot90(frame)
        print(frame.dtype)
        frame = frame.tobytes()

        frame = np.frombuffer(frame, dtype=numpy.uint8).reshape(frame.shape)




        frame = pygame.surfarray.make_surface(frame)
        screen.blit(frame, (160, 0))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == KEYDOWN:
                sys.exit(0)
except:
    pass
