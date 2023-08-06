# coding:utf-8
import numpy as np
import cv2
import os
from distutils.sysconfig import get_python_lib
import time as tm

class face_detector:
    def __init__(self,modelversion=1):
        self.site_package=get_python_lib()
        #print(self.site_package)
        if modelversion==1:
            PATH_TO_MODEL = os.path.join(self.site_package,'vcvf/data/lbp_face_20180629')
        elif modelversion==0:
            PATH_TO_MODEL = os.path.join(self.site_package,'vcvf/data/lbp_face_0628')
          
        print(PATH_TO_MODEL)
        #print(os.getcwd())
        #print(os.path.dirname(os.__file__))

        #print(get_python_lib()) 
        self.cascade = cv2.CascadeClassifier(PATH_TO_MODEL) 
   
    def detect(self,img):
        #rects = cascade.detectMultiScale(img, scaleFactor=1.3, minNeighbors=4, minSize=(30, 30), flags = cv2.CV_HAAR_SCALE_IMAGE)
        #rects = cascade.detectMultiScale(img,scaleFactor=1.05,minNeighbors=16,minSize=(30, 30),flags=0)
        rects = self.cascade.detectMultiScale(img,scaleFactor=1.3,minNeighbors=4,minSize=(30, 30),flags=0)
        if len(rects) == 0:
            return []
        rects[:,2:] += rects[:,:2]
        return rects 
    def detect_face(self,image):
       t1=tm.time() 
       gray=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
       gray=cv2.equalizeHist(gray)
       rects=self.detect(gray)
       num_detections =len(rects) 
       t2=tm.time()
       return (num_detections,rects,t2-t1)
    def test(self):
        fd=face_detector()
        imf=os.path.join(self.site_package,'vcvf/data/test.jpg')
        print(imf)
        image=cv2.imread(imf)
        print(fd.detect_face(image)) 

def log2(message,of):
    print(message)
    of.write(message)
def draw_rect(img,savepath,left,top,right,bottom):
    cv2.rectangle(img, (int(left), int(top)), (int(right), int(bottom)), (0, 255, 0), 3)
    #cv2.imwrite(resultsavedir+filename_old,img)
    cv2.imwrite(savepath,img)
    return img

if __name__=="__main__":

    dirname='/data1/mingmingzhao/data_sets/hand_data/test_images/'
    dirname='/data1/mingmingzhao/data_sets/hand_test_0614_child_1/'
    dirname='/data1/mingmingzhao/data_sets/no_hand_data/'
    #sess,dg,ci=init()
    #hd3=HandDetector3(int(sys.argv[1]))
    fd=face_detector()
    fd.test()
    ci=0 # the count of image
    ch=0 # the count of hand
    ts=0 # avg of time cost
    for f in os.listdir(dirname):
       if f.endswith('.jpg'):
        imf=os.path.join(dirname,f)
        print(imf)
        image=cv2.imread(imf)
        face_num,rect,tc=fd.detect_face(image)
        if face_num>0:
            ch+=1
        if ci>1:
           ts+=tc
           print("%d/%d,%fs,%fs,%fHz avg"%(ch,ci,tc,ts/(ci-1),(ci-1)/ts))
        ci+=1



