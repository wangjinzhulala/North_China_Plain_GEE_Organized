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

import geemap


# In[ ]:





# In[3]:


ee.Initialize()


# In[ ]:





# In[7]:


class Make_Fourier:
    
    '''This class create Fourier_image according to time range, harmonic number and indexse.

    1) start_date and end_date is a string like '2017-01-01'.
    2) hamornics = 3
    3) Normalized_Index = ['NDVI','NDBI','EVI']
    4) area is the research area, which should be a ee.Feature/Collection/Geometry

                
                
    __________________________An example of how to use this class____________________
    
    test = Make_Fourier(start_date ='2017-01-01',
                        end_date   ='2019-12-31',
                        area = ee.FeatureCollection("users/wangjinzhulala/North_China_Plain_Python/Boundary_shp/North_China_Plain_Boundary"))

    test.Stp_1_Create_hamonic_names()
    test.Stp_2_Add_harmonics()
    test.Stp_3_Harmonic_fit()
    
    
    #____________OUT_PUT______________

    # get the Fourier img. the Fourier img has been converted to integer
    # by -->multiply(1000).toInt16()
    Fourier_img = test.harmonicTrendCoefficients

    # get the Residule img.the Residule_img img has been converted to integer
    # by -->multiply(1000).toInt16()
    Residule_img = test.harmonicTrendResidule

    # get discrete original/fitted Normalized value. The value has been scaled 
    # by 1000
    # for example
    Original_NDVI_series = test.harmonicLandsat.select(['NDVI'])
    Fitted_NDVI_series   = test.fittedHarmonic['NDVI']

    # get the amplitude_phase img. The value has been scaled 
    # by 1000
    Amplitude_Phase_img = test.Amplitude_Phase_img
    ____________________________________________________________________________________
    '''    
   
    def __init__(self,start_date,end_date,area = ee.FeatureCollection("users/wangjinzhulala/North_China_Plain_Python/Boundary_shp/North_China_Plain_Boundary"),
                 harmonics = 3,Normalized_Index = ['NDVI','NDBI','EVI']):

        self.harmonics = harmonics        
        year_name = start_date[:4] + '_' + end_date[:4]
        self.Normalized_Index = Normalized_Index
        
        #______________________________Condition to define the right landsat img collecion__________________________
        if int(start_date[:4]) <= 2010:
            Landsat_img = ee.ImageCollection("LANDSAT/LT05/C01/T1_TOA")
            self.ND_formula = {'NDVI':['B4','B3'],
                          'NDBI':['B5','B4'],
                          'EVI':"2.5 * ((b('B4')-b('B3'))*1.0 / (b('B4')*1.0 + 6.0 * b('B3') - 7.5 * b('B1') + 1.0))"}

        elif int(start_date[:4]) <= 2013:
            Landsat_img = ee.ImageCollection("LANDSAT/LE07/C01/T1_TOA")
            self.ND_formula = {'NDVI':['B4','B3'],
                          'NDBI':['B5','B4'],
                          'EVI':"2.5 * ((b('B4')-b('B3'))*1.0 / (b('B4')*1.0 + 6.0 * b('B3') - 7.5 * b('B1') + 1.0))"}

        else:
            Landsat_img = ee.ImageCollection("LANDSAT/LC08/C01/T1_TOA")
            self.ND_formula = {'NDVI':['B5','B4'],
                          'NDBI':['B6','B5'],
                          'EVI':"2.5 * ((b('B5')-b('B4'))*1.0 / (b('B5')*1.0 + 6.0 * b('B4') - 7.5 * b('B2') + 1.0))"}
            
        # get the landsat imgs as raw input data
        self.Landsat_img_be_analized = Landsat_img.filterBounds(area)                                                  .filterDate(start_date,end_date)                                                  .map(lambda img: ee.Image(img.clip(area)))
            
        print(f'Analyzing the images of {year_name}')
    
    
    def Stp_1_Create_hamonic_names(self):
        
        # Make a list of harmonic frequencies to model.  
        # These also serve as band name suffixes.
        self.harmonicFrequencies = list(range(1,self.harmonics+1))
        
        # create all name_cos and name_sin.
        self.cosNames = ['cos_' + str(i) for i in self.harmonicFrequencies]
        self.sinNames = ['sin_' + str(i) for i in self.harmonicFrequencies]
        self.sinuate_and_constant = self.cosNames +  self.sinNames + ['constant','t']
        
        # Add normalized index ahead of all sin/cos names.
        self.Independents_variable_names = [f'{index}_{sin_cos_name}' 
                                            for index in self.Normalized_Index
                                            for sin_cos_name in self.sinuate_and_constant]


    def Stp_2_Add_harmonics(self):
        
        # Add Index to each img.
        def add_NDVI (image):
            return (
                    image
                    .addBands(image.normalizedDifference(self.ND_formula['NDVI']).rename('NDVI'))
                    .float()
                    )

        def add_NDBI (image):
            return (
                    image
                    .addBands(image.normalizedDifference(self.ND_formula['NDBI']).rename('NDBI'))
                    .float()
                    )
        # EVI are derived from TOA products, so here transfor the Raw data into a TOA product.
        def add_EVI (image):
            return (
                    image
                    .addBands(image.expression(self.ND_formula['EVI']).rename('EVI'))
                    .float())

        def addConstant(image):
            return (image
                  .addBands(ee.Image(1).rename('constant'))
                  .float())

        def addTime(image):
            # Compute time in fractional years since the epoch.
            date = ee.Date(image.get('system:time_start'))
            years = date.difference(ee.Date('1970-01-01'), 'year')
            # Here we use time to multiply 2π
            timeRadians = ee.Image(years.multiply(2*3.1415926))
            return (image.addBands(timeRadians.rename('t').float()))

        def addHarmonics (image):
            # Here to iterate for len(harmonicFrequencies) times
            for i in self.harmonicFrequencies:

                # Make an image of frequencies.
                self.frequencies = ee.Image.constant(i);
                # This band should represent time in radians.
                time    = ee.Image(image).select('t')
                # Get the cosine terms.
                cosines = time.multiply(self.frequencies).cos().rename(self.cosNames[i-1])
                # Get the sin terms.
                sines   = time.multiply(self.frequencies).sin().rename(self.sinNames[i-1])
                # add cos and sin bands to image
                image   = image.addBands(cosines).addBands(sines)
            return image
        
        # apply all the functions
        self.harmonicLandsat = self.Landsat_img_be_analized.map(lambda x: add_NDVI(x))                                                           .map(lambda x: add_NDBI(x))                                                           .map(lambda x: add_EVI(x))                                                            .map(lambda x: addConstant(x))                                                             .map(lambda x: addTime(x))                                                                 .map(lambda x: addHarmonics(x))
    def Stp_3_Harmonic_fit(self):
        
        harmonicTrendCoefficients_list = []
        residule_list = []
        
        fittedHarmonic_dict = {}
        Amplitude_Phase = []

        for idx in self.Normalized_Index:

            #_____________________Step_1_Define varibles required in later session__________________________
            
            independents = [s for s in self.Independents_variable_names if idx in s]
            dependent = idx
            fit_name = 'fitted_' + idx
            
            
            #_____________________Step_2_Harmonic_Fit__________________________
            
            # Using linearRgression to perform the Fourier Transformation
            # The output of the regression reduction is a [(n+2) x 1] array image, where n is harmonics.
            harmonicTrend = self.harmonicLandsat.select(ee.List(self.sinuate_and_constant).add(dependent))                                 .reduce(ee.Reducer.linearRegression(ee.List(self.sinuate_and_constant).length(), 1)) 
            
            
            #_____________________Step_3_Get_[Coefficients_img]_[fit_img]_and_[residul_img]__________________________
            
            # Turn the array image into a multi-band image of coefficients.
            # 1) get the coefficients
            harmonicTrendCoefficients = harmonicTrend.select('coefficients').arrayProject([0]).arrayFlatten([independents])
            # 2) get the residuls
            harmonicTrendResidules    = harmonicTrend.select('residuals').arrayProject([0]).arrayFlatten([[f'{idx}_residule']])

            # Compute fitted values.
            # the essense here is using (independents) matrix to multiply the (coefficients) matrix.
            fittedHarmonic_dict[idx] = self.harmonicLandsat.map(lambda image:                                             image.addBands(image.select(self.sinuate_and_constant)                                                                  .multiply(harmonicTrendCoefficients)                                                                .reduce('sum')                                                                                      .rename(fit_name)))
            
            # add the result into list
            residule_list.append(harmonicTrendResidules)
            harmonicTrendCoefficients_list.append(harmonicTrendCoefficients)
            
            
            #_____________________Step_4_Compute_the_Amplitude_and_Phases__________________________
            
            # initiate a list to hold each bands from amp/phs
            amp_phs_list = []
            
            # loop throught each cos/sin bands
            for i in range(1,self.harmonics+1):
                
                # get the names
                cos = f'{idx}_cos_{i}'
                sin = f'{idx}_cos_{i}'
                name_amp = f'{idx}_Amplitude_{i}'
                name_phs = f'{idx}_Phase_{i}'
                
                # compute the amplitude and phase
                amp = harmonicTrendCoefficients.select(cos).hypot(harmonicTrendCoefficients.select(sin)).rename(name_amp)
                phs = harmonicTrendCoefficients.select(cos).atan2(harmonicTrendCoefficients.select(sin)).rename(name_phs)
                
                # add amp and phs to list
                amp_phs_list.append(amp)
                amp_phs_list.append(phs)
            
            # stack amp_phs to a multiband img, note here need to add the constant and t coefficients
            # also, multiply by 1000 and convert the img to int
            amp_phs_img = ee.Image([amp_phs_list] + 
                                   [harmonicTrendCoefficients.select(f'{idx}_constant')] + 
                                   [harmonicTrendCoefficients.select(f'{idx}_t')]).multiply(1000).toInt16()
 
            Amplitude_Phase.extend([amp_phs_img])
    
    
        #_____________________Step_5_Store_result_to_class_attributes__________________________   
        
        # multiply all computated by 1000 and convet them into a Signed-16 interge to reduce space.
        self.harmonicTrendCoefficients = ee.Image(harmonicTrendCoefficients_list).multiply(1000).toInt16()
        self.harmonicTrendResidule     = ee.Image(residule_list).multiply(1000).toInt16()
        
        # store thefitted and amp_phs img to dict
        self.fittedHarmonic            = fittedHarmonic_dict
        self.Amplitude_Phase_img       = ee.Image(Amplitude_Phase)


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




