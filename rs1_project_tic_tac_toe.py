import cv2
from ultralytics import YOLO
from PIL import Image
from pymycobot.mycobot import MyCobot
import pymycobot
from pymycobot import PI_PORT, PI_BAUD 
import time
import os
import sys
from pymycobot.mycobot import MyCobot
from pymycobot.genre import Angle, Coord
import time
from tictactoe import *

path = 'C:\\Users\\adity\\project_tic_tac_toe\\test\\ds16.jpg'
cam_port = 0
mc = MyCobot("COM5", 115200)

class CaptureROI():
    def __init__(self) -> None:
        self.drawing = False
        self.ix, self.iy = -1, -1
        self.roi_coordinates = []
        self.img = None
        
    # Mouse callback function
    def draw_rectangle(self,event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.drawing = True
            self.ix, self.iy = x, y

        elif event == cv2.EVENT_LBUTTONUP:
            self.drawing = False
            cv2.rectangle(self.img, (self.ix, self.iy), (x, y), (0, 255, 0), 2)
            self.roi_coordinates.append((self.ix, self.iy, x, y))
            cv2.imshow('image', self.img)

    def get_roi(self,path):
        # Read an image
        #self.img = cv2.imread(path)

        # reading the input using the camera 
        cam = cv2.VideoCapture(cam_port)
        cam.set(cv2.CAP_PROP_FRAME_WIDTH,1920)
        cam.set(cv2.CAP_PROP_FRAME_HEIGHT,1080)
        result, image = cam.read()
        image = cv2.rotate(image, cv2.ROTATE_180)
        if result:
            print('Success Catured Image')
        self.img= image


        cv2.namedWindow('image')
        cv2.setMouseCallback('image', self.draw_rectangle)
        while True:
            cv2.imshow('image', self.img)
            k = cv2.waitKey(1) & 0xFF
            if k == 27:  # Press 'Esc' to exit
                break
        cv2.destroyAllWindows()
        return self.roi_coordinates
    
    def crop_resize_and_save(self,image_path):
        (x1, y1,x2, y2) = self.roi_coordinates[0]
        self.cropped_image = self.img[y1:y2, x1:x2]
        # Save the cropped image with a unique filename
        self.cropped_image = cv2.resize(self.cropped_image, (501, 501), interpolation = cv2.INTER_LINEAR)
        cv2.imwrite(image_path, self.cropped_image)
        return self.cropped_image
    
    def get_cropped_camera_input(self,path):
        '''
        Function will read the input image and return it.
        '''
        #Reading Image
        #self.img = cv2.imread(path)

        # reading the input using the camera 
        cam = cv2.VideoCapture(cam_port) 
        cam.set(cv2.CAP_PROP_FRAME_WIDTH,1920)
        cam.set(cv2.CAP_PROP_FRAME_HEIGHT,1080)
        result, image = cam.read()
        image = cv2.rotate(image, cv2.ROTATE_180)
        if result:
            print('Success Catured Image')
        self.img= image

        (x1, y1,x2, y2) = self.roi_coordinates[0]
        self.cropped_image = self.img[y1:y2, x1:x2]
        # Save the cropped image with a unique filename
        self.cropped_image = cv2.resize(self.cropped_image, (501, 501), interpolation = cv2.INTER_LINEAR)
        return self.cropped_image

    def __del__(self):
        cv2.destroyAllWindows()


# 1|2|3
# -+-+-
# 4|5|6
# -+-+-
# 7|8|9

def get_matrix_block(detections):
    '''
   |   |
  7|  8| 9
   |   |
-----------
   |   |
  4| 5 | 6
   |   |
-----------
   |   |
 1 | 2 | 3
   |   |
    '''
    all_pos = []
    #Because I am resizing the image to 501x501
    
    H33,W33 = (167.0, 167.0)
    for det in detections:
        center_x = (det[0] + det[2]) / 2
        center_y = (det[1] + det[3]) / 2
        
        x,y = 0,0
        for i in range(1,4):
            if center_x == min(center_x,W33*i) :
                #print(i)
                x = i
                break

        for i in range(1,4):
            if center_y == min(center_y,H33*i) :
                #print(i)
                y = i
                break

        if y == 3:
            all_pos.append(x)
        if y == 2:
            all_pos.append(3+x)
        if y == 1:
            all_pos.append(6+x)
        
    return all_pos

def getPlayerInputNumber(theBoard,user_input_indices):
    '''
    Checks the list and finds the new unique entry
    '''
    for i in user_input_indices:
        if theBoard[i] == ' ':
            return i


def pump_on():
    mc.set_basic_output(2, 0)
    mc.set_basic_output(5, 0)


def pump_off():
    mc.set_basic_output(2, 1)    
    mc.set_basic_output(5, 1)

REAL_WORLD_ANGLES = [[48.33, -32.95, -148.18, 81.91, 5.18, -3.95],[17.22, -42.27, -151.96, 92.98, 8.96, -12.39],[0.26, -38.93, -152.49, 93.95, 3.86, -1.31],[43.94, -38.49, -138.33, 82.79, 2.19, -2.46],[23.55, -36.91, -137.28, 79.36, 0.35, -2.37],[-1.23, -38.4, -134.38, 77.87, 2.98, -0.61],[31.46, -52.55, -102.12, 65.03, 3.33, 1.58],[17.75, -48.86, -109.77, 68.02, 0.52, -0.26],[-0.52, -49.13, -110.21, 69.16, 3.33, 7.82]]

def place_marker(position):
    mc.send_angles([-0.26, 6.76, -109.24, 15.38, 2.19, -2.19], 50) #Home position
    time.sleep(2)
    _ = input('Marker position is given by the Cobot.')
    pump_on()
    time.sleep(2)
    mc.send_angles(REAL_WORLD_ANGLES[position-1], 50)
    time.sleep(2)
    pump_off()
    time.sleep(2)
    mc.send_angles([-0.26, 6.76, -109.24, 15.38, 2.19, -2.19], 50) #Home position
    time.sleep(2)

class Inferyolo():
    def __init__(self) -> None:
        # Load a pretrained YOLOv8n model
        self.model = YOLO('C:\\Users\\adity\\project_tic_tac_toe\\file\\content\\runs\\detect\\train\\weights\\best.pt')
    
    def downstream(self,crop_image):
        results = self.model(crop_image)  # results list
        detections = results[0].boxes.xyxy.numpy().tolist()
        user_input_indexes = get_matrix_block(detections)
        return user_input_indexes


if __name__ == '__main__':
    print('Start')

    roi_capture = CaptureROI()
    infer = Inferyolo()

    roi_coordinates = roi_capture.get_roi(path)
    print("ROI Coordinates: ",roi_coordinates)
    crop_image = roi_capture.crop_resize_and_save('crop.png') # ignore # for debugging

    while True:
        # Reset the board
        theBoard = [' '] * 10
        playerLetter, computerLetter = inputPlayerLetter()
        turn = whoGoesFirst()
        print(' ' + turn + ' moves first.')
        gameIsPlaying = True

        while gameIsPlaying:
            # print(theBoard)
            # print(len(theBoard))
            if turn == 'player':
                # Player's turn.
                drawBoard(theBoard)
                #move = getPlayerMove(theBoard)

                #Read image from camera:
                input_image_cropped = roi_capture.get_cropped_camera_input('')#Change
                user_input_indices = infer.downstream(input_image_cropped)
                
                #print(user_input_indices,'      ',theBoard)    
                move = getPlayerInputNumber(theBoard,user_input_indices)
                
                _ = input('Give Input: ')

                if move == None:
                    continue

                makeMove(theBoard, playerLetter, move)

                if isWinner(theBoard, playerLetter):
                    drawBoard(theBoard)
                    print('You won')
                    gameIsPlaying = False
                else:
                    if isBoardFull(theBoard):
                        drawBoard(theBoard)
                        print('tie')
                        break
                    else:
                        turn = 'AI'

            else:
                # Computer's turn.
                move = getComputerMove(theBoard, computerLetter)
                makeMove(theBoard, computerLetter, move)
                
                place_marker(move)
                
                if isWinner(theBoard, computerLetter):
                    drawBoard(theBoard)
                    print('AI Won')
                    gameIsPlaying = False
                else:
                    if isBoardFull(theBoard):
                        drawBoard(theBoard)
                        print(' tie')
                        break
                    else:
                        turn = 'player'

        if not playAgain():
            break