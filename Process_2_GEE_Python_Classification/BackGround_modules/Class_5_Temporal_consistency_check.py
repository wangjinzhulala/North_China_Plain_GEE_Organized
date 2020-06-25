#!/usr/bin/env python
# coding: utf-8

# In[138]:


import ee
import datetime
import os
import itertools
import sys
import math

from pprint import pprint
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

import geemap

import subprocess
from subprocess import PIPE


# In[ ]:





# In[113]:


ee.Initialize()


# In[ ]:





# In[160]:


class Temporal_consistency_check:
    
    '''This class perform a temporal consistency check for input images, the underline idea 
    is that "conversion from built to non-built hardly happens". So, given a pixel in a series
    of classified images, if this pixel is a built-up pixel at start time, and remain as a 
    more than half of times in the next periods, we then confirm this pixel is a built-up 
    pixeal, otherwise change it to a non-built pixel.
    
    ________________________________A General Description__________________________________
    
    For example, say we have a 10-periods of classified maps(which contains only built and 
    non-built pixels), and we set the Check_len=3 and iteration_num=10, this class will 
    
    1) chop the input images into 8 (calculation:len(img)-Check_len+1) chunks:
    
        ([(img0,img1,img2),(img1,img2,img3),(img2,img3,img4) ... (img7,img8,img9)])
        
    2) for each built-pixel in img1, count the appereances of the pixel remained as built 
       in the next 2 imgs. 
       
                       if the count > 1:
                           built pixel in img1 will kept as built,
                       else:
                           it will be changed to non-built.
                           
    3) similarily, we also judge weather the pixel remained as an non-built from a backward 
       perpective:
    
        ([(img9, img8, img7),(img8,img7,img6),(img7,img6,img5) ... (img2,img1,img0)])
        
    4) for each non-built pixel in img9, count the appereances of the pixel remained as non-built 
       in the next 2 imgs.
        
                       if the count > 1:
                           non-built pixel in img1 will kept as non-built,
                       else:
                           it will be changed to built
                           
    ______________________________________An Example_______________________________________
 
    # define the names of each period
    year_range = list(f'{i[0]}_{i[1]}' for i in zip(range(1990,2018,3),range(1992,2020,3)))
    
    # get the classified_random_imgs and sum them up for each period
    Classified_Landsat_1990_2019 = [ee.ImageCollection(f"users/wangjinzhulala/North_China_Plain_Python/classification_img/Control_{year}")
                                      .sum().gte(8).set('name',year)   for year in year_range]
                                      
    Classified_Sentinel_2014_2019 = [ee.ImageCollection(f"users/wangjinzhulala/North_China_Plain_Python/classification_img/Sentinel_Landsat_{year}")
                                      .sum().gte(8).set('name',year)   for year in year_range[-2:]]

    # combine classification img together
    Classified_imgs = Classified_Landsat_1990_2019[:-2] + Classified_Sentinel_2014_2019
    
    # get the temporal checked imgs
    Iter_temporal_check_instaces = Temporal_consistency_check(Classified_imgs,6,10).Iterate_the_check()
    
    # visulize the maps
    Map = geemap.Map()
    Map.setCenter(115.4508, 35.2492,10)

    year_idx = 4

    Map.add_basemap('HYBRID')
    Map.addLayer(Classified_imgs[year_idx] ,{'min':0,'max':1},'origin')
    Map.addLayer(Iter_temporal_check_instaces[0][year_idx] ,{'min':0,'max':1},'Iter_0')
    Map.addLayer(Iter_temporal_check_instaces[1][year_idx] ,{'min':0,'max':1},'Iter_1')
    Map.addLayer(Iter_temporal_check_instaces[2][year_idx] ,{'min':0,'max':1},'Iter_2')
    Map.addLayer(Iter_temporal_check_instaces[3][year_idx] ,{'min':0,'max':1},'Iter_3')

    Map
    
    '''
    
    def __init__(self,classified_imgs,Check_len,iteration_num):
        
        # define input imgs and number of iteration
        self.classified_imgs = classified_imgs
        self.iteration_num   = iteration_num
        
        # define the periods to perform temporal check
        self.Check_len       = Check_len
        self.Check_wieght    = [Check_len] + [1] * (Check_len-1)
        self.Check_threshold = Check_len + math.ceil((len(self.Check_wieght) - 1)/2)
        
        # print out the check parameters
        print(f'Check length is    ---> {self.Check_len}')
        print(f'Check weights is   ---> {self.Check_wieght}')
        print(f'Check threshold is ---> {self.Check_threshold}')
    
 

    def Temporal_check(self,mode,in_tifs,weights):

        # get the name of the first img as the property for return img
        name = ee.Image(in_tifs[0]).get('name')

        # zip classified_random_sum with weights
        img_multiply = list(zip(in_tifs,self.Check_wieght))



        if mode == 'forward':

            # multiply each classified_sum_img with check_weight 
            # and sum 3-periods together
            sum_tif = ee.ImageCollection([i[0].multiply(i[1]) for i in img_multiply]).sum()

            # thoes pixel that GREATE THAN OR EQUALS are built-up pixel
            temporal_checked = sum_tif.gte(self.Check_threshold).set('name',name)

        elif mode == 'backward':

            #_______________________Get those pixel that was transformed from built to non-built______________

            # remap the img,so the pixel value changed (built-->0; non-built -->weight)
                                                                    # here need to rename other wise bandname changed to 'remap'
                                                                    # which will cause error to add with forward imgs
            backward_remap    = [i[0].remap([0,1],[i[1],0]).rename('classification') for i in img_multiply]

            # sum the back_remap and the those pixels with value GREATE THAN OR EQUALS the threshold is "Non-Built"
            non_built = ee.ImageCollection(backward_remap).sum().gte(self.Check_threshold)

            # change the pixel value to get the right pixel value (0--> non-built; 1-->built)
            temporal_checked = non_built.Not()


        else:
            print("Please provide a correct mode ['forward'|'backward']")

        return temporal_checked





    def Forward_backward(self,temporal_check_len,in_imgs):

        # because temporal check can not been conducted at the edge, so we define an index-range to those
        # img that can be checked in the process
        img_idx_for_temporal_check = range(len(in_imgs) - temporal_check_len + 1)


        #_______________________________Backward temporal check________________________________________________

        # because this is backward check, so first reverse the img order
        reverse_classified_tifs = in_imgs[::-1]

        # slice the backward_tifs into chunks with the length of temporal_check_len
        backward_chunks = [reverse_classified_tifs[i:i + temporal_check_len] for i in img_idx_for_temporal_check]

        # perform the backward temporal check
        backward_tif    = [self.Temporal_check('backward',chunk,self.Check_wieght) 
                           for chunk in backward_chunks]



        #_______________________________Forward temporal check________________________________________________

        # because the backward_tif are in reversed (descending) order, so reverse it back
        backward_tif_ascending = backward_tif[::-1]

        # add the imgs not been checked at the backward process,so we get a full-length img list for forward check    
        forward_input_tifs = in_imgs[:temporal_check_len] + backward_tif_ascending

        # slice the forward_input_tifs into chunks with the length of temporal_check_len
        forward_chunks  = [forward_input_tifs[i:i + temporal_check_len] for i in img_idx_for_temporal_check]

        # perform the forward temporal check
        forward_tif     = [self.Temporal_check('forward',chunk,self.Check_wieght) 
                           for chunk in forward_chunks]


        #___________________________Add Forward & Backward checked img together___________________________________

        # add the imgs not been checked at the forward process,so we get a completed img list  
        backward_forward = forward_tif + backward_tif_ascending[-(temporal_check_len - 1) :]

        return backward_forward

    def Iterate_the_check(self):
        
                      
        # Here iterate Check_iteration_num times and 
        Iter_temporal_check_instaces = {}

        
        for it in range(self.iteration_num):

            if it == 0:

                forward_backward_checked =  self.Forward_backward(self.Check_len,self.classified_imgs)
                forward_backward_with_iteration = [ee.Image(img).set('iteration',it) for img in forward_backward_checked]

                Iter_temporal_check_instaces[0]  = forward_backward_with_iteration


            else:

                in_imgs = Iter_temporal_check_instaces[it-1]

                forward_backward_checked =  self.Forward_backward(self.Check_len,self.classified_imgs)
                forward_backward_with_iteration = [ee.Image(img).set('iteration',it) for img in forward_backward_checked]

                Iter_temporal_check_instaces[it]  = forward_backward_with_iteration

        self.Iter_temporal_check_instaces = Iter_temporal_check_instaces
        
        return self.Iter_temporal_check_instaces


# In[ ]:




