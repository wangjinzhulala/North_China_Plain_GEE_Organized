#!/usr/bin/env python
# coding: utf-8

# In[1]:


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





# In[2]:


ee.Initialize()


# In[ ]:





# In[37]:


class Temporal_consistency_check:
    
    '''This class perform a temporal consistency check for input images, the underline idea 
    is that "conversion from built to non-built hardly happens". So, given a pixel in a series
    of classified images, if this pixel is a built-up pixel at start time, and remain as a 
    more than half of times in the next periods, we then confirm this pixel is a built-up 
    pixel, otherwise change it to a non-built pixel.
    
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
    Iter_temporal_check_instaces = Temporal_consistency_check(Classified_imgs,3,5).Iterate_the_check(mode = 'only_forward')

    # visulize the maps
    Map = geemap.Map()
    Map.setCenter(115.4508, 35.2492,10)

    year_idx = 2

    Map.add_basemap('HYBRID')
    Map.addLayer(Classified_imgs[year_idx] ,{'min':0,'max':1},'origin')
    Map.addLayer(Iter_temporal_check_instaces[1][year_idx] ,{'min':0,'max':1},'Iter_1')
    Map.addLayer(Iter_temporal_check_instaces[2][year_idx] ,{'min':0,'max':1},'Iter_2')
    Map.addLayer(Iter_temporal_check_instaces[3][year_idx] ,{'min':0,'max':1},'Iter_3')
    Map.addLayer(Iter_temporal_check_instaces[4][year_idx] ,{'min':0,'max':1},'Iter_4')
    Map.addLayer(Iter_temporal_check_instaces[5][year_idx] ,{'min':0,'max':1},'Iter_5')

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
        print('================  Check Report  ================')
        print(f'Check length is    ---> {self.Check_len}')
        print(f'Check weights are  ---> {self.Check_wieght}')
        print(f'Check threshold is ---> {self.Check_threshold}')
        print(f'Check iteration is ---> {self.iteration_num}')
        print('================================================')
    
 

    def Temporal_check(self,mode,in_tifs,weights):

        # zip classified_random_sum with weights
        img_multiply = list(zip(in_tifs,self.Check_wieght))

        if mode == 'forward':

            # multiply each classified_sum_img with check_weight 
            # and sum 3-periods together
            sum_tif = ee.ImageCollection([i[0].multiply(i[1]) for i in img_multiply]).sum()

            # thoes pixel that GREATE THAN OR EQUALS are built-up pixel
            temporal_checked = sum_tif.gte(self.Check_threshold)

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



    def Forward(self,temporal_check_len,in_imgs):
        
        # because temporal check can not been conducted at the edge, so we define an index-range to those
        # img that can be checked in the process
        img_idx_for_temporal_check = range(len(in_imgs) - temporal_check_len + 1)

        # slice the forward_input_tifs into chunks with the length of temporal_check_len
        forward_chunks  = [in_imgs[i:i + temporal_check_len] for i in img_idx_for_temporal_check]

        # perform the forward temporal check
        forward_tif     = [self.Temporal_check('forward',chunk,self.Check_wieght) 
                           for chunk in forward_chunks]
        
        # add the imgs of the edge to checked list, so we get a full img list 
        forward_checked = forward_tif + in_imgs[-temporal_check_len + 1:]

        return forward_checked
    
    
    
    

    def Backward(self,temporal_check_len,in_imgs):

        # because temporal check can not been conducted at the edge, so we define an index-range to those
        # img that can be checked in the process
        img_idx_for_temporal_check = range(len(in_imgs) - temporal_check_len + 1)
        
        # because this is backward check, so first reverse the img order
        reverse_classified_tifs = in_imgs[::-1]

        # slice the backward_tifs into chunks with the length of temporal_check_len
        backward_chunks = [reverse_classified_tifs[i:i + temporal_check_len] for i in img_idx_for_temporal_check]

        # perform the backward temporal check
        backward_tif    = [self.Temporal_check('backward',chunk,self.Check_wieght) 
                           for chunk in backward_chunks]
        
        # add the edge tifs to backward_tif and return the result
        backward_checked = in_imgs[:temporal_check_len-1] + backward_tif[::-1]
        
        return backward_checked
    
    
    
    


    def Iterate_the_check(self,mode = 'only_forward'):
        
        '''Here are there mode ==> 'only_backward'|'only_forward'|'forward_backward'|'backward_forward'
        
        The defalt mode is only_forward, which means only correct pixel 
        that were incorrecly classified as "built" to "non-built"
        
        1) 'only_backward' ==> slide a moving window from end year to start year (backward)
            and correct the pixel that are incorrecly classified as "non-built" to "built"
        2) 'only_forward' ==> slide a moving window from the start year to end year (forward)
            and correct the pixel that are incorrecly classified as "built" to "non-built"
        3) 'forward_backward' ==> first slide the 'only_backward' then the 'only_forward'
        4) 'forward_backward' ==> first slide the 'only_forward' then the 'only_backward'
        
        '''
                      
        # Here iterate Check_iteration_num times and 
        Iter_temporal_check_instaces = {}
        
        for it in range(1,self.iteration_num+1):
            
            #_______________________________here defines what happens in 'back_forward' mode_____________________________
            if mode == 'backward_forward':
            
                if it == 1:

                    # first proceed the backward check, then the forward check
                    backward_checked  = self.Backward(self.Check_len,self.classified_imgs)
                    temporal_checked  = self.Forward(self.Check_len,backward_checked)
                    
                    # write the iteration number to the img attribute
                    check_with_iteration = [ee.Image(img).set('iteration',it) for img in temporal_checked]
                    
                    # put the first iteration into result dictionary
                    Iter_temporal_check_instaces[1]  = check_with_iteration


                else:

                    in_imgs = Iter_temporal_check_instaces[it-1]

                    # first proceed the backward check, then the forward check
                    backward_checked  = self.Backward(self.Check_len,in_imgs)
                    temporal_checked  = self.Forward(self.Check_len,backward_checked)
                    
                    # write the iteration number to the img attribute
                    check_with_iteration = [ee.Image(img).set('iteration',it) for img in temporal_checked]

                    Iter_temporal_check_instaces[it]  = check_with_iteration
                    
                    
            #______________________________here defines what happens in 'forward_backward' mode______________________________
            elif mode == 'forward_backward':
            
                if it == 1:

                    # first proceed the backward check, then the forward check
                    forward_checked   = self.Forward(self.Check_len,self.classified_imgs)
                    temporal_checked  = self.Backward(self.Check_len,forward_checked)
                    
                    # write the iteration number to the img attribute
                    check_with_iteration = [ee.Image(img).set('iteration',it) for img in temporal_checked]
                    
                    # put the first iteration into result dictionary
                    Iter_temporal_check_instaces[1]  = check_with_iteration


                else:

                    in_imgs = Iter_temporal_check_instaces[it-1]

                    # first proceed the backward check, then the forward check
                    forward_checked   = self.Forward(self.Check_len,in_imgs)
                    temporal_checked  = self.Backward(self.Check_len,forward_checked)
                    
                    # write the iteration number to the img attribute
                    check_with_iteration = [ee.Image(img).set('iteration',it) for img in temporal_checked]

                    Iter_temporal_check_instaces[it]  = check_with_iteration
                    
            #__________________________here defines what happens in 'only_forward' mode_________________________________
            elif mode == 'only_forward':
            
                if it == 1:

                    # first proceed the backward check, then the forward check
                    temporal_checked   = self.Forward(self.Check_len,self.classified_imgs)
                    
                    # write the iteration number to the img attribute
                    check_with_iteration = [ee.Image(img).set('iteration',it) for img in temporal_checked]
                    
                    # put the first iteration into result dictionary
                    Iter_temporal_check_instaces[1]  = check_with_iteration


                else:

                    in_imgs = Iter_temporal_check_instaces[it-1]

                    # first proceed the backward check, then the forward check
                    temporal_checked = self.Forward(self.Check_len,in_imgs)
                    
                    # write the iteration number to the img attribute
                    check_with_iteration = [ee.Image(img).set('iteration',it) for img in temporal_checked]

                    Iter_temporal_check_instaces[it]  = check_with_iteration
                    
            #___________________________here defines what happens in 'only_backward' mode_________________________________
            elif mode == 'only_backward':
            
                if it == 1:

                    # first proceed the backward check, then the forward check
                    temporal_checked   = self.Backward(self.Check_len,self.classified_imgs)
                    
                    # write the iteration number to the img attribute
                    check_with_iteration = [ee.Image(img).set('iteration',it) for img in temporal_checked]
                    
                    # put the first iteration into result dictionary
                    Iter_temporal_check_instaces[1]  = check_with_iteration


                else:

                    in_imgs = Iter_temporal_check_instaces[it-1]

                    # first proceed the backward check, then the forward check
                    temporal_checked = self.Backward(self.Check_len,in_imgs)
                    
                    # write the iteration number to the img attribute
                    check_with_iteration = [ee.Image(img).set('iteration',it) for img in temporal_checked]

                    Iter_temporal_check_instaces[it]  = check_with_iteration
                    
            # in case given an incorrect mode        
            else:
                print("Please provide a correct mode ['only_backward'|'only_forward'|'forward_backward'|'backward_forward']")
                    
                    
        # here add the checked imgs to the class attribute, and return it
        self.Iter_temporal_check_instaces = Iter_temporal_check_instaces
        
        return self.Iter_temporal_check_instaces


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




