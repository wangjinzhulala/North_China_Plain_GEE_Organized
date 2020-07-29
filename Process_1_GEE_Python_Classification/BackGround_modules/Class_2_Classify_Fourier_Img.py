#!/usr/bin/env python
# coding: utf-8

# In[1]:


import ee


# In[2]:


ee.Initialize()


# In[ ]:





# In[1]:


class Classification:

    """
    This class will
    1) perform classification on a [Input_img] using [Verified_pt]
    2) make a randomeforrest classifier based on [Tree_num] parameter
    3) split input sample(Verified_sample) [Training_samples] and [Testing_samples] 
    4) get [Train_classification] and [Test_classification] based on samples.
    
    WARNING!!
    Make sure [Input_band] is the same with band of [Input_image] if intend to use classifier
    generated from Verified_samples.
    
    For {Input}: 
    1) The [Input_img] is a string, like:
       [Input_img = "users/wang8052664/Cloud_Free_Img/Landsat_cloud_free_2017_2019"]
    2) The [year_name] is a string like '2017_2019'
    3) the [Input_band] defines the bands that are used in the classification
    4) the [Verified_point] defines the sample points as the ground truthes,
    5) the [Input_band] is used to restrain feature points (by feature.Select()),
    6) the [seed] determines the random state of the training point, default to be 101,
    7) the [split_portion] determines how to perform trian/test split, training points are theose > split_portion,
    6) the [classProperty] is default to 'Built', which is the column name for ground truth,
    7) The default [Tree_num] is 100.

    For {Output}: 
    1) Classified imgs ==>   [classification_img].
    2) Classfied samples ==> [Train_sample_classification]
                             [Test_sample_classification].
                            
    
    
    __________________________________Sample for classfication on IMAGE___________________________________

    verified_sample_2017_2019 = ee.FeatureCollection("users/wangjinzhulala/North_China_Plain_Python/Sample_Points/Verified_pt_2017_2019")
    zone_pt = ee.FeatureCollection("users/Jinzhu_Deakin/North_China_Plain/Zone_sample_point_1987_1989/Zone_Sample")

    input_point = verified_sample_2017_2019.merge(zone_pt)

    # get necessary img and verified points
    imput_img = ee.Image("users/wang8052664/North_China_Plain/Fourier_imgs/Fourier_img_2017_2019_harmonic_3")

    # Instatiate the class with a name.
    test2 = Classification(year_name ='2017_2019',
                          Input_img  = imput_img,
                          Verified_point = input_point)


    # perform the classification on Input_img and Samples
    test2.Stp_1_Classification_on_img()
    test2.Stp_2_Classification_on_Samples()

    # Get the classified img
    classified_img = test2.classification_img

    # Get the classified samples
    train_sample_classified        = test2.Train_sample_classification
    test_sample_classified         = test2.Test_sample_classification
    
    __________________________________Sample for classfication on POINTS___________________________________
    
    verified_sample_img = ee.FeatureCollection("users/Jinzhu_Deakin/North_China_Plain/Sample_with_Landsat_Fourier_Normalized/Verified_point_2017_2019_extract_Landsat_Fourier_Normalized_img")
    zone_pt_img = ee.FeatureCollection("users/Jinzhu_Deakin/North_China_Plain/Sample_with_Landsat_Fourier_Normalized/Zone_point_2017_2019_extract_Landsat_Fourier_Normalized_img")

    input_point = verified_sample_img.merge(zone_pt_img)

    band_classification = ['NDVI_cos_1','NDVI_cos_2','NDVI_cos_3','NDVI_sin_1','NDVI_sin_2','NDVI_sin_3',
                           'NDVI_constant','NDVI_t','NDBI_cos_1','NDBI_cos_2','NDBI_cos_3','NDBI_sin_1',
                           'NDBI_sin_2','NDBI_sin_3', 'NDBI_constant','NDBI_t','EVI_cos_1','EVI_cos_2',
                           'EVI_cos_3','EVI_sin_1','EVI_sin_2','EVI_sin_3','EVI_constant','EVI_t']

    # Instatiate the class with a name.
    test3 = Classification(year_name ='2017_2019',
                           Verified_point = input_point,
                           Input_band=band_classification)


    # perform the classification on Samples
    test3.Stp_2_Classification_on_Samples()

    # Get the classified samples
    train_sample_classified        = test3.Train_sample_classification
    test_sample_classified         = test3.Test_sample_classification
    _______________________________________________________________________________________________
   
    """

    
    def __init__(self,year_name,
                      Verified_point,
                      Input_img     = None,
                      Input_band    = None,
                      Tree_num      = 100,
                      seed          = 101,
                      split_portion = 0.3,
                      Zone_sample   = None,
                      classProperty = 'Built'):
        
        self.Tree_num           = Tree_num
        self.Input_img          = Input_img
        self.year_name          = year_name
        self.Input_band         = Input_band
        self.classProperty      = classProperty
        self.Verified_point_all = ee.FeatureCollection(Verified_point)
        
        #__________________________Split the point into built and non-built________________________________________
        Verified_point_Built     =  self.Verified_point_all.filterMetadata(classProperty,'equals',1)
        Verified_point_non_Built =  self.Verified_point_all.filterMetadata(classProperty,'equals',0)

        # 70/30 Train/Test split on built/non-built points.
        Verified_built_pts_randomcolumn     = Verified_point_Built                                              .randomColumn(columnName = 'random',seed = seed) 
        Verified_non_built_pts_randomcolumn = Verified_point_non_Built                                              .randomColumn(columnName = 'random',seed = seed)


        Vetified_built_pts_train     = Verified_built_pts_randomcolumn                                       .filterMetadata('random',"greater_than",split_portion)
        Vetified_built_pts_test      = Verified_built_pts_randomcolumn                                       .filterMetadata('random',"not_greater_than",split_portion) 

        Vetified_non_built_pts_train = Verified_non_built_pts_randomcolumn                                      .filterMetadata('random','greater_than',split_portion)
        Vetified_non_built_pts_test  = Verified_non_built_pts_randomcolumn                                      .filterMetadata('random','not_greater_than',split_portion) 

        # Merge train/test datasets respectively.
        if Zone_sample != None:
            self.Verified_pts_train = Vetified_built_pts_train.merge(Vetified_non_built_pts_train)                                                              .merge(Zone_sample)
        else:  
            self.Verified_pts_train = Vetified_built_pts_train.merge(Vetified_non_built_pts_train)

        
        self.Verified_pts_test  = Vetified_built_pts_test.merge(Vetified_non_built_pts_test)
        
        # ________________________________Train the classifier_______________________________________
        
        # if input img provided, extract its value to Verified points, and make the classifier accordingly 
        if Input_img == None:
            
            self.Verified_pts_train_with_img_value = self.Verified_pts_train.select(self.Input_band + [self.classProperty])
            self.Verified_pts_test_with_img_value  = self.Verified_pts_test.select(self.Input_band + [self.classProperty])
            
            self.classifier = ee.Classifier.smileRandomForest(numberOfTrees = self.Tree_num)                                       .train(features        = self.Verified_pts_train_with_img_value,
                                              inputProperties = self.Input_band,
                                              classProperty   = self.classProperty)
        elif Input_band == None:
            
            self.Verified_pts_train_with_img_value = self.Input_img.sampleRegions(collection = self.Verified_pts_train, 
                                                                                  properties = [self.classProperty], 
                                                                                  scale      = 30,
                                                                                  geometries = False)

            self.Verified_pts_test_with_img_value = self.Input_img.sampleRegions(collection  = self.Verified_pts_test, 
                                                                                  properties = [self.classProperty], 
                                                                                  scale      = 30,
                                                                                  geometries = False)
            
            self.classifier = ee.Classifier.smileRandomForest(numberOfTrees = self.Tree_num)                                       .train(features        = self.Verified_pts_train_with_img_value,
                                              inputProperties = self.Input_img.bandNames().getInfo(),
                                              classProperty   = self.classProperty)
        else:
            self.Verified_pts_train_with_img_value = self.Verified_pts_train.select(self.Input_band + [self.classProperty])
            self.Verified_pts_test_with_img_value  = self.Verified_pts_test.select(self.Input_band + [self.classProperty])

            self.classifier = ee.Classifier.smileRandomForest(numberOfTrees = self.Tree_num)                                       .train(features        = self.Verified_pts_train_with_img_value,
                                              inputProperties = self.Input_band,
                                              classProperty   = self.classProperty)
            
      
    def Stp_1_Classification_on_img(self):

        self.classification_img = self.Input_img.classify(self.classifier)
   
    
    def Stp_2_Classification_on_Samples(self):
        
        # Classify the Train-data set.
        self.Train_sample_classification   = self.Verified_pts_train_with_img_value.classify(self.classifier)
        
        # Classify the Test-data set.
        self.Test_sample_classification    = self.Verified_pts_test_with_img_value.classify(self.classifier)


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




