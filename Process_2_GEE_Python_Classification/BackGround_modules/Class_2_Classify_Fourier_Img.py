#!/usr/bin/env python
# coding: utf-8

# In[1]:


import ee


# In[2]:


ee.Initialize()


# In[ ]:





# In[3]:


class Classification:

    """
    First thing first, remember to export the classfied samples, 
    otherwise, will probably get a "Momory Excedding" error!
    
    This class will
    1) perform classification on a [Input_img] using [Verified_pt]
    2) make a randomeforrest classifier based on [Tree_num] parameter
    3) extract [Training_samples] and [Testing_samples] based on given [Tree_num] parameter, and
    4) get [Train_classification] and [Test_classification] based on samples.

    For {Input}: 
    1) The [Input_img] is a string, like:
       [Input_img = "users/wang8052664/Cloud_Free_Img/Landsat_cloud_free_2017_2019"]
    2) The [year_name] is a string like '2017_2019'
    3) the [input_band] defines the bands that are used in the classification
    4) the [Verified_point] defines the sample points as the ground truthes
    4) The default [Tree_num] is 100.

    For {Output}: 
    1) Classified imgs ==>   [classification_img].
    2) Classfied samples ==> [Train_sample_classification]
                             [Test_sample_classification].
                            
    _____________________________An example of how to use this class____________________________
    
    # get necessary img and verified points
    imput_img = ee.Image("users/wang8052664/Cloud_Free_Img/Landsat_cloud_free_2017_2019")
    input_band = imput_img.bandNames().getInfo()
    Verified_point = ee.FeatureCollection("users/wangjinzhulala/North_China_Plain_Python/Sample_with_Landsat_Fourier_Nomalized_img_value/Sample_2017_2019_extract_Landsat_Fourier_Normalized_img")

    # Instatiate the class with a name.
    test = Classification(year_name ='2017_2019',
                          Input_img  = "users/wang8052664/Cloud_Free_Img/Landsat_cloud_free_2017_2019",
                          input_band = input_band,
                          Verified_point = Verified_point)


    # perform the classification on Input_img and Samples
    test.Stp_1_Classification_on_img()
    test.Stp_2_Classification_on_Samples()

    # Get the classified img
    classified_img = test.classification_img

    # Get the classified samples
    train_sample_classified        = test.Train_sample_classification
    test_sample_classified         = test.Test_sample_classification

    _______________________________________________________________________________________________
    
    
    
    """

    
    def __init__(self,year_name,
                      Input_img,
                      input_band,
                      Verified_point,
                      Tree_num      = 100,
                      classProperty = 'Built'):
        
        self.Tree_num           = Tree_num
        self.Input_img          = ee.Image(Input_img)
        self.year_name          = year_name
        self.Verified_point_all = ee.FeatureCollection(Verified_point)
        self.input_band         = input_band
        self.classProperty      = classProperty
        
        
        
        #__________________________Split the point into built and non-built________________________________________
        Verified_point_Built     =  self.Verified_point_all.filterMetadata(classProperty,'equals',1) 
        Verified_point_non_Built =  self.Verified_point_all.filterMetadata(classProperty,'equals',0) 

        # 70/30 Train/Test split on built/non-built points.
        Verified_built_pts_randomcolumn     = Verified_point_Built                                              .randomColumn(columnName = 'random',seed = 101) 
        Verified_non_built_pts_randomcolumn = Verified_point_non_Built                                              .randomColumn(columnName = 'random',seed = 101)


        Vetified_built_pts_train     = Verified_built_pts_randomcolumn                                       .filterMetadata('random',"greater_than",0.3)
        Vetified_built_pts_test      = Verified_built_pts_randomcolumn                                       .filterMetadata('random',"not_greater_than",0.3) 

        Vetified_non_built_pts_train = Verified_non_built_pts_randomcolumn                                      .filterMetadata('random','greater_than',0.3)
        Vetified_non_built_pts_test  = Verified_non_built_pts_randomcolumn                                      .filterMetadata('random','not_greater_than',0.3) 

        # Merge train/test datasets respectively.
        self.Verified_pts_train = Vetified_built_pts_train.merge(Vetified_non_built_pts_train) 
        self.Verified_pts_test  = Vetified_built_pts_test.merge(Vetified_non_built_pts_test)
        
        # ________________________________Train the classifier_______________________________________
        # Note that [smileRandomForest] is crazyly faster than [randomforest]!!!!

        self.classifier = ee.Classifier.smileRandomForest(numberOfTrees = self.Tree_num)                                       .train(features        = self.Verified_pts_train,
                                              inputProperties = self.input_band,
                                              classProperty   = self.classProperty)
        
        
    def Stp_1_Classification_on_img(self):

        self.classification_img = self.Input_img.select(self.input_band).classify(self.classifier)
   
    
    def Stp_2_Classification_on_Samples(self):
        
        # Classify the Train-data set.
        self.Train_sample_classification   = self.Verified_pts_train.select(self.input_band + [self.classProperty])                                                 .classify(self.classifier)
        
        # Classify the Test-data set.
        self.Test_sample_classification    = self.Verified_pts_test.select(self.input_band + [self.classProperty])                                                 .classify(self.classifier)


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




