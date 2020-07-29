#!/usr/bin/env python
# coding: utf-8

# In[1]:


import ee
import re
import sys


# In[2]:


ee.Initialize()


# In[ ]:





# In[2]:


class Make_Sample_Classification():
    '''This class stack 3 functions together and does not have any self.variables.
    
    function_1--> Reduce an input FeatureCollection with a given percentage
    
    function_2--> Create a list of tuples from input FeatureCollection,
      Note: the input FeatureCollection must have Landsat/Fourier/Mean-normalized band values
      The ruturn is like:
      [ ('Landsat',<FeatureCollection with {Landsat} values>)
        ('Fourier',<FeatureCollection with {Fourier} values>)
        ('Landsat_Fourier',<FeatureCollection with {Landsat and Fourier} values>)
        ('Landsat_Mean',<FeatureCollection with {Landsat and Mean_nomalized} values>)
        ('Fourier_Mean',<FeatureCollection with {Fourier and Mean_nomalized} values>)
        ('Landsat_Fourier_Mean',<FeatureCollection with {Landsat_Fourier_Mean} values>)]
                                        
    function_3--> Create sample_classificaiton instances (aka, classified sample point) without actual computation in GEE
      Note: need to from Class_2_Classify_Fourier_Img import Classification first to use this funcion
      In this function,:
      1) the input {verified_pt} will be split into a 7/3 partition, then
      2) create a classifier (hidden in the Classificaiton class) from the 7 portion, and
      3) use the classsifier to classify the left 3 portion of sample points and ,
      4) return the classified sample with multiindex of (year,combo_name,percent,tree)
                                    
    ___________________________________________Sample of Make_Sample_Classification__________________________________________
    # define variables for the Sample_classification clas
    year_name     = ['2017_2019','2011_2013', '2008_2010']
    percent_value = [0,1,2,3,5,7,10,20,30,50,70,100]
    tree_num      = [1] + list(range(10,121,10))

    # define the path to point_with_img_value 
    path = 'users/wangjinzhulala/North_China_Plain_Python/Sample_extract_img'

    # instantiate the combo_instance dictionary
    Combo_instance_with_village = {}

    # Create sample_classification instances through [year] --> [Percent] --> [band_combination] --> [Tree]
    for year in year_name:
    
    Invarient_sample = ee.FeatureCollection(f'{path}/Control_sample_ext_img_{year}')
    
    # import samples
    Invarient_built      = Invarient_sample.filterMetadata('Built','equals',1)
    Invarient_non_Built  = Invarient_sample.filterMetadata('Built','equals',0)
       
    for pct in percent_value:
        
        # Create percentage_reduced samples, only use non-built points from verified points
        Subset_Invarient_built     = Make_Sample_Classification.Step_1_Subset_sample(Invarient_built,pct)
        Subset_Invarient_non_Built = Make_Sample_Classification.Step_1_Subset_sample(Invarient_non_Built,pct)
        
        # Merge the built and non-built points that been percentage reduced
        Sample_merge = Subset_Invarient_built.merge(Subset_Invarient_non_Built)
        
        # Get the band_combo names
        Band_combo   = Make_Sample_Classification.Step_2_Create_Band_Combo(Sample_merge)
        
        for combo in Band_combo:
            Accuracy_instance = Make_Sample_Classification.\
                                Step_3_Create_Classification_Instance(year,Sample_merge,
                                                                      combo,tree_num,
                                                                      pct,classificaiton_func = Classification ) 
            Combo_instance_with_village.update(Accuracy_instance)
    
    '''
    
    def __init__():
        pass
    
    def Step_1_Subset_sample(In_sample,percent):

        Sample_select_num = int(In_sample.size().getInfo() * percent /100)
        print(f'Percetage coresponded size is {Sample_select_num}')

        # add some randomness so to make the result more reliable
        return In_sample.randomColumn('x', 101).limit(Sample_select_num,'x')

    def Step_2_Create_Band_Combo(fe):

        # use the first element to get all band name
        bands = list(fe.first().getInfo()['properties'].keys())

        # get the Landsat_band
        Landsat_re   = re.compile(r'^B\d')
        Landsat_band = list(filter(Landsat_re.match,bands))

        # get the Fourier_band
        Fourier_re   = re.compile(r'^EVI|NDBI|NDVI')
        Fourier_band = list(filter(Fourier_re.match,bands))

        # get the Mean_Normalized band
        Mean_re         = re.compile(r'^Mean')
        Mean_Normalized = list(filter(Mean_re.match,bands))
        
        # get the Climate band
        Climate_band = ['lrad','prec','pres','shum','srad','temp','wind']
        
        # get the Terrain band
        Terrain_band = ['DEM','SLOPE']

        # ________________________Create sample classification instaces_____________________________

        # create band_combinations
        band_combination = [Landsat_band,
                            Fourier_band,
                            Landsat_band + Fourier_band,
                            Landsat_band + Mean_Normalized,
                            Fourier_band + Mean_Normalized,
                            Landsat_band + Fourier_band + Mean_Normalized,
                            Landsat_band + Fourier_band + Mean_Normalized + Climate_band,
                            Landsat_band + Fourier_band + Mean_Normalized + Terrain_band,
                            Landsat_band + Fourier_band + Mean_Normalized + Climate_band + Terrain_band]

        # create comno_names
        global combination_name
        combination_name = ['Landsat',
                            'Fourier',
                            'Landsat_Fourier',
                            'Landsat_Mean',
                            'Fourier_Mean',
                            'Landsat_Fourier_Mean',
                            'Landsat_Fourier_Mean_Climate',
                            'Landsat_Fourier_Mean_Terrain',
                            'Landsat_Fourier_Mean_Terrain_Climate']


        return list(zip(combination_name,band_combination))

    def Step_3_Create_Classification_Instance(year,verified_pt,combo,tree_list,percent,classificaiton_func):
        # Initiate the Combo_dict
        Combo_acc_dict = {}

        for tree in tree_list:

            combo_name = combo[0]
            combo_band = combo[1]

            # Instatiate the class with a name
            Sample_classification = classificaiton_func( year_name    = year,
                                                  Input_band     = combo_band,
                                                  Verified_point = verified_pt,
                                                  Tree_num       = tree)

            # Proceed the classification
            Sample_classification.Stp_2_Classification_on_Samples()

            # add accuracy to the dictionary
            Combo_acc_dict.update({(year,combo_name,percent,tree) : Sample_classification.Test_sample_classification})

            # print out the process
            print(f'Classification of {year}_{combo_name}_pct_{percent:03}_tree_{tree:04} completed!')

        # get the accuracy value
        return Combo_acc_dict


# In[ ]:





# In[ ]:





# In[ ]:




