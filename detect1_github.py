__author__ = 'SHZ'
"""
Created on Fri Aug 30 20:49:52 2019

@author: Seyedhassan Zabihifar (SHZ)
@Sberbank Robotics Laboratory
"""
############################  To undrestand changing in pictures 

import numpy as np
import time
import cv2 


#%%
def get_outlined_object_cv_image(cv_image):
    rows,cols,channels=cv_image.shape
    gray = cv2.cvtColor(cv_image,cv2.COLOR_BGR2GRAY)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(100,100))
    blackhat = cv2.morphologyEx(gray,cv2.MORPH_BLACKHAT,kernel)
    _,thresh = cv2.threshold(blackhat,100,255,cv2.THRESH_BINARY|cv2.THRESH_OTSU)
    thresh = cv2.dilate(thresh,None)        #dilate thresholded image for better segmentation
    (cnts,_) = cv2.findContours(thresh.copy(),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    avgCntArea = np.mean([cv2.contourArea(k) for k in cnts])      #contourArea for digit approximation
   
    for i,c in enumerate(cnts):
        if cv2.contourArea(c)<avgCntArea/1.2:     #cv2.contourArea(c)<avgCntArea/10
           continue

        mask = np.zeros(thresh.shape,dtype="uint8")   #empty mask for each iteration
        (x,y,w,h) = cv2.boundingRect(c)
        hull = cv2.convexHull(c)
        cv2.drawContours(mask,[hull],-1,255,-1)     #draw hull on mask
        mask = cv2.bitwise_and(thresh,thresh,mask=mask) #segment digit from thresh

    
            
    return   thresh,mask
     
#%% 
#****************  The value of mdifthresh shows the different between two pictures which are loaded
#****************  For blank or small things do not working correctly
# Press R and hold for 4 second to reset
# Press Q to exit

camera = cv2.VideoCapture(1)

def reset():
    ret , image0 = camera.read()
    (thresh0,mask0)=get_outlined_object_cv_image(image0)
    print "reset"

    return image0,thresh0,mask0
    
time.sleep(0.5)
image0,thresh0,mask0=reset()
move=0


while True:

    ret, image1 = camera.read()
    time.sleep(0.2)
    ret, image2 = camera.read()
    
    (thresh1,mask1)=get_outlined_object_cv_image(image1)

    (thresh2,mask2)=get_outlined_object_cv_image(image2)

    
    mask0_array=np.array(mask0)
    mmask0=np.mean(mask0_array)
    
    mask1_array=np.array(mask1)
    mmask1=np.mean(mask1_array)

    mask2_array=np.array(mask2)
    mmask2=np.mean(mask2_array)
    
    
    difthresh1=thresh1-thresh2
    difthresh2=thresh2-thresh1
    difthresh=cv2.add(difthresh1,difthresh2)
    difthresh_array=np.array(difthresh)
    mdifthresh=np.mean(difthresh_array)

    if move==0:
        cv2.imshow("difthresh",difthresh)
        cc=cv2.add(image1,image2)
    
    difthresh0=thresh0-thresh2
    difthresh00=thresh2-thresh0
    difthresh02=cv2.add(difthresh0,difthresh00)
    difthresh02_array=np.array(difthresh02)
    mdifthresh02=np.mean(difthresh02_array)

    if move==1:
        cc=cv2.add(image0,image2)
        cv2.putText(cc,'Object is moved',(135,30),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,255,0),2)
        cv2.imshow("difthresh",difthresh02)
        
    if mdifthresh>5 and (mmask1>4 or mmask2>4):
        cv2.putText(cc,'Changes is detected',(135,50),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,255,0),2)
        print "Changes is detected",  mdifthresh

               
    else:
        if mdifthresh02>5:
            move=1
            print "Object is moved", mdifthresh02
        else:
            move=0
        cv2.putText(cc,'NO Change',(135,50),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,255,0),2)
        #print "NO Change"
        
    cv2.imshow("cc",cc)    
    if cv2.waitKey(5) & 0xFF == ord('q'):
            camera.release()            
            cv2.destroyAllWindows()
            exit
            break  
    if cv2.waitKey(10) & 0xFF == ord('r'):
            image0,thresh0,mask0=reset()
