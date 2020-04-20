#!/usr/bin/env python
# coding: utf-8

# In[2]:


import ee
import datetime
import folium
import os
from pprint import pprint
import pandas as pd
import numpy as np
import seaborn as sns


# In[3]:


ee.Initialize()


# In[ ]:





# In[ ]:





# In[8]:


class Classification:

    """
    First thing first, remember to export the classfied samples, 
    otherwise, will probably get a "Momory Excedding" error!
    
    This class will
    1) perform classification on a [Base_img] with [Supply_img] using [Verified_pt]
    2) make a classifier based on [Tree_num] parameter
    3) extract [Training_samples] and [Testing_samples] based on given [Tree_num] parameter, and
    4) get [Train_classification] and [Test_classification] based on samples.

    For {Input}: 
    1) The [Base_img] is a string, like:
       [Base_img ="users/wangjinzhulala/North_China_Plain_Python/Fourier_pixels/Fourier_Total_2017_2019"]
    2) The [year_name] is a string like '2017_2019'
    3) The default supplementary data a Zero img, change accordingly when classify other years imgs
    4) The default [Tree_num] is 100.

    For {Output}: 
    1) Classified imgs ==>   [classification_img_sin_cos |  classification_img_sin_cos_supply].
    2) Classfied samples ==>[Train_sample_classification |  Train_sample_supply_classification]
                            [Test_sample_classification  |  Test_sample_supply_classification].
                            
    _____________________________An example of how to use this class____________________________
    
    # Instatiate the class with a name.
    test = Classification(Base_img = ee.Image("users/wangjinzhulala/North_China_Plain_Python/Fourier_pixels/Fourier_Total_NDVI_2017_2019"),
                          year_name ='2017_2019')

    # Put supply_img to the class.
    test.Supply_img = ee.Image([
                                ee.Image("users/wangjinzhulala/North_China_Plain_Supply/DEM_Year_2017_2019").rename('DEM'),
                                ee.Image("users/wangjinzhulala/North_China_Plain_Supply/Slope_Year_2017_2019"),
                                ee.Image("users/wangjinzhulala/North_China_Plain_Supply/NDVI_Year_2017_2019") 
                                ])
                                
    test.Supply_img_names = Classification_Instance.Supply_img.bandNames().getInfo()
    
    # perform the classification on Base_img and Samples
    test.Stp_1_Classification_on_img()
    test.Stp_3_Classification_on_Samples()

    # Get the classified samples
    train_sample_classified        = test.Train_sample_classification
    train_supply_sample_classified = test.Train_sample_supply_classification
    test_sample_classified         = test.Test_sample_classification
    test_supply_sample_classified  = test.Test_sample_supply_classification
    _______________________________________________________________________________________________
    
    
    
    """


    

    print('The default supplementary data a Zero img, change accordingly when classify other years imgs')
    print()
    
    def __init__(self,year_name,Base_img,Verified_point,Tree_num = 100,Supply_img = ee.Image([ee.Image(0)]).rename(['Zero_img'])):
        
        self.Tree_num           = Tree_num
        self.Base_img           = ee.Image(Base_img)
        self.Supply_img         = Supply_img
        self.year_name          = year_name
        self.Verified_point_all = Verified_point
        
        
        
    def Stp_0_Split_sample_point(self):
        
        # First change the supply_img name 
        self.Supply_img_names   = self.Supply_img.bandNames().getInfo()
        
        # Split the point into built and non-built.
        Verified_point_Built     =  self.Verified_point_all.filterMetadata('Built','equals',1) 
        Verified_point_non_Built =  self.Verified_point_all.filterMetadata('Built','equals',0) 

        # 70/30 Train/Test split on built/non-built points.
        Verified_built_pts_randomcolumn     = Verified_point_Built.randomColumn(columnName = 'random',seed = 101) 
        Verified_non_built_pts_randomcolumn = Verified_point_non_Built.randomColumn(columnName = 'random',seed = 101)


        Vetified_built_pts_train     = Verified_built_pts_randomcolumn.filterMetadata('random',"greater_than",0.3)
        Vetified_built_pts_test      = Verified_built_pts_randomcolumn.filterMetadata('random',"not_greater_than",0.3) 

        Vetified_non_built_pts_train = Verified_non_built_pts_randomcolumn.filterMetadata('random','greater_than',0.3)
        Vetified_non_built_pts_test  = Verified_non_built_pts_randomcolumn.filterMetadata('random','not_greater_than',0.3) 

        # Merge train/test datasets respectively.
        self.Verified_pts_train = Vetified_built_pts_train.merge(Vetified_non_built_pts_train) 
        self.Verified_pts_test  = Vetified_built_pts_test.merge(Vetified_non_built_pts_test)

        # Tranning size
        built_size_train     = Vetified_built_pts_train.size().getInfo()
        non_built_size_train = Vetified_non_built_pts_train.size().getInfo()

        # Testing size
        built_size_test      = Vetified_built_pts_test.size().getInfo()
        non_built_size_test  = Vetified_non_built_pts_test.size().getInfo()
        
        
        
    def Stp_1_Classification_on_img(self):
        
            
        # _______________________________Step_1:Predefine the names for classification_______________________________________
        self.Base_img_names = self.Base_img.bandNames().getInfo()
        
        self.band_name_sin_cos = self.Base_img_names

        self.band_name_sin_cos_supply = self.band_name_sin_cos + self.Supply_img_names

        # Determine the colum name that included in the classifier
        self.classProperty = 'Built'
        
        # __________________________________________Step_2:Collect the training data_______________________________________

        self.Train_data = self.Base_img.addBands(self.Supply_img).sampleRegions(
                                                             collection= self.Verified_pts_train,
                                                             properties= [self.classProperty],
                                                             scale= 30,
                                                             # set geometries so we can export it to asset.
                                                             geometries = True
                                                             ) 
        
        # __________________________________________Step_3:Train the classifier_______________________________________
        # Note that [smileRandomForest] is crazyly faster than randomforest!!!!

        self.classifier_sin_cos = ee.Classifier.smileRandomForest(numberOfTrees = self.Tree_num).train(
                                                                              features = self.Train_data,
                                                                              inputProperties = self.band_name_sin_cos,
                                                                              classProperty = self.classProperty,
                                                                              )

        self.classifier_sin_cos_supply = ee.Classifier.smileRandomForest(numberOfTrees = self.Tree_num).train(
                                                                              features = self.Train_data,
                                                                              inputProperties = self.band_name_sin_cos_supply,
                                                                              classProperty = self.classProperty,
                                                                              )
        # __________________________________________Step_4:# Perform the classification_______________________________________

        self.classification_img_sin_cos = self.Base_img.classify(self.classifier_sin_cos)
        self.classification_img_sin_cos_supply = self.Base_img.addBands(self.Supply_img).classify(self.classifier_sin_cos_supply)
        
    def Stp_2_Add_Visualization(self):
        
        #_________________________________________Create a foluim layer function________________________________________
        def add_ee_layer(self, ee_image_object, vis_params, name):
            map_id_dict = ee.Image(ee_image_object).getMapId(vis_params)
            folium.raster_layers.TileLayer(
            tiles = map_id_dict['tile_fetcher'].url_format,
            attr = "Map Data © Google Earth Engine",
            name = name,
            overlay = True,
            control = True
            ).add_to(self)

        # Add EE drawing method to folium.
        folium.Map.add_ee_layer = add_ee_layer
        
        # create a classified map layer
        Foulium_map = folium.Map(location=[38.8132,116.28367],zoom_start = 10, height= 500)
        #______________________________________Import the GAIA data set_____________________________________________
        
        North_China_Plain_Boundary = ee.FeatureCollection("users/wangjinzhulala/North_China_Plain/0_1_North_China_Plain_Full")
        GAIA_Globe = ee.Image("users/wangjinzhulala/Gloable_Imprevious_area")
        GAIA_Norht_China_Plain = GAIA_Globe.clip(North_China_Plain_Boundary.geometry()).remap(list(range(1,36)),[2]*35,0)
        
        #____________________________________Add the imgs to the map object________________________________________
        # Add the imgs to the map object.
        Foulium_map.add_ee_layer(self.classification_img_sin_cos, {'min':0,'max':1}, 'classification_sin_cos')
        Foulium_map.add_ee_layer(self.classification_img_sin_cos_supply, {'min':0,'max':1}, 'classification_sin_cos_supply')

        # Add the imgs to the map object.
        Foulium_map.add_ee_layer(GAIA_Norht_China_Plain, {'min':0,'max':1}, 'GAIA_Norht_China_Plain map')

        # Add a layer control panel to the map.
        Foulium_map.add_child(folium.LayerControl())
        
        return Foulium_map
    
    def Stp_3_Classification_on_Samples(self):
        
        # Get training samples.
        self.Train_samples        = self.Train_data.select(self.band_name_sin_cos        + [self.classProperty])
        self.Train_samples_supply = self.Train_data.select(self.band_name_sin_cos_supply + [self.classProperty])

        # Get testing samples 
        self.Test_samples =  self.Base_img.select(self.band_name_sin_cos).sampleRegions(
                                                                                    collection= self.Verified_pts_test,
                                                                                    scale= 30,
                                                                                    properties = ['Built'],
                                                                                    # Set geometries to enable toDrive export.
                                                                                    geometries = True 
                                                                                    ) 



        self.Test_samples_supply =  self.Base_img.addBands(self.Supply_img).select(self.band_name_sin_cos_supply).sampleRegions(
                                                                                    collection= self.Verified_pts_test,
                                                                                    scale= 30,
                                                                                    properties = ['Built'],
                                                                                    geometries = True 
                                                                                    ) 
        # Classify the Train-data set.
        self.Train_sample_classification        = self.Train_samples.classify(self.classifier_sin_cos)
        self.Train_sample_supply_classification = self.Train_samples_supply.classify(self.classifier_sin_cos_supply)

        # Classify the Test-data set.
        self.Test_sample_classification = self.Test_samples.classify(self.classifier_sin_cos)
        self.Test_sample_supply_classification = self.Test_samples_supply.classify(self.classifier_sin_cos_supply)


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




