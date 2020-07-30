#!/usr/bin/env python
# coding: utf-8

# In[6]:


import ee


# In[7]:


ee.Initialize()


# In[ ]:





# In[43]:


class Classification:

    """
    This class will
    1) perform classification on a [Input_img] using [Verified_pt]
    2) make a randomeforrest classifier based on [Tree_num] parameter
    3) split input sample(Verified_sample) into [Training_samples] and [Testing_samples] 
    4) get [Train_classification] and [Test_classification] based on samples.
    
    NOTE: Input sample should already have the preperties from input img.
    
    For {Input}: 
    1) The [Input_img] is a string, like:
       [Input_img = "users/wang8052664/Cloud_Free_Img/Landsat_cloud_free_2017_2019"]
    2) The [year_name] is a string like '2017_2019'
    3) the [Input_band] defines the bands that are used in the classification
    4) the [Verified_point] defines the sample points as the ground truthes,
    5) the [seed] determines the random state of the training point, default to be 101,
    6) the [split_portion] determines how to perform trian/test split, training points are theose > split_portion,
    7) the [classProperty] is default to 'Built', which is the column name for ground truth,
    8) The default [Tree_num] is 100.

    For {Output}: 
    1) Classified imgs ==>   [classification_img].
    2) Classfied samples ==> [Train_sample_classification]
                             [Test_sample_classification].
                            
    
    
    __________________________________Sample for classfication on IMAGE___________________________________

    # prepare the input_sample points
    input_point = ee.FeatureCollection("users/wangjinzhulala/North_China_Plain_Python/Sample_extract_img/Control_sample_ext_img_2017_2019")

    # get necessary img and verified points
    imput_img = ee.Image("users/wang8052664/North_China_Plain/Fourier_imgs/Fourier_img_2017_2019_harmonic_3")

    # define the bands that are included in the classification
    input_bands = ['NDVI_cos_1','NDVI_cos_2','NDVI_cos_3']

    # Instatiate the class with a name.
    classification = Classification(year_name      ='2017_2019',
                           Input_img      = imput_img,
                           Verified_point = input_point,
                           Input_band     = input_bands)


    # Get the classified img
    classified_img = classification.classification_img

    # Get the classifier
    Classifier = classification.classifier

    # Get the classified samples
    train_sample_classified        = classification.Train_sample_classification
    test_sample_classified         = classification.Test_sample_classification

       
    """

    
    def __init__(self,year_name,
                      Verified_point,
                      Input_img     = None,
                      Input_band    = None,
                      Tree_num      = 100,
                      seed          = 100,
                      split_portion = 0.3,
                      classProperty = 'Built'):
        
        # initiate the variables
        self.Tree_num           = Tree_num
        self.Input_img          = Input_img.select(Input_band)
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
        self.Verified_pts_train = Vetified_built_pts_train.merge(Vetified_non_built_pts_train)
        self.Verified_pts_test  = Vetified_built_pts_test.merge(Vetified_non_built_pts_test)
        
        
        
        # ________________________________Train the classifier_______________________________________
        
        # here use input_bands to select the features that included in the classification
        self.Verified_pts_train_with_img_value = self.Verified_pts_train.select(self.Input_band + [self.classProperty])
        self.Verified_pts_test_with_img_value  = self.Verified_pts_test.select(self.Input_band + [self.classProperty])

        self.classifier = ee.Classifier.smileRandomForest(numberOfTrees = self.Tree_num)                                       .train(features        = self.Verified_pts_train_with_img_value,
                                              inputProperties = self.Input_band,
                                              classProperty   = self.classProperty)

      

        #_________________________________Perfor the classification on input_img and Train/Test samples.
        
        # Classify the input_img
        self.classification_img = self.Input_img.classify(self.classifier)
        
        # Classify the Train-data set.
        self.Train_sample_classification   = self.Verified_pts_train_with_img_value.classify(self.classifier)
        
        # Classify the Test-data set.
        self.Test_sample_classification    = self.Verified_pts_test_with_img_value.classify(self.classifier)


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




