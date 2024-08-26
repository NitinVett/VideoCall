import cv2
import pygame
from pygame.locals import *
import sys

camera = cv2.VideoCapture(0)
screen = pygame.display.set_mode([1280, 720])
pygame.init()
while True:
    ret, frame = camera.read()
    output = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    #output = conn.send(pickle.dumps(frame),encode=False)
    #output = pickle.loads(output)
    output = pygame.surfarray.make_surface(output)
    screen.blit(output, (0, 0))
    pygame.display.update()
    for event in pygame.event.get():
        if event.type == KEYDOWN:
            sys.exit(0)