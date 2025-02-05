path = '/Users/yashbellap/Desktop/Project/Testcase/T1.jpgc'

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
        self.img = cv2.imread(path)
        # Create a window and set the callback function
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
        self.img = cv2.imread(path)
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

class Inferyolo():
    def __init__(self) -> None:
        self.model = YOLO('/Users/yashbellap/Desktop/Project/content/runs/detect/train/weights/best.pt')

    # Load a pretrained YOLOv8n model
    
    def downstream(self,crop_image):

        results = self.model(crop_image)  # results list

        detections = results[0].boxes.xyxy.numpy().tolist()

        user_input_indexes = get_matrix_block(detections)

        return user_input_indexes


if __name__ == '__main__':
    print('Welcome to Tic Tac Toe!')

    roi_capture = CaptureROI()
    infer = Inferyolo()

    path = '/Users/yashbellap/Desktop/Project/Testcase/T1.jpg'
    roi_coordinates = roi_capture.get_roi(path)
    print("ROI Coordinates: ", roi_coordinates)
    crop_image = roi_capture.crop_resize_and_save('crop.png')  # ignore # for debugging

    while True:
        # Reset the board
        theBoard = [' '] * 10
        playerLetter, computerLetter = inputPlayerLetter()
        turn = whoGoesFirst()
        print('The ' + turn + ' will go first.')
        gameIsPlaying = True

        while gameIsPlaying:
            for testcase in ['/Users/yashbellap/Desktop/Project/Testcase/T1.jpg','/Users/yashbellap/Desktop/Project/Testcase/T2.jpg', '/Users/yashbellap/Desktop/Project/Testcase/T3.jpg', '/Users/yashbellap/Desktop/Project/Testcase/T4.jpg']:

                # print(theBoard)
                # print(len(theBoard))
                if turn == 'player':
                    # Player's turn.
                    drawBoard(theBoard)
                    #move = getPlayerMove(theBoard)

                    #Read image from camera:
                    input_image_cropped = roi_capture.get_cropped_camera_input(testcase)#Change
                    user_input_indices = infer.downstream(input_image_cropped)
                    
                    print(user_input_indices,'      ',theBoard)    
                    move = getPlayerInputNumber(theBoard,user_input_indices)
                    
                    _ = input('Press enter')
                    if move == None:
                        continue
                    
                    
                    makeMove(theBoard, playerLetter, move)

                    if isWinner(theBoard, playerLetter):
                        drawBoard(theBoard)
                        print('Hooray! You have won the game!')
                        gameIsPlaying = False
                    else:
                        if isBoardFull(theBoard):
                            drawBoard(theBoard)
                            print('The game is a tie!')
                            break
                        else:
                            turn = 'computer'

                else:
                    # Computer's turn.
                    move = getComputerMove(theBoard, computerLetter)
                    makeMove(theBoard, computerLetter, move)
                    
                    
                    # place_marker(move)
                    

                    if isWinner(theBoard, computerLetter):
                        drawBoard(theBoard)
                        print('The computer has beaten you! You lose.')
                        gameIsPlaying = False
                        break
                    else:
                        if isBoardFull(theBoard):
                            drawBoard(theBoard)
                            print('The game is a tie!')
                            break
                        else:
                            turn = 'player'

        if not playAgain():
            break