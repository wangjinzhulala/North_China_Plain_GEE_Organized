#!/usr/bin/env python
# coding: utf-8

# In[2]:


import ee
import datetime
import os
import itertools
import sys
import collections

from pprint import pprint
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

import math

import geemap

import subprocess
from subprocess import PIPE


# In[3]:


ee.Initialize()

# append module folter path into sys-path so wen can import necessary modules
sys.path.append('../')


# In[ ]:





# In[4]:


from BackGround_modules.Class_1_Make_fourier_imgs import Make_Fourier


# In[ ]:





# In[ ]:





# In[5]:


class Restore_Fourier_Fitting(Make_Fourier):
    '''This class extract the image value series of 
    orginal and pixel value been Fourier transformed,
    and attach the original and fitted value as 
    attributes of pd.DataFrame format in the instance.
    
    #_________________An_Example_______________________
    
    # instatiate the class
    test = Restore_Fourier_Fitting()

    # get the original and fitted value
    test.Get_Original_and_Fitting_df()

    orginal_df = test.original_df
    fitted_df = test.fitted_df

    # Plot the fitted value with original value
    plt.figure(figsize=(12,8))
    sns.lineplot(data=orginal_df,x='time',y='NDVI')
    sns.lineplot(data=fitted_df, x='time',y='NDVI')
    #______________Arguments_Explaination_______________
    This class inherate the Make_Fourier class so part of 
    the arguments are for Fourier transformation.
    
    start_date:       [both for Fourier transformation and 
                       original/fitted value extraction]
    end_date:         [for Fourier transformation]
    harmonics:        [for Fourier transformation]
    Normalized_Index: [both for Fourier transformation and 
                       original/fitted value extraction]
    point:            [for Fourier transformation]
    get_original_val: [for original/fitted value extraction] 
                      with bool of True/False
    
    '''
    
    def __init__(self,start_date = '2017-01-01',
                      end_date   = '2019-12-31',
                      harmonics  = 3,
                      Normalized_Index = ['NDVI', 'NDBI', 'EVI'],
                      point = [115.52126, 33.64591],
                      get_original_val = True,
                      get_fitted_val = True):
        
        super().__init__(start_date, end_date, harmonics, Normalized_Index)
        
        self.point = ee.Geometry.Point(point)
        self.advance_year_num =   int(self.end_date.format().getInfo()[:4])                                - int(self.start_date.format().getInfo()[:4]) + 1
        self.year_range = f'{self.start_date.format().getInfo()[:4]}_{self.end_date.format().getInfo()[:4]}'
        
        self.get_original_val = get_original_val
        self.get_fitted_val = get_fitted_val
        
        # determine the independents
        self.independents_idx = [f'cos_{i}' for i in range(1,self.harmonics+1)]                                  + [f'sin_{i}' for i in range(1,self.harmonics+1)]                                  + ['constant','t']
        
    #_______________________________Fourier_Transformation___________________________________
    
    def Get_Original_and_Fitting_df(self):
        
        # if the get_original_val is False, skip Fourier transformation
        
        if self.get_original_val:
            # Making the Fourier map
            self.Stp_1_Create_hamonic_names()
            self.Stp_2_Add_harmonics()
            self.Stp_3_Harmonic_fit()

            print('1/5 ==> Fourier Transformation Finished!')
            
        else:
            
            print('1/5 ==> Fourier Transformation skiped!')


    #__________________________Get the original [NDVI,NDBI,EVI] from harmonicLandsat_____________________
        
        # if the get_original_val is False, skip Original Image Value acquiration
        
        if self.get_original_val:
            # get the necessary data
            original_value = self.harmonicLandsat                                 .select(self.Normalized_Index)                                 .getRegion(self.point, 30)                                 .getInfo()

            # convert original value to dataframe
            original_df = pd.DataFrame(original_value[1:],columns=original_value[0])
            original_df['time'] = pd.to_datetime(original_df['time'],unit='ms')

            # formating the df
            original_df.drop(['id','longitude','latitude'],1,inplace=True)
            original_df.sort_values('time',inplace=True)
            original_df.reset_index(inplace=True,drop=True)

            # add attribute to self
            self.original_df = original_df

            print('2/5 ==> Original Image Value df Acquired!')
            
        else:
            
            print('2/5 ==> Original Image Value acquiration skiped!')

    #____________________________________Create indpendents_____________________________________________
    

        independents = {}

        # set a list to store t
        date_list = ee.List.sequence(0,365.25 * self.advance_year_num,1)
        date_list = date_list.map(lambda x: ee.Date(self.start_date).advance(x,'day'))    

        # put the data to independents
        time_stamp = date_list.map(lambda x :ee.Date(x).format()).getInfo()
        independents.update({'time':[i[:10] for i in time_stamp]})

        # Compute time in fractional years since the epoch.
        years = date_list.map(lambda x: ee.Date(x)                                           .difference(ee.Date('1970-01-01'), 'year')                                           .multiply(2*3.1415926)).getInfo()
        # add t to independents
        independents['t'] = np.array(years)


        # get other derivative time independents
        for i in range(1,self.harmonics+1):

            # Get the cosine terms.
            cos = {f'cos_{i}': np.cos(np.array(years) * np.array(i))}
            # Get the sin terms.
            sin = {f'sin_{i}': np.sin(np.array(years) * np.array(i))}

            # add cos and sin bands to image
            independents.update(cos)
            independents.update(sin)

        # add constant to independents
        independents.update({'constant':1})

        independents = pd.DataFrame(independents)
        
        # add independents to self for check purpose
        self.independents = independents
        
        print('3/5 ==> Independents Values Computation Completed!')

    #___________________________Get the coefficients from Fourier img value________________________
        
        # if the get_original_val is False, skip Fourier transformation
        if self.get_fitted_val:
        
            # if the year_range is not in the research periods, and the harmonic is not 3,
            # then do the calculation all again

            year_span = [f'{i}_{i+2}' for i in range(1990,2018,3)]

            if   self.year_range in year_span[:5] and self.harmonics == 3:
                # import Fourier img  
                print('________________Using GEE assest to reduce time of Fourier transformation!__________')
                Fourier_img = ee.Image(f"users/Jinzhu_Deakin/North_China_Plain/Fourier_img_harmonic_3/Fourier_img_{self.year_range}_harmonic_3")


            elif self.year_range in year_span[5:] and self.harmonics == 3:
                # import Fourier img 
                print('________________Using GEE assest to reduce time of Fourier transformation!__________')
                Fourier_img = ee.Image(f"users/wang8052664/North_China_Plain/Fourier_imgs/Fourier_img_{self.year_range}_harmonic_3")


            else:
                # get the Fourier_img
                Fourier_img = self.harmonicTrendCoefficients

            # get the value of Foutire img at Fig_pt, 
            #recall that the img was multipied by 1000 and converted into an integer
            Fig_pt_img_value = ee.ImageCollection(Fourier_img).getRegion(self.point, 30).getInfo()



            # get the coefficients and drop uesless columns
            coefficients = pd.DataFrame(Fig_pt_img_value[1:],columns=Fig_pt_img_value[0])
            coefficients.drop(['id','longitude','latitude','time'],1,inplace=True)
            coefficients = coefficients.T

            # divede by 1000, because the Fourier has been multiplied by 1000 at the Fourier fitting process
            coefficients = coefficients/1000

            # add coefficients to self for check purpose
            self.coefficients = coefficients

            print('4/5 ==> Coefficients Acquiring Finished!')


            #________________________Restore the fitted value using matrix multiply___________________________

            fitted_df_list = []

            # loop through indexes and use matrix multiply to get the fitted values
            for idx in self.Normalized_Index:

                X = independents[self.independents_idx].values
                y = coefficients.loc[[s for s in coefficients.index if idx in s]].values

                fitted_df_list.append(pd.DataFrame({idx:(X@y).reshape(1,-1)[0]}))

            #_____________________________get the fitted value and add time to it_________________________________

            fitted_df = pd.concat(fitted_df_list,1)
            fitted_df['time'] = pd.to_datetime(independents['time'])

            self.fitted_df = fitted_df

            print('5/5 ==> Fitted Value Computation Completed!')
            
        else:
            
            print('5/5 ==> Fitted Value Computation Skipped!')


# In[ ]:





# In[ ]:




