#!/usr/bin/env python
# coding: utf-8

# In[1]:


import ee
import re
import sys


# In[2]:


ee.Initialize()


# In[ ]:





# In[18]:


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
                                        
    function_3--> Create sample_classificaiton instances (aka, classified sample point) without computation in GEE
      Note: need to from Class_2_Classify_Fourier_Img import Classification first to use this funcion
      In this function,:
      1) the input {verified_pt} will be split into a 7/3 partition, the
      2) create a classifier (hidden in the Classificaiton class) from the 7 portion, and
      3) use the classsifier to classify the left 3 portion of sample points and ,
      4) return the classified sample with multiindex of (year,combo_name,percent,tree)
                                    
    ___________________________________________Sample of Make_Sample_Classification__________________________________________
    # define variables for the Sample_classification clas
    year_name     = ['2017_2019','2011_2013', '2008_2010']
    percent_value = [0,1,2,3,5,7,10,20,30,50,70,100]
    tree_num      = [1] + list(range(10,121,10))

    # define the path to point_with_value GEE-Path
    path = 'users/Jinzhu_Deakin/North_China_Plain/Sample_with_Landsat_Fourier_Normalized'

    # instantiate the combo_instance dictionary
    Combo_instance_with_village = {}

    # Create sample_classification instances through [year] --> [Percent] --> [band_combination] --> [Tree]
    for year in year_name:

        # import samples
        Verified_sample = ee.FeatureCollection(f'{path}/Verified_point_{year}_extract_Landsat_Fourier_Normalized_img')\
                            .filterMetadata('Built', 'equals', 0)
        Village_sample  = ee.FeatureCollection(f'{path}/Village_point_{year}_extract_Landsat_Fourier_Normalized_img')

        # make sure they are the same size.
        min_size = min(Verified_sample.size().getInfo(),Village_sample.size().getInfo())
        Verified_sample = Verified_sample.randomColumn('z', 101).limit(min_size,'z')
        Village_sample  = Village_sample.randomColumn('z', 101).limit(min_size,'z')

        for pct in percent_reduction:

            # Create percentage_reduced samples, only use non-built points from verified points
            Subset_verified_sample  = Make_Sample_Classification.Step_1_Subset_sample(Verified_sample,pct)
            Subset_village_sample   = Make_Sample_Classification.Step_1_Subset_sample(Village_sample,pct)

            # Merge Verified_points with Zone_points
            Sample_merge = Subset_verified_sample.merge(Subset_village_sample)

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

        # ________________________Create sample classification instaces_____________________________

        # create band_combinations
        band_combination = [Landsat_band,
                            Fourier_band,
                            Landsat_band + Fourier_band,
                            Landsat_band + Mean_Normalized,
                            Fourier_band + Mean_Normalized,
                            Landsat_band + Fourier_band + Mean_Normalized]

        # create comno_names
        global combination_name
        combination_name = ['Landsat',
                            'Fourier',
                            'Landsat_Fourier',
                            'Landsat_Mean',
                            'Fourier_Mean',
                            'Landsat_Fourier_Mean']


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




