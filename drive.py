import cv2
import numpy as np
from picarx import Picarx
from time import sleep
from vilib import Vilib
import os

def filter_color(image,lower_range,upper_range):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_range, upper_range)
    return mask

def is_main_color_detected(area_of_interest):
    lower_yellow = np.array([20, 100, 100])
    upper_yellow = np.array([40, 255, 255])
    
    mask = filter_color(area_of_interest, lower_yellow, upper_yellow)
    
    yellow_pixels = cv2.countNonZero(mask)
    
    if yellow_pixels > 100:
        cv2.imwrite("main_roi.jpg", area_of_interest)
        cv2.imwrite("main_mask.jpg", mask)
        return mask
    return None
    

def is_left_turn_color_detected(area_of_interest):
    lower_green = np.array([35, 100, 100])
    upper_green = np.array([85, 255, 255])
    
    mask = filter_color(area_of_interest, lower_green, upper_green)
    
    blue_pixels = cv2.countNonZero(mask)
    total_pixels = area_of_interest.shape[0] * area_of_interest.shape[1]
    if blue_pixels > 100:
        cv2.imwrite("left_roi.jpg", area_of_interest)
        cv2.imwrite("left_mask.jpg", mask)
        return mask
    return None

def is_right_turn_color_detected(area_of_interest):
    lower_red = np.array([0, 120, 70])
    upper_red = np.array([10, 255, 255])

    mask = filter_color(area_of_interest, lower_red, upper_red)

    red_pixels = cv2.countNonZero(mask)
    total_pixels = area_of_interest.shape[0] * area_of_interest.shape[1]
    if red_pixels > 100:
        cv2.imwrite("right_roi.jpg", area_of_interest)
        cv2.imwrite("right_mask.jpg", mask)
        return mask
    return None

def get_area_of_interest_rightMain_turn(image):
    height, width = image.shape[:2]
    roi_start_y = int(height * 0.95) 
    roi_start_x = int(width * 0.2)   
    roi_end_x = int(width * 0.8)     

    area_of_interest = image[roi_start_y:, roi_start_x:roi_end_x]
    return area_of_interest

def get_area_of_interest_left_turn(image):
    height, width = image.shape[:2]
    roi_start_y = int(height * 0.7) 
    roi_end_y = int(height * 0.75) 
    roi_start_x = int(width * 0.2)   
    roi_end_x = int(width * 0.8)     

    area_of_interest = image[roi_start_y:roi_end_y, roi_start_x:roi_end_x]
    return area_of_interest

def get_area_of_interest_stopLeft(image):
    width = image.shape[1]
    roi_start_x = int(width * 0.4)   
    roi_end_x = int(width * 0.6)     

    area_of_interest = image[:, roi_start_x:roi_end_x]
    return area_of_interest

def get_action(image):
    global turn
    global last_action
    global turn_index
    if last_action == "rotate_left":
        area_of_interest_stopLeft = get_area_of_interest_stopLeft(image)
        mask = is_left_turn_color_detected(area_of_interest_stopLeft)
        if mask is not None:
            return "stop_left_rotation"

    else:
        area_of_interest_rightMain_turn = get_area_of_interest_rightMain_turn(image)
        if turn == "right":
            right_turn_color_mask = is_right_turn_color_detected(area_of_interest_rightMain_turn)
            if right_turn_color_mask is not None:
                    turn_index += 1
                    return "rotate_right"
            else:
                main_color_mask = is_main_color_detected(area_of_interest_rightMain_turn)
                if main_color_mask is not None:
                    return get_direction(main_color_mask)
        elif turn == "left":
            area_of_interest_left_turn = get_area_of_interest_left_turn(image)
            left_turn_color_mask = is_left_turn_color_detected(area_of_interest_left_turn)
            if left_turn_color_mask is not None:
                turn_index += 1
                return "rotate_left"
            else:
                main_color_mask = is_main_color_detected(area_of_interest_rightMain_turn)
                if main_color_mask is not None:
                    return get_direction(main_color_mask)
        elif turn == "straight":
            area_of_interest_left_turn = get_area_of_interest_left_turn(image)
            left_turn_color_mask = is_left_turn_color_detected(area_of_interest_left_turn)
            if left_turn_color_mask is not None:
                turn_index += 1
                sleep(0.1)
            main_color_mask = is_main_color_detected(area_of_interest_rightMain_turn)
            if main_color_mask is not None:
                return get_direction(main_color_mask)
            

      
def get_direction(mask):
    height, width = mask.shape
    white_pixels = np.where(mask == 255)

    left_edge_x = np.min(white_pixels[1])
    right_edge_x = np.max(white_pixels[1])
    image_center_x = width // 2

    if left_edge_x <= image_center_x <= right_edge_x:
        direction = "forward"
    elif image_center_x < left_edge_x:
        direction = "left"
    else:
        direction = "right"
    return direction

def get_frame():
    name = 'temp'
    path = "/home/Cait/micro/Pictures"
    Vilib.take_photo(name, path)
    path = '%s/%s.jpg'%(path,name)
    image = cv2.imread(path)
    os.remove(path)
    return image

global turn
global last_action
global turn_index
def drive(turn_sequence):
    global turn
    global last_action
    global turn_index
    turn_sequence += ["straight"]
    try:
        px = Picarx()
        px_power = 2
        offset = 20
        Vilib.camera_start(vflip=False, hflip=False)
        Vilib.display(local=True,web=True)
        px.set_cam_tilt_angle(-60)
        px.set_cam_pan_angle(0)
        last_action = None
        turn_index = 0
        pause_after_left_turn = 0.7
        pause_after_right_turn = 0.2
        pause_at_turn = 0.7
        rotate_right = [1,-1]
        rotate_left = [-3,0.5]
        sleep(1)
        while True:
            if turn_index >= len(turn_sequence):
                break
            turn = turn_sequence[turn_index]
            print(turn)
    
            image = get_frame()
            action = get_action(image)
            
            if last_action =="rotate_right":
                px.cali_dir_value = rotate_right
                px.forward(px_power)
                if action == 'forward':
                  last_action = None
                  px.cali_dir_value = [1,1]
                  px.set_dir_servo_angle(0)
                  px.forward(px_power)
                  sleep(pause_after_right_turn)

            if last_action =="rotate_left":
                px.cali_dir_value = rotate_left
                px.forward(px_power)
                if action == 'stop_left_rotation':
                  cv2.imwrite("snap.jpg", image)
                  last_action = None
                  px.cali_dir_value = [1,1]
                  px.set_dir_servo_angle(0)
                  px.forward(px_power)
                  sleep(pause_after_left_turn)

            elif action == 'rotate_right':
                last_action = 'rotate_right'
                px.cali_dir_value = rotate_right
                px.forward(px_power)
                sleep(pause_at_turn)
            
            elif action == 'rotate_left':
                last_action = 'rotate_left'
                px.cali_dir_value = rotate_left
                px.forward(px_power)
                sleep(pause_at_turn)
        
            elif action == 'forward':
                px.set_dir_servo_angle(0)
                px.forward(px_power)
            elif action == 'left':
                px.set_dir_servo_angle(offset)
                px.forward(px_power)
            elif action == 'right':
                px.set_dir_servo_angle(-offset)
                px.forward(px_power)
            
    finally:
        px.stop()
        print("stop and exit")
        sleep(0.1)
