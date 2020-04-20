#!/usr/bin/env python
# coding: utf-8

# In[1]:


import ee
import datetime
import folium
import os
from pprint import pprint
import pandas as pd
import numpy as np
import seaborn as sns


# In[2]:


ee.Initialize()


# In[ ]:





# In[1]:


class Make_Fourier:
    
    '''This class create Fourier_image according to time range, harmonic number and indexse.

    For input:1) start_date and end_date is a string like '2017-01-01'.
              2) hamornics = 3
              3) Normalized_Index = ['NDVI','NDBI','EVI']

    For output: 1) the output is a list of [[fig_orginal_ndvi,fig_fit_ndvi],
                                            [fig_orginal_ndbi,fig_fit_ndbi],
                                            [fig_orginal_evi,fig_fit_evi]]
                2) the Stp_4_Make_a_figure function take the default point = (116.3, 38.5)
                
                
    __________________________An example of how to use this class____________________
    
    test = Make_Fourier(start_date='2017-01-01',end_date='2019-12-31')

    test.Stp_1_Create_hamonic_names()
    test.Stp_2_Add_harmonics()
    test.Stp_3_Harmonic_fit()
    
    # Step_4 is not necessary for the analysis.
    #test.Stp_4_Make_a_figure()
    
    # get the Fourier img.
    Fourier_img = test.harmonicTrendCoefficients
    ____________________________________________________________________________________
    '''    
   
    def __init__(self,start_date,end_date,harmonics = 3,Normalized_Index = ['NDVI','NDBI','EVI']):
        
        self.start_date = ee.Date(start_date)
        self.end_date = ee.Date(end_date)
        self.harmonics = harmonics
        
        self.year_name = str(self.start_date.get('Year').getInfo()) + '_' + str(self.end_date.get('Year').getInfo())
        self.Normalized_Index = Normalized_Index
        
        self.North_China_Plain_Boundary = ee.FeatureCollection("users/wangjinzhulala/North_China_Plain_Python/Boundary_shp/North_China_Plain_Boundary")
        
        #______________________________Condition to define the right landsat img collecion__________________________
        if self.end_date.get('year').getInfo() <= 2010:
            self.Landsat_img = ee.ImageCollection("LANDSAT/LT05/C01/T1")
            self.ND_formula = {'NDVI':['B4','B3'],
                          'NDBI':['B5','B4'],
                          'EVI':"2.5 * ((b('B4')-b('B3'))*1.0 / (b('B4')*1.0 + 6.0 * b('B3') - 7.5 * b('B1') + 1.0))"}

        elif self.end_date.get('year').getInfo() <= 2013:
            self.Landsat_img = ee.ImageCollection("LANDSAT/LE07/C01/T1")
            self.ND_formula = {'NDVI':['B4','B3'],
                          'NDBI':['B5','B4'],
                          'EVI':"2.5 * ((b('B4')-b('B3'))*1.0 / (b('B4')*1.0 + 6.0 * b('B3') - 7.5 * b('B1') + 1.0))"}

        else:
            self.Landsat_img = ee.ImageCollection("LANDSAT/LC08/C01/T1")
            self.ND_formula = {'NDVI':['B5','B4'],
                          'NDBI':['B6','B5'],
                          'EVI':"2.5 * ((b('B5')-b('B4'))*1.0 / (b('B5')*1.0 + 6.0 * b('B4') - 7.5 * b('B2') + 1.0))"}
        #_____________________________________________________________________________________________________________
        
        self.Landsat_img_be_analized = self.Landsat_img.filterBounds(self.North_China_Plain_Boundary)                                                  .filterDate(self.start_date,self.end_date)                                                  .map(lambda img: ee.Image(img.clip(self.North_China_Plain_Boundary)))
            
        print(f'Analyzing the images of {self.year_name}')
    
    
    def Stp_1_Create_hamonic_names(self):
        
        # Make a list of harmonic frequencies to model.  
        # These also serve as band name suffixes.
        self.harmonicFrequencies = list(range(1,self.harmonics+1))
        
        # create all name_cos and name_sin.
        self.cosNames = ['cos_' + str(i) for i in self.harmonicFrequencies]
        self.sinNames = ['sin_' + str(i) for i in self.harmonicFrequencies]
        self.sinuate_and_constant = self.cosNames +  self.sinNames + ['constant','t']
        
        # create necessary names for harmonic fitting of different indexes.
        Independents_variable_names = []

        for index in self.Normalized_Index:

            tmp_name_list = []
            index_constant = [index + '_' + 'constant']
            index_t = [index + '_' + 't']
            
            for sin_cos in zip(self.cosNames,self.sinNames):

                index_sin = index + '_' + sin_cos[1]
                index_con = index + '_' + sin_cos[0]

                tmp_name_list.extend([index_sin,index_con])

            Independents_variable_names = Independents_variable_names + tmp_name_list + index_constant + index_t
        self.Independents_variable_names = Independents_variable_names

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
                time = ee.Image(image).select('t')
                # Get the cosine terms.
                cosines = time.multiply(self.frequencies).cos().rename(self.cosNames[i-1])
                # Get the sin terms.
                sines = time.multiply(self.frequencies).sin().rename(self.sinNames[i-1])
                # add cos and sin bands to image
                image = image.addBands(cosines).addBands(sines)
            return image
        
        # apply all the functions
        self.harmonicLandsat = self.Landsat_img_be_analized.map(lambda x: add_NDVI(x))                                         .map(lambda x: add_NDBI(x))                                         .map(lambda x: add_EVI(x))                                          .map(lambda x: addConstant(x))                                           .map(lambda x: addTime(x))                                               .map(lambda x: addHarmonics(x))
    def Stp_3_Harmonic_fit(self):
        
        harmonicTrendCoefficients_list = []
        fittedHarmonic_list = []

        for idx in self.Normalized_Index:

            # Define varibles required in later session.
            independents = [s for s in self.Independents_variable_names if idx in s]
            dependent = idx
            fit_name = 'fitted_' + idx

            # Using linearRgression to perform the Fourier Transformation
            # The output of the regression reduction is a [(n+2) x 1] array image, where n is harmonics.
            harmonicTrend = self.harmonicLandsat.select(ee.List(self.sinuate_and_constant).add(dependent))                     .reduce(ee.Reducer.linearRegression(ee.List(self.sinuate_and_constant).length(), 1)) 

            # Turn the array image into a multi-band image of coefficients.
            harmonicTrendCoefficients = harmonicTrend.select('coefficients').arrayProject([0]).arrayFlatten([independents])


            # Compute fitted values.
            # the essense here is using (independents) matrix to multiply the (coefficients) matrix.
            fittedHarmonic = self.harmonicLandsat.map(lambda image:                                             image.addBands(image.select(self.sinuate_and_constant)                                                                  .multiply(harmonicTrendCoefficients)                                                                   .reduce('sum')                                                                                            .rename(fit_name)))

            harmonicTrendCoefficients_list.append(harmonicTrendCoefficients)
            fittedHarmonic_list.append(fittedHarmonic.select([idx,fit_name]))
                                                      
        self.harmonicTrendCoefficients = ee.Image(harmonicTrendCoefficients_list).multiply(1000).toInt16()
        self.fittedHarmonic_list = fittedHarmonic_list
    
    def Stp_4_Make_a_figure(self,point = (116.3, 38.5)):
        
        # Select a arbitrary point in the map.
        point = ee.Geometry.Point(point)
        
        # Define the original ND and fitted ND variable
        original_NDVI = self.fittedHarmonic_list[0].select(['NDVI']).getRegion(point,30).getInfo()
        fitted_NDVI = self.fittedHarmonic_list[0].select(['fitted_NDVI']).getRegion(point,30).getInfo()
        
        original_NDBI = self.fittedHarmonic_list[1].select(['NDBI']).getRegion(point,30).getInfo()
        fitted_NDBI = self.fittedHarmonic_list[1].select(['fitted_NDBI']).getRegion(point,30).getInfo()
        
        original_EVI = self.fittedHarmonic_list[2].select(['EVI']).getRegion(point,30).getInfo()
        fitted_EVI = self.fittedHarmonic_list[2].select(['fitted_EVI']).getRegion(point,30).getInfo()
        
        # put  value into a pd.dataframe and convert the time to a normal format
        original_ndvi_df = pd.DataFrame(original_NDVI[1:],columns = original_NDVI[0])
        fitted_ndvi_df = pd.DataFrame(fitted_NDVI[1:],columns = fitted_NDVI[0])
        
        original_ndbi_df = pd.DataFrame(original_NDBI[1:],columns = original_NDBI[0])
        fitted_ndbi_df = pd.DataFrame(fitted_NDBI[1:],columns = fitted_NDBI[0])
        
        original_evi_df = pd.DataFrame(original_EVI[1:],columns = original_EVI[0])
        fitted_evi_df = pd.DataFrame(fitted_EVI[1:],columns = fitted_EVI[0])
        
        # Add time to fitted_ndvi_df since it has the same time stamp with NDVI.
        ndvi_time = [datetime.datetime.fromtimestamp(i/1000) for i in original_ndvi_df['time']]
        fitted_ndvi_df['time'] = ndvi_time
        
        ndbi_time = [datetime.datetime.fromtimestamp(i/1000) for i in original_ndbi_df['time']]
        fitted_ndbi_df['time'] = ndbi_time
        
        evi_time = [datetime.datetime.fromtimestamp(i/1000) for i in original_evi_df['time']]
        fitted_evi_df['time'] = evi_time
        
        # Plot the original and fitted value to inspect the outcome.
        fig_orginal_ndvi = original_ndvi_df['NDVI'].plot(legend ='NDVI' )
        fig_fit_ndvi = fitted_ndvi_df['fitted_NDVI'].plot(legend ='fitted_NDVI')
        
        fig_orginal_ndbi = original_ndbi_df['NDBI'].plot(legend ='NDBI' )
        fig_fit_ndbi = fitted_ndbi_df['fitted_NDBI'].plot(legend ='fitted_NDBI')
        
        fig_orginal_evi = original_evi_df['EVI'].plot(legend ='EVI' )
        fig_fit_evi = fitted_evi_df['fitted_EVI'].plot(legend ='fitted_EVI')
        
        return [[fig_orginal_ndvi,fig_fit_ndvi],[fig_orginal_ndbi,fig_fit_ndbi],[fig_orginal_evi,fig_fit_evi]]
        
        


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





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




