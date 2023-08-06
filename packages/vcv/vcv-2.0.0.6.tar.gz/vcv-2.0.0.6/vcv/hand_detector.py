import numpy as np
import os
import cv2
import six.moves.urllib as urllib
import sys
import tarfile
import tensorflow as tf
import zipfile
import collections
from collections import defaultdict
from io import StringIO
#from matplotlib import pyplot as plt
#from matplotlib.pyplot import savefig
from PIL import Image
import datetime
import pdb
import time as tm

#sys.path.append("/data1/mingmingzhao/tensorflow/models/object_detection/")
#sys.path.append("/data1/mingmingzhao//tensorflow/models/")
from utils import label_map_util
from utils import visualization_utils as vis_util
from distutils.sysconfig import get_python_lib
os.environ["CUDA_VISIBLE_DEVICES"] = "0"

class hand_detector:
    def __init__(self,modelversion=1):
        #PATH_TO_CKPT = '/data1/mingmingzhao/hand_detector/bin/output_inference_graph.pb.1473/saved_model/saved_model.pb'
        #PATH_TO_CKPT = '/data1/mingmingzhao/hand_detector/bin/output_inference_graph.pb.1473/frozen_inference_graph.pb'
        #PATH_TO_CKPT = '/data1/mingmingzhao/hand_detector/bin/output_inference_graph.pb.%d/frozen_inference_graph.pb'%(number)
        self.site_package=get_python_lib()
        #print(self.site_package)
        if modelversion==1:
            PATH_TO_CKPT = os.path.join(self.site_package,'vcv/data/hdm41754')
        elif modelversion==0:
            PATH_TO_CKPT = os.path.join(self.site_package,'vcv/data/hdr6883')
          
        #print(PATH_TO_CKPT)
        #print(os.getcwd())
        #print(os.path.dirname(os.__file__))

        #print(get_python_lib()) 
        #PATH_TO_CKPT = '/home/zlj/hand_detector/train/output_inference_graph_6883.pb'
        #PATH_TO_CKPT = '/home/zlj/hand_detector/train.bak.20170808/output_inference_graph_9585.pb'
        PATH_TO_LABELS = os.path.join(self.site_package,'vcv/data/hand_label_map.pbtxt')
        
        ##detect hand
        #PATH_TO_CKPT = '/home/vipkid/project/emotion/models/output_inference_graph_6883.pb'
        
        #PATH_TO_LABELS = os.path.join('data', '/home/vipkid/project/emotion/models/hand_label_map.pbtxt')
        
        NUM_CLASSES =1
        
        self.detection_graph = tf.Graph()
        with self.detection_graph.as_default():
            od_graph_def = tf.GraphDef()
            with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
                self.serialized_graph = fid.read()
                #print serialized_graph
                od_graph_def.ParseFromString(self.serialized_graph)
                tf.import_graph_def(od_graph_def, name='')
        
        self.label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
        self.categories = label_map_util.convert_label_map_to_categories(self.label_map, max_num_classes=NUM_CLASSES, use_display_name=True)
        self.category_index = label_map_util.create_category_index(self.categories)
        
        self.sess=None
        with self.detection_graph.as_default():
           self.sess=tf.Session(graph=self.detection_graph)
        #return sess,self.detection_graph,category_index
   
 
    def load_image_into_numpy_array(self,image):
       return np.array(image).reshape((120,160, 3)).astype(np.uint8)
    def detect_hand(self,image):
       #resize to 160*120
       #img=cv2.imread(image_path)
       image=cv2.resize(image, (160,120), interpolation = cv2.INTER_CUBIC)
       im_height=120
       im_width=160
       image_np = self.load_image_into_numpy_array(image)
       image_np_expanded = np.expand_dims(image_np, axis=0)
       image_tensor = self.detection_graph.get_tensor_by_name('image_tensor:0')
       boxes = self.detection_graph.get_tensor_by_name('detection_boxes:0')
       scores = self.detection_graph.get_tensor_by_name('detection_scores:0')
       classes = self.detection_graph.get_tensor_by_name('detection_classes:0')
       num_detections = self.detection_graph.get_tensor_by_name('num_detections:0')
       #print boxes.shape
       t1=tm.time() 
       (boxes, scores, classes, num_detections) = self.sess.run([boxes, scores, classes, num_detections],feed_dict={image_tensor: image_np_expanded})
       t2=tm.time()
       #print 'boxes:',boxes
       #print 'scores:',scores
       #print 'classes:',classes
       #print 'num_detections:',num_detections
       hand_num,center_x,center_y,rect=self.get_hand_num(im_width,im_height,np.squeeze(boxes),np.squeeze(classes).astype(np.int32),np.squeeze(scores),self.category_index)
       return (hand_num,center_x,center_y,rect,t2-t1)
    def get_hand_num(self,im_width,im_height,boxes,classes,scores,category_index,max_boxes_to_draw=2,min_score_thresh=.5):
      hand_num=0
      if scores is None:
        return hand_num
      for i in range(min(max_boxes_to_draw, boxes.shape[0])):
        if scores[i] > min_score_thresh:
          hand_num=hand_num+1
    
      center_x=0
      center_y=0
      rect=[]
      if hand_num>0:
         box = tuple(boxes[0].tolist())
         ymin, xmin, ymax, xmax = box
         (left, right, top, bottom) = (xmin * im_width, xmax * im_width,ymin * im_height, ymax * im_height)
         left=int(left)
         right=int(right)
         top=int(top)
         bottom=int(bottom)
         center_x=(left+right)/2
         center_y=(right+bottom)/2
         rect.append(np.array([left,top,right,bottom,scores[0]]))
      return hand_num,center_x,center_y,rect
    def test(self):
        hd3=hand_detector()
        imf=os.path.join(self.site_package,'vcv/data/test.jpg')
        print(imf)
        image=cv2.imread(imf)
        print(hd3.detect_hand(image)) 

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
    model_number=[1473,41750,42394,43042,43687]
    #hd3=HandDetector3(int(sys.argv[1]))
    hd3=hand_detector()
    hd3.test()
    ci=0 # the count of image
    ch=0 # the count of hand
    ts=0 # avg of time cost
    for f in os.listdir(dirname):
       if f.endswith('.jpg'):
        imf=os.path.join(dirname,f)
        print(imf)
        image=cv2.imread(imf)
        hand_num,center_x,center_y,rect,tc=hd3.detect_hand(image)
        if hand_num>0:
            ch+=1
        if ci>1:
           ts+=tc
           print("%d/%d,%fs,%fs,%fHz avg"%(ch,ci,tc,ts/(ci-1),(ci-1)/ts))
        ci+=1



