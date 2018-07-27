# -*- coding: utf-8 -*-
"""
Created on Mon May  7 10:30:08 2018

@author: parit
"""
import cv2
import numpy as np
from time import sleep
kernel = np.ones((2,2),np.uint8)
img = cv2.imread('/home/shaaran/Pictures/Screenshot from 2018-07-26 23-42-44.png')
cnv_img  =cv2.cvtColor(img,cv2.COLOR_BGR2HSV)

#PRE PROCESSING

#--------------------------------------------
#for theory classes
def theory_class():
    low_range_theory_green  = np.array([10,150,254])
    high_range_theory_green = np.array([255,255,255])
    mask_green = cv2.inRange(cnv_img,low_range_theory_green,high_range_theory_green)
    #dilation = cv2.dilate(mask_green,kernel,iterations=1)
    eroder = cv2.erode(mask_green,kernel,iterations=1)
    reduce_opening = cv2.morphologyEx(eroder,cv2.MORPH_OPEN,kernel)
    res = cv2.bitwise_and(img,img,mask=reduce_opening)
    while True:
        cv2.imshow('ffcs_hsv', res)
        if cv2.waitKey(0):
            break
    cv2.destroyAllWindows()

#for lab slots classes
def lab_slots():
    low_range_lab  = np.array([25,80,250])
    high_range_lab = np.array([30,255,255])
    mask_lab = cv2.inRange(cnv_img,low_range_lab,high_range_lab)
    #dilation_lab = cv2.dilate(mask_lab,kernel,iterations=1)
    eroder_lab = cv2.erode(mask_lab,kernel,iterations=1)
    reduce_opening_lab = cv2.morphologyEx(eroder_lab,cv2.MORPH_OPEN,kernel)
    res_lab = cv2.bitwise_and(img,img,mask=reduce_opening_lab)
    while True:
        cv2.imshow('ffcs_hsv', res_lab)
        if cv2.waitKey(0):
            break
    cv2.destroyAllWindows()

def line_detect():
    import numpy as np
    import cv2



    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 250, apertureSize=3)
    print(img.shape[1])
    print(img.shape)
    minLineLength = img.shape[1] - 300
    lines = cv2.HoughLinesP(image=edges, rho=0.02, theta=np.pi / 500, threshold=10, lines=np.array([]),
                            minLineLength=minLineLength, maxLineGap=100)

    a, b, c = lines.shape
    for i in range(a):
        cv2.line(img, (lines[i][0][0], lines[i][0][1]), (lines[i][0][2], lines[i][0][3]), (0, 0, 255), 3, cv2.LINE_AA)

    cv2.imshow('edges', edges)
    cv2.imshow('result', img)

    cv2.waitKey(0)
    cv2.destroyAllWindows()



def findFirstBlock ( array , colors):
    
    flag = 0
    num_row = len(array)
    num_col = len(array[0])
    
    for i in range(num_col):
        for j in range(num_row):
            
            
            if((array[i][j]== colors[1]).all() or (array[i][j] == colors[0]).all() or (array[i][j] == colors[2]).all()):
                
                flag = 1
                #print(i,j)
                break
        if(flag == 1):
            break
        
    pos = [i,j]
    return pos

# -----------------------------------------------------------------------------------------------------------------------

def save2json (filename, free):
    
    import json,os
    current_dir = os.getcwd()
    
    free.sort()
    
    with open('slotNumbers.txt') as json_file: 
        slots = json.load(json_file)
        
    slots[filename.split('.')[0]] = free
    
    with open('slotNumbers.txt', 'w') as outfile:  
        json.dump(slots, outfile)
    

#   ---------------------------------------------------------------------------------------------------------------------   
def convertImage2json( filename ):
    
    
    from PIL import Image
    
    
    
    a = Image.open("test\\test images\\" + filename )
    
    
    if( a.format == 'png' or a.format == 'PNG'):
   
        lab_free = [249,239,164,255]
        theory_free = [255,255,204,255]
        busy = [204,255,51,255]
        break_color = [60,141,188,255] 
    
    else:
        
        print("Please upload the PNG screenshot file") 
        return
    
    colors = [lab_free, theory_free, busy, break_color]
        
    a = np.array(a)      #Converting image into numpy array
    num_row = len(a)
    num_col = len(a[0])
    pos =  findFirstBlock (a, colors)    #Finding the pixel positions of the first block of the timetable i.e Monday 8 AM block   
    i = pos[0]     # Row index of the first pixel of first block
    j = pos[1]     # Column index of the first pixel of first block
           
    free = [] # this contains the free slots . the slot number goes from 1-65 (vertically and then horizontally)
    classes = []  
    class_type = [] #0 for theory , 1 for lab
    L = 0
    first = 1 # Implies that we are on the first COLUMN of the slot 
    updated = 0 # Indicates whether LectureNo i.e L has been incremented or not

    
    for l in range(j,num_col - 1): #     l refers to the column number
        
        if(first == 1): # 1st column of lecture slot
            theory_flag = 1
            
            if(updated == 0): #    LectureNo hasn't been incremented
                
                L+=1
        
            
            for k in range(i,num_row):     #   k refers to the row number
                           
                if(theory_flag == 1):      #    Theory Slot
                
                    if((a[k][l] == busy).all() ):
                        #     "theory busy" 
                        th = 0
                        if(L not in classes):
                            classes.append(L)
                            class_type.append(0)
                       
                    elif((a[k][l]==theory_free).all()):
                        #     "theory empty"
                        th = 1
                    
                    elif((a[k][l]==break_color).all()):
                            #    "theory slot complete" and we move to Lab slot
                        theory_flag = 0
                    
                    
                    
                else:                       #     Lab Slot
                    
                    updated = 0
                    if((a[k][l]==busy).all()):
                        #print("lab busy",k,l)
                        if(L not in classes):
                            classes.append(L)
                            class_type.append(1)
                        lab = 0
                        
                        
                    elif((a[k][l]==lab_free).all()):
                        #print("lab empty",k,l)
                        lab = 1
                        if(th == 1):
                            if(L not in free):
                                free.append(L)
                            
                    elif((a[k][l]==break_color).all() ):
                        
                            
                            #print("lab complete",k,l)
                            theory_flag = 1
                            if(L%5==0):
                                break
                            else:
                                L+=1
                            
                                updated = 1
                        
                         
                    
            first = 0
        else: # We will skip until we are in the first column of the NEXT SLOT
            #             to identify the beginning of the next slot
            if((a[i][l]==break_color).all() and ((a[i][l+1]==theory_free).all() or (a[i][l+1]==busy).all())):
                first = 1
    
    # Slots which are always free for everyone             
    sure_free = [26, 27, 28, 29, 30, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65]   
    
    for e in sure_free:
        if(e not in free):
            free.append(e)
                
    #     Store the data of free slot numbers in  a json file
    save2json (filename, free)
    return free  
            
    
    
