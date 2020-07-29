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
import matplotlib.pyplot as plt


# In[2]:


ee.Initialize()


# In[3]:


class Accuracy_assesment:
    '''This class calculate the accuracy index of sample features.
    
    For input:1) classified_samples should have attributes of ['Built'],and ['classification'] 
                 or defined as [True_val] and [Pre_val]   
    
    For output: 1) the output is a dictionary like
                                   {'Overall_ACC': 76.71,
                                     'Precisioin_non_built': 76.42,
                                     'Precisioin_built': 76.98,
                                     'Recall_non_built': 76.44,
                                     'Recall_built': 76.97}
                     
    Below is an example to calculate a collection of accuracies.
    _______________________________________________________
    # Define the list to hold accuracy.
    Train_sample_acc = []
    Train_sample_supply_acc = []

    Test_sample_acc = []
    Test_sample_supply_acc = []

    # Calculate the accuracy of tree-number in range [1-10]
    for i in range(1,11):
    
        # define the tree number
        number = str(i).zfill(3)

        # fetch the samples
        train_sample_classification = ee.FeatureCollection('users/wangjinzhulala/North_China_Plain_Python/Test_samples/Single_year_all_index_Train_2017_2019_tree_' + number)    
        trian_supply_sample_classification = ee.FeatureCollection('users/wangjinzhulala/North_China_Plain_Python/Test_samples/Single_year_all_index_Train_supply_2017_2019_tree_'+ number)

        test_sample_classification = ee.FeatureCollection('users/wangjinzhulala/North_China_Plain_Python/Test_samples/Single_year_all_index_Test_2017_2019_tree_' + number)
        test_supply_sample_classification = ee.FeatureCollection('users/wangjinzhulala/North_China_Plain_Python/Test_samples/Single_year_all_index_Test_supply_2017_2019_tree_'+ number)

        # put accuracy into list.
        Train_sample_acc.append(Accuracy_assesment(train_sample_classification,number).Stp_1_Calculate_Accuracy())
        Train_sample_supply_acc.append(Accuracy_assesment(trian_supply_sample_classification,number).Stp_1_Calculate_Accuracy())

        Test_sample_acc.append(Accuracy_assesment(test_sample_classification,number).Stp_1_Calculate_Accuracy())
        Test_sample_supply_acc.append(Accuracy_assesment(test_supply_sample_classification,number).Stp_1_Calculate_Accuracy())
    _______________________________________________________
    
    '''
    def __init__(self,classified_samples,True_val ='Built',Pre_val = 'classification'):
        
        self.True_val = True_val
        self.Pre_val = Pre_val
        
        self.error_matrix = classified_samples.errorMatrix(True_val,Pre_val).getInfo()
        
        
    def Stp_1_Calculate_Accuracy(self):
    
        overall_acc =  np.diag(self.error_matrix).sum()/np.sum(self.error_matrix)
        precision_acc = np.diag(self.error_matrix)/np.sum(self.error_matrix,axis=0)
        recall_acc = np.diag(self.error_matrix)/np.sum(self.error_matrix,axis=1)

        
        value_concat = {'Overall_ACC':round(overall_acc*100,2),
                        'Precisioin_non_built':round(precision_acc[0]*100,2),
                        'Precisioin_built':round(precision_acc[1]*100,2),\
                        'Recall_non_built':round(recall_acc[0]*100,2),
                        'Recall_built':round(recall_acc[1]*100,2)}
               
        return value_concat
        
        


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




